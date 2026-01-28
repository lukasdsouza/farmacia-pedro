import os
import subprocess
import sys


def main():
    subprocess.check_call([sys.executable, "-m", "src.automation.flow"])


if __name__ == "__main__":
    main()
