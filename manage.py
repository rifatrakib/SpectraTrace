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


@app.command(name="start")
def run_containers(show_logs: bool = True, build: bool = False):
    command = "docker compose up"

    if not show_logs:
        command = f"{command} -d"

    if build:
        prep = "poetry export -f requirements.txt --output requirements.txt --without-hashes"
        subprocess.run(prep, shell=True)
        command = f"{command} --build"
        subprocess.run(command, shell=True)
        subprocess.run('docker image prune --force --filter "dangling=true"', shell=True)
        subprocess.run("rm requirements.txt", shell=True)
    else:
        subprocess.run(command, shell=True)


@app.command(name="stop")
def stop_containers(drop_volumes: bool = False):
    if drop_volumes:
        command = "docker compose down --volumes"
    else:
        command = "docker compose stop"

    subprocess.run(command, shell=True)


@app.command(name="build")
def rebuild_api_image():
    prep = "poetry export -f requirements.txt --output requirements.txt --without-hashes"
    subprocess.run(prep, shell=True)
    subprocess.run("docker build . -t spectratrace-api", shell=True)
    subprocess.run("docker build ./queue -t spectratrace-queue", shell=True)
    subprocess.run('docker image prune --force --filter "dangling=true"', shell=True)
    subprocess.run("rm requirements.txt", shell=True)


@app.command(name="run-tests")
def run_tests():
    subprocess.run("coverage run -m pytest", shell=True)
    subprocess.run("coverage report", shell=True)
    subprocess.run("coverage html", shell=True)


if __name__ == "__main__":
    app()
