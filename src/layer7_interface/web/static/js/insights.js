/* ==========================================================
   GeoSDI — Insights Page
   ========================================================== */

console.log("💡 insights.js loaded");

// ============================================================
// Load & Render Headline
// ============================================================
async function loadSummary() {
    try {
        const resp = await fetch('/api/insights/summary');
        const data = await resp.json();

        // Headline
        document.getElementById('headline').innerHTML = `
            <p style="font-size: 1.15rem; line-height: 1.8; margin: 0;">
                ${data.headline.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')}
            </p>
        `;

        // Stats
        const stats = data.stats;
        document.getElementById('statsGrid').innerHTML = `
            <div class="stat-card">
                <div class="label">Total WKP</div>
                <div class="value">${stats.total_wkp}</div>
            </div>
            <div class="stat-card">
                <div class="label">Rata-rata GDI</div>
                <div class="value">${stats.avg_gdi}</div>
            </div>
            <div class="stat-card">
                <div class="label">WKP Optimal</div>
                <div class="value">${stats.optimal_count}</div>
            </div>
            <div class="stat-card" style="border-left-color: #ef4444;">
                <div class="label">Alert Aktif</div>
                <div class="value" style="color: #ef4444;">${stats.active_alerts}</div>
            </div>
        `;

        console.log('✅ Summary loaded');
    } catch (e) {
        console.error('❌ Failed to load summary:', e);
    }
}

// ============================================================
// Load & Render Alerts
// ============================================================
async function loadAlerts() {
    try {
        const resp = await fetch('/api/insights/alerts');
        const data = await resp.json();

        const container = document.getElementById('alertsContainer');

        if (data.count === 0) {
            container.innerHTML = `
                <p style="color: #10b981; padding: 1rem; background: #ecfdf5; border-radius: 8px;">
                    ✅ Tidak ada alert aktif. Semua WKP dalam kondisi baik.
                </p>
            `;
            return;
        }

        const severityColors = {
            'critical': { bg: '#fef2f2', border: '#ef4444', text: '#991b1b' },
            'warning': { bg: '#fffbeb', border: '#f59e0b', text: '#92400e' },
            'info': { bg: '#eff6ff', border: '#3b82f6', text: '#1e3a8a' },
        };

        container.innerHTML = data.alerts.map(a => {
            const colors = severityColors[a.severity] || severityColors.info;
            return `
                <div style="
                    background: ${colors.bg};
                    border-left: 4px solid ${colors.border};
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 1rem;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="color: ${colors.text}; margin: 0 0 0.5rem 0;">
                                ${a.title}
                            </h4>
                            <p style="color: ${colors.text}; margin: 0; font-size: 0.9rem; line-height: 1.6;">
                                ${a.message.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')}
                            </p>
                            ${a.wkp_nama ? `<p style="color: ${colors.text}; margin: 0.5rem 0 0; font-size: 0.85rem; opacity: 0.7;">
                                WKP: ${a.wkp_kode} — ${a.wkp_nama}
                            </p>` : ''}
                        </div>
                        <span style="
                            background: ${colors.border};
                            color: white;
                            padding: 0.25rem 0.75rem;
                            border-radius: 12px;
                            font-size: 0.75rem;
                            font-weight: bold;
                            text-transform: uppercase;
                        ">
                            ${a.severity}
                        </span>
                    </div>
                </div>
            `;
        }).join('');

        console.log(`✅ ${data.count} alerts loaded`);
    } catch (e) {
        console.error('❌ Failed to load alerts:', e);
    }
}

// ============================================================
// Load & Render Health Report
// ============================================================
async function loadHealth() {
    try {
        const resp = await fetch('/api/insights/health');
        const data = await resp.json();

        const container = document.getElementById('healthContainer');

        const priorityColors = {
            'Critical': { bg: '#fef2f2', text: '#991b1b' },
            'High': { bg: '#fffbeb', text: '#92400e' },
            'Medium': { bg: '#eff6ff', text: '#1e3a8a' },
            'Low': { bg: '#ecfdf5', text: '#065f46' },
        };

        container.innerHTML = data.reports.map(r => {
            const colors = priorityColors[r.priority] || priorityColors.Low;
            return `
                <div style="
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                    border-left: 4px solid ${colors.text};
                ">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <div>
                            <h4 style="margin: 0; color: #1e3a8a;">
                                ${r.kode} — ${r.nama}
                            </h4>
                            <span style="color: #64748b; font-size: 0.85rem;">
                                ${r.provinsi} · GDI: <strong>${r.gdi_current ? r.gdi_current.toFixed(2) : 'N/A'}</strong>
                            </span>
                        </div>
                        <span style="
                            background: ${colors.bg};
                            color: ${colors.text};
                            padding: 0.25rem 0.75rem;
                            border-radius: 12px;
                            font-size: 0.75rem;
                            font-weight: bold;
                        ">
                            ${r.priority}
                        </span>
                    </div>

                    <p style="color: #334155; margin: 0.5rem 0; font-size: 0.9rem;">
                        ${r.narrative ? r.narrative.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') : 'Tidak ada prediksi tersedia.'}
                    </p>

                    <div style="display: flex; gap: 1rem; margin-top: 0.75rem; font-size: 0.85rem; flex-wrap: wrap;">
                        <span style="color: #64748b;">
                            ${r.summary_human || '➡️ Status normal'}
                        </span>
                        <span style="color: ${colors.text}; font-weight: bold;">
                            ${r.recommendation || 'Tidak ada rekomendasi'}
                        </span>
                    </div>
                </div>
            `;
        }).join('');

        console.log(`✅ ${data.count} health reports loaded`);
    } catch (e) {
        console.error('❌ Failed to load health report:', e);
    }
}

// ============================================================
// Init
// ============================================================
window.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('headline')) {
        loadSummary();
        loadAlerts();
        loadHealth();
    }
});