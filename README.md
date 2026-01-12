# Southeast London Affordability Map

An interactive map exploring housing affordability in Southeast London using ONS (Office for National Statistics) data.

## Features

- Interactive choropleth map showing affordability ratios by area
- Comparison of house prices vs median earnings
- Tooltips with detailed statistics per area
- Filter controls for different metrics

## Tech Stack

- **Data Pipeline**: Python (pandas, geopandas, requests)
- **Mapping**: Leaflet.js
- **Hosting**: GitHub Pages

## Project Structure

```
geographic/
├── data/                 # Processed GeoJSON and CSV files
├── scripts/              # Python data processing scripts
├── src/                  # Frontend HTML/CSS/JS
│   ├── index.html
│   ├── css/
│   └── js/
├── requirements.txt      # Python dependencies
└── README.md
```

## Setup

### 1. Install Python Dependencies

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Fetch and Process ONS Data

```bash
python scripts/fetch_ons_data.py
```

### 3. View the Map Locally

Open `src/index.html` in your browser, or use a local server:

```bash
python -m http.server 8000 --directory src
```

Then visit http://localhost:8000

## Data Sources

- [ONS House Price Statistics for Small Areas](https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/hpaboroughofenglandandwales)
- [ONS Annual Survey of Hours and Earnings](https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours)
- [ONS Open Geography Portal](https://geoportal.statistics.gov.uk/) - Boundary data

## Deployment

This project is designed for GitHub Pages:

1. Push to GitHub
2. Go to Settings → Pages
3. Select "Deploy from a branch" → main → /src
4. Your map will be live at `https://username.github.io/geographic`

## License

MIT
