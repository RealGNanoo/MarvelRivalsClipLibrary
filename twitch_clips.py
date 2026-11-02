from typing import Any, Dict, List, Optional, Set
import requests

CLIPS_URL = "https://api.twitch.tv/helix/clips"
CHANNELS_URL = "https://api.twitch.tv/helix/channels"


def get_game_clips(
    game_id: str,
    client_id: str,
    access_token: str,
    first: int = 50,
    after: Optional[str] = None,
    started_at: Optional[str] = None,
    ended_at: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch clips for a specific game ID from Twitch Helix API."""
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
    }
    params: Dict[str, Any] = {
        "game_id": game_id,
        "first": min(first, 100),
    }

    if after:
        params["after"] = after
    if started_at:
        params["started_at"] = started_at
    if ended_at:
        params["ended_at"] = ended_at

    response = requests.get(CLIPS_URL, headers=headers, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def get_broadcasters_language(
    broadcaster_ids: List[str],
    client_id: str,
    access_token: str,
) -> Dict[str, str]:
    """Batch query /helix/channels (up to 100 at a time) to map broadcaster_id -> language."""
    if not broadcaster_ids:
        return {}

    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
    }

    unique_ids = list(set(broadcaster_ids))
    language_map: Dict[str, str] = {}

    # Query in batches of 100 (Twitch Helix max)
    batch_size = 100
    for i in range(0, len(unique_ids), batch_size):
        batch = unique_ids[i : i + batch_size]
        params = [("broadcaster_id", b_id) for b_id in batch]

        response = requests.get(
            CHANNELS_URL,
            headers=headers,
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json().get("data", [])

        for channel in data:
            b_id = channel.get("broadcaster_id")
            lang = channel.get("broadcaster_language", "")
            if b_id:
                language_map[b_id] = lang.lower()

    return language_map


def filter_english_clips(
    clips: List[Dict[str, Any]],
    client_id: str,
    access_token: str,
) -> List[Dict[str, Any]]:
    """Filters clips to keep only those where broadcaster_language is 'en'."""
    if not clips:
        return []

    broadcaster_ids = [clip["broadcaster_id"] for clip in clips if "broadcaster_id" in clip]
    lang_map = get_broadcasters_language(broadcaster_ids, client_id, access_token)

    english_clips = [
        clip for clip in clips
        if lang_map.get(clip.get("broadcaster_id", "")) == "en"
    ]
    return english_clips