/* ==========================================================
   GeoSDI — Analytics Page
   ========================================================== */

console.log("📊 analytics.js loaded");

const GDI_COLORS = {
    'Optimal': '#10b981',
    'Stabil': '#3b82f6',
    'Berkembang': '#f59e0b',
    'Rentan': '#ef4444',
    'Kritis': '#7f1d1d',
};

async function loadGDI() {
    const resp = await fetch('/api/gdi');
    if (!resp.ok) throw new Error('Failed to load GDI');
    const data = await resp.json();
    return data.data;
}

async function renderChart() {
    const data = await loadGDI();
    const ctx = document.getElementById('gdiChartAnalytics');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(r => r.nama),
            datasets: [{
                label: 'GDI Score',
                data: data.map(r => r.gdi_mean),
                backgroundColor: data.map(r => (GDI_COLORS[r.status] || '#666') + 'cc'),
                borderColor: data.map(r => GDI_COLORS[r.status] || '#666'),
                borderWidth: 2,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'GDI Ranking WKP Indonesia',
                    font: { size: 16, weight: 'bold' },
                    color: '#1e3a8a'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const idx = context.dataIndex;
                            const r = data[idx];
                            return [
                                `GDI: ${r.gdi_mean.toFixed(2)} ± ${r.gdi_std.toFixed(2)}`,
                                `90% CI: [${r.gdi_ci_lower.toFixed(1)}, ${r.gdi_ci_upper.toFixed(1)}]`,
                                `Status: ${r.status}`,
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: 'GDI Score' }
                }
            }
        }
    });
}

async function renderTable() {
    const data = await loadGDI();
    const tbody = document.getElementById('analyticsTableBody');
    if (!tbody) return;

    tbody.innerHTML = data.map((r, i) => `
        <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 0.75rem; font-weight: bold; color: #64748b;">${i + 1}</td>
            <td style="padding: 0.75rem; font-weight: bold;">${r.kode} — ${r.nama}</td>
            <td style="padding: 0.75rem; color: #64748b;">${r.provinsi}</td>
            <td style="padding: 0.75rem; text-align: right; font-weight: bold; font-size: 1.05rem;">${r.gdi_mean.toFixed(2)}</td>
            <td style="padding: 0.75rem; text-align: right; color: #94a3b8;">± ${r.gdi_std.toFixed(2)}</td>
            <td style="padding: 0.75rem; text-align: center; color: #64748b; font-size: 0.85rem;">[${r.gdi_ci_lower.toFixed(1)}, ${r.gdi_ci_upper.toFixed(1)}]</td>
            <td style="padding: 0.75rem; text-align: center;">
                <span style="background: ${GDI_COLORS[r.status]}22; color: ${GDI_COLORS[r.status]}; padding: 0.25rem 0.75rem; border-radius: 12px; font-weight: bold; font-size: 0.8rem;">
                    ${r.status}
                </span>
            </td>
        </tr>
    `).join('');
}

async function renderInsights() {
    const data = await loadGDI();
    const container = document.getElementById('insightsContainer');
    if (!container) return;

    // Hitung insights
    const top = data[0];
    const bottom = data[data.length - 1];
    const avgGDI = (data.reduce((s, r) => s + r.gdi_mean, 0) / data.length).toFixed(2);
    const spread = (top.gdi_mean - bottom.gdi_mean).toFixed(2);

    // Cari WKP dengan conflict tertinggi
    const worstConflict = data.reduce((max, r) => {
        const c = r.contributions.C || 0;
        return c < (max.contributions.C || 0) ? r : max;
    }, data[0]);

    const insights = [
        {
            icon: '🏆',
            text: `<strong>${top.nama}</strong> memimpin dengan GDI <strong>${top.gdi_mean.toFixed(2)}</strong> (${top.status}). Ini WKP paling mature dan stabil.`,
        },
        {
            icon: '⚠️',
            text: `<strong>${bottom.nama}</strong> masih memerlukan pengembangan dengan GDI <strong>${bottom.gdi_mean.toFixed(2)}</strong> (${bottom.status}).`,
        },
        {
            icon: '📊',
            text: `Rata-rata GDI nasional: <strong>${avgGDI}</strong>. Rentang skor: <strong>${spread}</strong> poin (${top.nama} vs ${bottom.nama}).`,
        },
        {
            icon: '🎯',
            text: `<strong>${worstConflict.nama}</strong> memiliki intensitas konflik tertinggi. Resolusi konflik berpotensi menaikkan GDI secara signifikan.`,
        },
        {
            icon: '💡',
            text: `Gunakan <strong>Simulator Intervensi</strong> di Dashboard untuk mengeksplorasi skenario kebijakan.`,
        },
    ];

    container.innerHTML = insights.map(i => `
        <div style="
            display: flex;
            gap: 1rem;
            padding: 0.75rem 0;
            border-bottom: 1px solid #cbd5e1;
        ">
            <div style="font-size: 1.5rem;">${i.icon}</div>
            <div style="color: #334155; line-height: 1.6;">${i.text}</div>
        </div>
    `).join('');
}

window.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('gdiChartAnalytics')) {
        renderChart();
        renderTable();
        renderInsights();
    }
});