# Running the server automatically

By default, `serve.py` only runs while you have a terminal open. This
guide shows a few ways to keep it running in the background, so the
console is always available when you open http://127.0.0.1:8000/.

Pick whichever fits your setup. **systemd** is the "proper" way on
Debian and is what I'd recommend. The others are quicker but less
robust.

---

## Option 1 — systemd (recommended)

systemd is the init system Debian uses. It manages services that start
on boot, restart on crash, and log to `journalctl`. Once set up, you
can treat the console like any other daemon.

### 1. Create the service file

```bash
sudo nano /etc/systemd/system/homelab.service
```

Paste this — **replace `spadas` with your username if it's different**,
and double-check the paths:

```ini
[Unit]
Description=Homelab console server
After=network.target

[Service]
Type=simple
User=spadas
Group=spadas
WorkingDirectory=/home/spadas/homepage
ExecStart=/usr/bin/python3 /home/spadas/homepage/serve.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Save and exit: `Ctrl+O`, `Enter`, `Ctrl+X`.

**Field-by-field:**

| Line | What it does |
|---|---|
| `After=network.target` | Waits for the network to come up before starting |
| `User=` / `Group=` | Runs the server as your user, not root |
| `WorkingDirectory=` | The folder `serve.py` runs from — must contain `index.html` |
| `ExecStart=` | The exact command to run |
| `Restart=on-failure` | Restart automatically if it crashes |
| `RestartSec=5` | Wait 5 seconds before restarting |
| `WantedBy=multi-user.target` | Start when the system reaches normal boot |

### 2. Enable and start it

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now homelab
```

- `daemon-reload` tells systemd to re-read the service file you just wrote
- `enable` makes it start on every boot
- `--now` also starts it immediately, without waiting for a reboot

### 3. Verify it's running

```bash
systemctl status homelab
```

You should see `Active: active (running)`. If it says `failed`, check
the logs (next step).

### 4. Watch the logs

```bash
journalctl -u homelab -f
```

`-u homelab` filters to just your service. `-f` follows live output, like
`tail -f`. Press `Ctrl+C` to stop following.

Useful variants:

```bash
journalctl -u homelab --since "1 hour ago"     # last hour
journalctl -u homelab -n 50                    # last 50 lines
journalctl -u homelab -p err                   # only errors
```

### 5. Common management commands

```bash
sudo systemctl start homelab       # start
sudo systemctl stop homelab        # stop
sudo systemctl restart homelab     # restart
sudo systemctl reload homelab      # reload config (rarely needed)
systemctl status homelab           # is it running?

sudo systemctl disable homelab     # don't start on boot anymore
sudo systemctl enable homelab      # start on boot again
```

### 6. After editing `serve.py` or `index.html`

`index.html` is served fresh on every request — no restart needed.

If you edit `serve.py`, you need to restart the service:

```bash
sudo systemctl restart homelab
```

### 7. Removing the service

```bash
sudo systemctl disable --now homelab
sudo rm /etc/systemd/system/homelab.service
sudo systemctl daemon-reload
```

---

## Option 2 — nohup (quick and dirty)

If you don't want to touch systemd, `nohup` runs a command that survives
your terminal closing. It won't restart on crash or on reboot, but it's
fine for occasional use.

```bash
cd ~/homepage
nohup python3 serve.py > serve.log 2>&1 &
```

- `nohup` — "no hangup," keeps the process alive after the terminal closes
- `> serve.log 2>&1` — redirects stdout and stderr to `serve.log`
- `&` — runs it in the background

Check if it's running:

```bash
ps aux | grep serve.py
```

See its output:

```bash
tail -f ~/homepage/serve.log
```

Stop it:

```bash
pkill -f serve.py
```

You'll need to re-run the `nohup` command after every reboot.

---

## Option 3 — screen or tmux (interactive)

If you want a persistent terminal session you can reattach to:

```bash
# with screen
screen -S homelab
cd ~/homepage
python3 serve.py
# press Ctrl+A, then D to detach
```

Reattach later:

```bash
screen -r homelab
```

Same idea with `tmux` if you prefer it:

```bash
tmux new -s homelab
cd ~/homepage
python3 serve.py
# press Ctrl+B, then D to detach
tmux attach -t homelab
```

Also doesn't survive a reboot on its own. Combine with systemd if you
want both.

---

## Which should you pick?

- **systemd** if you want it to Just Work, starts on boot, restarts on
  crash, proper logging.
- **nohup** if you just want it running in the background for the rest of
  today and don't care about reboots.
- **screen/tmux** if you want to be able to pop into the running process
  and see live output without digging through logs.

For a homelab, systemd is the answer 95% of the time.

---

## Troubleshooting

**Service fails immediately after `systemctl start`:**

```bash
journalctl -u homelab -n 30
```

Common causes:

- Wrong path in `WorkingDirectory=` or `ExecStart=` — check with
  `ls /home/spadas/homepage/serve.py`
- Wrong username in `User=`
- Port 8000 already in use — check with `sudo lsof -i :8000`

**"Address already in use":**

Something else is already bound to port 8000. Either stop it, or change
`BIND_PORT` in `serve.py` to something else (e.g. `8080`) and
`systemctl restart homelab`.

**Can't reach the page from another device on the LAN:**

`serve.py` binds to `0.0.0.0`, so it should be reachable, but your
firewall may be blocking port 8000. Check with:

```bash
sudo ufw status
```

If UFW is active and blocking, allow the port:

```bash
sudo ufw allow 8000/tcp
```

(Only do this if you actually want LAN access. If you just want
`localhost`, don't open the port.)
