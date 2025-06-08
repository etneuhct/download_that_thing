import hashlib
import os
import subprocess

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

active_streams = {}


class LivestreamRequest(BaseModel):
    url: str
    duration_min: int
    output_name: str
    output_dir: str = "./downloads/livestreams"


@app.post("/start-livestream")
def start_livestream(req: LivestreamRequest, background_tasks: BackgroundTasks):
    stream_id = hashlib.sha256(f"{req.output_dir}/{req.output_name}".encode()).hexdigest()

    if stream_id in active_streams:
        raise HTTPException(
            status_code=400,
            detail="Un téléchargement est déjà en cours pour ce nom."
        )

    def run_command():
        try:
            cmd = [
                "python",
                "youtube_livestream_downloader.py",
                "--url", req.url,
                "--duration", str(req.duration_min),
                "--output-name", req.output_name,
                "--output-dir", os.path.join("./data", req.output_dir)
            ]
            subprocess.run(cmd)
        finally:
            active_streams.pop(stream_id, None)

    background_tasks.add_task(run_command)
    active_streams[stream_id] = True

    return {
        "message": "Commande lancée en tâche de fond",
        "cmd": f"python youtube_livestream_downloader.py --url {req.url} --duration {req.duration_min} --output-name {req.output_name} --output-dir {req.output_dir}",
        "stream_id": stream_id
    }
