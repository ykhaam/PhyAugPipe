#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metadata.panda70m_index import Panda70MIndex, Panda70MIndexConfig
from src.utils.io import load_yaml


def main():
    p70 = load_yaml("configs/panda70m.yaml")
    idx = Panda70MIndex(Panda70MIndexConfig(**p70["metadata"]))
    print(idx.inspect())


if __name__ == "__main__":
    main()
