import hashlib
import os
import re
import shutil

import scrapetube
import yt_dlp

from shared import lock, in_progress, logger


def sanitize_filename(name):
    return re.sub(r'[\/*?:"<>|]', "_", name)

class YoutubeChannelDownloader:

    def download_channel(self, channel_id):
        channel_hash = hashlib.sha256(channel_id.encode()).hexdigest()
        export_path = os.path.join(os.getcwd(), "exports", "channels", f"{channel_hash}.zip")

        with lock:
            if channel_hash in in_progress:
                print("Download already in progress.")
                return
            in_progress.add(channel_hash)

        try:
            if os.path.exists(export_path):
                print(f"Archive already exists at {export_path}, skipping download.")
                return

            base_folder = os.path.join(os.getcwd(), "downloads", "channels")
            folder_path = os.path.join(base_folder, channel_hash)
            os.makedirs(folder_path, exist_ok=True)

            videos = scrapetube.get_channel(channel_id)
            for video in videos:
                self.download_video(video, folder_path)

            YoutubeChannelDownloader.archive_download("channels", channel_hash, folder_path)
        finally:
            with lock:
                in_progress.discard(channel_hash)

    def download_playlist(self, playlist_id):
        playlist_hash = hashlib.sha256(playlist_id.encode()).hexdigest()
        export_path = os.path.join(os.getcwd(), "exports", "playlists", f"{playlist_hash}.zip")

        with lock:
            if playlist_hash in in_progress:
                print("Download already in progress.")
                return
            in_progress.add(playlist_hash)

        try:
            if os.path.exists(export_path):
                print(f"Archive already exists at {export_path}, skipping download.")
                return

            base_folder = os.path.join(os.getcwd(), "downloads", "playlists")
            folder_path = os.path.join(base_folder, playlist_hash)
            os.makedirs(folder_path, exist_ok=True)

            videos = scrapetube.get_playlist(playlist_id)
            for video in videos:
                self.download_video(video, folder_path)

            YoutubeChannelDownloader.archive_download("playlists", playlist_hash, folder_path)
        finally:
            with lock:
                in_progress.discard(playlist_hash)

    @staticmethod
    def archive_download(category, hash_id, folder_path):
        export_base = os.path.join(os.getcwd(), "exports", category)
        os.makedirs(export_base, exist_ok=True)
        archive_path = os.path.join(export_base, f"{hash_id}.zip")
        shutil.make_archive(base_name=archive_path[:-4], format='zip', root_dir=folder_path)
        print(f"Archived to {archive_path}")

    @staticmethod
    def download_video(video, folder_path):
        video_id = video['videoId']
        title = video['title']['runs'][0]['text']
        safe_title = sanitize_filename(title)
        video_path = os.path.join(folder_path, f"{safe_title}.mp4")

        if os.path.exists(video_path):
            print(f"Skipping: {title} already exists in {folder_path}")
            return

        url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            'format': 'bv*+ba/best',
            'merge_output_format': 'mp4',
            'outtmpl': video_path,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
            'quiet': True,
            'no_warnings': True,
            'logger': logger,
        }

        print(f"Downloading: {title} to {folder_path}")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"Error downloading {title}: {e}")
