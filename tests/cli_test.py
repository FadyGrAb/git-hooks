import pathlib
import subprocess

import pytest


def test_setup():
    subprocess.run("pip uninstall git-hooks -y", shell=True)
    setup_path = pathlib.Path(__file__).parents[1]
    subprocess.run(
        f"pip install --editable {str(setup_path)}/.", shell=True
    ).check_returncode()


@pytest.mark.parametrize(
    "command", ["init", "disable", "enable", "exec", "status", "list"]
)
def test_run_commands(command):
    if command in ["status", "list"]:
        subprocess.run(f"git-hooks {command}", shell=True).check_returncode()
    else:
        subprocess.run(f"git-hooks {command} test", shell=True).check_returncode()


@pytest.mark.parametrize("command", ["none", "existing", "commands"])
def test_fail_none_existing_commands(command):
    try:
        subprocess.run(f"git-hooks {command} test", shell=True).check_returncode()
        raise Exception("This command shouldn't have run.")
    except subprocess.CalledProcessError:
        # None existing commands should error out.
        pass


@pytest.mark.parametrize("command", ["init", "disable", "enable", "exec"])
def test_fail_none_existing_hooks(command):
    try:
        subprocess.run(
            f"git-hooks {command} nonexisting", shell=True
        ).check_returncode()
        raise Exception("This command shouldn't have run.")
    except subprocess.CalledProcessError:
        # None existing commands should error out.
        pass
