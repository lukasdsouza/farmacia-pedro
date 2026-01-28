import os
import subprocess
import sys


def main():
    root = os.path.dirname(os.path.dirname(__file__))
    subprocess.check_call([sys.executable, "-m", "src.chat.engine"], cwd=root)


if __name__ == "__main__":
    main()
