import textwrap

from colorama import Back, Fore, Style


class PrettyOutput:
    @staticmethod
    def error(text: str) -> str:
        return Fore.RED + f"[ERROR] {textwrap.dedent(text)}" + Style.RESET_ALL

    @staticmethod
    def success(text: str) -> str:
        return Fore.GREEN + f"[SUCCESS] {textwrap.dedent(text)}" + Style.RESET_ALL

    @staticmethod
    def info(text: str) -> str:
        return Fore.BLUE + f"[INFO] {textwrap.dedent(text)}" + Style.RESET_ALL

    @staticmethod
    def warning(text: str) -> str:
        return Fore.RED + f"[WARNING] {textwrap.dedent(text)}" + Style.RESET_ALL
