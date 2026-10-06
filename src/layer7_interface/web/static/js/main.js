/* ==========================================================
   GeoSDI Geothermal v2.0 — Main JavaScript
   ==========================================================
   Catatan: Auto-refresh stats DIHAPUS karena endpoint /api/stats
   belum dibuat. Akan ditambahkan lagi di masa depan.
   ========================================================== */

console.log("🌋 GeoSDI Geothermal loaded (main.js)");

// Utility: format angka
function formatNumber(num, decimals = 1) {
    return Number(num).toFixed(decimals);
}

// Utility: fetch dengan error handling
async function fetchJSON(url) {
    try {
        const resp = await fetch(url);
        if (!resp.ok) {
            console.warn(`⚠️ API ${url} returned ${resp.status}`);
            return null;
        }
        return await resp.json();
    } catch (e) {
        console.error(`❌ Failed to fetch ${url}:`, e);
        return null;
    }
}

console.log("✅ main.js loaded");