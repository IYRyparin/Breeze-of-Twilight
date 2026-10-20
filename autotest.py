from src.manager.manage import ConfigManager


def testout():
    a = ConfigManager()
    a.load_file(".\\grammar\\examples\\basic.bot", True)
    a.printer()


if __name__ == "__main__":
    testout()
