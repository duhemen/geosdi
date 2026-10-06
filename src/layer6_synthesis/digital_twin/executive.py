"""
GeoSDI Digital Twin — Executive Summary Generator
===================================================
Generate narasi eksekutif untuk decision maker.
"""
from __future__ import annotations

from datetime import datetime

from src.layer6_synthesis.digital_twin.aggregator import get_national_gdi, get_health_score
from src.layer6_synthesis.digital_twin.priority import get_priority_summary


def generate_executive_summary() -> dict:
    """
    Generate executive summary dalam bahasa manusia.
    
    Cocok untuk Menteri, Direktur, atau decision maker.
    """
    national = get_national_gdi()
    health = get_health_score(national)
    priority = get_priority_summary()

    # Headline dengan health_phrase
    if health["health_score"] >= 70:
        health_icon = "🟢"
        health_phrase = "Sangat Baik"
    elif health["health_score"] >= 55:
        health_icon = "🟡"
        health_phrase = "Baik"
    elif health["health_score"] >= 40:
        health_icon = "🟠"
        health_phrase = "Perlu Perhatian"
    else:
        health_icon = "🔴"
        health_phrase = "Kritis"

    # Distribusi
    optimal = national.by_status.get("Optimal", 0)
    stabil = national.by_status.get("Stabil", 0)
    optimal_pct = (optimal / national.total_wkp * 100) if national.total_wkp > 0 else 0

    # Headline yang benar
    headline = (
        f"{health_icon} **Kesehatan Ekosistem Geothermal Indonesia: {health_phrase}** "
        f"(Health Score: {health['health_score']}/100). "
        f"Dari {national.total_wkp} WKP yang dipantau, "
        f"**{optimal}** WKP ({optimal_pct:.1f}%) sudah **Optimal** dan "
        f"**{stabil}** dalam kondisi **Stabil**. "
        f"Rata-rata GDI nasional: **{national.gdi_mean:.1f}**."
    )

    # Key findings
    findings = []

    # Finding 1: Distribusi
    findings.append({
        "icon": "📊",
        "title": "Distribusi Kualitas",
        "body": (
            f"**{optimal}** WKP ({optimal_pct:.1f}%) dalam kondisi **Optimal**, "
            f"**{stabil}** dalam kondisi **Stabil**. "
            f"Sisanya **{national.total_wkp - optimal - stabil}** WKP dalam kondisi "
            f"**Berkembang** atau lebih rendah."
        ),
    })

    # Finding 2: Prioritas intervensi
    critical = priority["by_level"]["Critical"]
    high = priority["by_level"]["High"]
    medium = priority["by_level"]["Medium"]

    if critical + high > 0:
        priority_body = (
            f"**{critical}** WKP kategori **Critical**, "
            f"**{high}** kategori **High**, "
            f"**{medium}** kategori **Medium**. "
            f"Total **{critical + high}** WKP memerlukan intervensi segera."
        )
    else:
        priority_body = (
            f"Tidak ada WKP dalam kategori **Critical** atau **High**. "
            f"**{medium}** WKP kategori **Medium**, sisanya **Low**. "
            f"Ekosistem geothermal nasional dalam kondisi stabil."
        )

    findings.append({
        "icon": "🎯",
        "title": "Prioritas Intervensi",
        "body": priority_body,
    })

    # Finding 3: Top priority
    if priority["top_10"]:
        top1 = priority["top_10"][0]
        findings.append({
            "icon": "🚨",
            "title": "Prioritas Utama",
            "body": (
                f"**{top1['kode']} — {top1['nama']}** ({top1['provinsi']}) "
                f"memerlukan perhatian utama dengan priority score **{top1['priority_score']:.1f}** "
                f"({top1['priority_level']}). "
                f"Intervensi: **{top1['intervention_type'].upper()}**. "
                f"{top1['recommendation']}"
            ),
        })

    # Finding 4: Kapasitas
    avg_capacity = national.total_kapasitas_mw / max(national.total_operasi, 1)
    findings.append({
        "icon": "⚡",
        "title": "Kapasitas Terpasang",
        "body": (
            f"Total kapasitas terpasang saat ini: **{national.total_kapasitas_mw:,.0f} MW**. "
            f"Dengan **{national.total_operasi}** WKP beroperasi, "
            f"kapasitas rata-rata per WKP operasi adalah "
            f"**{avg_capacity:,.1f} MW**."
        ),
    })

    # Finding 5: Konteks Investasi
    findings.append({
        "icon": "💰",
        "title": "Konteks Investasi",
        "body": (
            f"Untuk **Rp 10 triliun** investasi, kita bisa mengintervensi sekitar "
            f"**13-20 WKP** dengan gain rata-rata **+0.3 sampai +0.5 GDI per WKP**. "
            f"Dampak nasional mungkin kecil (~+0.05 GDI) karena hanya "
            f"sebagian WKP yang diintervensi, tetapi dampak **lokal signifikan**."
        ),
    })

    # ============================================================
    # Recommendations dengan konteks
    # ============================================================
    recommendations = []

    if critical > 0:
        recommendations.append({
            "priority": "URGENT",
            "action": f"Alokasikan tim khusus untuk {critical} WKP Critical",
            "expected_impact": "Mencegah penurunan GDI lebih lanjut di WKP paling rentan",
            "context": "Investasi per WKP ~Rp 1-5 T, durasi 6-12 bulan",
        })

    if priority["by_intervention"].get("sosial", 0) > 5:
        social_count = priority["by_intervention"]["sosial"]
        recommendations.append({
            "priority": "HIGH",
            "action": f"Program pemberdayaan masyarakat di {social_count} WKP",
            "expected_impact": "Meningkatkan social acceptance & mengurangi konflik",
            "context": "Biaya ~Rp 500 M per WKP, fokus jangka panjang",
        })

    if priority["by_intervention"].get("teknis", 0) > 20:
        tech_count = priority["by_intervention"]["teknis"]
        recommendations.append({
            "priority": "HIGH",
            "action": f"Investasi teknologi di {tech_count} WKP eksplorasi",
            "expected_impact": "Membuka potensi kapasitas baru & meningkatkan GDI transformasional",
            "context": "Biaya ~Rp 5 T per WKP, durasi 3-5 tahun, ROI jangka panjang",
        })

    if priority["by_intervention"].get("ekonomi", 0) > 10:
        eco_count = priority["by_intervention"]["ekonomi"]
        recommendations.append({
            "priority": "MEDIUM",
            "action": f"Optimalisasi operasional di {eco_count} WKP mature",
            "expected_impact": "Meningkatkan efisiensi & output tanpa investasi besar",
            "context": "Biaya ~Rp 1.5 T per WKP, ROI cepat (6-12 bulan)",
        })

    if health["health_score"] < 70:
        recommendations.append({
            "priority": "MEDIUM",
            "action": "Review kebijakan nasional & insentif",
            "expected_impact": "Meningkatkan iklim investasi geothermal",
            "context": "Jangka panjang, butuh koordinasi lintas kementerian",
        })

    return {
        "generated_at": datetime.now().isoformat(),
        "headline": headline,
        "findings": findings,
        "recommendations": recommendations,
        "raw": {
            "national": {
                "total_wkp": national.total_wkp,
                "total_provinsi": national.total_provinsi,
                "total_operasi": national.total_operasi,
                "gdi_mean": national.gdi_mean,
                "health_score": health["health_score"],
            },
            "priority_summary": priority["by_level"],
            "intervention_summary": priority["by_intervention"],
        },
    }