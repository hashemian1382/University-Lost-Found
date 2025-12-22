export function initMap() {
   
    const map = L.map('map').setView([35.70, 51.41], 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    }).addTo(map);

    return map;
}