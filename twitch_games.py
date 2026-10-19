import requests


GAMES_URL = "https://api.twitch.tv/helix/games"


def get_game(game_name: str, client_id: str, access_token: str):
    response = requests.get(
        GAMES_URL,
        headers={
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}",
        },
        params={
            "name": game_name,
        },
        timeout=15,
    )

    response.raise_for_status()

    return response.json()