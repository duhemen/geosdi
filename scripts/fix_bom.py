"""
Fix BOM (Byte Order Mark) di file Python.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def fix_bom(filepath):
    """Hapus BOM dari file."""
    try:
        with open(filepath, "rb") as f:
            content = f.read()

        # Cek BOM UTF-8: EF BB BF
        if content.startswith(b"\xef\xbb\xbf"):
            content = content[3:]  # Strip BOM
            with open(filepath, "wb") as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  [X] Error: {e}")
        return False


def main():
    print("=" * 60)
    print("  FIX BOM — Byte Order Mark Remover")
    print("=" * 60)

    src_dir = Path("src")
    py_files = list(src_dir.rglob("*.py"))

    fixed = 0
    for f in py_files:
        if fix_bom(f):
            print(f"  [FIXED] {f.relative_to(src_dir)}")
            fixed += 1

    print()
    print(f"  [OK] Fixed: {fixed} files")
    print("=" * 60)


if __name__ == "__main__":
    main()