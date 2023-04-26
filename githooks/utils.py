from colorama import Fore, Back, Style


class PrettyOutput:
    @staticmethod
    def error(text: str) -> str:
        return Fore.RED + f"[ERROR] {text}" + Style.RESET_ALL

    @staticmethod
    def success(text: str) -> str:
        return Fore.GREEN + f"[SUCCESS] {text}" + Style.RESET_ALL

    @staticmethod
    def info(text: str) -> str:
        return Fore.BLUE + f"[INFO] {text}" + Style.RESET_ALL

    @staticmethod
    def warning(text: str) -> str:
        return Fore.RED + f"[WARNING] {text}" + Style.RESET_ALL
