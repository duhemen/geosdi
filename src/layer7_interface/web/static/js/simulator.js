/* ==========================================================
   GeoSDI — Intervensi Simulator
   ========================================================== */

console.log("🎛️ simulator.js loaded");

let simulatorState = {
    kode: null,
    nama: null,
    baseline: null,
    currentVars: {},
};

// Buka modal simulator
window.openSimulator = async function(kode, nama) {
    console.log(`🎛️ Opening simulator for ${kode} (${nama})`);

    // Fetch detail GDI
    try {
        const resp = await fetch(`/api/gdi/${kode}`);
        if (!resp.ok) throw new Error('GDI not found');
        const gdi = await resp.json();

        simulatorState.kode = kode;
        simulatorState.nama = nama;
        simulatorState.baseline = gdi;
        simulatorState.currentVars = { ...gdi.variables };

        showSimulatorModal(gdi);
    } catch (e) {
        console.error('❌ Failed to open simulator:', e);
        alert('Gagal membuka simulator: ' + e.message);
    }
};

function showSimulatorModal(gdi) {
    // Buat modal HTML
    const modalHTML = `
        <div id="simulatorModal" style="
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.7);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            overflow-y: auto;
        ">
            <div style="
                background: white;
                border-radius: 12px;
                max-width: 800px;
                width: 100%;
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            ">
                <!-- Header -->
                <div style="
                    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 12px 12px 0 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <div>
                        <h2 style="margin: 0; font-size: 1.3rem;">
                            🎛️ Simulasi Intervensi
                        </h2>
                        <p style="margin: 0.5rem 0 0; opacity: 0.9; font-size: 0.9rem;">
                            ${gdi.nama} — ${gdi.kode}
                        </p>
                    </div>
                    <button onclick="closeSimulator()" style="
                        background: rgba(255,255,255,0.2);
                        color: white;
                        border: none;
                        width: 36px;
                        height: 36px;
                        border-radius: 50%;
                        font-size: 1.2rem;
                        cursor: pointer;
                    ">✕</button>
                </div>

                <!-- Body -->
                <div style="padding: 1.5rem;">
                    <!-- Baseline -->
                    <div style="
                        background: #f8fafc;
                        padding: 1rem;
                        border-radius: 8px;
                        margin-bottom: 1.5rem;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    ">
                        <div>
                            <div style="color: #64748b; font-size: 0.85rem;">GDI Baseline</div>
                            <div style="font-size: 1.8rem; font-weight: bold; color: #1e3a8a;">
                                ${gdi.gdi_mean.toFixed(2)}
                                <span style="font-size: 0.9rem; color: #94a3b8; font-weight: normal;">
                                    ± ${gdi.gdi_std.toFixed(2)}
                                </span>
                            </div>
                        </div>
                        <div style="
                            background: #10b98122;
                            color: #10b981;
                            padding: 0.5rem 1rem;
                            border-radius: 20px;
                            font-weight: bold;
                        ">
                            ${gdi.status}
                        </div>
                    </div>

                    <!-- Sliders -->
                    <h3 style="color: #1e3a8a; margin-bottom: 1rem;">
                        📊 Variabel (0.0 - 1.0)
                    </h3>

                    <div id="slidersContainer" style="
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                        gap: 1rem;
                    "></div>

                    <!-- Simulated Result -->
                    <div id="simResult" style="
                        margin-top: 1.5rem;
                        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                        padding: 1.5rem;
                        border-radius: 8px;
                        display: none;
                    ">
                        <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 0.5rem;">
                            GDI Simulasi
                        </div>
                        <div style="
                            display: flex;
                            align-items: baseline;
                            gap: 1rem;
                            flex-wrap: wrap;
                        ">
                            <div id="simGDIValue" style="
                                font-size: 2.2rem;
                                font-weight: bold;
                                color: #1e3a8a;
                            ">—</div>
                            <div id="simDelta" style="
                                font-size: 1.1rem;
                                font-weight: bold;
                            ">—</div>
                        </div>
                        <div id="simCI" style="
                            margin-top: 0.5rem;
                            color: #64748b;
                            font-size: 0.9rem;
                        ">—</div>
                    </div>

                    <!-- Actions -->
                    <div style="
                        display: flex;
                        gap: 0.5rem;
                        margin-top: 1.5rem;
                        justify-content: flex-end;
                    ">
                        <button onclick="resetSimulator()" style="
                            background: #f1f5f9;
                            color: #334155;
                            border: none;
                            padding: 0.75rem 1.5rem;
                            border-radius: 8px;
                            font-weight: bold;
                            cursor: pointer;
                        ">🔄 Reset</button>
                        <button onclick="runSimulation()" style="
                            background: #1e3a8a;
                            color: white;
                            border: none;
                            padding: 0.75rem 1.5rem;
                            border-radius: 8px;
                            font-weight: bold;
                            cursor: pointer;
                        ">▶️ Jalankan Simulasi</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
    buildSliders(gdi.variables);
}

function buildSliders(vars) {
    const VAR_LABELS = {
        'R': { name: 'Reservoir Potential', icon: '🔥' },
        'T': { name: 'Technology Readiness', icon: '⚙️' },
        'E': { name: 'Economic Viability', icon: '💰' },
        'P': { name: 'Policy Support', icon: '📜' },
        'S': { name: 'Social Acceptance', icon: '👥' },
        'N': { name: 'Environmental', icon: '🌿' },
        'C': { name: 'Conflict Intensity', icon: '⚠️' },
        'H': { name: 'Historical Momentum', icon: '📚' },
    };

    const container = document.getElementById('slidersContainer');

    container.innerHTML = Object.entries(VAR_LABELS).map(([key, info]) => {
        const value = vars[key] || 0;
        return `
            <div style="
                background: #f8fafc;
                padding: 0.75rem;
                border-radius: 8px;
            ">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 0.5rem;
                ">
                    <label style="font-weight: bold; font-size: 0.9rem; color: #334155;">
                        ${info.icon} ${info.name}
                    </label>
                    <span id="val-${key}" style="
                        background: #1e3a8a;
                        color: white;
                        padding: 0.15rem 0.6rem;
                        border-radius: 12px;
                        font-size: 0.8rem;
                        font-weight: bold;
                    ">${value.toFixed(2)}</span>
                </div>
                <input
                    type="range"
                    id="slider-${key}"
                    min="0" max="1" step="0.05"
                    value="${value}"
                    oninput="onSliderChange('${key}', this.value)"
                    style="width: 100%;"
                >
            </div>
        `;
    }).join('');
}

window.onSliderChange = function(key, value) {
    const display = document.getElementById(`val-${key}`);
    if (display) display.textContent = parseFloat(value).toFixed(2);
    simulatorState.currentVars[key] = parseFloat(value);
};

window.resetSimulator = function() {
    if (!simulatorState.baseline) return;
    buildSliders(simulatorState.baseline.variables);
    simulatorState.currentVars = { ...simulatorState.baseline.variables };
    document.getElementById('simResult').style.display = 'none';
};

window.runSimulation = async function() {
    if (!simulatorState.kode) return;

    const btn = event.target;
    btn.textContent = '⏳ Menghitung...';
    btn.disabled = true;

    try {
        const payload = {
            kode: simulatorState.kode,
            ...simulatorState.currentVars,
        };

        const resp = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) throw new Error(`Simulation failed: ${resp.status}`);
        const result = await resp.json();

        // Tampilkan hasil
        const resultDiv = document.getElementById('simResult');
        const gdiVal = document.getElementById('simGDIValue');
        const deltaDiv = document.getElementById('simDelta');
        const ciDiv = document.getElementById('simCI');

        gdiVal.textContent = result.simulated_mean.toFixed(2);

        const deltaSign = result.delta >= 0 ? '+' : '';
        const deltaColor = result.delta > 0 ? '#10b981' : result.delta < 0 ? '#ef4444' : '#64748b';
        deltaDiv.textContent = `${deltaSign}${result.delta.toFixed(2)} (${deltaSign}${result.delta_percent}%)`;
        deltaDiv.style.color = deltaColor;

        ciDiv.textContent = `90% CI: [${result.simulated_ci_lower.toFixed(1)}, ${result.simulated_ci_upper.toFixed(1)}] | Status: ${result.simulated_status}`;

        resultDiv.style.display = 'block';
        console.log('✅ Simulation result:', result);
    } catch (e) {
        console.error('❌ Simulation failed:', e);
        alert('Simulasi gagal: ' + e.message);
    } finally {
        btn.textContent = '▶️ Jalankan Simulasi';
        btn.disabled = false;
    }
};

window.closeSimulator = function() {
    const modal = document.getElementById('simulatorModal');
    if (modal) modal.remove();
    simulatorState = { kode: null, nama: null, baseline: null, currentVars: {} };
};