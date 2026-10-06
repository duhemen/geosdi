/* ==========================================================
   GeoSDI — GDI + Multi-Select Comparison
   Version: 2.2.0
   ==========================================================
   Changes in 2.2.0:
   - Empty state handling for time series (clean slate mode)
   - Removed auto-select (fresh start for users)
   - Better error messages
   ========================================================== */

console.log("📊 gdi.js v2.2.0 loaded");

const GDI_COLORS = {
    'Optimal': '#10b981',
    'Stabil': '#3b82f6',
    'Berkembang': '#f59e0b',
    'Rentan': '#ef4444',
    'Kritis': '#7f1d1d',
};

// Chart color palette
const CHART_COLORS = [
    '#3b82f6', // blue
    '#10b981', // green
    '#f59e0b', // amber
    '#ef4444', // red
    '#8b5cf6', // purple
];

// ============================================================
// State
// ============================================================
const comparisonState = {
    selected: [],
    allWkp: [],
    chart: null,
};

// ============================================================
// Load semua WKP untuk dropdown
// ============================================================
async function loadAllWkp() {
    try {
        const resp = await fetch('/api/nodes?page_size=500');
        if (!resp.ok) throw new Error('Failed to load WKP');
        const data = await resp.json();
        comparisonState.allWkp = data.data.sort((a, b) => a.kode.localeCompare(b.kode));
        console.log(`[OK] Loaded ${comparisonState.allWkp.length} WKP`);
        return comparisonState.allWkp;
    } catch (e) {
        console.error('[X] Failed to load WKP:', e);
        return [];
    }
}

// ============================================================
// Search WKP
// ============================================================
function searchWkp(query) {
    if (!query || query.length < 2) return [];
    const q = query.toLowerCase();

    return comparisonState.allWkp
        .filter(w =>
            w.kode.toLowerCase().includes(q) ||
            w.nama.toLowerCase().includes(q) ||
            w.provinsi.toLowerCase().includes(q)
        )
        .filter(w => !comparisonState.selected.some(s => s.kode === w.kode))
        .slice(0, 20);
}

// ============================================================
// Render Search Results
// ============================================================
function renderSearchResults(results) {
    const container = document.getElementById('searchResults');
    if (!container) return;

    if (results.length === 0) {
        container.style.display = 'none';
        return;
    }

    container.innerHTML = results.map(w => `
        <div class="search-result-item" data-kode="${w.kode}" style="
            padding: 0.6rem 1rem;
            cursor: pointer;
            border-bottom: 1px solid #f1f5f9;
            display: flex;
            justify-content: space-between;
            align-items: center;
        " onmouseover="this.style.background='#eff6ff'" onmouseout="this.style.background='white'">
            <div>
                <strong style="color: #1e3a8a;">${w.kode}</strong>
                <span style="margin-left: 0.5rem;">${w.nama}</span>
                <span style="color: #64748b; font-size: 0.85rem; margin-left: 0.5rem;">· ${w.provinsi}</span>
            </div>
            <span style="
                background: ${GDI_COLORS[w.status] || '#666'}22;
                color: ${GDI_COLORS[w.status] || '#666'};
                padding: 0.15rem 0.5rem;
                border-radius: 10px;
                font-size: 0.7rem;
                font-weight: bold;
            ">${w.status}</span>
        </div>
    `).join('');

    container.style.display = 'block';

    container.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
            const kode = item.dataset.kode;
            addToSelection(kode);
            document.getElementById('wkpSearchInput').value = '';
            container.style.display = 'none';
        });
    });
}

// ============================================================
// Add/Remove Selection
// ============================================================
function addToSelection(kode) {
    if (comparisonState.selected.length >= 5) {
        alert('Maksimal 5 WKP. Hapus salah satu dulu.');
        return;
    }

    const wkp = comparisonState.allWkp.find(w => w.kode === kode);
    if (!wkp) return;

    if (comparisonState.selected.some(s => s.kode === kode)) {
        return;
    }

    comparisonState.selected.push(wkp);
    renderChips();
    renderComparison();
}

function removeFromSelection(kode) {
    comparisonState.selected = comparisonState.selected.filter(s => s.kode !== kode);
    renderChips();
    renderComparison();
}

window.addToComparison = addToSelection;
window.removeFromComparison = removeFromSelection;

// ============================================================
// Render Chips
// ============================================================
function renderChips() {
    const container = document.getElementById('selectedChips');
    if (!container) return;

    if (comparisonState.selected.length === 0) {
        container.innerHTML = '<span style="color: #94a3b8; font-size: 0.85rem;">Belum ada WKP dipilih</span>';
        return;
    }

    container.innerHTML = comparisonState.selected.map((w, i) => {
        const color = CHART_COLORS[i % CHART_COLORS.length];
        return `
            <div style="
                background: ${color}22;
                border: 2px solid ${color};
                color: ${color};
                padding: 0.4rem 0.75rem;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: bold;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            ">
                <span>${w.kode} — ${w.nama}</span>
                <button onclick="removeFromComparison('${w.kode}')" style="
                    background: none;
                    border: none;
                    color: ${color};
                    cursor: pointer;
                    font-size: 1.1rem;
                    font-weight: bold;
                    padding: 0;
                    line-height: 1;
                ">×</button>
            </div>
        `;
    }).join('');
}

// ============================================================
// Render Comparison Chart — WITH EMPTY STATE HANDLING
// ============================================================
async function renderComparison() {
    const info = document.getElementById('comparisonInfo');
    const ctx = document.getElementById('comparisonChart');

    if (comparisonState.selected.length === 0) {
        if (comparisonState.chart) {
            comparisonState.chart.destroy();
            comparisonState.chart = null;
        }
        if (info) {
            info.innerHTML = '💡 Pilih minimal 1 WKP untuk mulai perbandingan.';
        }
        return;
    }

    if (info) {
        info.innerHTML = '⏳ Loading comparison data...';
    }

    try {
        const kodes = comparisonState.selected.map(s => s.kode).join(',');
        const resp = await fetch(`/api/gdi/history/bulk?kodes=${kodes}&months=12`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();

        // ============================================================
        // EMPTY STATE HANDLING (New in v2.2.0)
        // ============================================================
        if (!data.series || data.series.length === 0) {
            if (info) {
                info.innerHTML = `
                    <div style="color: #92400e; padding: 1rem; background: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <strong>⚠️ Belum Ada Data Historis</strong><br>
                        <span style="font-size: 0.9rem;">
                            GeoSDI menggunakan mode "starter kit" — data historis belum tersedia.
                            Anda bisa menambahkan data melalui API atau admin panel.
                        </span>
                    </div>
                `;
            }
            if (comparisonState.chart) {
                comparisonState.chart.destroy();
                comparisonState.chart = null;
            }
            if (ctx) {
                ctx.style.display = 'none';
            }
            console.log('[INFO] No history data (clean slate mode)');
            return;
        }

        // Filter series yang punya data
        const validSeries = data.series.filter(s => s.data && s.data.length > 0);

        if (validSeries.length === 0) {
            if (info) {
                info.innerHTML = `
                    <div style="color: #92400e; padding: 1rem; background: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <strong>⚠️ Belum Ada Data Historis</strong><br>
                        <span style="font-size: 0.9rem;">
                            WKP yang dipilih belum memiliki data historis.
                            Data akan tersedia setelah Anda menambahkan.
                        </span>
                    </div>
                `;
            }
            if (comparisonState.chart) {
                comparisonState.chart.destroy();
                comparisonState.chart = null;
            }
            if (ctx) {
                ctx.style.display = 'none';
            }
            return;
        }

        // Show chart (in case it was hidden)
        if (ctx) {
            ctx.style.display = 'block';
        }

        // Labels dari WKP pertama yang valid
        const labels = validSeries[0].data.map(d => {
            const date = new Date(d.date);
            return date.toLocaleDateString('id-ID', { month: 'short', year: '2-digit' });
        });

        // Datasets
        const datasets = validSeries.map((s, i) => ({
            label: `${s.kode} — ${s.nama}`,
            data: s.data.map(d => d.gdi),
            borderColor: CHART_COLORS[i % CHART_COLORS.length],
            backgroundColor: CHART_COLORS[i % CHART_COLORS.length] + '22',
            borderWidth: 3,
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
            fill: false,
        }));

        // Info
        if (info) {
            const lines = validSeries.map((s, i) => {
                const color = CHART_COLORS[i % CHART_COLORS.length];
                const trendIcon = s.trend === 'naik' ? '📈' : s.trend === 'turun' ? '📉' : '➡️';
                const sign = s.delta > 0 ? '+' : '';
                return `<div style="color: ${color}; font-weight: bold;">
                    ${trendIcon} ${s.kode} (${s.nama}): ${s.trend.toUpperCase()} ${sign}${s.delta}
                </div>`;
            }).join('');

            info.innerHTML = `
                <div style="margin-bottom: 0.5rem; font-weight: bold; color: #1e3a8a;">
                    📊 Perbandingan ${validSeries.length} WKP (12 bulan)
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.5rem;">
                    ${lines}
                </div>
            `;
        }

        // Destroy old chart
        if (comparisonState.chart) {
            comparisonState.chart.destroy();
        }

        comparisonState.chart = new Chart(ctx, {
            type: 'line',
            data: { labels, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: { size: 12, weight: 'bold' },
                            padding: 15,
                        }
                    },
                    title: {
                        display: true,
                        text: 'Perbandingan Trend GDI — 12 Bulan Terakhir',
                        font: { size: 16, weight: 'bold' },
                        color: '#1e3a8a',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                return `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        title: { display: true, text: 'GDI Score' },
                        grid: { color: '#f1f5f9' }
                    },
                    x: {
                        title: { display: true, text: 'Bulan' },
                        grid: { display: false }
                    }
                }
            }
        });

        console.log(`[OK] Comparison rendered for ${validSeries.length} WKP`);
    } catch (e) {
        console.error('[X] Comparison failed:', e);
        if (info) {
            info.innerHTML = `<span style="color: #ef4444;">[X] Gagal load comparison: ${e.message}</span>`;
        }
    }
}

// ============================================================
// GDI Table
// ============================================================
async function renderGDITable() {
    try {
        const resp = await fetch('/api/gdi');
        const data = await resp.json();

        const tbody = document.getElementById('gdiTableBody');
        if (!tbody) return;

        if (!data.data || data.data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="padding: 2rem; text-align: center; color: #94a3b8;">
                        <strong>Belum Ada Data GDI</strong><br>
                        <span style="font-size: 0.85rem;">GDI scores akan muncul setelah data WKP ditambahkan.</span>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = data.data.slice(0, 50).map((r, i) => `
            <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 0.5rem; font-weight: bold; color: #64748b;">${i + 1}</td>
                <td style="padding: 0.5rem; font-weight: bold; font-size: 0.85rem;">
                    ${r.kode} — ${r.nama}
                </td>
                <td style="padding: 0.5rem; color: #64748b; font-size: 0.85rem;">${r.provinsi}</td>
                <td style="padding: 0.5rem; text-align: right; font-weight: bold;">${r.gdi_mean.toFixed(2)}</td>
                <td style="padding: 0.5rem; text-align: center;">
                    <span style="background: ${GDI_COLORS[r.status]}22; color: ${GDI_COLORS[r.status]}; padding: 0.15rem 0.5rem; border-radius: 10px; font-weight: bold; font-size: 0.7rem;">
                        ${r.status}
                    </span>
                </td>
                <td style="padding: 0.5rem; text-align: center;">
                    <button onclick="addToComparison('${r.kode}')" style="background: #3b82f6; color: white; border: none; padding: 0.3rem 0.6rem; border-radius: 4px; cursor: pointer; font-size: 0.75rem; font-weight: bold;">
                        + Compare
                    </button>
                </td>
            </tr>
        `).join('');

        console.log(`[OK] GDI table rendered (${Math.min(50, data.data.length)} of ${data.total})`);
    } catch (e) {
        console.error('[X] Failed to render table:', e);
    }
}

// ============================================================
// Init
// ============================================================
window.addEventListener('DOMContentLoaded', async () => {
    // Load semua WKP dulu
    await loadAllWkp();

    // Search input
    const searchInput = document.getElementById('wkpSearchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const results = searchWkp(e.target.value);
            renderSearchResults(results);
        });

        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                const container = document.getElementById('searchResults');
                if (container) container.style.display = 'none';
            }, 200);
        });
    }

    // Clear button
    const clearBtn = document.getElementById('clearSelectionBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            comparisonState.selected = [];
            renderChips();
            renderComparison();
        });
    }

    // GDI table
    renderGDITable();

    // NOTE: Auto-select removed in v2.2.0 (fresh start for users)
    // Users now select their own WKP via search box.
});