from datetime import datetime, timedelta, timezone
from database import (
    get_undownloaded_clips,
    init_db,
    mark_clip_downloaded,
    save_clips,
)
from twitch_auth import get_app_access_token, get_client_id
from twitch_clips import filter_english_clips, get_game_clips
from twitch_downloader import download_clip
from twitch_games import get_game


def main(days_back: int = 7, max_pages: int = 4, page_size: int = 50, download_batch: int = 5):
    """
    Fetches clips across multiple pages using Twitch cursor pagination,
    filters for English channels only, and saves them to the database.
    """
    init_db()

    access_token = get_app_access_token()
    client_id = get_client_id()

    game_data = get_game("Marvel Rivals", client_id, access_token)
    if not game_data.get("data"):
        print("[-] Marvel Rivals not found on Twitch.")
        return

    game_id = game_data["data"][0]["id"]

    now = datetime.now(timezone.utc)
    started_at = (now - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ended_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"[*] Discovering clips (Last {days_back} days, up to {max_pages} pages)...")

    cursor = None
    all_raw_clips = []

    for page in range(1, max_pages + 1):
        print(f"[*] Requesting page {page} (Cursor: {cursor or 'Start'})...")
        response = get_game_clips(
            game_id=game_id,
            client_id=client_id,
            access_token=access_token,
            first=page_size,
            after=cursor,
            started_at=started_at,
            ended_at=ended_at,
        )

        page_clips = response.get("data", [])
        if not page_clips:
            print("[*] No more clips returned for this date window.")
            break

        all_raw_clips.extend(page_clips)

        # Get next page cursor
        pagination = response.get("pagination", {})
        cursor = pagination.get("cursor")

        if not cursor:
            print("[*] Reached end of pagination stream.")
            break

    print(f"[*] Retrieved {len(all_raw_clips)} raw clips across {page} page(s).")

    # Filter for English channels
    print("[*] Verifying broadcaster language for retrieved clips...")
    english_clips = filter_english_clips(all_raw_clips, client_id, access_token)
    print(f"[*] Filtered down to {len(english_clips)} English-language clips.")

    # Save to local database
    new_records = save_clips(english_clips)
    print(f"[*] Successfully added {new_records} new English clips to database.")

    # Download batch of pending clips
    pending = get_undownloaded_clips(limit=download_batch)
    print(f"[*] Found {len(pending)} un-downloaded clips queued for local storage.")

    for clip in pending:
        saved_path = download_clip(
            slug=clip["id"],
            title=clip["title"],
            thumbnail_url=clip.get("thumbnail_url", ""),
        )
        if saved_path:
            mark_clip_downloaded(clip["id"], saved_path)


if __name__ == "__main__":
    # max_pages=4 with page_size=50 scans up to 200 clips per run
    main(days_back=7, max_pages=4, page_size=50, download_batch=5)