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


def main():
    init_db()

    access_token = get_app_access_token()
    client_id = get_client_id()

    game_data = get_game("Marvel Rivals", client_id, access_token)
    if not game_data["data"]:
        print("Marvel Rivals not found on Twitch.")
        return

    game_id = game_data["data"][0]["id"]

    # 1. Discover top 20 clips
    print("[*] Fetching top clips...")
    response = get_game_clips(game_id, client_id, access_token, first=20)
    clips = response.get("data", [])
    new_records = save_clips(clips)
    print(f"[*] Indexed {new_records} new clips into local database.")

    # 2. Process pending downloads (e.g., top 5 highest-viewed)
    pending = get_undownloaded_clips(limit=5)
    print(f"[*] Found {len(pending)} clips queued for download.")

    for clip in pending:
        saved_path = download_clip(
            slug=clip["id"],
            title=clip["title"],
            thumbnail_url=clip["thumbnail_url"],
        )
        if saved_path:
            mark_clip_downloaded(clip["id"], saved_path)


if __name__ == "__main__":
    main()
