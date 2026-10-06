/* ==========================================================
   GeoSDI Geothermal v2.0 — Interactive Map + Choropleth
   Version: 2.3.0
   ==========================================================
   Changes in 2.3.0:
   - Removed duplicate layer control
   - Fixed data_quality reading
   - Better console logging
   ========================================================== */

console.log("🌋 GeoSDI Geothermal loaded (map.js v2.3.0)");

// Inisialisasi peta
const map = L.map('map').setView([CENTER.lat, CENTER.lon], 5);

// ============================================================
// Basemaps
// ============================================================
const basemaps = {
    "Esri Street": L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
        { attribution: 'Tiles © Esri', maxZoom: 19 }
    ),
    "OpenStreetMap": L.tileLayer(
        'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        { attribution: '© OpenStreetMap contributors', maxZoom: 19 }
    ),
    "Esri Satellite": L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        { attribution: 'Tiles © Esri', maxZoom: 19 }
    ),
    "OSM HOT": L.tileLayer(
        'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        { attribution: '© OpenStreetMap contributors, Tiles style by HOT', subdomains: 'abc', maxZoom: 19 }
    ),
    "Esri Terrain": L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}',
        { attribution: 'Tiles © Esri', maxZoom: 13 }
    ),
};

basemaps["Esri Street"].addTo(map);

// NOTE: Layer control akan di-set SETELAH marker clusters dibuat (di bawah)

// ============================================================
// Marker Icon
// ============================================================
const STATUS_COLORS = {
    'Operasi': '#10b981',
    'Eksplorasi': '#f59e0b',
    'Konstruksi': '#3b82f6',
    'Perencanaan': '#6b7280',
};

function createIcon(status) {
    const color = STATUS_COLORS[status] || '#ef4444';
    return L.divIcon({
        className: 'custom-marker',
        html: `
            <div style="
                background: ${color};
                width: 32px;
                height: 32px;
                border-radius: 50% 50% 50% 0;
                transform: rotate(-45deg);
                border: 3px solid white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <i class="fas fa-fire" style="
                    color: white;
                    transform: rotate(45deg);
                    font-size: 14px;
                "></i>
            </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32],
    });
}

// ============================================================
// Marker Cluster Groups
// ============================================================
const markerClusterVerified = L.markerClusterGroup({
    chunkedLoading: true,
    maxClusterRadius: 40,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    zoomToBoundsOnClick: true,
    iconCreateFunction: function(cluster) {
        const count = cluster.getChildCount();
        return L.divIcon({
            html: `<div style="background: #10b981; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">${count}</div>`,
            className: 'marker-cluster-verified',
            iconSize: L.point(40, 40)
        });
    }
});

const markerClusterEstimated = L.markerClusterGroup({
    chunkedLoading: true,
    maxClusterRadius: 40,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    zoomToBoundsOnClick: true,
    iconCreateFunction: function(cluster) {
        const count = cluster.getChildCount();
        return L.divIcon({
            html: `<div style="background: #94a3b8; color: white; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; border: 2px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">${count}</div>`,
            className: 'marker-cluster-estimated',
            iconSize: L.point(36, 36)
        });
    }
});

// ============================================================
// Loop through NODES
// ============================================================
let verifiedCount = 0;
let estimatedCount = 0;

NODES.forEach(function(node) {
    const quality = node.data_quality || 'user_provided';
    const isVerified = quality === 'verified';

    const icon = isVerified
        ? createIcon(node.status)
        : L.divIcon({
            className: 'estimated-marker',
            html: `<div style="
                background: #94a3b8;
                width: 14px;
                height: 14px;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 1px 4px rgba(0,0,0,0.3);
            "></div>`,
            iconSize: [14, 14],
            iconAnchor: [7, 7],
        });

    const popupHTML = `
        <div style="font-family: Arial; min-width: 240px;">
            <h4 style="margin: 0 0 8px 0; color: #1e3a8a;
                       border-bottom: 2px solid #4a90e2; padding-bottom: 5px;">
                ${isVerified ? '🌋' : '📍'} ${node.nama}
            </h4>
            <div style="margin-bottom: 6px;">
                ${isVerified
                    ? '<span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;">✅ VERIFIED</span>'
                    : '<span style="background: #94a3b8; color: white; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;">📍 ESTIMATED</span>'
                }
            </div>
            <table style="font-size: 12px; width: 100%;">
                <tr><td><b>Kode</b></td><td>: ${node.kode}</td></tr>
                <tr><td><b>Provinsi</b></td><td>: ${node.provinsi}</td></tr>
                <tr><td><b>Status</b></td><td>: ${node.status}</td></tr>
                ${node.kapasitas_mw ? `<tr><td><b>Kapasitas</b></td><td>: ${node.kapasitas_mw} MW</td></tr>` : ''}
            </table>
            ${isVerified ? `
                <button onclick="window.addToComparison('${node.kode}')" style="
                    background: #3b82f6; color: white; border: none; padding: 6px 12px;
                    border-radius: 4px; cursor: pointer; font-weight: bold;
                    font-size: 12px; width: 100%; margin-top: 8px;
                ">
                    📊 Tambah ke Comparison
                </button>
            ` : `
                <div style="margin-top: 8px; font-size: 11px; color: #64748b; font-style: italic;">
                    Data estimasi dari peta Genesis ESDM
                </div>
            `}
        </div>
    `;

    const marker = L.marker([node.latitude, node.longitude], {
        icon: icon,
        zIndexOffset: isVerified ? 1000 : 0,
    })
    .bindPopup(popupHTML)
    .bindTooltip(`${node.nama} (${isVerified ? 'Verified' : 'Estimated'})`);

    if (isVerified) {
        markerClusterVerified.addLayer(marker);
        verifiedCount++;
    } else {
        markerClusterEstimated.addLayer(marker);
        estimatedCount++;
    }
});

// Add both clusters to map
map.addLayer(markerClusterEstimated);
map.addLayer(markerClusterVerified);

// ============================================================
// Layer Control (HANYA 1, setelah cluster dibuat)
// ============================================================
const overlayMaps = {
    "✅ WKP Verified": markerClusterVerified,
    "📍 WKP Estimated": markerClusterEstimated,
};

L.control.layers(basemaps, overlayMaps, {
    position: 'topright',
    collapsed: false,
}).addTo(map);

console.log(`[OK] ${verifiedCount} verified + ${estimatedCount} estimated WKP dimuat`);

// ============================================================
// CHOROPLETH
// ============================================================
let choroplethLayer = null;
let choroplethStatsCache = null;

function getChoroplethColor(count) {
    if (count >= 3) return '#d73027';
    if (count === 2) return '#fc8d59';
    if (count === 1) return '#fee08b';
    return '#f7f7f7';
}

async function toggleChoropleth() {
    const btn = document.getElementById('toggleChoropleth');
    if (!btn) {
        console.error('❌ Tombol toggleChoropleth tidak ditemukan!');
        return;
    }

    if (choroplethLayer) {
        map.removeLayer(choroplethLayer);
        choroplethLayer = null;
        btn.textContent = '🎨 Choropleth: OFF';
        btn.style.background = 'white';
        btn.style.color = '#1e3a8a';
        console.log('🎨 Choropleth REMOVED');
        return;
    }

    btn.textContent = '⏳ Loading...';
    btn.style.background = '#fee08b';
    btn.style.color = '#1e3a8a';

    try {
        if (!choroplethStatsCache) {
            const dataResp = await fetch('/api/spatial/provinces/choropleth');
            if (!dataResp.ok) throw new Error(`API error: ${dataResp.status}`);
            const data = await dataResp.json();
            choroplethStatsCache = data.reduce((acc, r) => {
                acc[r.provinsi] = r.jumlah_wkp;
                return acc;
            }, {});
            console.log('📊 Stats loaded:', choroplethStatsCache);
        }

        const geojsonResp = await fetch('/static/data/indonesia_provinces.geojson');
        if (!geojsonResp.ok) throw new Error(`GeoJSON error: ${geojsonResp.status}`);
        const geojson = await geojsonResp.json();
        console.log(`📍 GeoJSON loaded: ${geojson.features.length} features`);

        choroplethLayer = L.geoJSON(geojson, {
            style: feature => {
                const provinsi = feature.properties.adm1_name;
                const count = choroplethStatsCache[provinsi] || 0;
                return {
                    fillColor: getChoroplethColor(count),
                    weight: 0.8,
                    opacity: 1,
                    color: '#666',
                    fillOpacity: 0.55,
                };
            },
            onEachFeature: (feature, layer) => {
                const provinsi = feature.properties.adm1_name || 'Unknown';
                const count = choroplethStatsCache[provinsi] || 0;
                layer.bindTooltip(`<b>${provinsi}</b><br/>WKP: ${count}`, { sticky: true });
            },
        }).addTo(map);

        btn.textContent = '🎨 Choropleth: ON';
        btn.style.background = '#d73027';
        btn.style.color = 'white';
        console.log('✅ Choropleth ADDED');

    } catch (e) {
        console.error('❌ Choropleth failed:', e);
        btn.textContent = '🎨 Choropleth: ERROR';
        btn.style.background = '#ef4444';
        btn.style.color = 'white';
        alert('Gagal load choropleth: ' + e.message);
        setTimeout(() => {
            btn.textContent = '🎨 Choropleth: OFF';
            btn.style.background = 'white';
            btn.style.color = '#1e3a8a';
        }, 3000);
    }
}

// Bind tombol setelah DOM ready
window.addEventListener('DOMContentLoaded', () => {
    console.log('🔧 DOMContentLoaded fired');
    const btn = document.getElementById('toggleChoropleth');
    if (btn) {
        btn.addEventListener('click', toggleChoropleth);
        console.log('✅ Tombol Choropleth ter-bind');
    } else {
        console.error('❌ Tombol toggleChoropleth tidak ditemukan di DOM');
    }
});