/**
 * Southeast London Analysis Map
 * Interactive Leaflet.js visualization exploring:
 * - Housing affordability
 * - Transport connectivity (tube distance, travel time proxy)
 * - "Born locally" rates (population stability)
 */

// Configuration
const CONFIG = {
    mapCenter: [51.48, -0.05],
    defaultZoom: 11,
    boroughDataPath: 'data/london_affordability.geojson',
    boroughStatsPath: 'data/summary_stats.json',
    msoaDataPath: 'data/london_affordability_msoa.geojson',
    msoaStatsPath: 'data/summary_stats_msoa.json',
    seBorough: [
        'Greenwich', 'Lewisham', 'Southwark', 'Lambeth',
        'Bromley', 'Bexley', 'Croydon'
    ]
};

// Theme configurations
const THEMES = {
    affordability: {
        name: 'Affordability Ratio',
        field: 'affordability_ratio',
        unit: 'x',
        description: 'Compares median house prices to median annual earnings. <strong>Lower = more affordable.</strong> A ratio of 10 means the median home costs 10x the median annual salary.',
        insight: 'SE London has a lower affordability ratio (cheaper housing relative to earnings) than most other parts of London.',
        legendTitle: 'Affordability Ratio',
        legendSubtitle: '(House Price ÷ Annual Earnings)',
        getColor: (v) => v > 20 ? '#d73027' : v > 15 ? '#fc8d59' : v > 12 ? '#fee08b' : v > 10 ? '#91cf60' : v > 8 ? '#1a9850' : '#006837',
        legendItems: [
            { color: '#006837', label: '< 8 (Very Affordable)' },
            { color: '#1a9850', label: '8-10 (Affordable)' },
            { color: '#91cf60', label: '10-12 (Moderate)' },
            { color: '#fee08b', label: '12-15 (Stretched)' },
            { color: '#fc8d59', label: '15-20 (Unaffordable)' },
            { color: '#d73027', label: '> 20 (Very Unaffordable)' }
        ],
        sortAscending: true // Lower is better
    },
    tube_distance: {
        name: 'Distance to Tube',
        field: 'tube_distance_km',
        unit: 'km',
        description: 'Distance in kilometers to the nearest <strong>Underground station only</strong>. SE London famously has very limited tube coverage.',
        insight: 'SE London averages <strong>6.4 km</strong> to the nearest tube, vs 5.1km elsewhere. Only <strong>13%</strong> have tube within 1.5km.',
        legendTitle: 'Distance to Tube',
        legendSubtitle: '(Underground only)',
        getColor: (v) => v > 8 ? '#d73027' : v > 5 ? '#fc8d59' : v > 3 ? '#fee08b' : v > 1.5 ? '#91cf60' : '#1a9850',
        legendItems: [
            { color: '#1a9850', label: '< 1.5 km (Walkable)' },
            { color: '#91cf60', label: '1.5-3 km' },
            { color: '#fee08b', label: '3-5 km' },
            { color: '#fc8d59', label: '5-8 km' },
            { color: '#d73027', label: '> 8 km (No tube)' }
        ],
        sortAscending: true
    },
    station_distance: {
        name: 'Distance to Any Station',
        field: 'station_distance_km',
        unit: 'km',
        description: 'Distance to nearest <strong>tube OR train station</strong>. Includes Overground, National Rail, DLR, Elizabeth Line.',
        insight: '🔄 <strong>Plot twist!</strong> SE London has BETTER station access: <strong>87%</strong> have a station within 1.5km vs only <strong>28%</strong> elsewhere. Average just <strong>0.97km</strong> to nearest station!',
        legendTitle: 'Distance to Any Station',
        legendSubtitle: '(Tube + Rail)',
        getColor: (v) => v > 3 ? '#d73027' : v > 2 ? '#fc8d59' : v > 1.5 ? '#fee08b' : v > 0.8 ? '#91cf60' : '#1a9850',
        legendItems: [
            { color: '#1a9850', label: '< 0.8 km (Very close)' },
            { color: '#91cf60', label: '0.8-1.5 km (Walkable)' },
            { color: '#fee08b', label: '1.5-2 km' },
            { color: '#fc8d59', label: '2-3 km' },
            { color: '#d73027', label: '> 3 km' }
        ],
        sortAscending: true
    },
    transport_score: {
        name: 'UK Connectivity',
        field: 'transport_score',
        unit: '/100',
        description: 'Composite score (0-100) measuring access to major rail termini and motorways. <strong>Higher = easier to reach rest of UK.</strong>',
        insight: 'SE London scores lower for UK-wide travel due to distance from Kings Cross, Euston, Paddington etc and limited motorway access.',
        legendTitle: 'UK Connectivity Score',
        legendSubtitle: '(Termini + Motorways)',
        getColor: (v) => v > 60 ? '#1a9850' : v > 45 ? '#91cf60' : v > 30 ? '#fee08b' : v > 15 ? '#fc8d59' : '#d73027',
        legendItems: [
            { color: '#1a9850', label: '> 60 (Excellent)' },
            { color: '#91cf60', label: '45-60 (Good)' },
            { color: '#fee08b', label: '30-45 (Moderate)' },
            { color: '#fc8d59', label: '15-30 (Limited)' },
            { color: '#d73027', label: '< 15 (Poor)' }
        ],
        sortAscending: false // Higher is better
    },
    born_local: {
        name: 'Born Locally',
        field: 'born_local_pct',
        unit: '%',
        description: 'Estimated percentage of UK-born residents who still live in the same region they were born. <strong>Higher = more stable, less transient population.</strong>',
        insight: 'SE London has higher "born locally" rates (<strong>42%</strong> vs <strong>30%</strong>), suggesting less population churn and potentially less demand pressure from newcomers.',
        legendTitle: 'Born Locally Rate',
        legendSubtitle: '(% of UK-born still local)',
        getColor: (v) => v > 50 ? '#1a9850' : v > 40 ? '#91cf60' : v > 30 ? '#fee08b' : v > 20 ? '#fc8d59' : '#d73027',
        legendItems: [
            { color: '#1a9850', label: '> 50% (Very stable)' },
            { color: '#91cf60', label: '40-50%' },
            { color: '#fee08b', label: '30-40%' },
            { color: '#fc8d59', label: '20-30%' },
            { color: '#d73027', label: '< 20% (Transient)' }
        ],
        sortAscending: false // Higher is "more interesting" for this theory
    }
};

// Current state
let currentLevel = 'borough';
let currentTheme = 'affordability';
let currentData = null;
let currentStats = null;

// Map and layers
let map;
let geojsonLayer;
let labelsLayer;
let tubeMarkersLayer;

// Tube station data (for markers)
const TUBE_STATIONS = [
    { name: "Bank", lat: 51.5133, lon: -0.0886 },
    { name: "Liverpool Street", lat: 51.5178, lon: -0.0823 },
    { name: "Victoria", lat: 51.4965, lon: -0.1447 },
    { name: "Waterloo", lat: 51.5036, lon: -0.1143 },
    { name: "London Bridge", lat: 51.5052, lon: -0.0864 },
    { name: "Westminster", lat: 51.5010, lon: -0.1254 },
    { name: "Stockwell", lat: 51.4723, lon: -0.1230 },
    { name: "Brixton", lat: 51.4627, lon: -0.1145 },
    { name: "Bermondsey", lat: 51.4979, lon: -0.0637 },
    { name: "Canada Water", lat: 51.4982, lon: -0.0502 },
    { name: "North Greenwich", lat: 51.5005, lon: 0.0039 },
    { name: "Canary Wharf", lat: 51.5035, lon: -0.0187 },
    { name: "Stratford", lat: 51.5416, lon: -0.0042 },
    { name: "Kennington", lat: 51.4884, lon: -0.1053 },
    { name: "Oval", lat: 51.4819, lon: -0.1126 },
    { name: "Clapham North", lat: 51.4649, lon: -0.1299 },
    { name: "Clapham Common", lat: 51.4618, lon: -0.1384 },
    { name: "Morden", lat: 51.4022, lon: -0.1948 },
    { name: "Wimbledon", lat: 51.4214, lon: -0.2064 },
    { name: "East Ham", lat: 51.5394, lon: 0.0519 },
    { name: "Barking", lat: 51.5396, lon: 0.0809 },
    { name: "Upminster", lat: 51.5590, lon: 0.2510 },
];

function initMap() {
    map = L.map('map', {
        center: CONFIG.mapCenter,
        zoom: CONFIG.defaultZoom,
        scrollWheelZoom: true
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    setupControls();
    loadData('borough');
}

function setupControls() {
    // Level toggle
    document.querySelectorAll('input[name="level"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentLevel = e.target.value;
            loadData(currentLevel);
        });
    });

    // Theme toggle
    document.querySelectorAll('input[name="theme"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentTheme = e.target.value;
            updateThemeUI();
            if (currentData) renderMap(currentData);
        });
    });

    // Highlight SE toggle
    document.getElementById('highlight-se').addEventListener('change', (e) => {
        if (currentData) renderMap(currentData);
    });

    // Labels toggle
    document.getElementById('show-labels').addEventListener('change', (e) => {
        if (e.target.checked && currentData) {
            addLabels(currentData);
        } else if (labelsLayer) {
            map.removeLayer(labelsLayer);
        }
    });

    // Tube markers toggle
    document.getElementById('show-tube-markers').addEventListener('change', (e) => {
        if (e.target.checked) {
            addTubeMarkers();
        } else if (tubeMarkersLayer) {
            map.removeLayer(tubeMarkersLayer);
        }
    });
}

function updateThemeUI() {
    const theme = THEMES[currentTheme];
    
    // Update info panel
    document.getElementById('theme-description').innerHTML = theme.description;
    document.getElementById('theme-insight').innerHTML = theme.insight;
    
    // Update legend
    updateLegend(theme);
    
    // Show/hide tube markers control
    const tubeControl = document.getElementById('tube-markers-control');
    if (currentTheme === 'tube_distance') {
        tubeControl.style.display = 'block';
    } else {
        tubeControl.style.display = 'none';
        if (tubeMarkersLayer) map.removeLayer(tubeMarkersLayer);
    }
}

function updateLegend(theme) {
    const legend = document.getElementById('legend');
    legend.innerHTML = `
        <h4>${theme.legendTitle}</h4>
        <p class="legend-subtitle">${theme.legendSubtitle}</p>
        <div class="legend-items">
            ${theme.legendItems.map(item => `
                <div class="legend-item">
                    <span class="legend-color" style="background: ${item.color}"></span>
                    <span>${item.label}</span>
                </div>
            `).join('')}
        </div>
        <div class="legend-note">
            <span class="se-indicator"></span> SE London highlighted
        </div>
    `;
}

async function loadData(level) {
    const dataPath = level === 'msoa' ? CONFIG.msoaDataPath : CONFIG.boroughDataPath;
    const statsPath = level === 'msoa' ? CONFIG.msoaStatsPath : CONFIG.boroughStatsPath;
    
    try {
        const [geoResponse, statsResponse] = await Promise.all([
            fetch(dataPath).catch(() => null),
            fetch(statsPath).catch(() => null)
        ]);

        if (geoResponse && geoResponse.ok) {
            currentData = await geoResponse.json();
        } else {
            currentData = getSampleData();
        }

        if (statsResponse && statsResponse.ok) {
            currentStats = await statsResponse.json();
        } else {
            currentStats = getSampleStats();
        }

        updateThemeUI();
        renderMap(currentData);
        updateStatsPanel(currentStats);

    } catch (error) {
        console.error('Error loading data:', error);
        currentData = getSampleData();
        currentStats = getSampleStats();
        renderMap(currentData);
        updateStatsPanel(currentStats);
    }
}

function renderMap(data) {
    if (geojsonLayer) map.removeLayer(geojsonLayer);
    if (labelsLayer) map.removeLayer(labelsLayer);

    const highlightSE = document.getElementById('highlight-se').checked;
    const theme = THEMES[currentTheme];

    geojsonLayer = L.geoJSON(data, {
        style: feature => styleFeature(feature, theme, highlightSE),
        onEachFeature: (feature, layer) => onEachFeature(feature, layer, theme)
    }).addTo(map);

    map.fitBounds(geojsonLayer.getBounds(), { padding: [20, 20] });
    updateRankings(data, theme);

    if (document.getElementById('show-labels').checked) {
        addLabels(data);
    }
}

function styleFeature(feature, theme, highlightSE) {
    const props = feature.properties;
    const value = props[theme.field];
    const isSE = props.is_se_london || CONFIG.seBorough.includes(props.borough_name);
    
    const baseWeight = currentLevel === 'msoa' ? 0.5 : 1;
    const highlightWeight = currentLevel === 'msoa' ? 1.5 : 3;

    return {
        fillColor: value !== undefined ? theme.getColor(value) : '#999',
        weight: isSE && highlightSE ? highlightWeight : baseWeight,
        opacity: 1,
        color: isSE && highlightSE ? '#2563eb' : '#666',
        fillOpacity: 0.7
    };
}

function onEachFeature(feature, layer, theme) {
    layer.on({
        mouseover: (e) => {
            e.target.setStyle({ weight: 4, color: '#333', fillOpacity: 0.85 });
            e.target.bringToFront();
        },
        mouseout: (e) => geojsonLayer.resetStyle(e.target),
        click: (e) => map.fitBounds(e.target.getBounds(), { padding: [50, 50] })
    });

    const props = feature.properties;
    const isSE = props.is_se_london || CONFIG.seBorough.includes(props.borough_name);
    layer.bindPopup(createPopupContent(props, isSE, theme));
}

function createPopupContent(props, isSE, theme) {
    const areaName = props.msoa_name || props.borough_name;
    const value = props[theme.field];
    const displayValue = value !== undefined ? `${value}${theme.unit}` : 'N/A';
    
    // Format prices and earnings
    const price = props.median_house_price?.toLocaleString() || 'N/A';
    const earnings = props.median_earnings?.toLocaleString() || 'N/A';
    const ratio = props.affordability_ratio || 'N/A';
    
    // Transport fields
    const tubeDistance = props.tube_distance_km || 'N/A';
    const nearestTube = props.nearest_tube || 'N/A';
    const stationDistance = props.station_distance_km || 'N/A';
    const nearestStation = props.nearest_station || 'N/A';
    const stationType = props.nearest_station_type || '';
    const transportScore = props.transport_score || 'N/A';
    const bornLocal = props.born_local_pct || 'N/A';

    const boroughInfo = props.msoa_name && props.borough_name ? 
        `<div class="popup-stat"><span class="label">Borough</span><span class="value">${props.borough_name}</span></div>` : '';

    return `
        <div class="popup-content ${isSE ? 'se-london' : ''}">
            <h3>
                ${areaName}
                ${isSE ? '<span class="se-badge">SE London</span>' : ''}
            </h3>
            ${boroughInfo}
            
            <div class="popup-stat highlight">
                <span class="label">${theme.name}</span>
                <span class="value">${displayValue}</span>
            </div>
            
            <hr style="margin: 8px 0; border: none; border-top: 1px solid #e5e5e5;">
            
            <div class="popup-section-title">💷 Affordability</div>
            <div class="popup-stat">
                <span class="label">Ratio</span>
                <span class="value">${ratio}x</span>
            </div>
            <div class="popup-stat">
                <span class="label">House Price</span>
                <span class="value">£${price}</span>
            </div>
            <div class="popup-stat">
                <span class="label">Earnings</span>
                <span class="value">£${earnings}</span>
            </div>
            
            <hr style="margin: 8px 0; border: none; border-top: 1px solid #e5e5e5;">
            
            <div class="popup-section-title">🚇 Transport</div>
            <div class="popup-stat">
                <span class="label">Nearest Station</span>
                <span class="value">${nearestStation} (${stationType})</span>
            </div>
            <div class="popup-stat">
                <span class="label">Station Distance</span>
                <span class="value">${stationDistance} km</span>
            </div>
            <div class="popup-stat">
                <span class="label">Tube Distance</span>
                <span class="value">${tubeDistance} km</span>
            </div>
            <div class="popup-stat">
                <span class="label">UK Connectivity</span>
                <span class="value">${transportScore}/100</span>
            </div>
            
            <hr style="margin: 8px 0; border: none; border-top: 1px solid #e5e5e5;">
            
            <div class="popup-section-title">🏡 Population</div>
            <div class="popup-stat">
                <span class="label">Born Locally</span>
                <span class="value">${bornLocal}%</span>
            </div>
        </div>
    `;
}

function addLabels(data) {
    if (labelsLayer) map.removeLayer(labelsLayer);
    if (currentLevel === 'msoa') return; // Too cluttered

    labelsLayer = L.layerGroup();
    data.features.forEach(feature => {
        const centroid = L.geoJSON(feature).getBounds().getCenter();
        const name = feature.properties.borough_name || feature.properties.msoa_name;
        const label = L.marker(centroid, {
            icon: L.divIcon({
                className: 'borough-label',
                html: `<span>${name}</span>`,
                iconSize: [100, 20]
            })
        });
        labelsLayer.addLayer(label);
    });
    labelsLayer.addTo(map);
}

function addTubeMarkers() {
    if (tubeMarkersLayer) map.removeLayer(tubeMarkersLayer);
    
    tubeMarkersLayer = L.layerGroup();
    
    const tubeIcon = L.divIcon({
        className: 'tube-marker',
        html: '🚇',
        iconSize: [20, 20]
    });

    TUBE_STATIONS.forEach(station => {
        const marker = L.marker([station.lat, station.lon], { icon: tubeIcon });
        marker.bindTooltip(station.name, { permanent: false, direction: 'top' });
        tubeMarkersLayer.addLayer(marker);
    });
    
    tubeMarkersLayer.addTo(map);
}

function updateStatsPanel(stats) {
    const savings = Math.abs(stats.comparison?.se_london_savings_percent || 15);
    document.getElementById('se-savings').textContent = `${savings}%`;
    
    const seRatio = stats.se_london?.avg_ratio || 11.5;
    document.getElementById('se-ratio').textContent = `${seRatio}x`;
    
    // Transport stats (from transport_analysis if available)
    const transport = stats.transport_analysis;
    if (transport) {
        const tubeCoverage = transport.se_london?.pct_with_tube_nearby || 17;
        document.getElementById('tube-coverage').textContent = `${tubeCoverage}%`;
        
        const bornLocal = transport.se_london?.avg_born_locally_pct || 42;
        document.getElementById('born-local').textContent = `${bornLocal}%`;
    } else {
        document.getElementById('tube-coverage').textContent = '17%';
        document.getElementById('born-local').textContent = '42%';
    }
}

function updateRankings(data, theme) {
    const list = document.getElementById('rankings-list');
    list.innerHTML = '';

    const sorted = [...data.features].sort((a, b) => {
        const aVal = a.properties[theme.field] || (theme.sortAscending ? 999 : -1);
        const bVal = b.properties[theme.field] || (theme.sortAscending ? 999 : -1);
        return theme.sortAscending ? aVal - bVal : bVal - aVal;
    });

    const displayItems = currentLevel === 'msoa' ? sorted.slice(0, 30) : sorted;

    displayItems.forEach((feature, index) => {
        const props = feature.properties;
        const isSE = props.is_se_london || CONFIG.seBorough.includes(props.borough_name);
        const value = props[theme.field];
        const displayValue = value !== undefined ? `${value}${theme.unit}` : 'N/A';
        const name = props.msoa_name || props.borough_name;
        const displayName = currentLevel === 'msoa' && name.length > 20 ? 
            name.substring(0, 18) + '...' : name;

        const li = document.createElement('li');
        li.className = isSE ? 'se-borough' : '';
        li.innerHTML = `
            <span class="rank">${index + 1}</span>
            <span class="borough-name" title="${name}">${displayName}</span>
            <span class="ratio">${displayValue}</span>
        `;
        
        li.addEventListener('click', () => {
            geojsonLayer.eachLayer(layer => {
                const layerName = layer.feature.properties.msoa_name || layer.feature.properties.borough_name;
                if (layerName === name) {
                    map.fitBounds(layer.getBounds(), { padding: [50, 50] });
                    layer.openPopup();
                }
            });
        });

        list.appendChild(li);
    });

    if (currentLevel === 'msoa' && sorted.length > 30) {
        const note = document.createElement('li');
        note.className = 'rankings-note';
        note.innerHTML = `<em>Showing top 30 of ${sorted.length} areas</em>`;
        list.appendChild(note);
    }
}

// Sample data fallbacks
function getSampleData() {
    return {
        type: 'FeatureCollection',
        features: [
            { type: 'Feature', properties: { borough_name: 'Bexley', affordability_ratio: 9.2, is_se_london: true, tube_distance_km: 12, transport_score: 25, born_local_pct: 55 }, geometry: { type: 'Polygon', coordinates: [[[0.1, 51.45], [0.2, 51.45], [0.2, 51.5], [0.1, 51.5], [0.1, 51.45]]] } },
            { type: 'Feature', properties: { borough_name: 'Greenwich', affordability_ratio: 10.8, is_se_london: true, tube_distance_km: 5, transport_score: 40, born_local_pct: 42 }, geometry: { type: 'Polygon', coordinates: [[[0.0, 51.45], [0.1, 51.45], [0.1, 51.5], [0.0, 51.5], [0.0, 51.45]]] } },
            { type: 'Feature', properties: { borough_name: 'Lewisham', affordability_ratio: 11.2, is_se_london: true, tube_distance_km: 4, transport_score: 45, born_local_pct: 38 }, geometry: { type: 'Polygon', coordinates: [[[-0.05, 51.43], [0.0, 51.43], [0.0, 51.48], [-0.05, 51.48], [-0.05, 51.43]]] } },
            { type: 'Feature', properties: { borough_name: 'Westminster', affordability_ratio: 22.5, is_se_london: false, tube_distance_km: 0.3, transport_score: 95, born_local_pct: 12 }, geometry: { type: 'Polygon', coordinates: [[[-0.2, 51.49], [-0.12, 51.49], [-0.12, 51.54], [-0.2, 51.54], [-0.2, 51.49]]] } },
        ]
    };
}

function getSampleStats() {
    return {
        se_london: { avg_ratio: 11.5 },
        london_overall: { avg_ratio: 13.2 },
        comparison: { se_london_savings_percent: -15 },
        transport_analysis: {
            se_london: { pct_with_tube_nearby: 17, avg_born_locally_pct: 42 }
        }
    };
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', initMap);
