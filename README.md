# 🗺️ Why is SE London Cheaper?

An interactive map exploring housing affordability, transport isolation, and population stability in Southeast London using ONS (Office for National Statistics) data.

**[View Live Map →](https://tolliam.github.io/se-london/)**

## Features

- Interactive choropleth map showing affordability ratios by MSOA
- Comparison of house prices vs median earnings
- Transport connectivity analysis (tube/rail station distances)
- Population stability metrics ("born locally" rates)
- Tooltips with detailed statistics per area

## Tech Stack

- **Data Pipeline**: Python (pandas, geopandas, requests)
- **Mapping**: Leaflet.js
- **Hosting**: GitHub Pages (via Actions)

## Project Structure

```
se-london/
├── data/                 # Processed GeoJSON and statistics
├── scripts/              # Python data processing scripts
├── src/                  # Frontend HTML/CSS/JS
│   ├── index.html
│   ├── css/
│   └── js/
├── .github/workflows/    # GitHub Actions deployment
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

This project deploys automatically to GitHub Pages via GitHub Actions when you push to `main`.

The live site is available at: https://tolliam.github.io/se-london/

## License

MIT
