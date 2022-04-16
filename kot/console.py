from typing import Optional
from colorama import init as colorama_init, Fore, Style

_verbose = 0


def setverbose(verbose):
    global _verbose
    _verbose = verbose


def verbose():
    return _verbose


def coloprint(*args, **kwargs):
    colorama_init(autoreset=True)
    print(*args, **kwargs)


def log(text, good: Optional[bool] = None, wait=False):
    if good is None:
        color = Fore.CYAN
    elif good:
        color = Fore.GREEN
    else:
        color = Fore.RED

    coloprint(f"{Style.BRIGHT}{color}{text}", end="")

    if wait:
        input()
    else:
        print()


def error(text):
    coloprint(f"{Style.BRIGHT}{Fore.RED}Error: {text}")


def debug(text):
    if verbose():
        coloprint(f"{Style.BRIGHT}{Fore.YELLOW}{text}")
