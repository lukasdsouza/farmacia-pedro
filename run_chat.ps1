$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

python scripts\seed_demo_db.py
python scripts\chat_cli.py
