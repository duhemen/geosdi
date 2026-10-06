"""
Syntax checker untuk semua file Python di src/
"""
import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def check_file(filepath):
    """Cek syntax Python file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 60)
    print("  SYNTAX CHECKER")
    print("=" * 60)

    src_dir = Path("src")
    py_files = list(src_dir.rglob("*.py"))

    print(f"\nChecking {len(py_files)} Python files...\n")

    errors = 0
    for f in py_files:
        ok, err = check_file(f)
        if ok:
            print(f"  [OK] {f.relative_to(src_dir)}")
        else:
            print(f"  [X] {f.relative_to(src_dir)}")
            print(f"      {err}")
            errors += 1

    print()
    print("=" * 60)
    if errors == 0:
        print("  [OK] ALL FILES VALID")
    else:
        print(f"  [X] {errors} FILE(S) WITH ERRORS")
    print("=" * 60)

    return errors


if __name__ == "__main__":
    sys.exit(main())