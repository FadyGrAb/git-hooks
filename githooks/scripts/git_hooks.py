import pathlib
import shutil
import subprocess
import sys
import textwrap

import click

from ..exceptions import *
from ..hooks.mask import MaskGitHook
from ..utils import PrettyOutput


def get_current_repo_root_path() -> pathlib.Path:
    cmd_git_dir = (
        subprocess.run("git rev-parse --show-toplevel", capture_output=True, shell=True)
        .stdout.decode("utf8")
        .strip()
    )
    return pathlib.Path(cmd_git_dir)


supported_hooks = ["mask", "test"]


@click.group()
def cli():
    """A CLI tool to implement git hooks on git commits."""
    pass


@cli.command()
@click.argument("hook")
def init(hook: str) -> None:
    """Adds the hook and template config to '.git/hooks'.
    Currently the 'hook' arg can take only 'mask' value.
    """
    try:
        templates_dir = pathlib.Path(__file__).parents[1] / "templates"
        repo_root_dir = get_current_repo_root_path()
        git_dir = repo_root_dir / ".git"
        hooks_dir = git_dir / "hooks"

        if not git_dir.exists():
            raise GitPathNotFound()

        hooks_dir.mkdir(exist_ok=True)

        if hook.lower() == "mask":
            # pre-commit file
            pre_commit_script = hooks_dir / "pre-commit"
            code = textwrap.dedent(
                f"""\
                #!{str(pathlib.Path(sys.executable))}
                import subprocess

                subprocess.run('git-hooks exec mask', shell=True)
                """
            )
            with pre_commit_script.open(mode="w") as script:
                script.writelines(code)
            print(PrettyOutput.info(f"pre-commit is created in {hooks_dir}"))

            # mask.config file
            config_toml = templates_dir / "mask.config"
            if not (repo_root_dir / "mask.config").exists():
                shutil.copy2(config_toml, repo_root_dir)
                print(PrettyOutput.info(f"mask.config is created in {repo_root_dir}"))
            else:
                print(
                    PrettyOutput.info(
                        f"mask.config already exists in {repo_root_dir}. Skipping creation."
                    )
                )

            # Add _unmasked_* to .gitignore
            gitignore = repo_root_dir / ".gitignore"
            content = ""
            if gitignore.exists():
                with gitignore.open(mode="r") as f:
                    content = f.read()

            if ("_unmasked_*" not in content) or (not gitignore.exists()):
                with gitignore.open(mode="a") as f:
                    f.write(f"\n_unmasked_*")
                    print(PrettyOutput.info("'_unmasked_*' was added to gitignore."))
                    f.write(f"\n/mask.config")
                    print(PrettyOutput.info("'/mask.config' was added to gitignore."))
            elif ("_unmasked_*" in content) and ("/mask.config" not in content):
                print(
                    PrettyOutput.warning(
                        """\
                        ******************************************************************
                        /mask.config is NOT in .gitignore. Your secrets will be committed.
                        If you do not want that, add it manually to .gitignore.
                        ******************************************************************"""
                    )
                )

            print(
                PrettyOutput.success(
                    """\
                    =============================================================
                    Mask git hook is initiated successfully.
                    Please edit 'mask.config' in your repo's root directory.
                    You can use '{{ ENV_VAR }}' to include environment variables.
                    You can remove 'mask.config' form the gitignore file if you want to commit it"""
                )
            )
        elif hook.lower() == "test":
            sys.exit(0)
        else:
            print(
                PrettyOutput.error(
                    f"This hook is not supported: {hook}. Type 'git-hooks list' for the full list."
                )
            )
            sys.exit(1)

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
@click.option(
    "-r",
    "--reverse",
    is_flag=True,
    default=False,
    show_default=True,
    help="Execute reverse hook operation if available",
)
@click.option(
    "-f",
    "--file",
    default=None,
    type=click.Path(exists=True),
    help="Specify the file for the reverse operation. If not specified, all files in the .ghunmask file will be unmasked",
)
def exec(hook: str, reverse: bool, file: pathlib.Path) -> None:
    """Executes the passed hook."""
    if hook.lower() == "mask":
        masker = MaskGitHook(get_current_repo_root_path())
        if not reverse:
            masker.mask()
        else:
            masker.reverse_mask(file)

    elif hook.lower() == "test":
        sys.exit(0)
    else:
        print(
            PrettyOutput.error(
                f"This hook is not supported: {hook}. Type 'git-hooks list' for the full list."
            )
        )
        sys.exit(1)


@cli.command()
@click.argument("hook")
def disable(hook: str) -> None:
    """Disables the passed hook"""
    git_dir = get_current_repo_root_path() / ".git"
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
    elif hook.lower() == "test":
        sys.exit(0)
    else:
        print(
            PrettyOutput.error(
                f"This hook is not supported: {hook}. Type 'git-hooks list' for the full list."
            )
        )
        sys.exit(1)


@cli.command()
@click.argument("hook")
def enable(hook: str) -> None:
    """Enables the passed hook. Must be initiated first."""
    git_dir = get_current_repo_root_path() / ".git"
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
    elif hook.lower() == "test":
        sys.exit(0)
    else:
        print(
            PrettyOutput.error(
                f"This hook is not supported: {hook}. Type 'git-hooks list' for the full list."
            )
        )
        sys.exit(1)


@cli.command()
def list():
    """Lists currently supported git hooks"""
    print("Currently supported hooks:")
    hooks = [hook for hook in supported_hooks if (hook != "test")]
    for idx, hook in enumerate(hooks):
        print(str(idx + 1).rjust(2) + "- " + hook)


@cli.command()
def status():
    """Lists the status of currently enabled or disabled hooks."""
    git_dir = get_current_repo_root_path() / ".git"
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
