from datetime import datetime, timedelta, timezone
from database import (
    get_undownloaded_clips,
    init_db,
    mark_clip_downloaded,
    save_clips,
)
from twitch_auth import get_app_access_token, get_client_id
from twitch_clips import get_game_clips
from twitch_downloader import download_clip
from twitch_games import get_game


def main(days_back: int = 7, fetch_limit: int = 50):
    init_db()

    access_token = get_app_access_token()
    client_id = get_client_id()

    game_data = get_game("Marvel Rivals", client_id, access_token)
    if not game_data.get("data"):
        print("Marvel Rivals not found on Twitch.")
        return

    game_id = game_data["data"][0]["id"]

    # Calculate RFC 3339 date range for recent clips
    now = datetime.now(timezone.utc)
    started_at = (now - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ended_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"[*] Fetching clips created in the last {days_back} days (Limit: {fetch_limit})...")
    response = get_game_clips(
        game_id=game_id,
        client_id=client_id,
        access_token=access_token,
        first=fetch_limit,
        started_at=started_at,
        ended_at=ended_at,
    )

    clips = response.get("data", [])
    new_records = save_clips(clips)
    print(f"[*] Discovered {len(clips)} recent clips. Added {new_records} new entries to database.")

    # Process pending downloads for the top 5
    pending = get_undownloaded_clips(limit=5)
    print(f"[*] Found {len(pending)} clips queued for download.")

    for clip in pending:
        saved_path = download_clip(
            slug=clip["id"],
            title=clip["title"],
            thumbnail_url=clip.get("thumbnail_url", ""),
        )
        if saved_path:
            mark_clip_downloaded(clip["id"], saved_path)


if __name__ == "__main__":
    main(days_back=7, fetch_limit=50)