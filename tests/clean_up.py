import subprocess
import pathlib


def cleanup():
    subprocess.run("pip uninstall git-hooks -y")
    mask_config = pathlib.Path(__file__).parents[1] / "mask.config"
    mask_config.unlink()
    pre_commit = pathlib.Path(__file__).parents[1] / ".git/hooks/pre-commit"
    pre_commit.unlink()
