import os
import subprocess
import sys


def main():
    root = os.path.dirname(os.path.dirname(__file__))
    subprocess.check_call([sys.executable, "-m", "src.chat.webhook"], cwd=root)


if __name__ == "__main__":
    main()
