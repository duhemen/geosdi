"""
Test enhanced scenario simulator.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.layer6_synthesis.digital_twin.scenario import run_preset, PRESET_SCENARIOS


def print_result(result):
    """Print scenario result dengan rapi."""
    delta_sign = "+" if result.delta_gdi >= 0 else ""

    print(f"\n   Baseline GDI : {result.baseline_gdi}")
    print(f"   Simulated    : {result.simulated_gdi}")
    print(f"   Delta        : {delta_sign}{result.delta_gdi} ({delta_sign}{result.delta_percent}%)")
    print(f"\n   Affected     : {result.wkp_affected}")
    print(f"   Improved     : {result.wkp_improved}")
    print(f"   Worsened     : {result.wkp_worsened}")
    print(f"   Unchanged    : {result.wkp_unchanged}")

    print(f"\n   📊 By WKP Type:")
    for t, data in result.by_type.items():
        if data["count"] > 0:
            print(f"      {t:12} : {data['count']:3} WKP, avg Δ = {data['avg_delta']:+.2f}")

    if result.top_improvements:
        print(f"\n   🏆 Top Improvements:")
        for w in result.top_improvements[:3]:
            print(f"      {w['kode']:8} {w['nama']:20} Δ {w['delta']:+.2f} ({w['wkp_type']}, mult={w['multiplier']})")


def main():
    print("=" * 70)
    print("  ENHANCED SCENARIO SIMULATOR — Test")
    print("=" * 70)

    # Baseline
    print("\n📊 BASELINE (no change):")
    print_result(run_preset("baseline"))

    # Optimistic
    print("\n" + "=" * 70)
    print("🎯 OPTIMISTIC — Investasi & Kebijakan")
    print("=" * 70)
    print_result(run_preset("optimistic"))

    # Pessimistic
    print("\n" + "=" * 70)
    print("🎯 PESSIMISTIC — Krisis Ekonomi & Konflik")
    print("=" * 70)
    print_result(run_preset("pessimistic"))

    # Social First
    print("\n" + "=" * 70)
    print("🎯 SOCIAL FIRST — Pemberdayaan Masyarakat")
    print("=" * 70)
    print_result(run_preset("social_first"))

    # Tech First
    print("\n" + "=" * 70)
    print("🎯 TECH FIRST — Investasi Teknologi")
    print("=" * 70)
    print_result(run_preset("tech_first"))

    # Mature Only
    print("\n" + "=" * 70)
    print("🎯 MATURE ONLY — Fokus WKP Mature")
    print("=" * 70)
    print_result(run_preset("mature_only"))

    # Exploration Only
    print("\n" + "=" * 70)
    print("🎯 EXPLORATION ONLY — Fokus Eksplorasi")
    print("=" * 70)
    print_result(run_preset("exploration_only"))

    print()
    print("=" * 70)
    print("  ✅ ALL SCENARIOS TESTED")
    print("=" * 70)


if __name__ == "__main__":
    main()