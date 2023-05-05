import os
import pathlib
import re
import shutil
import subprocess
import sys
from collections import OrderedDict

import toml
from jinja2 import Environment, FileSystemLoader, meta

from ..exceptions import *
from ..utils import PrettyOutput


class MaskGitHook:
    def __init__(self, root_dir: pathlib.Path) -> None:
        self.root_dir = root_dir
        try:
            self.configs = toml.loads(self.__render_toml_template())
        except toml.decoder.TomlDecodeError as e:
            print(PrettyOutput.error("[mask.config] " + e.__str__()))
            print(PrettyOutput.error("Please revise your mask.config"))
            sys.exit(1)

    def __render_toml_template(self) -> str:
        jinja_env = Environment(loader=FileSystemLoader(str(self.root_dir)))
        parsed_template = jinja_env.parse(
            jinja_env.loader.get_source(jinja_env, "mask.config")
        )
        vars = meta.find_undeclared_variables(parsed_template)
        env_vars = {var: os.environ.get(var, None) for var in vars}
        for var, value in env_vars.items():
            if not value:
                print(
                    PrettyOutput.warning(
                        f"Env. variable '{var}' in mask.config is not set."
                    )
                )
        env_vars = {var: value for var, value in env_vars.items() if value}
        template = jinja_env.get_template("mask.config")
        result = template.render(env_vars)
        result = re.sub(r"\n\s+=.*\n?", "\n", result)
        return result

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
                    # Write a .masked file
                    masked_file = file.parent / ".masked"
                    mode = "+r" if masked_file.exists() else "w"
                    with masked_file.open(mode=mode) as f:
                        if mode == "w":
                            f.write(file.name)
                        else:
                            contents = f.read()
                            if file.name not in contents:
                                f.seek(0)
                                f.write(contents.strip() + f"\n{file.name}")
                                f.truncate()

                    print(
                        PrettyOutput.success(
                            f"[MASK GITHOOK] Sensitive data were masked in: {file.absolute()}"
                        )
                    )

    def reverse_mask(self, file: str):
        file = pathlib.Path(file)
        masked_secrets = OrderedDict(
            [
                (self.__mask_data(key, show), key)
                for key, show in self.configs["show"].items()
            ]
        )
        mask_count = 0
        _masked_secrets = masked_secrets.copy()
        for masked, original in _masked_secrets.items():
            if all([c == "*" for c in masked]):
                if len(masked) > mask_count:
                    mask_count = len(masked)
                    masked_secrets.move_to_end(masked, last=False)

        with file.open("+r") as f:
            content = f.read()
            new_content = content
            for masked, original in masked_secrets.items():
                new_content = new_content.replace(masked, original)
            if content != new_content:
                f.seek(0)
                f.write(new_content)
                f.truncate()

        print(PrettyOutput.success(f"[SUCCESS] file {file.name} is unmasked."))
