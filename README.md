# GTA 6 Clipper

Put in a long gameplay video. Get back ready-to-post clips. No editing on your part.

For each video it makes:

- **Vertical Shorts / TikToks / Reels** (1080×1920): the best moments, with burned-in captions and a title banner.
- **A YouTube compilation** (1920×1080): the top highlights in order, with fades between them. A paste-ready description includes chapters.
- **A `.txt` file next to every clip** with a title, caption, hashtags, and a credit line when the footage came from another creator.

Everything runs on your Mac. It's free: no subscriptions and no paid AI.

---

## 1. One-time setup (about 10 minutes)

1. Download this repo (green **Code** button → **Download ZIP**) and unzip it.
2. Open **Terminal**, type `cd ` (with a space), drag the unzipped folder into the window, and press Enter.
3. Run:
   ```
   ./setup.sh
   ```
   This installs ffmpeg, Python, the YouTube downloader and the local speech-to-text engine. The first time captions run, it downloads a speech model of about 0.5 GB.

## 2. Make clips

**The easy way:** double-click **`Clip.command`**. Paste a URL or drag a video file into the window and press Enter. The `clips` folder opens when it's done.

> First time only: macOS may block it. Right-click `Clip.command` → **Open** → **Open**.

**From Terminal:**

```bash
.venv/bin/gta6clip run ~/Movies/gta6-session-1.mp4          # your own recording
.venv/bin/gta6clip run "https://www.youtube.com/watch?v=..."  # a creator you're allowed to clip
.venv/bin/gta6clip run --from-file vods.txt                   # a whole list, one per line
.venv/bin/gta6clip watch ~/Movies/GTA6                        # hands-off: auto-clip every new recording
```

Useful options: `--shorts 12` (more clips), `--deep` (slower but smarter picks), `--layout crop` (zoomed full-screen vertical), `--no-longform`, `--no-captions`.

## 3. Output

```
clips/20261119-203000-gta6-session-1/
  short_01.mp4   short_01.txt     <- upload + paste the text
  short_02.mp4   short_02.txt
  ...
  compilation.mp4  compilation.txt <- YouTube video + description with chapters
  source.json                     <- where the footage came from / permission note
  summary.json                    <- timestamps and scores of every clip
```

---

## How it picks moments

| Signal | Why it works for GTA |
|---|---|
| **Loudness** | Gunfights, explosions, crashes, sirens, people yelling |
| **Sudden volume spikes** | The "OH NO" moment, compared with the seconds before it |
| **YouTube "Most replayed"** | When a creator's video has it, viewers have already voted on the best parts |
| **Hype words** (`--deep`) | "no way", "clip that", "five stars", "let's go"… (edit the list in `config.toml`) |

Cut points are moved so nobody gets cut off mid-word. Clips put the build-up first and the payoff just after the middle.

**Speed:** on Apple Silicon, rendering uses the Mac's hardware video encoder and captions run on the GPU. Default mode only transcribes the clips it keeps, so a 2-hour session takes minutes, not hours. `--deep` transcribes everything: slower, but it catches funny dialogue that isn't loud.

---

## GTA 6 launch-day checklist: what you need

**GTA 6 launches on PS5 and Xbox Series X|S only, with no PC version.** Gameplay has to get from your console to your Mac. Pick one way:

| Option | Cost | How | Hands-off? |
|---|---|---|---|
| **Capture card + OBS** (best) | ~$100–200 (e.g. Elgato HD60 X, works on Mac) | Console → capture card → Mac. Have OBS save recordings into `~/Movies/GTA6` and run `gta6clip watch ~/Movies/GTA6` | Yes: play, and clips appear |
| **Stream to your own YouTube/Twitch** | Free | Use the console's built-in streaming, then run the clipper on your VOD URL (add your channel to `allowed_channels`) | Almost |
| **Console's built-in captures** | Free | PS5: Create button / PS App. Xbox: Xbox app. Move files to the Mac and run on them | Manual transfer |

Before launch:

- [ ] Run `./setup.sh`, then `.venv/bin/gta6clip doctor`. Everything should say `ok`.
- [ ] Test it on any long gaming video of your own so you know it works before release day.
- [ ] **Turn off HDR** for captures and streams on the console. HDR footage looks washed out after conversion.
- [ ] Record at 1080p, 60 fps if you can. 4K files are huge and Shorts are 1080p anyway.
- [ ] Set up accounts: a YouTube channel (Shorts and long-form), TikTok, Instagram. Use a consistent name.
- [ ] Put your own channel, and creators who said yes, into `allowed_channels` in `config.toml`.
- [ ] Have free disk space. An hour of 1080p60 is about 5–10 GB.

## Rules (read this, it protects your channel)

- **Your own gameplay:** fine. Rockstar generally allows gameplay videos, but some content (leaks, spoilers before launch, monetization edge cases) can still be taken down. Read Rockstar's current policy.
- **Other creators:** only with permission. Common legit routes are paid **clipping campaigns** (creators pay clippers per view, e.g. on Whop) or direct agreement. The tool refuses URLs from channels not in `allowed_channels` unless you add `--permission "how you got it"`. That note is saved in `source.json` as your record.
- Re-uploading other people's videos without permission gets copyright strikes. Three strikes and the channel is deleted. Fully automatic cuts without your own commentary are not "fair use".
- Downloading from YouTube is against YouTube's Terms of Service even when the creator agrees. Creators in clipping programs usually provide download links or accept it, but it's your call.

## Settings

Everything lives in `config.toml` (created from `config.example.toml`): clip count and length, vertical layout, caption font and size, speech model (`large-v3-turbo` for better accuracy), hype words, hashtags, and title prefix.

## Troubleshooting

- **"Sign in to confirm you're not a bot"**: set `cookies_from_browser = "safari"` (or `"chrome"`) in `config.toml`.
- **YouTube download broke after an update**: `Clip.command` updates yt-dlp on every run. From Terminal, run `.venv/bin/pip install -U yt-dlp`.
- **Anything else**: run `.venv/bin/gta6clip doctor`.

## Developers

```bash
pip install -e ".[dev]" && pytest
```

Code: `gta6clipper/` holds `sources` (download and permission), `highlights` (scoring), `transcribe` (Whisper), `captions` (ASS), `render` (ffmpeg), `pipeline` (glue) and `cli`.
