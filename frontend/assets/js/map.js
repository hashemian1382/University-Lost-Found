let map;
let marker;
let tempMarker;

function initMap(editable = false, initialCoords = null) {
    const coords = initialCoords || DEFAULT_COORDS;
    
    map = L.map('map').setView(coords, DEFAULT_ZOOM);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    if (editable) {
        map.on('click', function(e) {
            if (tempMarker) {
                map.removeLayer(tempMarker);
            }
            tempMarker = L.marker(e.latlng).addTo(map);
            
            const latInput = document.getElementById('lat');
            const lngInput = document.getElementById('lng');
            if(latInput && lngInput) {
                latInput.value = e.latlng.lat;
                lngInput.value = e.latlng.lng;
            }
        });

        if (initialCoords) {
            tempMarker = L.marker(initialCoords).addTo(map);
        }
    }
}

function addPin(item) {
    if (!map) return;
    
    const color = item.type === 'LOST' ? 'red' : 'green';
    
    const circleMarker = L.circleMarker([item.latitude, item.longitude], {
        color: color,
        fillColor: color,
        fillOpacity: 0.5,
        radius: 10
    }).addTo(map);

    circleMarker.bindPopup(`
        <b>${item.title}</b><br>
        ${item.type === 'LOST' ? 'گمشده' : 'پیدا شده'}<br>
        <a href="#" onclick="showItemDetails(${item.id})">مشاهده</a>
    `);
}

function locateUser() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            map.flyTo([lat, lng], 16);
            L.marker([lat, lng]).addTo(map).bindPopup("مکان شما").openPopup();
        });
    } else {
        alert("مرورگر شما از موقعیت مکانی پشتیبانی نمی‌کند.");
    }
}