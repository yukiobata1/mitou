# MITOU Advanced PM public-source monitor

- Last run: 2026-10-20T22:02:11Z
- New events: 1
- X API auth: configured
- GitHub auth: missing (public API still works)
- LinkedIn, Facebook, and Wantedly third-party personal posts are manual-only because of official API access restrictions.

| Role | Name | Platform | Method | Status | Saved | URL |
|---|---|---|---|---|---:|---|
| 統括PM | 竹内郁雄 | linkedin | manual | manual: profile_visible_no_recent_posts_confirmed | 0 | [link](https://www.linkedin.com/in/ikuo-takeuchi-4b145694/) |
| 統括PM | 竹内郁雄 | note | manual | manual: published_2025-02-17 | 0 | [link](https://note.com/ipsj/n/n1036cbfab26e) |
| 統括PM | 夏野剛 | x | x_api | ok: 0 new | 25 | [link](https://x.com/tnatsu) |
| 統括PM | 夏野剛 | linkedin | manual | manual: profile_visible | 0 | [link](https://www.linkedin.com/in/takeshi-natsuno-ab3778342/) |
| 統括PM | 夏野剛 | facebook | manual | manual: profile_visible_posts_login_gated | 0 | [link](https://www.facebook.com/tnatsu) |
| 統括PM | 夏野剛 | niconico | manual | manual: official_channel | 0 | [link](https://ch.nicovideo.jp/natsuno) |
| PM | 石黒浩 | x | x_api | ok: 1 new | 25 | [link](https://x.com/hiroshiishiguro) |
| PM | 石黒浩 | linkedin | manual | manual: profile_visible_no_recent_posts_confirmed | 0 | [link](https://www.linkedin.com/in/hiroshi-ishiguro-7b30072b/) |
| PM | 石黒浩 | note | rss | ok: 6 matched | 6 | [link](https://note.com/avita/rss) |
| PM | 漆原茂 | x | x_api | ok: 0 new | 20 | [link](https://x.com/urucrunch) |
| PM | 漆原茂 | linkedin | manual | manual: active_but_api_restricted | 0 | [link](https://www.linkedin.com/in/shigeru-urushibara/) |
| PM | 漆原茂 | facebook | manual | manual: public_profile_partial_posts_login_gated | 0 | [link](https://www.facebook.com/shigeru.urushibara) |
| PM | 梶田真実 | linkedin | manual | manual: profile_visible_no_recent_posts_confirmed | 0 | [link](https://www.linkedin.com/in/mamikajita/) |
| PM | 梶田真実 | wantedly | manual | manual: profile_visible_no_stories_confirmed | 0 | [link](https://www.wantedly.com/id/mami_kajita) |
| PM | 梶田真実 | facebook | manual | manual: unavailable_2026-08-14 | 0 | [link](https://www.facebook.com/mami.kajitapp/) |
| PM | 首藤一幸 | x | x_api | ok: 0 new | 25 | [link](https://x.com/shudo) |
| PM | 首藤一幸 | linkedin | manual | manual: profile_visible_no_recent_posts_confirmed | 0 | [link](https://www.linkedin.com/in/shudo/) |
| PM | 首藤一幸 | github | github_events | ok: 1 fetched | 1 | [link](https://github.com/shudo) |
| PM | 首藤一幸 | facebook | manual | manual: lab_account_not_personal | 0 | [link](https://www.facebook.com/shudolab) |
| PM | 原田達也 | lab_blog | web_hash | ok: checked | 3 | [link](https://www.mi.t.u-tokyo.ac.jp/harada/) |
| PM | 原田達也 | lab_blog | manual | manual: published_2023-01-20 | 0 | [link](https://www.mi.t.u-tokyo.ac.jp/blog/research/statement/) |
| PM | 平野豊 | linkedin | manual | manual: profile_visible_no_recent_posts_confirmed | 0 | [link](https://www.linkedin.com/in/yutaka-hirano-6617451b7/) |
| PM | 藤井彰人 | linkedin | manual | manual: profile_visible_sparse_self_authored_posts | 0 | [link](https://www.linkedin.com/in/akihitofujii/) |
| PM | 三木寛文 | wantedly | manual | manual: profile_visible_no_stories_confirmed | 0 | [link](https://www.wantedly.com/id/hirofumi_miki) |
| PM | 三木寛文 | professional_profile | manual | manual: owned_profile_not_sns_dynamic_page | 0 | [link](https://portal.mirai-cross.ventures/advisory/hirofumimiki/) |
| PM | 吉崎航 | x | x_api | ok: 0 new | 25 | [link](https://x.com/W_Yoshizaki) |
| PM | 吉崎航 | facebook | manual | manual: unavailable_2026-08-14 | 0 | [link](https://www.facebook.com/wataru.yoshizaki) |
| PM | 吉崎航 | note | rss | ok: 2 matched | 2 | [link](https://note.com/asratec/rss) |

## Operation

- Manual run: `powershell -ExecutionPolicy Bypass -File scripts/update-pm-social.ps1`
- Register Windows task: `powershell -ExecutionPolicy Bypass -File scripts/install-pm-social-task.ps1`
- X API auth: set `BEARER_TOKEN` in the gitignored root `.env`, or set the process environment variable `X_BEARER_TOKEN`.
- See `research/pm-sns-and-pitch-signals-2026-08-14.md` for the analysis.

