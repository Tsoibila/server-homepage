# Homelab Console

A retro CRT-style terminal dashboard for a personal homelab. Runs entirely
locally — no cloud, no accounts, no telemetry.

![Screenshot](screenshots/console.png)

## Features

- Boot sequence with typewriter animation
- Auto-detecting service links (builds URLs from the host you're accessing it from)
- Live weather panel for configurable cities (Open-Meteo, no API key)
- Rotating quotes
- Interactive terminal with commands:
  - `help` — list all commands
  - `weather <city>, <country>` — live weather lookup
  - `image [filter]` — show a random image from `./Images/`
  - `random-song` — play a random track from `./random-songs/`
  - `bookmarks` — list configured bookmarks
  - `badapple` — play Bad Apple in-terminal (video) or as ASCII + audio
  - `stop` — stop any playing media
  - `clear` — clear the terminal
- CRT effects: scanlines, flicker, chromatic aberration

## Requirements

- Python 3.9 or newer
- A modern browser

That's it. No dependencies, no `pip install`, no build step.

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/Tsoibila/server-homepage.git
   cd server-homepage
   ```

2. Create the media folders (they're gitignored, so they won't exist after clone):
   ```bash
   mkdir -p Images stuff random-songs
   ```

3. Start the server:
   ```bash
   python3 serve.py
   ```

4. Open http://127.0.0.1:8000/ in your browser.

## Configuration

Everything you need to edit lives in the `<script>` block at the top of
`index.html`. There's an editing guide in the comments, but the four
things you'll most likely change are:

**Services** — the list of links shown under `[ SERVICES ]`:
```js
const services = [
  { port: '8096', name: 'Jellyfin', scheme: 'http' },
  { port: '443',  name: 'Tailscale', host: 'console.tailscale.com', scheme: 'https' },
];
```

**Bookmarks** — same pattern:
```js
const bookmarks = [
  { name: 'GitHub', url: 'https://github.com', note: 'code hosting' },
];
```

**Cities** — weather panel:
```js
const CITIES = [
  { label: 'ATHENS, GR', lat: 37.9838, lon: 23.7275 },
];
```

**Quotes** — rotating footer:
```js
const QUOTES = [
  { text: 'Somewhere, something incredible is waiting to be known.', author: 'Carl Sagan' },
];
```

## Media

The `image`, `random-song`, and `badapple` commands look for files in:

- `./Images/` — images (`.jpg`, `.png`, `.gif`, `.webp`, etc.)
- `./stuff/` — anything media-related
- `./random-songs/` — audio (`.mp3`, `.ogg`, `.wav`, `.m4a`, `.flac`)
- `./badapple.mp4` — optional, falls back to `./badapple.mp3` + ASCII

These folders are empty in the repo. Drop your own files in.

## Adding a command

Commands live in the `COMMANDS` object. Each one is a name plus a
`{ help, usage?, run }` object:

```js
const COMMANDS = {
  hello: {
    help: 'Say hello.',
    run: (args, ctx) => { ctx.print('hello world'); }
  },
};
```

The `help` command auto-lists every entry, so no need to update it.

## License

Code is released under the [MIT License](LICENSE).

Photos and other media you add yourself are your own — they're not
covered by this license.
