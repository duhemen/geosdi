/* ==========================================================
   GeoSDI — Choropleth Layer
   ==========================================================
   Menambahkan layer choropleth ke peta utama:
   provinsi diwarnai berdasarkan jumlah WKP.
   ========================================================== */

// Data contoh (akan di-fetch dari API)
const CHOROPLETH_DATA = {
    "Jawa Barat": { jumlah_wkp: 1, kapasitas: 235 },
    "Jawa Tengah": { jumlah_wkp: 1, kapasitas: 60 },
    "Sulawesi Utara": { jumlah_wkp: 1, kapasitas: 120 },
    "Sumatera Utara": { jumlah_wkp: 1, kapasitas: 330 },
    "Sumatera Selatan": { jumlah_wkp: 2, kapasitas: 220 },
};

// Fungsi: warna berdasarkan jumlah WKP
function getChoroplethColor(count) {
    if (count >= 3) return '#d73027';  // merah tua
    if (count === 2) return '#fc8d59'; // orange
    if (count === 1) return '#fee08b'; // kuning
    return '#ffffbf';                   // kuning pucat
}

// Fetch data dari API
async function loadChoroplethData() {
    try {
        const response = await fetch('/api/spatial/provinces/choropleth');
        if (!response.ok) return null;
        return await response.json();
    } catch (e) {
        console.warn('Failed to load choropleth:', e);
        return null;
    }
}

// Global function untuk digunakan di map.js
window.addChoroplethLayer = async function (map, indonesiaGeojson) {
    const data = await loadChoroplethData();
    const stats = data ? data.reduce((acc, r) => {
        acc[r.provinsi] = r.jumlah_wkp;
        return acc;
    }, {}) : {};

    L.geoJSON(indonesiaGeojson, {
        style: function (feature) {
            const provinsi = feature.properties.adm1_name;
            const count = stats[provinsi] || 0;
            return {
                fillColor: getChoroplethColor(count),
                weight: 0.5,
                opacity: 1,
                color: '#666',
                fillOpacity: 0.5,
            };
        },
        onEachFeature: function (feature, layer) {
            const provinsi = feature.properties.adm1_name;
            const count = stats[provinsi] || 0;
            layer.bindTooltip(`${provinsi}: ${count} WKP`);
        },
    }).addTo(map);

    console.log('✅ Choropleth layer added');
};