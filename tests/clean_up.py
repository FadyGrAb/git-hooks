import subprocess
import pathlib


def cleanup():
    subprocess.run("pip uninstall git-hooks -y")
    files = [
        pathlib.Path(file)
        for file in [".ghunmask", "mask.config", ".git/hooks/pre-commit"]
    ]
    for file in files:
        file.unlink()
