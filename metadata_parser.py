import requests
from bs4 import BeautifulSoup


class MetadataParser:
    def __init__(self, url):
        self.url = url
        self.tags = {}

    def parse_metadata_and_og_tags(self):
        # Fetch the webpage
        response = requests.get(self.url)

        # Create a BeautifulSoup object
        soup = BeautifulSoup(response.text, "html.parser")

        # Parse metadata tags
        meta_tags = soup.find_all("meta")
        for tag in meta_tags:
            if "name" in tag.attrs:
                self.tags[tag.attrs["name"]] = tag.attrs.get("content", "")
            elif "property" in tag.attrs:
                self.tags[tag.attrs["property"]] = tag.attrs.get("content", "")

        # Parse Open Graph tags
        og_tags = soup.find_all("meta", property=lambda x: x and x.startswith("og:"))
        for tag in og_tags:
            self.tags[tag.attrs["property"]] = tag.attrs.get("content", "")

        return self.tags

    def get_attributes(self, *args):
        for arg in args:
            if arg in self.tags and self.tags[arg] is not None:
                return self.tags[arg]
        return None

    @property
    def title(self):
        return self.get_attributes("og:title", "title", "twitter:title")

    @property
    def description(self):
        return self.get_attributes("og:description", "description", "twitter:description")

    @property
    def image_url(self):
        return self.get_attributes("og:image", "twitter:image")

    def get_image(self):
        response = requests.get(self.image_url)
        response.raise_for_status()
        return response.content, response.headers.get("Content-Type")
