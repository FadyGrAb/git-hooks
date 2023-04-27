import pathlib
import re
import shutil
import subprocess
import sys

import toml

from ..exceptions import *
from ..utils import PrettyOutput


class MaskGitHook:
    def __init__(self, git_dir: pathlib.Path) -> None:
        try:
            config_file = git_dir / "hooks/mask.toml"
            if not config_file.exists():
                raise NoConfigurationFileFound()
            self.configs = toml.load(config_file)
        except NoConfigurationFileFound as e:
            print(e)
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    def __get_modified_files(self) -> list[pathlib.Path]:
        cmd_str = "git diff-index --cached --name-only HEAD"
        cmd_stdout = subprocess.run(cmd_str, capture_output=True, shell=True).stdout
        files_modified = cmd_stdout.decode("utf8").strip().split("\n")
        files_modified = [
            pathlib.Path(file)
            for file in files_modified
            if file not in self.configs["ignore"]["files"]
        ]
        return files_modified

    def __read_file(self, file: pathlib.Path) -> str:
        with file.open(mode="r") as f:
            file_content = f.read()
        return file_content

    def __write_file(self, file: pathlib.Path, content: str) -> None:
        with file.open(mode="w") as f:
            f.write(content)

    @staticmethod
    def __mask_data(key: str, show_char: int) -> str:
        mask_stop = len(key) - show_char
        return ("*" * mask_stop) + key[mask_stop:]

    def mask(self) -> None:
        modified_files = self.__get_modified_files()
        if len(modified_files) == 0:
            PrettyOutput.info("[MASK GITHOOK] There aren't any modified files.")
        else:
            for file in modified_files:
                try:
                    file_content = self.__read_file(file)
                except FileNotFoundError:
                    continue
                except PermissionError:
                    continue

                original_content = file_content

                for mask_key, show_char_count in self.configs["show"].items():
                    # mask_stop = len(mask_key) - show_char_count
                    # replacement = ("*" * mask_stop) + mask_key[mask_stop:]
                    replacement = self.__mask_data(mask_key, show_char_count)
                    file_content = re.sub(mask_key, replacement, file_content)

                if original_content != file_content:
                    shutil.copy2(file, file.parent / ("_unmasked_" + file.name))
                    self.__write_file(file, file_content)
                    subprocess.run(f"git add {str(file)}", shell=True)
                    print(
                        PrettyOutput.success(
                            f"[MASK GITHOOK] Sensitive data were masked in: {file.absolute()}"
                        )
                    )
