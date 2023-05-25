import os
import subprocess

import uvicorn
from typer import Typer

app = Typer()


@app.command(name="run-server")
def run_api_server(mode: str = "development"):
    os.environ["MODE"] = mode

    if mode == "development":
        subprocess.Popen("wsl redis-server", shell=True)

    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)


@app.command(name="run-containers")
def run_containers(show_logs: bool = True):
    command = "docker compose up"

    if not show_logs:
        command = f"{command} -d"

    subprocess.run(command, shell=True)


@app.command(name="stop-containers")
def stop_containers(drop_volumes: bool = False):
    command = "docker compose down"

    if drop_volumes:
        command = f"{command} --volumes"

    subprocess.run(command, shell=True)


@app.command(name="rebuild-api-image")
def rebuild_api_image():
    subprocess.run("docker build . -t spectratrace-api", shell=True)
    subprocess.run('docker image prune --force --filter "dangling=true"', shell=True)


if __name__ == "__main__":
    app()
