
from database.init_db import init_db
from menus.main_menu import MainMenu


def main() -> None:
    init_db()  
    try:
        MainMenu().run()
    except (KeyboardInterrupt, EOFError):
        print()
    print("Viszlát!")


if __name__ == "__main__":
    main()
