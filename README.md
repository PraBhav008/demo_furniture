# Aurelia Verde site (placeholder brand name)
Static site, no dependencies. Edit `build.py` (CONFIG + content) then run `python3 build.py` to regenerate HTML, sitemap.xml, robots.txt and check links.

## Add your assets
- Fonts (Fontshare, free to download): put `Panchang-Variable.woff2`, `Sentient-Variable.woff2`, `Sentient-VariableItalic.woff2` in `assets/fonts/`. If your filenames differ, edit the 3 `@font-face` lines in `css/styles.css`.
- Images: every box shows the exact filename and size to use (e.g. `assets/img/hero.jpg`, 1200x1500). Also add `assets/img/og-image.jpg` (1200x630) for social previews.
- Compress before upload: export WebP/JPG at 2x display size, target < 200 KB each (squoosh.app or `cwebp -q 80`). Keep filenames or update them in `build.py`.

## Before launch
Set `url`, `email`, `phone`, `address`, socials, `ga_id` and `form_endpoint` in CONFIG. Get the legal pages reviewed by a lawyer. Enable HTTPS (`.htaccess` handles Apache; otherwise use your host's "Force HTTPS"). Run Lighthouse on the live URL. Never put private API keys in these files; the form uses a public endpoint or a server.
