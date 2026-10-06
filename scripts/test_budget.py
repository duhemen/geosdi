"""Test budget allocation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.layer6_synthesis.digital_twin.budget import optimize_budget


def main():
    # Test 3 budget levels
    budgets = [5000, 10000, 25000]  # 5T, 10T, 25T

    for budget in budgets:
        print("\n" + "=" * 80)
        print(f"  BUDGET: Rp {budget:,} MILIAR ({budget/1000:.1f} TRILIUN)")
        print("=" * 80)

        plan = optimize_budget(budget)

        print(f"\n💰 Budget           : Rp {plan.total_budget_billion:,.0f} M")
        print(f"💰 Allocated        : Rp {plan.allocated_billion:,.0f} M")
        print(f"💰 Remaining        : Rp {plan.remaining_billion:,.0f} M")
        print(f"📊 WKP Funded       : {plan.total_wkp_funded}")
        print(f"📈 Expected Gain    : +{plan.total_expected_gdi_gain:.2f} GDI points")
        print(f"📈 National GDI     : {plan.national_gdi_before} → {plan.national_gdi_after} (+{plan.national_gdi_delta})")

        print(f"\n📋 Top 5 Allocations:")
        for i, a in enumerate(plan.allocations[:5], 1):
            print(f"   {i}. {a.kode} — {a.nama} ({a.intervention_type})")
            print(f"      Cost: Rp {a.cost_billion:.0f} M | Gain: +{a.expected_gdi_gain:.2f} | ROI: {a.roi:.2f}")

        print(f"\n📊 By Intervention Type:")
        for t, data in plan.by_intervention.items():
            print(f"   {t:15} : {data['count']:2} WKP | Rp {data['total_cost']:,.0f} M | Gain +{data['total_gain']:.2f}")

    print()


if __name__ == "__main__":
    main()