import os

import requests
from dotenv import load_dotenv


TOKEN_URL = "https://id.twitch.tv/oauth2/token"


def get_app_access_token() -> str:
    load_dotenv()

    client_id = os.getenv("TWITCH_CLIENT_ID")
    client_secret = os.getenv("TWITCH_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError("Twitch credentials are missing from the .env file.")

    response = requests.post(
        TOKEN_URL,
        params={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()
    return data["access_token"]


def get_client_id() -> str:
    load_dotenv()

    client_id = os.getenv("TWITCH_CLIENT_ID")

    if not client_id:
        raise RuntimeError("Client ID missing from .env")

    return client_id