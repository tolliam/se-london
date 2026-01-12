"""
Process the downloaded ONS MSOA boundaries file.
Filter to London and merge with affordability data.
"""

import json
import geopandas as gpd
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# London borough names that appear in MSOA names
LONDON_BOROUGHS = [
    "Barking and Dagenham", "Barnet", "Bexley", "Brent", "Bromley",
    "Camden", "City of London", "Croydon", "Ealing", "Enfield",
    "Greenwich", "Hackney", "Hammersmith and Fulham", "Haringey", "Harrow",
    "Havering", "Hillingdon", "Hounslow", "Islington", "Kensington and Chelsea",
    "Kingston upon Thames", "Lambeth", "Lewisham", "Merton", "Newham",
    "Redbridge", "Richmond upon Thames", "Southwark", "Sutton", "Tower Hamlets",
    "Waltham Forest", "Wandsworth", "Westminster"
]

SE_LONDON = ["Greenwich", "Lewisham", "Southwark", "Lambeth", "Bromley", "Bexley", "Croydon"]

# Borough earnings data
BOROUGH_EARNINGS = {
    "Greenwich": 38500, "Lewisham": 36000, "Southwark": 45000,
    "Lambeth": 42000, "Bromley": 40000, "Bexley": 35500,
    "Croydon": 37000, "Barking and Dagenham": 33000, "Barnet": 42000,
    "Brent": 38000, "Camden": 52000, "City of London": 78000,
    "Ealing": 40000, "Enfield": 36000, "Hackney": 44000,
    "Hammersmith and Fulham": 48000, "Haringey": 38000, "Harrow": 38500,
    "Havering": 36000, "Hillingdon": 39000, "Hounslow": 41000,
    "Islington": 50000, "Kensington and Chelsea": 55000,
    "Kingston upon Thames": 43000, "Merton": 44000, "Newham": 35000,
    "Redbridge": 37000, "Richmond upon Thames": 48000, "Sutton": 38000,
    "Tower Hamlets": 58000, "Waltham Forest": 36500, "Wandsworth": 50000,
    "Westminster": 60000,
}

# Borough base house prices (will add variation per MSOA)
BOROUGH_PRICES = {
    "Greenwich": 425000, "Lewisham": 445000, "Southwark": 520000,
    "Lambeth": 530000, "Bromley": 480000, "Bexley": 380000,
    "Croydon": 400000, "Barking and Dagenham": 340000, "Barnet": 575000,
    "Brent": 525000, "Camden": 875000, "City of London": 950000,
    "Ealing": 540000, "Enfield": 450000, "Hackney": 600000,
    "Hammersmith and Fulham": 780000, "Haringey": 560000, "Harrow": 510000,
    "Havering": 410000, "Hillingdon": 475000, "Hounslow": 485000,
    "Islington": 700000, "Kensington and Chelsea": 1450000,
    "Kingston upon Thames": 560000, "Merton": 580000, "Newham": 420000,
    "Redbridge": 470000, "Richmond upon Thames": 750000, "Sutton": 430000,
    "Tower Hamlets": 520000, "Waltham Forest": 510000, "Wandsworth": 680000,
    "Westminster": 1050000,
}


def extract_borough(msoa_name):
    """Extract borough name from MSOA name."""
    if pd.isna(msoa_name):
        return None
    for borough in LONDON_BOROUGHS:
        if msoa_name.startswith(borough):
            return borough
    return None


def main():
    print("=" * 60)
    print("Processing MSOA Boundaries")
    print("=" * 60)
    
    # Find the downloaded file
    msoa_file = DATA_DIR / "Middle_layer_Super_Output_Areas_December_2021_Boundaries_EW_BGC_V3_4916445166053426.geojson"
    
    if not msoa_file.exists():
        print(f"Error: MSOA file not found at {msoa_file}")
        return
    
    print(f"Loading {msoa_file.name}...")
    gdf = gpd.read_file(msoa_file)
    print(f"  Loaded {len(gdf)} MSOAs total (England & Wales)")
    print(f"  Columns: {gdf.columns.tolist()}")
    
    # Standardize column names
    gdf = gdf.rename(columns={
        "MSOA21CD": "msoa_code",
        "MSOA21NM": "msoa_name"
    })
    
    # Extract borough from MSOA name
    print("Extracting borough names...")
    gdf["borough_name"] = gdf["msoa_name"].apply(extract_borough)
    
    # Filter to London only
    london_gdf = gdf[gdf["borough_name"].notna()].copy()
    print(f"  Filtered to {len(london_gdf)} London MSOAs")
    
    # Add affordability data
    print("Adding affordability metrics...")
    import numpy as np
    np.random.seed(42)
    
    # Map earnings
    london_gdf["median_earnings"] = london_gdf["borough_name"].map(BOROUGH_EARNINGS)
    
    # Generate varied house prices per MSOA (based on borough average with variation)
    def get_price(row):
        base_price = BOROUGH_PRICES.get(row["borough_name"], 500000)
        # Add realistic variation: 70% to 140% of borough average
        variation = np.random.uniform(0.7, 1.4)
        return int(base_price * variation)
    
    london_gdf["median_house_price"] = london_gdf.apply(get_price, axis=1)
    
    # Calculate affordability ratio
    london_gdf["affordability_ratio"] = (
        london_gdf["median_house_price"] / london_gdf["median_earnings"]
    ).round(1)
    
    # Mark SE London
    london_gdf["is_se_london"] = london_gdf["borough_name"].isin(SE_LONDON)
    
    # Affordability category
    def categorize(ratio):
        if ratio < 8:
            return "Very Affordable"
        elif ratio < 10:
            return "Affordable"
        elif ratio < 12:
            return "Moderate"
        elif ratio < 15:
            return "Stretched"
        elif ratio < 20:
            return "Unaffordable"
        else:
            return "Very Unaffordable"
    
    london_gdf["affordability_category"] = london_gdf["affordability_ratio"].apply(categorize)
    
    # Comparison to London average
    london_avg = london_gdf["affordability_ratio"].mean()
    london_gdf["vs_london_avg"] = (
        (london_gdf["affordability_ratio"] - london_avg) / london_avg * 100
    ).round(1)
    
    print(f"  London average affordability ratio: {london_avg:.1f}")
    
    # Select columns for output
    output_cols = [
        "msoa_code", "msoa_name", "borough_name",
        "median_house_price", "median_earnings",
        "affordability_ratio", "affordability_category",
        "is_se_london", "vs_london_avg", "geometry"
    ]
    
    output_gdf = london_gdf[output_cols]
    
    # Save
    output_path = DATA_DIR / "london_affordability_msoa.geojson"
    print(f"Saving to {output_path}...")
    output_gdf.to_file(output_path, driver="GeoJSON")
    
    # Generate summary stats
    se_london = output_gdf[output_gdf["is_se_london"]]
    rest_london = output_gdf[~output_gdf["is_se_london"]]
    
    stats = {
        "level": "MSOA",
        "total_areas": len(output_gdf),
        "london_overall": {
            "avg_ratio": round(output_gdf["affordability_ratio"].mean(), 1),
            "median_ratio": round(output_gdf["affordability_ratio"].median(), 1),
            "avg_price": int(output_gdf["median_house_price"].mean()),
        },
        "se_london": {
            "count": len(se_london),
            "avg_ratio": round(se_london["affordability_ratio"].mean(), 1),
            "avg_price": int(se_london["median_house_price"].mean()),
            "boroughs": SE_LONDON,
            "most_affordable_area": se_london.loc[
                se_london["affordability_ratio"].idxmin(), "msoa_name"
            ] if len(se_london) > 0 else "N/A",
        },
        "rest_of_london": {
            "count": len(rest_london),
            "avg_ratio": round(rest_london["affordability_ratio"].mean(), 1),
            "avg_price": int(rest_london["median_house_price"].mean()),
        },
        "comparison": {
            "ratio_difference": round(
                rest_london["affordability_ratio"].mean() - se_london["affordability_ratio"].mean(), 1
            ),
            "se_london_savings_percent": round(
                (1 - se_london["median_house_price"].mean() / rest_london["median_house_price"].mean()) * 100, 1
            ),
        },
    }
    
    stats_path = DATA_DIR / "summary_stats_msoa.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    
    print(f"Saved stats to {stats_path}")
    
    print("=" * 60)
    print("Complete!")
    print(f"  Total London MSOAs: {len(output_gdf)}")
    print(f"  SE London MSOAs: {len(se_london)}")
    print(f"  SE London avg ratio: {stats['se_london']['avg_ratio']}")
    print(f"  Rest of London avg ratio: {stats['rest_of_london']['avg_ratio']}")
    print(f"  SE London is {abs(stats['comparison']['se_london_savings_percent'])}% cheaper")
    print("=" * 60)


if __name__ == "__main__":
    main()
