# IG Outreach Pro — marketing site

Static marketing site for **IG Outreach Pro**, a Chrome extension for personalized
Instagram DM outreach at scale. Lives at [igoutreachpro.com](https://www.igoutreachpro.com).

- **Extension:** [Chrome Web Store](https://chromewebstore.google.com/detail/ig-outreach-pro/iabflpjdaaaljedkocccimhfjonakcon) — v2.3.2, 5.0★
- **Stack:** hand-written HTML + CSS + vanilla JS. No build step, no framework, no runtime dependencies.
- **Hosting:** Vercel (static).

## Structure

```
index.html          Landing page
privacy.html        Privacy policy (ported verbatim — required for the CWS listing)
terms.html          Terms of service
support.html        Troubleshooting, billing, data deletion
vercel.json         cleanUrls, cache + security headers, redirects
robots.txt          Allows all, points at the sitemap
sitemap.xml         Four URLs
assets/
  css/site.css      The entire design system (tokens → components → responsive)
  js/site.js        Nav, scroll reveal, YouTube facade, tour tabs, savings calculator
  img/
    demo-poster.jpg    16:9 poster for the hero walkthrough
    testimonial-*.jpg  9:16 poster frames extracted from the customer videos
    og.png             1200x630 social card
    icon-*.png         Extension icons, reused as favicon/logo
```

## Copy is sourced, not invented

Every customer claim on the landing page is transcribed word-for-word from one of three
customer videos. The transcripts drive the hero proof strip, the testimonial cards, and
the framing of the comparison and FAQ sections:

| Video | Where | Claim used |
| --- | --- | --- |
| [Walkthrough](https://youtu.be/xifoBSs37P0) (10:18) | Hero | Full product tour — setup to results |
| [01](https://youtube.com/shorts/yudZjhCt2qY) (0:23) | Testimonials | Replaced two appointment setters |
| [02](https://youtube.com/shorts/k4D9WhHkO4w) (0:35) | Testimonials | Hours of daily outreach/follow-ups/scraping now unattended |
| [03](https://youtube.com/shorts/Sk2gVu6yjsk) (0:35) | Testimonials | First lead in 24h off 100 DMs from a 1-follower account |

Feature copy is likewise limited to what the extension actually ships (v2.3.2): campaigns
with follower/following/hashtag/custom-list targeting, spintax + placeholder templates,
AI drafting from tone + goal, follow-up sequences, reply scanning, the six safety controls
(Test Mode, Safe Start, pacing presets, hourly cap, break schedule, auto opt-outs),
10,000+ username duplicate memory, stats with a 7-day sparkline, CSV export, and the send
log with per-outcome reasons.

**Do not add integrations or outcomes the extension does not have.** The previous version
of this site advertised Zapier/Slack/Calendly integrations, calendar booking, and "30+
booked calls a month" — none of which exist. They are gone deliberately.

There is also **no pricing section** — that was removed on request, along with the nav and
footer links to it and the `offers` array in the JSON-LD. The price still appears
incidentally in the VA savings calculator, one FAQ answer, `terms.html` and `support.html`.

## Videos

All four videos are click-to-load facades: a self-hosted poster frame plus a play button,
which swaps in a `youtube-nocookie.com` iframe on click. Nothing is requested from YouTube
until the visitor asks for it, and hovering preconnects so playback still starts quickly.

The hero walkthrough uses `.player.player-wide` (16:9); the testimonials use the base
`.player` (9:16). The wide variant needs the doubled class for specificity — `.player` is
defined later in the stylesheet and would otherwise win on source order.

To regenerate a testimonial poster frame:

```sh
yt-dlp -f "bv*[height<=1080]+ba/b" -o "vid.%(ext)s" "https://youtube.com/shorts/<ID>"
ffmpeg -ss 3 -i vid.webm -frames:v 1 \
  -vf "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280" \
  -q:v 2 assets/img/testimonial-N.jpg
```

## Local preview

`file://` breaks the scroll-reveal observers and the relative asset paths, so serve over HTTP:

```sh
python3 -m http.server 8477
```

Then open <http://localhost:8477>.

## Deploying

Pushes to `main` deploy to production on Vercel. `cleanUrls` is on, so `/privacy.html`
serves as `/privacy` — internal links use the `.html` form and Vercel normalises them.

## Conventions

- Colours come from the custom properties at the top of `site.css`. Don't hard-code hexes
  in markup; add a token.
- The Instagram gradient (`--grad`) is an **accent**, not a background wash. It belongs on
  small surfaces: primary buttons, numerals, single words, 1px rules.
- Every section is `.rv` (reveal-on-scroll) with optional `.rv-d1`–`.rv-d5` stagger delays.
- Media queries are ordered widest → narrowest so the narrow ones win.
- Keep the page dependency-free. The only external request is the Google Fonts stylesheet.
