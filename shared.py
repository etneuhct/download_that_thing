import threading
import logging

lock = threading.Lock()
in_progress = set()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yt-dlp")