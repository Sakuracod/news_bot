# -*- coding: utf-8 -*-
import json
import os
import time
from typing import List, Tuple

import feedparser
import requests

TOPIC = os.environ["NTFY_TOPIC"]
SEEN_FILE = "seen.json"

RSS_FEEDS: List[Tuple[str, str]] = [
    ("Fed News", "https://www.federalreserve.gov/feeds/press_all.xml"),
    ("IMF News", "https://www.imf.org/en/News/RSS"),
    ("ECB News", "https://www.ecb.europa.eu/rss/press.html"),
]