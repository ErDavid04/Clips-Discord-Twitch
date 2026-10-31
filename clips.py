"""
Publica en un canal de Discord (vía webhook) los clips nuevos de un canal de Twitch.
Pensado para ejecutarse cada pocos minutos con GitHub Actions. Solo usa la librería estándar.
"""
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

STATE_FILE = "state.json"
LOOKBACK_HOURS = 24      # ventana de búsqueda (cubre retrasos de Twitch y de GitHub)
MAX_REMEMBERED = 500     # cuántos IDs de clips ya publicados se recuerdan

CLIENT_ID = os.environ["TWITCH_CLIENT_ID"].strip()
CLIENT_SECRET = os.environ["TWITCH_CLIENT_SECRET"].strip()
WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"].strip()
LOGIN = os.environ["TWITCH_LOGIN"].strip().lower()

UA = {"User-Agent": "TwitchClipsToDiscord/1.0"}


def http(method, url, headers=None, data=None):
    headers = {**UA, **(headers or {})}
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    elif method == "POST":
        body = b""
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        return json.loads(raw) if raw else None


def twitch_token():
    q = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
    })
    return http("POST", f"https://id.twitch.tv/oauth2/token?{q}")["access_token"]


def helix(path, token, params):
    q = urllib.parse.urlencode(params)
    return http("GET", f"https://api.twitch.tv/helix/{path}?{q}", headers={
        "Client-Id": CLIENT_ID,
        "Authorization": f"Bearer {token}",
    })


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"posted": [], "heartbeat": ""}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    state = load_state()
    posted = state.get("posted", [])
    posted_set = set(posted)

    token = twitch_token()

    users = helix("users", token, {"login": LOGIN})["data"]
    if not users:
        raise SystemExit(f"No existe el canal de Twitch '{LOGIN}'")
    broadcaster_id = users[0]["id"]

    now = datetime.now(timezone.utc)
    params = {
        "broadcaster_id": broadcaster_id,
        "started_at": (now - timedelta(hours=LOOKBACK_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ended_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "first": 100,
    }

    clips = []
    while True:
        res = helix("clips", token, params)
        clips.extend(res.get("data", []))
        cursor = res.get("pagination", {}).get("cursor")
        if not cursor:
            break
        params["after"] = cursor

    new_clips = sorted(
        (c for c in clips if c["id"] not in posted_set),
        key=lambda c: c["created_at"],
    )

    for clip in new_clips:
        content = (
            f"🎬 **{clip['title']}** — clip de {clip['creator_name']}\n"
            f"{clip['url']}"
        )
        http("POST", WEBHOOK, data={
            "content": content,
            "allowed_mentions": {"parse": []},
        })
        posted.append(clip["id"])
        print(f"Publicado: {clip['title']} ({clip['url']})")
        time.sleep(1.5)  # evita el límite de peticiones de Discord

    if not new_clips:
        print("No hay clips nuevos.")

    # Marca semanal: hace que el repo reciba al menos un commit por semana,
    # para que GitHub no desactive la tarea programada por inactividad.
    year, week, _ = now.isocalendar()
    state["heartbeat"] = f"{year}-W{week:02d}"
    state["posted"] = posted[-MAX_REMEMBERED:]
    save_state(state)


if __name__ == "__main__":
    main()
