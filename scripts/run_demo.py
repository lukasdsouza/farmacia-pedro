import os
import subprocess
import sys


def ensure_db():
    db_path = os.path.join("data", "erp_demo.db")
    if not os.path.exists(db_path):
        subprocess.check_call([sys.executable, os.path.join("scripts", "seed_demo_db.py")])


def main():
    ensure_db()
    subprocess.check_call([sys.executable, "-m", "src.runner"])


if __name__ == "__main__":
    main()
