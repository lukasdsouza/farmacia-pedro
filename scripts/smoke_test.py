import os
import json
import subprocess
import sys


def main():
    subprocess.check_call([sys.executable, os.path.join("scripts", "seed_demo_db.py")])
    subprocess.check_call([sys.executable, "-m", "src.runner"])

    json_path = os.path.join("out", "report.json")
    md_path = os.path.join("out", "report.md")

    assert os.path.exists(json_path), "report.json nao foi gerado"
    assert os.path.exists(md_path), "report.md nao foi gerado"

    with open(json_path, "r", encoding="ascii") as handle:
        data = json.load(handle)

    assert "operacional" in data, "faltando relatorio operacional"
    assert "estoque" in data, "faltando relatorio de estoque"
    assert "regras" in data, "faltando relatorio de regras"

    print("Teste de fumaca OK")


if __name__ == "__main__":
    main()
