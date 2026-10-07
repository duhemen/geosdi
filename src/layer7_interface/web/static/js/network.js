/* ==========================================================
   GeoSDI — Network Dynamics Visualizer (Full Version)
   ========================================================== */

console.log("🕸️ network.js v2.0 loaded");

let networkInstance = null;
let allNodes = [];
let allEdges = [];
let currentSelection = null;
let animationInterval = null;
let gdiHistory = {};

// ============================================================
// Constants
// ============================================================
const COMMUNITY_COLORS = [
    "#3b82f6", "#10b981", "#8b5cf6", "#ef4444", "#f59e0b", "#06b6d4",
    "#ec4899", "#eab308", "#14b8a6", "#f97316", "#6366f1", "#84cc16",
];

const MONTH_LABELS = [
    "Nov 2024", "Des 2024", "Jan 2025", "Feb 2025",
    "Mar 2025", "Apr 2025", "Mei 2025", "Jun 2025",
    "Jul 2025", "Agu 2025", "Sep 2025", "Okt 2025",
    "Nov 2025", "Des 2025", "Jan 2026", "Feb 2026",
    "Mar 2026", "Apr 2026", "Mei 2026", "Jun 2026",
    "Jul 2026", "Agu 2026", "Sep 2026", "Okt 2026",
];

// ============================================================
// Color helpers
// ============================================================
function getCommunityColor(communityId) {
    if (communityId === null || communityId === undefined) return "#94a3b8";
    return COMMUNITY_COLORS[communityId % COMMUNITY_COLORS.length];
}

function getGDIColor(gdi) {
    if (gdi >= 85) return "#10b981";   // Optimal - green
    if (gdi >= 80) return "#22c55e";   // Stabil baik
    if (gdi >= 75) return "#eab308";   // Sedang - yellow
    if (gdi >= 70) return "#f97316";   // Rendah - orange
    return "#ef4444";                   // Kritis - red
}

function getTypeColor(type) {
    const colors = {
        mature: "#10b981",
        developing: "#3b82f6",
        new: "#f59e0b",
        exploration: "#8b5cf6",
    };
    return colors[type] || "#64748b";
}

function getNodeColor(node, mode) {
    if (mode === "community") return getCommunityColor(node.community);
    if (mode === "gdi") return getGDIColor(node.gdi_mean);
    return getTypeColor(node.type);
}

// ============================================================
// Load & render network graph
// ============================================================
async function loadGraph() {
    const minWeight = document.getElementById("min-weight").value || 0.3;
    const filterProv = document.getElementById("filter-provinsi").value;
    const filterType = document.getElementById("filter-type").value;
    const colorMode = document.getElementById("color-mode")?.value || "type";

    try {
        const resp = await fetch(`/api/network/graph?min_weight=${minWeight}`);
        const data = await resp.json();

        allNodes = data.nodes;
        allEdges = data.edges;

        // Populate province filter (hanya sekali)
        const provSelect = document.getElementById("filter-provinsi");
        if (provSelect.options.length <= 1) {
            const provinces = [...new Set(allNodes.map(n => n.provinsi))].sort();
            provinces.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p;
                opt.textContent = p;
                provSelect.appendChild(opt);
            });
        }

        // Filter
        let filteredNodes = allNodes;
        if (filterProv) filteredNodes = filteredNodes.filter(n => n.provinsi === filterProv);
        if (filterType) filteredNodes = filteredNodes.filter(n => n.type === filterType);

        const nodeIds = new Set(filteredNodes.map(n => n.id));
        const filteredEdges = allEdges.filter(e => nodeIds.has(e.from) && nodeIds.has(e.to));

        renderNetwork(filteredNodes, filteredEdges, colorMode);
        updateStats(data.summary);

        console.log(`✅ Network rendered: ${filteredNodes.length} nodes, ${filteredEdges.length} edges, color=${colorMode}`);
    } catch (e) {
        console.error("❌ Failed to load graph:", e);
    }
}

// ============================================================
// Render vis.js network
// ============================================================
function renderNetwork(nodes, edges, colorMode = "type") {
    const container = document.getElementById("network-graph");

    const visNodes = nodes.map(n => {
        const color = getNodeColor(n, colorMode);
        return {
            id: n.id,
            label: n.label,
            title: `${n.kode} — ${n.nama}<br>Provinsi: ${n.provinsi}<br>GDI: ${n.gdi_mean}<br>Community: #${n.community}`,
            size: n.size,
            color: {
                background: color,
                border: color,
                highlight: { background: color, border: "#1e3a8a" },
            },
            font: { color: "#0f172a", size: 12, face: "Tahoma" },
            borderWidth: 2,
        };
    });

    const visEdges = edges.map(e => ({
        from: e.from,
        to: e.to,
        value: e.value,
        title: e.title,
        color: { color: "#cbd5e1", highlight: "#3b82f6" },
        width: Math.max(1, e.value * 4),
        smooth: { type: "continuous" },
    }));

    const data = {
        nodes: new vis.DataSet(visNodes),
        edges: new vis.DataSet(visEdges),
    };

    const options = {
        nodes: { shape: "dot", scaling: { min: 12, max: 40 } },
        edges: { scaling: { min: 1, max: 6 } },
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -3000,
                springLength: 150,
                springConstant: 0.04,
                damping: 0.09,
            },
            stabilization: { iterations: 200 },
        },
        interaction: { hover: true, tooltipDelay: 100 },
    };

    if (networkInstance) networkInstance.destroy();
    networkInstance = new vis.Network(container, data, options);

    networkInstance.on("click", function (params) {
        if (params.nodes.length > 0) {
            showNodeDetail(params.nodes[0]);
        }
    });
}

// ============================================================
// Apply color mode (dipanggil saat dropdown change)
// ============================================================
function applyColorMode() {
    const mode = document.getElementById("color-mode").value;
    console.log(`🎨 Applying color mode: ${mode}`);

    if (!networkInstance || allNodes.length === 0) {
        console.warn("⚠️ Network belum siap");
        return;
    }

    const visNodes = networkInstance.body.data.nodes;

    allNodes.forEach(n => {
        const color = getNodeColor(n, mode);
        visNodes.update({
            id: n.id,
            color: {
                background: color,
                border: color,
                highlight: { background: color, border: "#1e3a8a" },
            },
        });
    });

    console.log(`✅ Color mode applied: ${mode}`);
}

// ============================================================
// Node detail panel
// ============================================================
function showNodeDetail(nodeId) {
    const node = allNodes.find(n => n.id === nodeId);
    if (!node) return;

    currentSelection = nodeId;

    const panel = document.getElementById("node-detail");
    panel.classList.remove("empty");
    panel.innerHTML = `
        <div class="node-detail">
            <div style="font-weight: 700; color: #1e3a8a; font-size: 1rem; margin-bottom: 0.5rem;">
                ${node.kode} — ${node.nama}
            </div>
            <div style="margin-bottom: 0.4rem;"><span class="key">Provinsi:</span> <span class="value">${node.provinsi}</span></div>
            <div style="margin-bottom: 0.4rem;"><span class="key">Status:</span> <span class="value">${node.status}</span></div>
            <div style="margin-bottom: 0.4rem;"><span class="key">Type:</span> <span class="value">${node.type}</span></div>
            <div style="margin-bottom: 0.4rem;"><span class="key">GDI:</span> <span class="value"><strong>${node.gdi_mean}</strong></span></div>
            <div style="margin-bottom: 0.4rem;"><span class="key">Kapasitas:</span> <span class="value">${node.kapasitas_mw} MW</span></div>
            <div style="margin-bottom: 0.4rem;"><span class="key">Community:</span> <span class="value">#${node.community ?? "—"}</span></div>
            ${node.centrality ? `
                <div style="margin-top: 0.6rem; padding-top: 0.6rem; border-top: 1px dashed #cbd5e1;">
                    <div style="font-weight: 600; color: #1e3a8a; margin-bottom: 0.3rem;">📊 Centrality:</div>
                    <div><span class="key">Degree:</span> <span class="value">${node.centrality.degree.toFixed(3)}</span></div>
                    <div><span class="key">PageRank:</span> <span class="value">${node.centrality.pagerank.toFixed(5)}</span></div>
                    <div><span class="key">Betweenness:</span> <span class="value">${node.centrality.betweenness.toFixed(4)}</span></div>
                </div>
            ` : ""}
        </div>
    `;

    fetchNeighbors(nodeId);
}

async function fetchNeighbors(kode) {
    try {
        const resp = await fetch(`/api/network/neighbors/${kode}`);
        const data = await resp.json();

        const panel = document.getElementById("node-detail");
        const neighborsHtml = data.neighbors.map(n => `
            <div style="font-size: 0.8rem; padding: 0.4rem; background: white; border-radius: 6px; margin-bottom: 0.3rem; border-left: 3px solid ${getTypeColor(n.type)};">
                <div style="font-weight: 600; color: #1e3a8a;">${n.kode} — ${n.nama}</div>
                <div style="color: #64748b; font-size: 0.75rem;">${n.provinsi} · ${n.distance_km.toFixed(1)} km · w=${n.adjacency_weight.toFixed(3)}</div>
            </div>
        `).join("");

        panel.insertAdjacentHTML("beforeend", `
            <div style="margin-top: 1rem;">
                <div style="font-weight: 700; color: #1e3a8a; margin-bottom: 0.5rem;">
                    🔗 Tetangga (${data.count})
                </div>
                ${neighborsHtml || '<div style="color:#94a3b8; font-size:0.8rem;">Tidak ada tetangga</div>'}
            </div>
        `);
    } catch (e) {
        console.error("❌ Failed to load neighbors:", e);
    }
}

// ============================================================
// Update stats
// ============================================================
function updateStats(summary) {
    document.getElementById("statNodes").textContent = summary.n_nodes;
    document.getElementById("statEdges").textContent = summary.n_edges;
    fetch("/api/network/communities")
        .then(r => r.json())
        .then(d => {
            document.getElementById("statCommunities").textContent = d.n_communities;
        });
    document.getElementById("statDensity").textContent = "0.071";
    document.getElementById("statDegree").textContent = "4.26";
}

// ============================================================
// Intervention
// ============================================================
async function runIntervention() {
    const sourceKode = currentSelection || "";
    const delta = parseFloat(document.getElementById("delta-gdi").value);

    if (!sourceKode) {
        alert("Pilih WKP dulu — klik node di graph atau cari via dropdown.");
        return;
    }

    const resultDiv = document.getElementById("intervention-result");
    resultDiv.innerHTML = "⏳ Menghitung...";

    try {
        const resp = await fetch("/api/network/propagate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ source_kode: sourceKode, delta_gdi: delta, decay: 0.3, max_hops: 2 }),
        });

        if (!resp.ok) {
            const err = await resp.json();
            resultDiv.innerHTML = `<span style="color:#dc2626;">❌ ${err.detail || "Error"}</span>`;
            return;
        }

        const data = await resp.json();
        const topList = data.affected_wkps.slice(0, 5).map(a => `
            <div style="font-size: 0.78rem; margin-bottom: 0.2rem;">
                • <strong>${a.kode}</strong> +${a.delta_gdi.toFixed(3)} GDI
            </div>
        `).join("");

        resultDiv.innerHTML = `
            <div style="padding: 0.5rem; background: white; border-radius: 6px;">
                <div style="font-weight: 700; color: #92400e; margin-bottom: 0.35rem;">🎯 Hasil Propagasi</div>
                <div style="font-size: 0.82rem;">
                    <div><strong>Source:</strong> ${data.source.kode} (${data.source.nama})</div>
                    <div><strong>Delta langsung:</strong> +${data.source.delta_direct}</div>
                    <div><strong>WKP terpengaruh:</strong> ${data.summary.n_affected}</div>
                    <div><strong>Total network effect:</strong> <span style="color:#10b981; font-weight:700;">+${data.summary.total_network_effect.toFixed(3)}</span></div>
                    <div><strong>Grand total:</strong> <span style="color:#10b981; font-weight:700;">+${data.summary.grand_total.toFixed(3)} GDI</span></div>
                </div>
                <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px dashed #cbd5e1;">
                    <div style="font-weight: 600; font-size: 0.78rem; margin-bottom: 0.3rem;">Top 5:</div>
                    ${topList}
                </div>
            </div>
        `;
    } catch (e) {
        resultDiv.innerHTML = `<span style="color:#dc2626;">❌ ${e.message}</span>`;
    }
}

// ============================================================
// Export functions
// ============================================================
function exportPNG() {
    if (!networkInstance) { alert("Graph belum dimuat"); return; }
    try {
        const canvas = networkInstance.canvas.body.container.getElementsByTagName("canvas")[0];
        if (!canvas) { alert("Canvas tidak ditemukan"); return; }
        const link = document.createElement("a");
        link.download = `geosdi-network-${new Date().toISOString().slice(0, 10)}.png`;
        link.href = canvas.toDataURL("image/png");
        link.click();
        console.log("✅ PNG exported");
    } catch (e) {
        console.error("❌ PNG export failed:", e);
        alert("Export PNG gagal: " + e.message);
    }
}

async function exportGraphML() {
    const minWeight = document.getElementById("min-weight").value || 0.3;
    try {
        const resp = await fetch(`/api/network/export?format=graphml&min_weight=${minWeight}`);
        if (!resp.ok) { alert("Export gagal"); return; }
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `geosdi-network-${new Date().toISOString().slice(0, 10)}.graphml`;
        link.click();
        URL.revokeObjectURL(url);
    } catch (e) { alert("Export gagal: " + e.message); }
}

async function exportJSON() {
    const minWeight = document.getElementById("min-weight").value || 0.3;
    try {
        const resp = await fetch(`/api/network/graph?min_weight=${minWeight}`);
        const data = await resp.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `geosdi-network-${new Date().toISOString().slice(0, 10)}.json`;
        link.click();
        URL.revokeObjectURL(url);
    } catch (e) { alert("Export gagal: " + e.message); }
}

// ============================================================
// TIME-LAPSE ANIMATION
// ============================================================
async function loadHistory() {
    try {
        const resp = await fetch("/api/network/history");
        if (!resp.ok) { console.warn("History API tidak tersedia"); return; }
        const data = await resp.json();
        gdiHistory = data.history || {};
        console.log(`✅ History loaded for ${Object.keys(gdiHistory).length} WKP`);
    } catch (e) {
        console.warn("History load failed:", e);
    }
}

function onTimeSliderChange(value) {
    const idx = parseInt(value);
    const label = document.getElementById("time-label");
    if (label) label.textContent = MONTH_LABELS[idx] || `Bulan ${idx}`;
    updateNodesByTime(idx);
}

function updateNodesByTime(monthIdx) {
    if (!networkInstance || allNodes.length === 0) return;

    const visNodes = networkInstance.body.data.nodes;
    const colorMode = document.getElementById("color-mode").value;

    allNodes.forEach(n => {
        const hist = gdiHistory[n.kode];
        let gdi = n.gdi_mean;

        if (hist && hist[monthIdx]) {
            gdi = hist[monthIdx].gdi_mean;
        }

        // Kalau time-lapse aktif (bukan bulan terakhir), selalu pakai GDI color
        let color;
        if (monthIdx < 23) {
            color = getGDIColor(gdi);
        } else {
            color = getNodeColor(n, colorMode);
        }

        const size = Math.max(10, Math.min(40, 15 + (gdi - 70) * 0.8));

        visNodes.update({
            id: n.id,
            color: {
                background: color,
                border: color,
                highlight: { background: color, border: "#1e3a8a" },
            },
            size: size,
            title: `${n.kode} — ${n.nama}<br>GDI: ${gdi.toFixed(2)} (${MONTH_LABELS[monthIdx]})`,
        });
    });
}

function togglePlayAnimation() {
    const btn = document.getElementById("play-btn");
    const slider = document.getElementById("time-slider");
    if (!btn || !slider) return;

    if (animationInterval) {
        clearInterval(animationInterval);
        animationInterval = null;
        btn.textContent = "▶️ Play";
        return;
    }

    btn.textContent = "⏸️ Pause";
    slider.value = 0;
    onTimeSliderChange(0);

    animationInterval = setInterval(() => {
        let current = parseInt(slider.value);
        if (current >= 23) {
            current = 0;
        } else {
            current += 1;
        }
        slider.value = current;
        onTimeSliderChange(current);
    }, 800);
}

// ============================================================
// Reload graph
// ============================================================
function reloadGraph() {
    loadGraph();
}

// ============================================================
// Init on page load
// ============================================================
window.addEventListener("DOMContentLoaded", () => {
    if (!document.getElementById("network-graph")) return;

    loadGraph();
    loadHistory();

    // Color mode listener
    const colorModeSelect = document.getElementById("color-mode");
    if (colorModeSelect) {
        colorModeSelect.addEventListener("change", applyColorMode);
    }
});

// Make functions globally available (untuk onclick handler)
window.reloadGraph = reloadGraph;
window.exportPNG = exportPNG;
window.exportGraphML = exportGraphML;
window.exportJSON = exportJSON;
window.onTimeSliderChange = onTimeSliderChange;
window.togglePlayAnimation = togglePlayAnimation;
window.applyColorMode = applyColorMode;
window.runIntervention = runIntervention;