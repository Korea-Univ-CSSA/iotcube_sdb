import argparse
import sys
from pathlib import Path
from typing import Optional

#!/usr/bin/env python3
"""
Read a file (default: sample_ts) with lines like:
    asdf/asdf
and output git clone commands:
    git clone https://github.com/asdf/asdf.git

Usage:
    python add_gitclone.py            # reads sample_ts, prints to stdout
    python add_gitclone.py -i input -o out.txt
    python add_gitclone.py --ssh     # produce ssh form: git clone git@github.com:org/repo.git
"""
def make_clone_cmd(s):
        return f"git clone https://github.com/{s}.git"


f = open("sample_ts", "r")
lines = f.readlines()
print(lines)
lines_out = [make_clone_cmd(i.strip()) for i in lines]
print(lines_out)
f.close()

f = open("sample_ts_git", "w")

for i in lines_out:
    f.write(i + "\n")

f.close()
