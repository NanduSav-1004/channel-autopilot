# Automated YouTube Channel: End-to-End Plan (v0.1 draft)

## 0. Decisions locked
| Item | Decision |
|---|---|
| Format | Hybrid: 8-12 min long-form (watch hours, ad RPM) + auto-clipped Shorts (discovery) |
| Audience | English, US/UK |
| Budget | **Free stack ($0/month)** |
| Niche | Chosen by data in Phase 0 (not guessed) |
| Host | GitHub Actions (free cron). Dev machine is i5-1035G1, 7 GB RAM, no GPU, so it is not a production server |

## 1. Honest constraints (design around these, don't ignore them)
1. **No guaranteed views or income.** The system maximizes odds and measures itself. Revenue is gated by YPP.
2. **YouTube "inauthentic content" policy (July 2025).** Mass-produced, templated, repetitive videos get demonetized. Every video needs original script, varied visuals, a consistent voice and a real angle. Quality gates are a core feature.
3. **YPP threshold:** 1,000 subs + 4,000 watch hours (12 mo), or 1,000 subs + 10M Shorts views (90 d). Until then: $0 ad income, so the bridge is affiliate links.
4. **API quota:** 10,000 units/day by default; one upload costs about 1,600, so about 6 uploads/day. A quota-extension audit can be requested later.
5. **New API projects:** uploads from unverified API projects are locked to private. We must pass the YouTube API compliance audit, or the project needs to be verified, before public uploads work. **This is the biggest technical risk and is tested first (Phase 1).**
6. **One-time human steps (unavoidable, then zero manual):** create Google account and channel, phone verification, OAuth consent, GitHub secrets.
7. **Free-tier limits:** GitHub Actions gives 2,000 min/month on private repos (unlimited on public). Free LLM tiers rate-limit. Design for retries and queueing.

## 2. Free tool stack
| Stage | Tool | Cost |
|---|---|---|
| Orchestration | GitHub Actions cron + Python 3.12 | free |
| State/queue | SQLite committed to repo (or Actions cache / a `data` branch) | free |
| Topic research | YouTube Data API (search, outlier detection), Google Trends (pytrends), Reddit/HN/RSS | free |
| Script LLM | Gemini API free tier (primary), Groq free tier (fallback) | free |
| Fact/policy check | Second LLM pass with a rubric + source retrieval via Wikipedia/RSS | free |
| Voiceover | Kokoro-82M or Piper TTS (CPU, offline, commercial-friendly licenses) | free |
| Captions/timing | faster-whisper (CPU, `small` model) | free |
| Visuals | Pexels + Pixabay APIs (video/photo), Wikimedia Commons, Pollinations/HF free image gen, code-rendered charts and kinetic text (Pillow/Matplotlib/Remotion) | free |
| Music/SFX | YouTube Audio Library, Pixabay Music, Free Music Archive (license-tracked per video) | free |
| Editing | FFmpeg + MoviePy | free |
| Thumbnails | Pillow templates + free image gen, A/B via YouTube Test & Compare | free |
| Upload/analytics | YouTube Data API v3 + Analytics API | free |
| Alerts | Telegram bot or email on failure/weekly report | free |

## 3. Architecture
```
 [scheduler: GH Actions cron]
        |
 research -> topic scoring -> script -> QA gate -> TTS -> visuals -> edit(long)
                                                                        |-> clip -> Shorts
        -> thumbnail/title -> policy+copyright gate -> upload/schedule -> analytics
                  ^                                                           |
                  +-------------- feedback loop (retention/CTR/RPM) <---------+
```
Each stage is an idempotent module with a typed input/output, stored artifacts per video ID, retries, and a dead-letter state so one failure never blocks the queue.

## 4. Phases
**Phase 0: Niche selection (data-driven).** Score candidate niches on RPM, competition, faceless-fit, topic supply, and policy risk. Use YouTube API outlier analysis (small channels with big views) plus public CPM data. Output: `docs/niche_report.md` and one chosen niche plus a channel brand and persona.

**Phase 1: Foundations and risk spike.** Repo scaffold, config, secrets, CI. Prove the OAuth + upload flow, including the private-upload lock and audit path. Prove the CPU-only TTS + FFmpeg render of one 60 s video.

**Phase 2: Content engine.** Research, scoring, script generation (hook, retention beats, CTA), fact/policy gate, series formats so output is varied and not templated.

**Phase 3: Production engine.** TTS, visuals, captions, music, long-form render, auto-clipping to Shorts, thumbnails.

**Phase 4: Publishing and ops.** Scheduler, upload, metadata, playlists, affiliate-link injection, alerts, cost/quota tracking, kill switch.

**Phase 5: Feedback loop.** Daily analytics pull; auto-tune topics, hooks, title style, upload times; retire losers.

**Phase 6: Monetization.** YPP readiness tracker, AdSense link, affiliate program, cross-posting (TikTok/Reels), optional digital product.

**Phase 7: Hardening.** Tests, dry-run mode, duplicate-content detection, copyright/licence ledger, monitoring.

## 5. Milestones and exit criteria
- M1: one video generated end-to-end locally (private upload).
- M2: pipeline runs unattended on GitHub Actions for 7 days.
- M3: 1-2 long + 3-5 Shorts per day, fully unattended for 30 days.
- M4: YPP eligibility reached, then revenue tracking.

## 6. Open items needing you
1. A Google account for the channel (new, dedicated).
2. A GitHub repo (public gives unlimited free Actions minutes; private gives 2,000 min).
3. Confirmation that the public-repo tradeoff is OK, since the code would be visible. Secrets stay in GitHub Secrets.
