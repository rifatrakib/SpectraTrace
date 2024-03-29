import subprocess

from typer import Typer

app = Typer()


@app.command(name="start")
def run_containers(show_logs: bool = True, build: bool = False):
    command = "docker compose up"

    if not show_logs:
        command = f"{command} -d"

    if build:
        subprocess.run("docker compose build", shell=True)
        subprocess.run('docker image prune --force --filter "dangling=true"', shell=True)

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
    subprocess.run("docker build . -t spectratrace-api", shell=True)
    subprocess.run("docker build ./queue -t spectratrace-queue", shell=True)
    subprocess.run('docker image prune --force --filter "dangling=true"', shell=True)


@app.command(name="run-tests")
def run_tests():
    subprocess.run("coverage run -m pytest", shell=True)
    subprocess.run("coverage report", shell=True)
    subprocess.run("coverage html", shell=True)


if __name__ == "__main__":
    app()
