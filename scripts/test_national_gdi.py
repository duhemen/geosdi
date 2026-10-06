"""Test national GDI aggregator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.layer6_synthesis.digital_twin.aggregator import get_national_gdi, get_health_score


def main():
    print("=" * 60)
    print("  NATIONAL GDI — AGREGAT")
    print("=" * 60)

    n = get_national_gdi()

    print(f"\n📊 Total WKP       : {n.total_wkp}")
    print(f"🏝️  Total Provinsi  : {n.total_provinsi}")
    print(f"⚡ Total Operasi    : {n.total_operasi}")
    print(f"💾 Total Kapasitas  : {n.total_kapasitas_mw} MW")
    print(f"\n📈 GDI Mean         : {n.gdi_mean}")
    print(f"📈 GDI Std          : ± {n.gdi_std}")
    print(f"📈 GDI Weighted     : {n.gdi_weighted}")

    print(f"\n📊 By Status:")
    for s, c in n.by_status.items():
        print(f"   {s}: {c}")

    print(f"\n🏆 Top 5 WKP:")
    for w in n.top_wkp:
        print(f"   {w['kode']:8} {w['nama']:20} GDI: {w['gdi_mean']:.2f}")

    print(f"\n⚠️  Bottom 5 WKP:")
    for w in n.bottom_wkp:
        print(f"   {w['kode']:8} {w['nama']:20} GDI: {w['gdi_mean']:.2f}")

    health = get_health_score(n)
    print(f"\n💚 Health Score     : {health['health_score']}")
    print(f"💚 Category         : {health['category']}")
    print(f"💚 Diversity        : {health['diversity_score']}%")
    print(f"💚 Operasi Ratio    : {health['operasi_ratio']}%")
    print()


if __name__ == "__main__":
    main()