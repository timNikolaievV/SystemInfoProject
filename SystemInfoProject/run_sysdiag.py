import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from sysdiag.cli import main

if __name__ == "__main__":

    main()