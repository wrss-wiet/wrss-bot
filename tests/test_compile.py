import unittest
import py_compile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {"env", "tests", ".venv", "__pycache__"}

def all_python_files():
    for path in REPO_ROOT.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        yield path

class TestCompilation(unittest.TestCase):
    def test_every_file_compiles(self):
        failed = []
        for pyfile in all_python_files():
            try:
                py_compile.compile(pyfile, doraise=True)
            except Exception as e:
                failed.append(f"{pyfile}: {e}")

        if failed:
            self.fail("❌ Błąd kompilacji:\n" + "\n".join(failed))

if __name__ == "__main__":
    unittest.main()
