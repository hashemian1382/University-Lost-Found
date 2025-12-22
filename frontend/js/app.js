import { initMap } from './map.js';
import { API_URL } from './config.js';

document.addEventListener('DOMContentLoaded', async () => {
    console.log("Application Started...");
    
    // map
    const map = initMap();

    // server test
    try {
        const response = await fetch(`${API_URL}/`);
        const data = await response.json();
        console.log("Server Status:", data);
    } catch (error) {
        console.error("Backend is unavailable. Make sure FastAPI is running.");
    }
});