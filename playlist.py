import base64

import requests


def get_playlist_id(playlist):
    if playlist.startswith("https://open.spotify.com/playlist/"):
        return playlist.split("/")[-1].split("?")[0]
    else:
        return playlist


def get_token(client_id, client_secret):
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

    # Define the API endpoint
    url = "https://accounts.spotify.com/api/token"

    # Set up the headers
    headers = {"Authorization": f"Basic {client_creds_b64}"}

    # Set up the data for the POST request
    data = {"grant_type": "client_credentials"}

    # Make the POST request
    response = requests.post(url, headers=headers, data=data)

    response_json = response.json()

    # Extract the access token
    token = response_json["access_token"]

    return token


def get_playlist(client_id, client_secret, playlist):
    token = get_token(client_id, client_secret)
    playlist_id = get_playlist_id(playlist)

    all_track_items = []

    # Define the API endpoint
    base_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"

    # Set up the headers
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(base_url, headers=headers)
    base_playlist = response.json()
    all_track_items.extend(base_playlist["tracks"]["items"])

    next_url = base_playlist["tracks"]["next"]

    while next_url:
        response = requests.get(next_url, headers=headers)
        tracks = response.json()
        all_track_items.extend(tracks["items"])
        next_url = tracks.get("next", None)

    base_playlist["tracks"] = {
        "items": all_track_items,
        "total": len(all_track_items),
        "limit": len(all_track_items),
    }

    return base_playlist
