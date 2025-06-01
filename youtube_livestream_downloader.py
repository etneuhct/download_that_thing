import subprocess
import os
import argparse
import subprocess
import os
import time
import argparse
import signal

class YouTubeLivestreamDownloader:
    def __init__(self, url: str, duration_min: int, output_name: str, output_dir: str = "./downloads"):
        self.url = url
        self.duration_sec = duration_min * 60
        self.output_name = output_name
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def record(self):
        print("Obtention du lien direct HLS via yt-dlp...")

        result = subprocess.run(
            ["yt-dlp", "-g", self.url],
            capture_output=True,
            text=True
        )

        hls_url = result.stdout.strip()
        if not hls_url:
            print("Impossible d'extraire l'URL du flux HLS.")
            return

        output_path = os.path.join(self.output_dir, self.output_name + ".ts")

        print(f"Téléchargement en cours pendant {self.duration_sec} secondes...")
        print(f"Flux HLS : {hls_url}")

        command = [
            "ffmpeg",
            "-y",
            "-i", hls_url,
            "-c", "copy",
            output_path
        ]

        # Démarre ffmpeg
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        try:
            time.sleep(self.duration_sec)
            print("Durée atteinte. Envoi d'un signal d'arrêt à ffmpeg...")
            process.send_signal(signal.SIGINT)  # Ctrl+C simulé pour qu'il ferme correctement
            process.wait()
        except KeyboardInterrupt:
            print("Arrêt manuel détecté. Fermeture de ffmpeg...")
            process.terminate()
            process.wait()

        print("Téléchargement terminé.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--duration", type=int, required=True)
    parser.add_argument("--output-name", required=True)
    parser.add_argument("--output-dir", default="./downloads")

    args = parser.parse_args()

    downloader = YouTubeLivestreamDownloader(
        url=args.url,
        duration_min=args.duration,
        output_name=args.output_name,
        output_dir=args.output_dir
    )
    downloader.record()
