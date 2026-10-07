/* ==========================================================
   GeoSDI — ABM Simulation UI
   ========================================================== */

console.log("🤖 abm.js loaded");

let agentMetadata = {};
let currentAgents = [];  // { type, id, name, params }

// ============================================================
// Load agent metadata & presets
// ============================================================
async function loadMetadata() {
    try {
        const [agentsResp, scenariosResp] = await Promise.all([
            fetch("/api/abm/agents"),
            fetch("/api/abm/scenarios"),
        ]);

        const agentsData = await agentsResp.json();
        const scenariosData = await scenariosResp.json();

        // Build metadata map
        agentMetadata = {};
        agentsData.agents.forEach(a => {
            agentMetadata[a.type] = a;
        });

        // Render palette
        renderPalette(agentsData.agents);

        // Render presets
        renderPresets(scenariosData.scenarios);

        console.log(`✅ ${agentsData.agents.length} agent types loaded, ${scenariosData.scenarios.length} presets`);
    } catch (e) {
        console.error("❌ Failed to load metadata:", e);
    }
}

// ============================================================
// Render agent palette
// ============================================================
function renderPalette(agents) {
    const container = document.getElementById("agent-palette");
    container.innerHTML = agents.map(a => `
        <div class="agent-chip" onclick="addAgent('${a.type}')" title="${a.description}">
            ${a.icon} ${a.label}
        </div>
    `).join("");
}

// ============================================================
// Render presets
// ============================================================
function renderPresets(scenarios) {
    const container = document.getElementById("preset-grid");
    container.innerHTML = scenarios.map(s => `
        <div class="preset-card" onclick="loadPreset('${s.key}')">
            <h4>${s.name}</h4>
            <p>${s.description}</p>
            <div style="font-size: 0.72rem; color: #7c3aed; margin-top: 0.5rem;">
                👥 ${s.n_agents} agen
            </div>
        </div>
    `).join("");
}

// ============================================================
// Add agent
// ============================================================
function addAgent(type) {
    const meta = agentMetadata[type];
    if (!meta) return;

    const id = `${type}-${Date.now()}`;
    const name = `${meta.label} ${currentAgents.filter(a => a.type === type).length + 1}`;

    currentAgents.push({
        type: type,
        id: id,
        name: name,
        params: { ...meta.default_params },
    });

    renderAgentList();
}

function removeAgent(id) {
    currentAgents = currentAgents.filter(a => a.id !== id);
    renderAgentList();
}

function clearAgents() {
    if (currentAgents.length === 0) return;
    if (!confirm("Hapus semua agen?")) return;
    currentAgents = [];
    renderAgentList();
}

function renderAgentList() {
    const container = document.getElementById("agent-list");

    if (currentAgents.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 1rem;">
                Belum ada agen. Tambah dari palette ↓
            </div>
        `;
        return;
    }

    container.innerHTML = currentAgents.map(a => {
        const meta = agentMetadata[a.type];
        return `
            <div class="agent-item">
                <div class="info">
                    <div class="name">${meta.icon} ${a.name}</div>
                    <div class="type">${meta.label}</div>
                </div>
                <button class="remove-btn" onclick="removeAgent('${a.id}')">×</button>
            </div>
        `;
    }).join("");
}

// ============================================================
// Load preset
// ============================================================
async function loadPreset(key) {
    try {
        const resp = await fetch(`/api/abm/scenarios`);
        const data = await resp.json();
        const scenario = data.scenarios.find(s => s.key === key);
        if (!scenario) return;

        // Clear current
        currentAgents = [];

        // Need to fetch full scenario definition — we don't have it here
        // Instead, use the run endpoint directly
        await runPresetScenario(key);
    } catch (e) {
        console.error("❌ Failed to load preset:", e);
        alert("Gagal load preset: " + e.message);
    }
}

async function runPresetScenario(key) {
    const maxSteps = parseInt(document.getElementById("max-steps").value) || 15;

    showLoading();

    try {
        const resp = await fetch(`/api/abm/scenario/${key}/run?max_steps=${maxSteps}`);
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || "Error");
        }

        const data = await resp.json();
        renderResults(data);
        console.log("✅ Preset scenario completed:", data);
    } catch (e) {
        console.error("❌ Preset failed:", e);
        alert("Gagal jalankan preset: " + e.message);
        showEmpty();
    }
}

// ============================================================
// Run custom simulation
// ============================================================
async function runSimulation() {
    if (currentAgents.length === 0) {
        alert("Tambah minimal 1 agen dulu.");
        return;
    }

    const maxSteps = parseInt(document.getElementById("max-steps").value) || 15;
    const seed = parseInt(document.getElementById("seed").value) || 42;

    const payload = {
        name: "Custom Simulation",
        max_steps: maxSteps,
        seed: seed,
        agents: currentAgents.map(a => ({
            type: a.type,
            id: a.id,
            name: a.name,
            params: a.params,
        })),
    };

    showLoading();

    try {
        const resp = await fetch("/api/abm/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.detail || "Error");
        }

        const data = await resp.json();
        renderResults(data);
        console.log("✅ Simulation completed:", data);
    } catch (e) {
        console.error("❌ Simulation failed:", e);
        alert("Gagal jalankan simulation: " + e.message);
        showEmpty();
    }
}

// ============================================================
// Render results
// ============================================================
function renderResults(data) {
    const container = document.getElementById("results-area");

    const env = data.environment;
    const deltaGdi = env.delta.gdi_national;
    const deltaPct = env.delta.gdi_percent;
    const deltaColor = deltaGdi > 0 ? "#10b981" : deltaGdi < 0 ? "#ef4444" : "#64748b";

    const agentsHtml = data.agents.map(a => `
        <div style="padding: 0.5rem; background: #f8fafc; border-radius: 6px; margin-bottom: 0.4rem; display: flex; justify-content: space-between; font-size: 0.85rem;">
            <span><strong>${a.name}</strong></span>
            <span style="color: #64748b;">${a.memory_size} actions</span>
        </div>
    `).join("");

    container.innerHTML = `
        <h3 style="color: #7c3aed; margin: 0 0 0.75rem;">📊 Hasil Simulation: ${data.name}</h3>

        <div class="stats-grid">
            <div class="stat-box">
                <div class="label">Steps</div>
                <div class="value">${data.n_steps}</div>
            </div>
            <div class="stat-box">
                <div class="label">Agents</div>
                <div class="value">${data.n_agents}</div>
            </div>
            <div class="stat-box">
                <div class="label">Events</div>
                <div class="value">${data.n_events}</div>
            </div>
            <div class="stat-box">
                <div class="label">GDI Awal</div>
                <div class="value">${env.initial.gdi_national}</div>
            </div>
            <div class="stat-box">
                <div class="label">GDI Akhir</div>
                <div class="value" style="color: ${deltaColor};">${env.final.gdi_national}</div>
                <div class="delta" style="color: ${deltaColor};">
                    ${deltaGdi > 0 ? '+' : ''}${deltaGdi} (${deltaPct > 0 ? '+' : ''}${deltaPct}%)
                </div>
            </div>
            <div class="stat-box">
                <div class="label">Total Investment</div>
                <div class="value" style="font-size: 1.2rem;">${env.final.total_investment_billion} M</div>
            </div>
            <div class="stat-box">
                <div class="label">Total Capacity</div>
                <div class="value" style="font-size: 1.2rem;">${env.final.total_capacity_mw} MW</div>
            </div>
        </div>

        <h3 style="color: #7c3aed; margin: 1.5rem 0 0.75rem;">👥 Agent Activity</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0.5rem;">
            ${agentsHtml}
        </div>
    `;
}

function showLoading() {
    document.getElementById("results-area").innerHTML = `
        <div style="text-align: center; padding: 3rem;">
            <div style="display: inline-block; width: 40px; height: 40px; border: 3px solid #e9d5ff; border-top-color: #7c3aed; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            <div style="margin-top: 1rem; color: #64748b; font-weight: 600;">Simulasi berjalan...</div>
        </div>
        <style>@keyframes spin { to { transform: rotate(360deg); } }</style>
    `;
}

function showEmpty() {
    document.getElementById("results-area").innerHTML = `
        <div class="empty-state">
            <div class="icon">🤖</div>
            <div class="title">Belum ada hasil simulasi</div>
            <div>Pilih preset scenario di atas, atau configure agen manual lalu klik "Jalankan Simulation".</div>
        </div>
    `;
}

// ============================================================
// Init
// ============================================================
window.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("agent-palette")) {
        loadMetadata();
    }
});

// Bind to window
window.addAgent = addAgent;
window.removeAgent = removeAgent;
window.clearAgents = clearAgents;
window.runSimulation = runSimulation;
window.loadPreset = loadPreset;