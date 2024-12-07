from collections import namedtuple
from datetime import datetime

from atproto import Client, client_utils

Post = namedtuple("Post", ["author", "record", "created_at"])


class Bluesky:
    def __init__(self, username, password):
        self.client = Client()
        self.client.login(username, password)
        self.username = username

    def get_posts(self, limit=20, only_self=True):
        feed_response = self.client.app.bsky.feed.get_author_feed(
            {
                "actor": self.username,
                "limit": limit,
            }
        )
        feed = feed_response.feed
        feed_posts = [feed_post["post"] for feed_post in feed]

        posts = [
            Post(
                author=post.author.handle,
                record=post.record,
                created_at=datetime.strptime(post.record.created_at[:23], "%Y-%m-%dT%H:%M:%S.%f"),
            )
            for post in feed_posts
            if not only_self or post.author.handle == self.username
        ]

        sorted_posts = sorted(posts, key=lambda x: x.created_at, reverse=True)

        return sorted_posts

    def send_post(self, text_builder: client_utils.TextBuilder, embed):
        self.client.send_post(text_builder, langs=["es"], embed=embed)
