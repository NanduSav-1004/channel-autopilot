# Runbook

How the channel runs, how to tell it is healthy, and what to do when it is not.

## What runs, and when
- **GitHub Actions workflow "Daily video"** is scheduled five times a day, at **02:17, 04:43, 08:17, 09:43 and 11:11 UTC**
  (7:47 AM, 10:13 AM, 1:47 PM, 3:13 PM and 4:41 PM IST). GitHub has been starting scheduled runs 5+ hours late, so
  the early slots exist to land before the 15:00 UTC go-live slot. GitHub's scheduler is best-effort and sometimes delays or drops runs, so the
  later times are backups. A run **skips itself** if today's video is already uploaded, so you still get one a day.
- It queues one new topic (chosen by real search demand), writes the script, fact-checks it, voices it,
  finds licensed images and footage, renders the video, and uploads it.
- The long video is **scheduled to go public at 15:00 UTC** (11:00 ET / 16:00 UK). Up to 3 Shorts are cut from it
  and scheduled 2, 6 and 10 hours after that.
- A run takes about 15-30 minutes. Cost: $0 (free tiers only).
- Job state is kept between runs on the single-commit `state` branch (`data/autopilot.db`).

## Is it healthy? (30 seconds)
GitHub only emails you when a run **fails**. A run that **never starts** is silent, so if there is no new video by
about 12:00 UTC, check the Actions tab and start it by hand (Run workflow, tick live, privacy public).

1. https://github.com/NanduSav-1004/channel-autopilot/actions : the latest "Daily video" run should be green.
   A day that makes no video **fails on purpose** (red), and GitHub emails you.
2. YouTube Studio, Content: a video marked "Scheduled" or newly public, plus its Shorts.
3. Open the run, then the step "Make today's video". A good log ends with `processed N job(s)`.
   Useful lines: `[topics] queued ...`, `[job N] qa done`, `scheduled to go public at ...`, `queued N Short(s)`.

## Checks before pushing (local, not on GitHub)
- `scripts/check.sh` runs lint, the tests and a secret scan of the whole git history (about 5 seconds). It is also the
  **pre-push hook**, so `git push` is blocked if anything fails. Install it once per clone: `scripts/install_hooks.sh`.
- GitHub's CI workflow is manual now (Actions tab, Run workflow). It adds the fuller gitleaks scan; use it occasionally.

## What makes the videos punchy
- Scripts are written to measured targets: sentences averaging under about 13 words, a hook of at most 12 words, "you" in
  about one sentence in four. A section that misses is rewritten once. `[job N] style: ...` in the log shows the numbers.
- Captions are word by word: a short phrase on screen with the spoken word in amber, timed from Whisper (Groq) and fitted
  to the screen width. If Whisper is unavailable the timing is estimated (less exact, still works).
- Cuts: a new shot about every 3.5 s in long videos and 2.6 s in Shorts. A piece of media is used at most twice (Shorts:
  three times) with a different camera move; a section with little media cuts more slowly instead of repeating.

## Voice and music
- Each video gets a **random voice** from the three in `config/channel.yaml` (`audio.voices`): Kokoro `bm_george`,
  Kokoro `am_michael`, Gemini `Sadachbia`. It never repeats the previous video's voice, and a long video and its
  Shorts share one voice. The chosen voice is logged as `[tts] voice for this video: ...`.
- Kokoro runs offline with no limit. **Gemini's free tier allows about 20 requests a day per model**, and its audio
  has no timing, so sentences are located with Groq Whisper. If Gemini fails at any point, the **whole** narration is
  redone with the fallback voice (`audio.fallback`), so a video never mixes two voices.
- Music: `audio.music_style: ambient` (the soft pad). Beat styles (`upbeat`, `lofi`, `pulse`) exist but are not used.
  Mix levels are fixed: narration -16 LUFS, music -21 LUFS and ducked hard while the narrator speaks.
- Voice or music not wanted? Edit `audio:` in `config/channel.yaml`. Keep one voice by listing just one entry.

## Controls (GitHub: Settings, Secrets and variables, Actions, Variables)
| Want to... | Do this |
|---|---|
| **Pause** the schedule | Set variable `AUTOPILOT_ENABLED` to `false` (or delete it). Manual runs still work. |
| Upload privately (review first) | Add variable `UPLOAD_PRIVACY` = `private`. Default is `public`. |
| Run once by hand | Actions, Daily video, Run workflow. Tick **live** to really upload and set privacy; otherwise it is a dry run. |
| Make a second video today | Locally: `autopilot daily --live --force`. The scheduled runs never do this. |
| Change counts or times | Edit `config/channel.yaml` (`per_day`, `publish_hour_utc`, `publish_offsets_hours`). |

## Reading the log lines
| Log line | Meaning |
|---|---|
| `[llm] groq:... unavailable: ... daily quota exhausted` | Normal. A model hit its free daily limit; the next one is used. |
| `[job N] qa: ...repairing sections [..]` | The fact-check found unsupported claims and is rewriting only those sections. |
| `[shorts] dropped N Short(s) with unsupported claims` | The gate worked; fewer Shorts is fine. |
| `WARNING: no usable Shorts this time` | The long video is fine; just no Shorts today. |
| `thumbnail not set` | Upload worked; thumbnail failed (see Thumbnails below). |
| `ERROR: daily run finished no video` | Red run. Read the `[llm]`/`FAILED` lines above it. Usually all models were out of quota. |

## Common problems
**All models out of quota** (`all LLM models are out of quota or busy`). The job stays pending and is retried
on the next run without using an attempt. Free quotas reset about 07:00 UTC (Gemini) and daily (Groq). Nothing to do.

**A job shows `failed`** (3 real attempts). Look at its `error` with `autopilot status` (locally), then
`autopilot retry` to reset failed jobs.

**Thumbnail not set.** Custom thumbnails need the channel to have intermediate features (phone verified).
Once fixed: `autopilot thumbnails`.

**Uploads fail with an authorization error.** The YouTube refresh token stopped working. Re-login locally:
`.venv/bin/python src/autopilot/youtube_auth.py`, then update the secret `YOUTUBE_REFRESH_TOKEN`
(`python scripts/set_github_secrets.py` after `gh auth login`; run `gh auth logout` afterwards).
The OAuth app is published to production, so the token does not expire weekly.

**Schedule silently stopped.** GitHub disables schedules after 60 days without repo activity. Each run re-enables
its own schedule, so this should not happen. If it does, re-enable it in the Actions tab.

**A video has a mistake.** Edit or delete it in Studio. To stop a topic recurring, nothing is needed: used
topics are remembered in the state database.

## Running locally
```
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
cp .env.example .env        # fill in keys; never commit .env
.venv/bin/autopilot daily                       # dry run, uploads nothing
.venv/bin/autopilot daily --live --privacy private
.venv/bin/autopilot status | retry | thumbnails
.venv/bin/pytest -q && .venv/bin/ruff check .
```

## Safety rails (built in)
- Narration, **title and description** are fact-checked against the source article; failures are repaired or rejected.
- Medical, financial and legal advice topics are filtered out.
- Only commercially reusable images and footage are used; credits go in every description.
- Every description discloses AI-assisted scripting and a synthetic voice.
- A video's id is saved the moment it uploads, so a retry can never upload it twice.
- Secrets live only in GitHub Secrets and the local `.env`; CI scans every push for leaked keys.

## Things that are manual by nature
Channel name and picture (Studio only), pinned comments and end screens (not in the API), replying to comments,
and applying to the YouTube Partner Program once eligible.
