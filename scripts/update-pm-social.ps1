param(
    [string]$ConfigPath = 'research\pm-social-sources.json',
    [string]$DataDirectory = 'research\data\pm-social',
    [string]$StatusFile = 'research\pm-sns-monitor-status.md',
    [ValidateRange(5, 100)]
    [int]$MaxItems = 25
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

function Import-DotEnv {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return }

    foreach ($line in Get-Content -Encoding UTF8 -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith('#')) { continue }
        if ($trimmed.StartsWith('export ')) { $trimmed = $trimmed.Substring(7).Trim() }
        $separator = $trimmed.IndexOf('=')
        if ($separator -lt 1) { continue }

        $name = $trimmed.Substring(0, $separator).Trim()
        $value = $trimmed.Substring($separator + 1).Trim()
        if ($name -notmatch '^[A-Za-z_][A-Za-z0-9_]*$') { continue }
        if ($value.Length -ge 2 -and (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'")))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name, 'Process'))) {
            [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        }
    }
}

Import-DotEnv (Join-Path $repoRoot '.env')

function Get-UtcTimestamp {
    return [DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
}

function Get-ObjectProperty {
    param($Object, [string]$Name, $Default = $null)
    if ($null -eq $Object) { return $Default }
    if ($Object -is [Collections.IDictionary]) {
        if ($Object.Contains($Name)) { return $Object[$Name] }
        return $Default
    }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $Default }
    return $property.Value
}

function Get-Sha256Hex {
    param([string]$Value)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        $hash = $algorithm.ComputeHash([Text.Encoding]::UTF8.GetBytes($Value))
        return ([BitConverter]::ToString($hash)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $algorithm.Dispose()
    }
}

function ConvertTo-StateTable {
    param($StateObject)
    $table = [ordered]@{}
    if ($null -ne $StateObject) {
        foreach ($property in $StateObject.PSObject.Properties) {
            $table[$property.Name] = $property.Value
        }
    }
    return $table
}

function Get-SourceKey {
    param([string]$PersonSlug, $Source)
    $identity = Get-ObjectProperty $Source 'handle'
    if (-not $identity) { $identity = $Source.url }
    return "$PersonSlug`:$($Source.platform)`:$identity"
}

function Invoke-PublicRequest {
    param(
        [string]$Uri,
        [hashtable]$Headers = @{},
        [switch]$AsWebResponse
    )
    $mergedHeaders = @{
        'User-Agent' = 'mitou-pm-public-research/1.0 (+local research monitor)'
        'Accept' = 'application/json, application/xml, text/xml, text/html;q=0.8'
    }
    foreach ($key in $Headers.Keys) { $mergedHeaders[$key] = $Headers[$key] }
    try {
        if ($AsWebResponse) {
            return Invoke-WebRequest -UseBasicParsing -Uri $Uri -Headers $mergedHeaders -TimeoutSec 30
        }
        return Invoke-RestMethod -Uri $Uri -Headers $mergedHeaders -TimeoutSec 30
    }
    catch {
        $responseBody = ''
        if ($_.Exception.Response) {
            $responseStream = $_.Exception.Response.GetResponseStream()
            if ($responseStream) {
                $reader = [IO.StreamReader]::new($responseStream)
                try { $responseBody = $reader.ReadToEnd() } finally { $reader.Dispose() }
            }
        }
        if ($responseBody) {
            if ($responseBody.Length -gt 500) { $responseBody = $responseBody.Substring(0, 500) }
            throw "Request failed for $Uri`: $responseBody"
        }
        throw "Request failed for $Uri`: $($_.Exception.Message)"
    }
}

function Get-XItems {
    param($Source, [hashtable]$State, [string]$Token, [int]$Limit, [string]$FetchedAt)
    $headers = @{ Authorization = "Bearer $Token" }
    $handle = [string]$Source.handle
    $userId = Get-ObjectProperty $State 'user_id'
    $profile = Get-ObjectProperty $State 'profile'
    if (-not $userId) {
        $encodedHandle = [Uri]::EscapeDataString($handle)
        $lookupUri = "https://api.x.com/2/users/by/username/${encodedHandle}?user.fields=created_at,description,public_metrics,verified"
        $lookup = Invoke-PublicRequest -Uri $lookupUri -Headers $headers
        if (-not $lookup.data) { throw "X user lookup failed for @$handle" }
        $profile = $lookup.data
        $userId = [string]$lookup.data.id
    }

    $parameters = [ordered]@{
        max_results = [string]$Limit
        exclude = 'replies,retweets'
        'tweet.fields' = 'created_at,public_metrics,lang,conversation_id'
    }
    $priorMaxId = Get-ObjectProperty $State 'max_item_id'
    if ($priorMaxId) { $parameters.since_id = [string]$priorMaxId }
    $queryParts = foreach ($entry in $parameters.GetEnumerator()) {
        '{0}={1}' -f [Uri]::EscapeDataString([string]$entry.Key), [Uri]::EscapeDataString([string]$entry.Value)
    }
    $timelineUri = "https://api.x.com/2/users/${userId}/tweets?$($queryParts -join '&')"
    $timeline = Invoke-PublicRequest -Uri $timelineUri -Headers $headers
    if ($timeline.errors -and -not $timeline.data) {
        throw "X timeline failed for @$handle`: $($timeline.errors | ConvertTo-Json -Compress)"
    }

    $items = @()
    foreach ($post in @($timeline.data)) {
        if ($null -eq $post) { continue }
        $postId = [string]$post.id
        $items += [pscustomobject][ordered]@{
            id = $postId
            platform = 'x'
            author_handle = $handle
            url = "https://x.com/$handle/status/$postId"
            published_at = $post.created_at
            text = [string]$post.text
            lang = $post.lang
            public_metrics = $post.public_metrics
            fetched_at = $FetchedAt
        }
    }
    $maxId = $priorMaxId
    if ($items.Count -gt 0) {
        $maxId = ($items | ForEach-Object { [System.Numerics.BigInteger]::Parse($_.id) } | Sort-Object -Descending | Select-Object -First 1).ToString()
    }
    return [pscustomobject]@{
        Items = $items
        State = [ordered]@{ user_id = $userId; profile = $profile; max_item_id = $maxId }
    }
}

function Get-GitHubItems {
    param($Source, [hashtable]$State, [string]$Token, [int]$Limit, [string]$FetchedAt)
    $headers = @{
        Accept = 'application/vnd.github+json'
        'X-GitHub-Api-Version' = '2022-11-28'
    }
    if ($Token) { $headers.Authorization = "Bearer $Token" }
    $handle = [string]$Source.handle
    $encodedHandle = [Uri]::EscapeDataString($handle)
    $events = @(Invoke-PublicRequest -Uri "https://api.github.com/users/$encodedHandle/events/public?per_page=$Limit" -Headers $headers)
    $items = @()
    foreach ($event in $events) {
        if ($null -eq $event) { continue }
        $repo = Get-ObjectProperty $event.repo 'name'
        $url = $Source.url
        if ($repo) { $url = "https://github.com/$repo" }
        $items += [pscustomobject][ordered]@{
            id = [string]$event.id
            platform = 'github'
            author_handle = $handle
            url = $url
            published_at = $event.created_at
            text = (([string]$event.type + ' ' + [string]$repo).Trim())
            event_type = $event.type
            repository = $repo
            fetched_at = $FetchedAt
        }
    }
    $maxId = Get-ObjectProperty $State 'max_item_id'
    if ($items.Count -gt 0) { $maxId = $items[0].id }
    return [pscustomobject]@{ Items = $items; State = [ordered]@{ max_item_id = $maxId } }
}

function Get-NodeText {
    param($Node, [string[]]$Names)
    foreach ($name in $Names) {
        $match = $Node.SelectSingleNode("./*[local-name()='$name']")
        if ($null -ne $match -and $match.InnerText) { return $match.InnerText.Trim() }
    }
    return ''
}

function ConvertTo-CleanText {
    param([string]$Text)
    if (-not $Text) { return '' }
    $decoded = [Net.WebUtility]::HtmlDecode($Text)
    $withoutTags = [regex]::Replace($decoded, '<[^>]+>', ' ')
    return [regex]::Replace($withoutTags, '\s+', ' ').Trim()
}

function Get-RssItems {
    param($Source, [hashtable]$State, [int]$Limit, [string]$FetchedAt)
    $response = Invoke-PublicRequest -Uri $Source.url -Headers @{ Accept = 'application/rss+xml, application/atom+xml, text/xml' } -AsWebResponse
    [xml]$feed = $response.Content
    $nodes = @($feed.SelectNodes("//*[local-name()='item' or local-name()='entry']"))
    $terms = @((Get-ObjectProperty $Source 'include_terms' @()) | ForEach-Object { ([string]$_).ToLowerInvariant() })
    $items = @()
    foreach ($node in $nodes) {
        $title = Get-NodeText $node @('title')
        $description = Get-NodeText $node @('description', 'summary', 'content', 'encoded')
        $link = Get-NodeText $node @('link')
        if (-not $link) {
            $linkNode = $node.SelectSingleNode("./*[local-name()='link' and @href]")
            if ($linkNode) { $link = [string]$linkNode.href }
        }
        $published = Get-NodeText $node @('pubDate', 'published', 'updated', 'date')
        $guid = Get-NodeText $node @('guid', 'id')
        if (-not $guid) { $guid = if ($link) { $link } else { $title } }
        $clean = ConvertTo-CleanText "$title - $description"
        $haystack = $clean.ToLowerInvariant()
        if ($terms.Count -gt 0 -and -not @($terms | Where-Object { $haystack.Contains($_) }).Count) { continue }
        $dateValue = $published
        try { $dateValue = ([DateTimeOffset]::Parse($published)).ToUniversalTime().ToString('o') } catch {}
        $id = (Get-Sha256Hex $guid).Substring(0, 24)
        if ($clean.Length -gt 4000) { $clean = $clean.Substring(0, 4000) }
        $items += [pscustomobject][ordered]@{
            id = $id
            platform = $Source.platform
            url = if ($link) { $link } else { $Source.url }
            published_at = $dateValue
            text = $clean
            fetched_at = $FetchedAt
        }
        if ($items.Count -ge $Limit) { break }
    }
    $maxId = Get-ObjectProperty $State 'max_item_id'
    if ($items.Count -gt 0) { $maxId = $items[0].id }
    return [pscustomobject]@{ Items = $items; State = [ordered]@{ max_item_id = $maxId } }
}

function Get-WebHashItems {
    param($Source, [hashtable]$State, [string]$FetchedAt)
    $response = Invoke-PublicRequest -Uri $Source.url -Headers @{ Accept = 'text/html' } -AsWebResponse
    $digest = Get-Sha256Hex ([string]$response.Content)
    $priorHash = Get-ObjectProperty $State 'content_hash'
    $items = @()
    if (-not $priorHash -or $priorHash -ne $digest) {
        $message = if ($priorHash) { 'Public page content changed' } else { 'Public page availability and hash checked' }
        $items += [pscustomobject][ordered]@{
            id = $digest
            platform = $Source.platform
            url = $Source.url
            published_at = $null
            text = $message
            fetched_at = $FetchedAt
        }
    }
    return [pscustomobject]@{ Items = $items; State = [ordered]@{ content_hash = $digest } }
}

function Merge-Items {
    param($PriorItems, $NewItems, [int]$Limit)
    $byKey = @{}
    foreach ($item in @($PriorItems) + @($NewItems)) {
        if ($null -eq $item) { continue }
        $key = "$($item.platform):$($item.id)"
        $byKey[$key] = $item
    }
    return @($byKey.Values | Sort-Object -Property published_at, id -Descending | Select-Object -First $Limit)
}

try {
    $config = Get-Content -Raw -Encoding UTF8 $ConfigPath | ConvertFrom-Json
    $latestPath = Join-Path $DataDirectory 'latest.json'
    $eventsPath = Join-Path $DataDirectory 'events.ndjson'
    $priorSnapshot = $null
    if (Test-Path $latestPath) { $priorSnapshot = Get-Content -Raw -Encoding UTF8 $latestPath | ConvertFrom-Json }
    $priorSources = @{}
    foreach ($person in @(Get-ObjectProperty $priorSnapshot 'people' @())) {
        foreach ($source in @($person.sources)) { $priorSources[[string]$source.key] = $source }
    }

    $knownEvents = [Collections.Generic.HashSet[string]]::new()
    if (Test-Path $eventsPath) {
        foreach ($line in Get-Content -Encoding UTF8 $eventsPath) {
            if (-not $line.Trim()) { continue }
            try { [void]$knownEvents.Add([string](($line | ConvertFrom-Json).event_key)) } catch {}
        }
    }

    $fetchedAt = Get-UtcTimestamp
    $xToken = [Environment]::GetEnvironmentVariable('X_BEARER_TOKEN')
    if (-not $xToken) { $xToken = [Environment]::GetEnvironmentVariable('BEARER_TOKEN') }
    $githubToken = [Environment]::GetEnvironmentVariable('GITHUB_TOKEN')
    $outputPeople = @()
    $newEvents = @()

    foreach ($person in $config.people) {
        $outputSources = @()
        foreach ($source in $person.sources) {
            $key = Get-SourceKey $person.slug $source
            $prior = $priorSources[$key]
            if ($null -ne $prior -and [string]$prior.kind -ne [string]$source.kind) {
                $prior = $null
            }
            $state = ConvertTo-StateTable (Get-ObjectProperty $prior 'state')
            $newItems = @()
            $runStatus = $null
            try {
                switch ([string]$source.kind) {
                    'x_api' {
                        if (-not $xToken) {
                            $runStatus = [pscustomobject]@{ status = 'skipped'; message = 'X_BEARER_TOKEN required' }
                        } else {
                            $result = Get-XItems $source $state $xToken $MaxItems $fetchedAt
                            $newItems = @($result.Items)
                            $state = $result.State
                            $runStatus = [pscustomobject]@{ status = 'ok'; message = "$($newItems.Count) new" }
                        }
                    }
                    'github_events' {
                        $result = Get-GitHubItems $source $state $githubToken $MaxItems $fetchedAt
                        $newItems = @($result.Items)
                        $state = $result.State
                        $runStatus = [pscustomobject]@{ status = 'ok'; message = "$($newItems.Count) fetched" }
                    }
                    'rss' {
                        $result = Get-RssItems $source $state $MaxItems $fetchedAt
                        $newItems = @($result.Items)
                        $state = $result.State
                        $runStatus = [pscustomobject]@{ status = 'ok'; message = "$($newItems.Count) matched" }
                    }
                    'web_hash' {
                        $result = Get-WebHashItems $source $state $fetchedAt
                        $newItems = @($result.Items)
                        $state = $result.State
                        $runStatus = [pscustomobject]@{ status = 'ok'; message = 'checked' }
                    }
                    default {
                        $runStatus = [pscustomobject]@{ status = 'manual'; message = [string]$source.status }
                    }
                }
            } catch {
                $runStatus = [pscustomobject]@{ status = 'error'; message = $_.Exception.Message.Substring(0, [Math]::Min(240, $_.Exception.Message.Length)) }
            }

            $items = @(Merge-Items (Get-ObjectProperty $prior 'items' @()) $newItems $MaxItems)
            $outputSource = [ordered]@{}
            foreach ($property in $source.PSObject.Properties) { $outputSource[$property.Name] = $property.Value }
            $outputSource.key = $key
            $outputSource.run_status = $runStatus
            $outputSource.state = $state
            $outputSource.last_attempt_at = $fetchedAt
            $outputSource.items = [object[]]$items
            $outputSource.new_items = $newItems
            if ($runStatus.status -eq 'ok') { $outputSource.last_success_at = $fetchedAt }
            elseif (Get-ObjectProperty $prior 'last_success_at') { $outputSource.last_success_at = $prior.last_success_at }
            $outputSources += [pscustomobject]$outputSource

            foreach ($item in $newItems) {
                $eventKey = "$key`:$($item.id)"
                if ($knownEvents.Add($eventKey)) {
                    $newEvents += [pscustomobject][ordered]@{
                        event_key = $eventKey
                        person_slug = $person.slug
                        person_name = $person.name
                        role = $person.role
                        source_key = $key
                        first_seen_at = $item.fetched_at
                        item = $item
                    }
                }
            }
        }
        $outputPeople += [pscustomobject][ordered]@{ slug = $person.slug; name = $person.name; role = $person.role; sources = $outputSources }
    }

    New-Item -ItemType Directory -Path $DataDirectory -Force | Out-Null
    foreach ($event in $newEvents) {
        Add-Content -Encoding UTF8 -Path $eventsPath -Value ($event | ConvertTo-Json -Depth 20 -Compress)
    }
    foreach ($person in $outputPeople) {
        foreach ($source in $person.sources) { $source.PSObject.Properties.Remove('new_items') }
    }

    $snapshot = [pscustomobject][ordered]@{
        schema_version = 1
        fetched_at = $fetchedAt
        official_pm_page = $config.official_pm_page
        credentials = [pscustomobject]@{ x_bearer_token = [bool]$xToken; github_token = [bool]$githubToken }
        new_event_count = $newEvents.Count
        people = $outputPeople
    }
    $snapshot | ConvertTo-Json -Depth 30 | Set-Content -Encoding UTF8 $latestPath

    $xAuthText = if ($xToken) { 'configured' } else { 'missing' }
    $gitHubAuthText = if ($githubToken) { 'configured' } else { 'missing (public API still works)' }
    $lines = @(
        '# MITOU Advanced PM public-source monitor',
        '',
        "- Last run: $fetchedAt",
        "- New events: $($newEvents.Count)",
        "- X API auth: $xAuthText",
        "- GitHub auth: $gitHubAuthText",
        '- LinkedIn, Facebook, and Wantedly third-party personal posts are manual-only because of official API access restrictions.',
        '',
        '| Role | Name | Platform | Method | Status | Saved | URL |',
        '|---|---|---|---|---|---:|---|'
    )
    foreach ($person in $snapshot.people) {
        foreach ($source in $person.sources) {
            $statusText = [string]$source.run_status.status
            if ($source.run_status.message) { $statusText += ': ' + ([string]$source.run_status.message).Replace('|', '/') }
            $savedCount = 0
            if ($null -ne $source.items) { $savedCount = @($source.items).Count }
            $lines += "| $($person.role) | $($person.name) | $($source.platform) | $($source.kind) | $statusText | $savedCount | [link]($($source.url)) |"
        }
    }
    $lines += @(
        '',
        '## Operation',
        '',
        '- Manual run: `powershell -ExecutionPolicy Bypass -File scripts/update-pm-social.ps1`',
        '- Register Windows task: `powershell -ExecutionPolicy Bypass -File scripts/install-pm-social-task.ps1`',
        '- X API auth: set `BEARER_TOKEN` in the gitignored root `.env`, or set the process environment variable `X_BEARER_TOKEN`.',
        '- See `research/pm-sns-and-pitch-signals-2026-08-14.md` for the analysis.',
        ''
    )
    $lines -join "`n" | Set-Content -Encoding UTF8 $StatusFile

    $logDirectory = Join-Path $DataDirectory 'logs'
    New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
    $logPath = Join-Path $logDirectory ((Get-Date -Format 'yyyy-MM-dd') + '.log')
    Add-Content -Encoding UTF8 -Path $logPath -Value "$fetchedAt new_events=$($newEvents.Count) x_auth=$([bool]$xToken)"
    Write-Output "updated $latestPath; new events=$($newEvents.Count); x_auth=$([bool]$xToken)"
}
finally {
    Pop-Location
}
