import os
import random
from datetime import datetime, timedelta

import requests
from atproto import client_utils, models
from atproto_client import models

from bluesky import Bluesky
from metadata_parser import MetadataParser
from playlist import get_playlist

NOW = datetime.now()
TRACK_CUTOFF = NOW - timedelta(days=7)
DAYS_SINCE_LAST_POST = 3
CHANCE_OF_SHARE_OLD_TRACK = 0.2
TAG = "RecomendaciónMusical"

playlist = get_playlist(
    client_id=os.environ["SPOTIFY_CLIENT_ID"],
    client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
    playlist=os.environ["SPOTIFY_PLAYLIST"],
)

bsky = Bluesky(
    os.environ["BLUESKY_USERNAME"],
    os.environ["BLUESKY_PASSWORD"],
)

tracks_with_dates = [
    (track, datetime.strptime(track["added_at"], "%Y-%m-%dT%H:%M:%SZ")) for track in playlist["tracks"]["items"]
]
sorted_tracks = sorted(tracks_with_dates, key=lambda x: x[1], reverse=True)
selected_track = sorted_tracks[0]

if selected_track[1] < TRACK_CUTOFF:
    print("No new tracks to share")

    if random.random() > CHANCE_OF_SHARE_OLD_TRACK:
        print("Picking one at random")
        selected_track = random.choice(sorted_tracks)
    else:
        exit()

print("Selected track: ", selected_track[0]["track"]["name"])

actual_track = selected_track[0]

artist_names = [entry["name"] for entry in actual_track["track"]["artists"]]
track_url = actual_track["track"]["external_urls"]["spotify"]
track_name = actual_track["track"]["name"]

posts = bsky.get_posts()

from atproto_client.models.app.bsky.richtext.facet import Tag


def has_tag(post, tag):
    if post.record.facets is None:
        return False
    for facet in post.record.facets:
        for feature in facet.features:
            if isinstance(feature, Tag) and feature.tag == tag:
                return True
    return False


def filter_out_own_posts(posts):
    return [post for post in posts if not has_tag(post, TAG)]


non_recommendation_posts = filter_out_own_posts(posts)

time_since_last_post = NOW - non_recommendation_posts[0].created_at

if time_since_last_post > timedelta(days=DAYS_SINCE_LAST_POST):
    print("You have not posted in a while... I will not post")
    exit()

parser = MetadataParser(track_url)
parser.parse_metadata_and_og_tags()
image_data, image_content_type = parser.get_image()

image_blob = bsky.client.upload_blob(image_data)

main = models.AppBskyEmbedExternal.Main(
    external=models.AppBskyEmbedExternal.External(
        description=parser.description, title=parser.title, image=parser.image_url, uri=track_url, thumb=image_blob.blob
    )
)

tb = client_utils.TextBuilder()

tb.tag("Recomendación musical", TAG)
tb.text(": ")
tb.link(track_name, track_url)
tb.text(f' por {", ".join(artist_names)}\n')

bsky.send_post(text_builder=tb, embed=main)
