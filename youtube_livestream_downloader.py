import subprocess
import os
import time
import argparse
import signal
import uuid
import shutil

class YouTubeLivestreamDownloader:
    def __init__(self, url: str, duration_min: int, output_name: str, output_dir: str = "./downloads"):
        self.url = url
        self.duration_sec = duration_min * 60
        self.output_name = output_name
        self.output_dir = output_dir
        self.temp_dir = os.path.join("./temp", str(uuid.uuid4()))

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

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

        temp_path = os.path.join(self.temp_dir, self.output_name + ".ts")
        final_path = os.path.join(self.output_dir, self.output_name + ".ts")

        print(f"Téléchargement en cours pendant {self.duration_sec} secondes...")
        print(f"Flux HLS : {hls_url}")

        command = [
            "ffmpeg",
            "-y",
            "-i", hls_url,
            "-c", "copy",
            temp_path
        ]

        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        try:
            time.sleep(self.duration_sec)
            print("Durée atteinte. Envoi d'un signal d'arrêt à ffmpeg...")
            process.send_signal(signal.SIGINT)
            process.wait()
        except KeyboardInterrupt:
            print("Arrêt manuel détecté. Fermeture de ffmpeg...")
            process.terminate()
            process.wait()

        if os.path.exists(temp_path):
            shutil.move(temp_path, final_path)
            print(f"Fichier déplacé vers : {final_path}")
        else:
            print("Aucun fichier à déplacer.")

        # Nettoyage du dossier temporaire
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        print("Téléchargement terminé et dossier temporaire nettoyé.")



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
