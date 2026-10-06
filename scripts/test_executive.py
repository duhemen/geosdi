"""Test executive summary."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.layer6_synthesis.digital_twin.executive import generate_executive_summary


def main():
    summary = generate_executive_summary()

    print("=" * 80)
    print("  EXECUTIVE SUMMARY — GeoSDI Geothermal")
    print("=" * 80)
    print(f"\nGenerated: {summary['generated_at']}\n")

    print(f"📌 HEADLINE:\n   {summary['headline']}\n")

    print("─" * 80)
    print("🔍 KEY FINDINGS")
    print("─" * 80)

    for f in summary["findings"]:
        print(f"\n{f['icon']} {f['title']}")
        print(f"   {f['body']}")

    print("\n" + "─" * 80)
    print("💡 RECOMMENDATIONS")
    print("─" * 80)

    for r in summary["recommendations"]:
        print(f"\n[{r['priority']}] {r['action']}")
        print(f"   Impact: {r['expected_impact']}")

    print()


if __name__ == "__main__":
    main()