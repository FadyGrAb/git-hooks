import pathlib
import shutil
import subprocess
import sys

import click

from ..exceptions import *
from ..hooks.mask import MaskGitHook
from ..utils import PrettyOutput


def get_current_repo_git_path() -> pathlib.Path:
    cmd_git_dir = (
        subprocess.run("git rev-parse --show-toplevel", capture_output=True, shell=True)
        .stdout.decode("utf8")
        .strip()
    )
    return pathlib.Path(cmd_git_dir) / ".git"


supported_hooks = ["mask"]


@click.group()
def cli():
    """A CLI tool to create a data masking git hook to mask the user's
    predefined sensitive data before the git commit.
    """
    pass


@cli.command()
@click.argument("hook")
def init(hook: str) -> None:
    """Adds the hook and template config to '.git/hooks'.
    Currently the 'hook' arg can take only 'mask' value.
    """
    try:
        if hook.lower() not in supported_hooks:
            raise NotSupportedHook(hook=hook)

        templates_dir = pathlib.Path(__file__).parents[1] / "templates"
        git_dir = get_current_repo_git_path()
        hooks_dir = git_dir / "hooks"

        if not git_dir.exists():
            raise GitPathNotFound()

        hooks_dir.mkdir(exist_ok=True)

        if hook.lower() == "mask":
            # pre-commit file
            pre_commit_script = hooks_dir / "pre-commit"
            code = [
                f"#!{str(pathlib.Path(sys.executable))}\n",
                "import subprocess\n",
                "subprocess.run('git-hooks exec mask', shell=True)",
            ]
            with pre_commit_script.open(mode="w") as script:
                script.writelines(code)
            print(PrettyOutput.info(f"pre-commit is created in {hooks_dir}"))

            # mask.toml file
            config_toml = templates_dir / "mask.toml"
            shutil.copy2(config_toml, hooks_dir)
            print(PrettyOutput.info(f"mask.toml is created in {hooks_dir}"))

            print(PrettyOutput.success("Mask git hook is initiated successfully."))

    except NotSupportedHook as e:
        print(e)
        sys.exit(1)
    except GitPathNotFound as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)


@cli.command()
@click.argument("hook")
def exec(hook: str) -> None:
    """Executes the passed hook."""
    if hook.lower() == "mask":
        masker = MaskGitHook(get_current_repo_git_path())
        masker.mask()
    else:
        print(PrettyOutput.error(f"This hook is not supported: {hook}"))


@cli.command()
@click.argument("hook")
def disable(hook: str) -> None:
    """Disables the passed hook"""
    git_dir = get_current_repo_git_path()
    hooks_dir = git_dir / "hooks"

    if hook.lower() == "mask":
        pre_commit_script = hooks_dir / "pre-commit"
        if pre_commit_script.exists():
            shutil.move(pre_commit_script, pre_commit_script.parent / "_pre-commit")
            print(PrettyOutput.success("Mask git hook is disabled"))
        else:
            print(
                PrettyOutput.warning(
                    "Mask git hook is not initiated. Nothing will happen."
                )
            )
    else:
        print(PrettyOutput.error(f"This hook is not supported: {hook}"))


@cli.command()
@click.argument("hook")
def enable(hook: str) -> None:
    """Enables the passed hook. Must be initiated first."""
    git_dir = get_current_repo_git_path()
    hooks_dir = git_dir / "hooks"

    if hook.lower() == "mask":
        pre_commit_script = hooks_dir / "_pre-commit"
        if pre_commit_script.exists():
            shutil.move(pre_commit_script, pre_commit_script.parent / "pre-commit")
            print(PrettyOutput.success("Mask git hook is enabled"))
        else:
            print(
                PrettyOutput.warning(
                    "Mask git hook is not initiated or already enabled. Nothing will happen."
                )
            )
    else:
        print(PrettyOutput.error(f"This hook is not supported: {hook}"))


@cli.command()
def list():
    """Lists currently supported git hooks"""
    print("Currently supported hooks:")
    for idx, hook in enumerate(supported_hooks):
        print(str(idx + 1).rjust(2) + "- " + hook)


@cli.command()
def status():
    """Lists the status of currently enabled or disabled hooks."""
    git_dir = get_current_repo_git_path()
    hooks_dir = git_dir / "hooks"
    for hook in supported_hooks:
        if hook == "mask":
            status = (
                "Enabled"
                if (hooks_dir / "pre-commit").exists()
                else "Disabled"
                if (hooks_dir / "_pre-commit").exists()
                else "Not initialized"
            )
            print("mask".ljust(8) + status)
        else:
            pass  # Future implementation


if __name__ == "__main__":
    cli()
