import sys

from dotenv import load_dotenv

from manage import main as manage_main
from utils.get_pyscript import get_pyscript


def main():
    load_dotenv()

    get_pyscript('./')

    if len(sys.argv) <= 1:
        sys.argv.append("runserver")

    manage_main()


if __name__ == "__main__":
    main()
