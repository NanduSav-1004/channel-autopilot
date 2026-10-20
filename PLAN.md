# Brightwork Science: automated YouTube channel (plan, v1.0)

Status: **built and running.** See `docs/RUNBOOK.md` for operations and `docs/niche_report.md` for the niche research.

## What it is
A free-stack pipeline that makes and publishes educational science and technology explainers every day, with
no manual step, on GitHub Actions. Channel: **Brightwork Science** (@brightworkscience), English, US/UK audience.

## Honest constraints
1. **No guaranteed views or income.** Ad revenue needs the YouTube Partner Program: 1,000 subscribers and 4,000
   public watch hours in 12 months (or 10M Shorts views in 90 days). Until then income is $0.
2. **YouTube's "inauthentic content" policy.** Templated, mass-produced videos get demonetised, so every video is
   grounded in a source, fact-checked, varied in structure, and disclosed as AI-assisted.
3. **Free-tier limits.** Models have daily quotas (Groq, Gemini); the system falls back across providers and
   models, and a day with every model exhausted fails visibly and retries on the next run.
4. **One-time human steps** (done): channel, phone verification, Google Cloud OAuth, GitHub secrets.

## Pipeline (per day)
```
topic (LLM brainstorm -> real search demand -> verified Wikipedia article)
  -> script (outline, then one call per section for length control)
  -> QA (fact-check narration + title + description; repair only the bad parts)
  -> voice (Piper TTS, sentence timings) -> visuals (Wikimedia Commons + Pixabay, vision-rated)
  -> render (1080p Ken Burns, boxed captions, generated ambient music with ducking) + thumbnail
  -> upload (scheduled for 15:00 UTC prime time, chapters, source, credits, disclosure)
  -> Shorts (up to 3 standalone 45 s scripts, fact-checked, 9:16 render, scheduled through the day)
```
Orchestrated by `autopilot daily`; state in SQLite on a `state` branch; failures never block the queue.

## Tools (all free)
| Stage | Tool |
|---|---|
| Orchestration | GitHub Actions cron, Python 3.12 |
| Text LLM | Groq (gpt-oss-120b, qwen, gpt-oss-20b), Gemini free tier as fallback |
| Vision rating | Gemini (images) |
| Voice | Piper TTS (CPU, offline) |
| Media | Wikimedia Commons (CC0/PD/CC BY/CC BY-SA), Pixabay stock video |
| Music | generated in code (no licence or Content ID risk) |
| Demand | YouTube autocomplete (US) |
| Render | FFmpeg, Pillow |
| Publish | YouTube Data API v3 |

## Done
- [x] Niche research and choice (evergreen science and tech explainers)
- [x] Content engine with fact-check and targeted repair; title and description checked too
- [x] Voice, visuals, music, captions, thumbnails, chapters, credits
- [x] Upload, scheduling, duplicate-upload protection, thumbnail retry
- [x] Daily GitHub Actions run, state persistence, loud failure alerts, schedule keepalive
- [x] Shorts (planner with fact-check, vertical renderer, scheduling)
- [x] Reach: prime-time scheduling, topics ranked by search demand
- [x] Brand: name, logo, banner, description (applied)
- [x] Runbook

## Next
1. **Weekly analytics report** (views, watch time, CTR, retention, subscribers) and a **Partner Program tracker**,
   after the first week of data. Use it to tune topic choice toward what the audience actually watches.
2. Tune topic selection toward mid-demand, lower-competition topics once there is data.
3. Better visual relevance when vision quota allows; caption chunking polish for Shorts.
4. Optional: Telegram alerts, subtitles and translated metadata for wider reach, cross-posting Shorts.
5. When eligible: apply to the Partner Program (manual).

## Success criteria
- Daily run green for 30 days, one long video and its Shorts per day, no manual step.
- Partner Program thresholds reached; then revenue tracking begins.
