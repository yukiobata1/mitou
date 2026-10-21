$ErrorActionPreference = 'Stop'

$secureToken = Read-Host 'Enter X API Bearer Token (input is hidden)' -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
try {
    $plainToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    if ([string]::IsNullOrWhiteSpace($plainToken)) {
        throw 'Token was empty.'
    }
    [Environment]::SetEnvironmentVariable('X_BEARER_TOKEN', $plainToken, 'User')
}
finally {
    if ($pointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
    }
    $plainToken = $null
    $secureToken.Dispose()
}

Write-Output 'X_BEARER_TOKEN was stored in the current Windows user environment.'
Write-Output 'Run scripts\update-pm-social.ps1 from a new PowerShell process to verify it.'
