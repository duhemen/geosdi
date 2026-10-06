/* ==========================================================
   GeoSDI — Decision Support (Priority + Budget + Executive)
   Version: 2.3.0
   ========================================================== */

console.log("🎯 decision_support.js v2.3.0 loaded");

// ============================================================
// Load Priority Ranking
// ============================================================
async function loadPriority() {
    try {
        const resp = await fetch('/api/digital-twin/priority?limit=10');
        const data = await resp.json();

        const container = document.getElementById('priorityRanking');
        if (!container) return;

        const levelColors = {
            'Critical': { bg: '#fef2f2', border: '#ef4444', text: '#991b1b' },
            'High': { bg: '#fffbeb', border: '#f59e0b', text: '#92400e' },
            'Medium': { bg: '#eff6ff', border: '#3b82f6', text: '#1e3a8a' },
            'Low': { bg: '#f0fdf4', border: '#10b981', text: '#065f46' },
        };

        container.innerHTML = data.rankings.map(r => {
            const c = levelColors[r.priority_level] || levelColors.Low;
            return `
                <div style="
                    background: ${c.bg};
                    border-left: 4px solid ${c.border};
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 0.75rem;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 0.5rem;">
                        <div style="flex: 1; min-width: 250px;">
                            <div style="font-weight: bold; color: #1e3a8a; font-size: 1.05rem;">
                                #${r.rank} — ${r.kode} ${r.nama}
                            </div>
                            <div style="color: #64748b; font-size: 0.85rem; margin-top: 0.25rem;">
                                ${r.provinsi} · GDI: <strong>${r.gdi_current}</strong> · 
                                Kapasitas: <strong>${r.kapasitas_mw} MW</strong>
                            </div>
                            <div style="color: ${c.text}; font-size: 0.85rem; margin-top: 0.5rem;">
                                💡 ${r.recommendation}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="background: ${c.border}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-weight: bold; font-size: 0.8rem;">
                                ${r.priority_level} · ${r.priority_score.toFixed(1)}
                            </div>
                            <div style="color: ${c.text}; font-size: 0.75rem; margin-top: 0.5rem; text-transform: uppercase;">
                                ${r.intervention_type}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        console.log(`✅ Priority loaded (${data.count})`);
    } catch (e) {
        console.error('❌ Priority failed:', e);
    }
}

// ============================================================
// Load Executive Summary
// ============================================================
async function loadExecutive() {
    try {
        const resp = await fetch('/api/digital-twin/executive-summary');
        const data = await resp.json();

        const container = document.getElementById('executiveSummary');
        if (!container) return;

        const findings = data.findings.map(f => `
            <div style="margin-bottom: 1rem; padding: 0.75rem; background: rgba(255, 255, 255, 0.5); border-radius: 6px;">
                <div style="font-weight: bold; color: #92400e; font-size: 1rem;">
                    ${f.icon} ${f.title}
                </div>
                <div style="color: #78350f; font-size: 0.9rem; margin-top: 0.25rem; line-height: 1.6;">
                    ${f.body.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')}
                </div>
            </div>
        `).join('');

        const recommendations = data.recommendations.map(r => {
            const colors = {
                'URGENT': '#ef4444',
                'HIGH': '#f59e0b',
                'MEDIUM': '#3b82f6',
            };
            const color = colors[r.priority] || '#64748b';
            return `
                <div style="background: white; border-left: 4px solid ${color}; padding: 0.75rem; border-radius: 6px; margin-bottom: 0.5rem;">
                    <div style="font-weight: bold; color: ${color}; font-size: 0.85rem;">
                        [${r.priority}]
                    </div>
                    <div style="color: #334155; margin-top: 0.25rem; font-weight: 500;">
                        ${r.action}
                    </div>
                    <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.35rem;">
                        📊 <strong>Expected:</strong> ${r.expected_impact}
                    </div>
                    ${r.context ? `
                        <div style="color: #94a3b8; font-size: 0.75rem; margin-top: 0.25rem; font-style: italic;">
                            💡 ${r.context}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div style="
                background: white;
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1rem;
                font-size: 1rem;
                line-height: 1.7;
                border-left: 4px solid #f59e0b;
            ">
                ${data.headline.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')}
            </div>
            <div style="margin-bottom: 1.5rem;">
                ${findings}
            </div>
            <div>
                <h4 style="color: #92400e; margin-bottom: 0.75rem; border-bottom: 2px solid #fde68a; padding-bottom: 0.5rem;">
                    💡 Rekomendasi untuk Decision Maker
                </h4>
                ${recommendations}
            </div>
        `;

        console.log('✅ Executive summary loaded');
    } catch (e) {
        console.error('❌ Executive failed:', e);
    }
}

// ============================================================
// Budget Optimize — VERSI BARU dengan Detail per WKP
// ============================================================
async function optimizeBudget() {
    const budget = parseFloat(document.getElementById('budgetInput').value);
    const btn = document.getElementById('optimizeBtn');
    const container = document.getElementById('budgetResult');

    btn.textContent = '⏳ Optimizing...';
    btn.disabled = true;

    try {
        const resp = await fetch('/api/digital-twin/budget/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ total_budget_billion: budget }),
        });

        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();

        // Handle response format (kompatibel dengan lama & baru)
        const summary = data.summary || {};
        const impact = data.impact || {};
        const allocations = data.allocations || [];

        const wkpFunded = summary.wkp_funded || 0;
        const gdiGain = summary.expected_gdi_gain_total || summary.expected_gdi_gain || 0;
        const mwGain = summary.expected_mw_gain_total || summary.expected_mw_gain || 0;
        const avgGain = summary.avg_gdi_gain_per_wkp || (gdiGain / Math.max(wkpFunded, 1));
        const nationalDelta = impact.national_gdi_delta || impact.delta || 0;
        const interpretation = impact.interpretation || '';

        container.style.display = 'block';
        container.innerHTML = `
            <!-- Summary Cards -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
                <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981;">
                    <div style="color: #065f46; font-size: 0.85rem;">Total Budget</div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #065f46;">
                        Rp ${(data.budget.total/1000).toFixed(1)} T
                    </div>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6;">
                    <div style="color: #1e3a8a; font-size: 0.85rem;">WKP Funded</div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #1e3a8a;">
                        ${wkpFunded}
                    </div>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #f59e0b;">
                    <div style="color: #92400e; font-size: 0.85rem;">Avg GDI Gain/WKP</div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #f59e0b;">
                        +${avgGain.toFixed(2)}
                    </div>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #8b5cf6;">
                    <div style="color: #6b21a8; font-size: 0.85rem;">MW Gain</div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #8b5cf6;">
                        +${mwGain.toFixed(0)} MW
                    </div>
                </div>
            </div>

            <!-- Interpretation -->
            ${interpretation ? `
                <div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #10b981;">
                    <div style="color: #065f46; font-weight: bold; margin-bottom: 0.5rem;">
                        💡 Interpretasi
                    </div>
                    <div style="color: #064e3b; font-size: 0.9rem; line-height: 1.6;">
                        ${interpretation}
                    </div>
                </div>
            ` : ''}

            <!-- Allocations Table -->
            <h4 style="color: #065f46; margin-bottom: 0.75rem;">
                📋 Detail Alokasi per WKP (Top ${Math.min(10, allocations.length)})
            </h4>
            <div style="background: white; border-radius: 8px; padding: 0.5rem; max-height: 500px; overflow-y: auto;">
                ${allocations.slice(0, 10).map((a, i) => {
                    // Handle both response formats
                    const gdiBefore = a.gdi?.before || a.gdi_before || 0;
                    const gdiAfter = a.gdi?.after || a.gdi_after || 0;
                    const gdiGainVal = a.gdi?.gain || a.expected_gdi_gain || a.gdi_gain || 0;
                    const capacityGain = a.capacity?.gain_mw || a.capacity_gain_mw || 0;

                    return `
                        <div style="padding: 0.75rem; border-bottom: 1px solid #f1f5f9;">
                            <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 0.5rem;">
                                <div style="flex: 1; min-width: 250px;">
                                    <div style="font-weight: bold; color: #065f46;">
                                        #${i + 1} — ${a.kode} ${a.nama}
                                    </div>
                                    <div style="color: #64748b; font-size: 0.8rem;">
                                        ${a.provinsi} · ${(a.intervention_type || '').toUpperCase()}
                                        ${a.priority_level ? ` · Priority: ${a.priority_level}` : ''}
                                    </div>
                                    <div style="color: #334155; font-size: 0.85rem; margin-top: 0.25rem;">
                                        📈 GDI: ${gdiBefore.toFixed(2)} → <strong style="color: #10b981;">${gdiAfter.toFixed(2)}</strong> 
                                        (<strong style="color: #10b981;">+${gdiGainVal.toFixed(2)}</strong>)
                                        ${capacityGain > 0 ? ` · ⚡ +${capacityGain.toFixed(0)} MW` : ''}
                                    </div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="color: #065f46; font-weight: bold;">
                                        Rp ${a.cost_billion.toLocaleString('id-ID')} M
                                    </div>
                                    <div style="color: #10b981; font-size: 0.8rem;">
                                        ROI: ${a.roi.toFixed(2)}
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;

        console.log('✅ Budget optimized');
    } catch (e) {
        console.error('❌ Budget failed:', e);
        container.style.display = 'block';
        container.innerHTML = `
            <div style="padding: 1rem; background: #fef2f2; border-left: 4px solid #ef4444; border-radius: 8px;">
                <strong style="color: #991b1b;">❌ Error:</strong>
                <span style="color: #991b1b;">${e.message}</span>
            </div>
        `;
    } finally {
        btn.textContent = '🎯 Optimize';
        btn.disabled = false;
    }
}

// ============================================================
// Init
// ============================================================
window.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('priorityRanking')) {
        loadPriority();
        loadExecutive();
    }

    const btn = document.getElementById('optimizeBtn');
    if (btn) {
        btn.addEventListener('click', optimizeBudget);
    }
});