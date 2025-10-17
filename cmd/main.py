import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from interpreter.saga import run_file, run_prompt

if __name__ == "__main__":
    args = sys.argv
    argn = len(args)

    if argn > 2:
        sys.exit("Usage: saga [script]")
    elif argn == 2:
        try:
            run_file(args[1])
        except Exception as err:
            sys.exit(f"Error: running file {err}")
    else:
        run_prompt()
        