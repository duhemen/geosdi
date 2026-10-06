/* ==========================================================
   GeoSDI — Digital Twin Dashboard
   ========================================================== */

console.log("🌏 digital_twin.js loaded");

let scenarioChart = null;

// ============================================================
// Load National Stats
// ============================================================
async function loadNational() {
    try {
        const resp = await fetch('/api/digital-twin/national');
        const data = await resp.json();

        // Stats cards
        document.getElementById('nationalStats').innerHTML = `
            <div class="stat-card">
                <div class="label">Total WKP</div>
                <div class="value">${data.summary.total_wkp}</div>
            </div>
            <div class="stat-card">
                <div class="label">Provinsi</div>
                <div class="value">${data.summary.total_provinsi}</div>
            </div>
            <div class="stat-card">
                <div class="label">Operasi</div>
                <div class="value">${data.summary.total_operasi}</div>
            </div>
            <div class="stat-card">
                <div class="label">Kapasitas (MW)</div>
                <div class="value">${data.summary.total_kapasitas_mw.toFixed(0)}</div>
            </div>
        `;

        // Health section
        const h = data.health;
        document.getElementById('healthSection').innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem;">
                <div>
                    <div style="opacity: 0.8; font-size: 0.9rem;">💚 Health Score Nasional</div>
                    <div style="font-size: 3rem; font-weight: bold;">${h.health_score}</div>
                    <div style="font-size: 1.2rem;">${h.category}</div>
                </div>
                <div>
                    <div style="opacity: 0.8; font-size: 0.9rem;">📊 GDI Nasional</div>
                    <div style="font-size: 2rem; font-weight: bold;">${data.gdi.mean}</div>
                    <div style="font-size: 0.9rem;">± ${data.gdi.std} · Weighted: ${data.gdi.weighted}</div>
                </div>
                <div>
                    <div style="opacity: 0.8; font-size: 0.9rem;">🎯 Coverage</div>
                    <div style="font-size: 2rem; font-weight: bold;">${h.diversity_score.toFixed(0)}%</div>
                    <div style="font-size: 0.9rem;">Diversity Score</div>
                </div>
                <div>
                    <div style="opacity: 0.8; font-size: 0.9rem;">⚡ Operasi Ratio</div>
                    <div style="font-size: 2rem; font-weight: bold;">${h.operasi_ratio.toFixed(0)}%</div>
                    <div style="font-size: 0.9rem;">dari Total WKP</div>
                </div>
            </div>
        `;

        console.log('✅ National loaded');
    } catch (e) {
        console.error('❌ Failed to load national:', e);
    }
}

// ============================================================
// Load Preset Scenarios
// ============================================================
async function loadPresets() {
    try {
        const resp = await fetch('/api/digital-twin/scenarios/presets');
        const data = await resp.json();

        const container = document.getElementById('presetButtons');
        container.innerHTML = data.presets.map(p => `
            <button onclick="runPreset('${p.key}')" style="
                padding: 1rem;
                border: 2px solid #3b82f6;
                background: white;
                color: #1e3a8a;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
                font-size: 0.9rem;
                text-align: left;
                transition: all 0.3s ease;
            " onmouseover="this.style.background='#eff6ff'" onmouseout="this.style.background='white'">
                ${p.name}
            </button>
        `).join('');

        console.log(`✅ ${data.presets.length} presets loaded`);
    } catch (e) {
        console.error('❌ Failed to load presets:', e);
    }
}

// ============================================================
// Run Preset Scenario
// ============================================================
window.runPreset = async function(name) {
    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.innerHTML = '⏳ Running...';
    btn.disabled = true;

    try {
        const resp = await fetch(`/api/digital-twin/scenarios/preset/${name}`);

        // === FIX: Baca pesan error dari backend kalau request gagal ===
        if (!resp.ok) {
            let errorMsg = `HTTP ${resp.status}`;
            try {
                const errData = await resp.json();
                if (errData && errData.detail) {
                    errorMsg = errData.detail;  // ← Pesan asli dari backend
                }
            } catch (jsonErr) {
                // Response bukan JSON (misal HTML error page), pakai default
                console.warn('Could not parse error response as JSON', jsonErr);
            }
            throw new Error(errorMsg);
        }

        const data = await resp.json();

        renderScenarioResult(data);
        renderScenarioChart(data);
        console.log('✅ Scenario result:', data);
    } catch (e) {
        console.error('❌ Scenario failed:', e);
        alert('Tidak dapat menjalankan skenario:\n\n' + e.message);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
};

// ============================================================
// Render Scenario Result
// ============================================================
function renderScenarioResult(data) {
    const container = document.getElementById('scenarioContent');
    const deltaColor = data.delta.gdi > 0 ? '#10b981' : data.delta.gdi < 0 ? '#ef4444' : '#64748b';
    const deltaSign = data.delta.gdi > 0 ? '+' : '';

    container.innerHTML = `
        <div style="margin-bottom: 1rem;">
            <h3 style="color: #1e3a8a; margin: 0;">${data.scenario_name}</h3>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;">
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px;">
                <div style="color: #64748b; font-size: 0.85rem;">GDI Baseline</div>
                <div style="font-size: 1.8rem; font-weight: bold;">${data.baseline.gdi}</div>
            </div>
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px;">
                <div style="color: #64748b; font-size: 0.85rem;">GDI Simulasi</div>
                <div style="font-size: 1.8rem; font-weight: bold;">${data.simulated.gdi}</div>
            </div>
            <div style="background: ${deltaColor}15; padding: 1rem; border-radius: 8px; border-left: 4px solid ${deltaColor};">
                <div style="color: #64748b; font-size: 0.85rem;">Delta</div>
                <div style="font-size: 1.8rem; font-weight: bold; color: ${deltaColor};">
                    ${deltaSign}${data.delta.gdi} (${deltaSign}${data.delta.percent}%)
                </div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem;">
            <div style="text-align: center; padding: 0.75rem; background: #eff6ff; border-radius: 8px;">
                <div style="color: #64748b; font-size: 0.75rem;">Affected</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #1e3a8a;">${data.wkp_summary.affected}</div>
            </div>
            <div style="text-align: center; padding: 0.75rem; background: #ecfdf5; border-radius: 8px;">
                <div style="color: #065f46; font-size: 0.75rem;">📈 Improved</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #10b981;">${data.wkp_summary.improved}</div>
            </div>
            <div style="text-align: center; padding: 0.75rem; background: #fef2f2; border-radius: 8px;">
                <div style="color: #991b1b; font-size: 0.75rem;">📉 Worsened</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #ef4444;">${data.wkp_summary.worsened}</div>
            </div>
            <div style="text-align: center; padding: 0.75rem; background: #f1f5f9; border-radius: 8px;">
                <div style="color: #64748b; font-size: 0.75rem;">Unchanged</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #64748b;">${data.wkp_summary.unchanged}</div>
            </div>
        </div>
        
        <div style="margin-top: 1.5rem;">
            <h4 style="color: #1e3a8a; margin-bottom: 0.75rem;">📊 Dampak per WKP Type</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;">
                ${Object.entries(data.by_type || {}).filter(([k, v]) => v.count > 0).map(([type, stat]) => {
                    const colors = {
                        'mature': { bg: '#ecfdf5', border: '#10b981', icon: '🏆' },
                        'developing': { bg: '#eff6ff', border: '#3b82f6', icon: '📈' },
                        'new': { bg: '#fef3c7', border: '#f59e0b', icon: '🌟' },
                        'exploration': { bg: '#f3e8ff', border: '#8b5cf6', icon: '🔍' },
                    };
                    const c = colors[type] || colors.new;
                    const deltaSign = stat.avg_delta > 0 ? '+' : '';
                    return `
                        <div style="background: ${c.bg}; border-left: 4px solid ${c.border}; padding: 0.75rem; border-radius: 8px;">
                            <div style="font-weight: bold; color: #1e3a8a; font-size: 0.9rem;">
                                ${c.icon} ${type.toUpperCase()}
                            </div>
                            <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.25rem;">
                                ${stat.count} WKP · Avg Δ: <strong style="color: ${c.border};">${deltaSign}${stat.avg_delta}</strong>
                            </div>
                            <div style="color: #64748b; font-size: 0.75rem;">
                                Improved: ${stat.improved} · Worsened: ${stat.worsened}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        </div>


        <div style="margin-top: 1.5rem;">
            <h4 style="color: #1e3a8a; margin-bottom: 0.5rem;">🏆 Top 5 Improvements</h4>
            <ul style="list-style: none; padding: 0;">
                ${data.top_improvements.slice(0, 5).map(w => `
                    <li style="padding: 0.5rem; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between;">
                        <span><strong>${w.kode}</strong> — ${w.nama}</span>
                        <span style="color: #10b981; font-weight: bold;">${w.delta > 0 ? '+' : ''}${w.delta}</span>
                    </li>
                `).join('')}
            </ul>
        </div>
    `;

    document.getElementById('scenarioResult').style.display = 'block';
    document.getElementById('scenarioChartSection').style.display = 'block';
}

// ============================================================
// Render Scenario Chart
// ============================================================
function renderScenarioChart(data) {
    const ctx = document.getElementById('scenarioChart');
    if (!ctx) return;

    if (scenarioChart) scenarioChart.destroy();

    scenarioChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['GDI Nasional', 'Health Score'],
            datasets: [
                {
                    label: 'Baseline',
                    data: [data.baseline.gdi, data.baseline.health],
                    backgroundColor: 'rgba(100, 116, 139, 0.6)',
                    borderColor: '#64748b',
                    borderWidth: 2,
                },
                {
                    label: 'Simulasi',
                    data: [data.simulated.gdi, data.simulated.health],
                    backgroundColor: 'rgba(59, 130, 246, 0.6)',
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: data.scenario_name,
                    font: { size: 14, weight: 'bold' },
                }
            },
            scales: {
                y: { beginAtZero: false, min: 60, max: 100 }
            }
        }
    });
}

// ============================================================
// Init
// ============================================================
window.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('nationalStats')) {
        loadNational();
        loadPresets();
    }
});