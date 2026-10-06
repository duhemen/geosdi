"""Test priority ranking."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.layer6_synthesis.digital_twin.priority import (
    compute_priority_ranking,
    get_priority_summary,
)


def main():
    print("=" * 80)
    print("  PRIORITY RANKING — Top 10 WKP")
    print("=" * 80)

    rankings = compute_priority_ranking(limit=10)

    for r in rankings:
        print(f"\n#{r.priority_rank:2} | {r.kode} — {r.nama} ({r.provinsi})")
        print(f"    Priority: {r.priority_score:.2f} [{r.priority_level}]")
        print(f"    GDI: {r.gdi_current:.2f} | Kapasitas: {r.kapasitas_mw:.0f} MW")
        print(f"    Scores → Impact: {r.impact_score:.1f} | Urgency: {r.urgency_score:.1f} | Effort: {r.effort_score:.1f} | Conf: {r.confidence_score:.1f}")
        print(f"    Intervention: {r.intervention_type.upper()}")
        print(f"    Rec: {r.recommendation[:80]}...")

    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80)

    summary = get_priority_summary()
    print(f"\n📊 Total WKP: {summary['total_wkp']}")
    print(f"\n📊 By Priority Level:")
    for level, count in summary["by_level"].items():
        print(f"   {level}: {count}")

    print(f"\n📊 By Intervention Type:")
    for t, count in summary["by_intervention"].items():
        print(f"   {t}: {count}")

    print()


if __name__ == "__main__":
    main()