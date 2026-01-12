"""
Add amenity density data (pubs, cafes, restaurants) from OpenStreetMap.

Theory: SE London may have fewer 'lifestyle' amenities, making it less
desirable for young professionals who drive up prices elsewhere.
"""

import json
import requests
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from shapely.geometry import Point, shape
import time

DATA_DIR = Path(__file__).parent.parent / "data"

# Overpass API endpoint
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def fetch_amenities_for_bbox(south, west, north, east, amenity_type):
    """
    Fetch amenities from OpenStreetMap using Overpass API.
    """
    query = f"""
    [out:json][timeout:60];
    (
      node["amenity"="{amenity_type}"]({south},{west},{north},{east});
      way["amenity"="{amenity_type}"]({south},{west},{north},{east});
    );
    out center;
    """
    
    try:
        response = requests.post(OVERPASS_URL, data={"data": query}, timeout=120)
        if response.status_code == 200:
            data = response.json()
            return data.get("elements", [])
        else:
            print(f"  API returned {response.status_code}")
            return []
    except Exception as e:
        print(f"  Error fetching {amenity_type}: {e}")
        return []


def extract_coordinates(element):
    """Extract lat/lon from OSM element (handles nodes and ways)."""
    if element["type"] == "node":
        return element["lat"], element["lon"]
    elif element["type"] == "way" and "center" in element:
        return element["center"]["lat"], element["center"]["lon"]
    return None, None


def count_amenities_in_msoa(msoa_geometry, amenity_points):
    """Count how many amenity points fall within an MSOA polygon."""
    count = 0
    for lat, lon in amenity_points:
        point = Point(lon, lat)
        if msoa_geometry.contains(point):
            count += 1
    return count


def main():
    print("=" * 60)
    print("Adding Amenity Density Data from OpenStreetMap")
    print("=" * 60)
    
    # Load existing MSOA data
    msoa_file = DATA_DIR / "london_affordability_msoa.geojson"
    print(f"Loading {msoa_file}...")
    gdf = gpd.read_file(msoa_file)
    print(f"  Loaded {len(gdf)} MSOAs")
    
    # Get London bounding box (with buffer)
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    west, south, east, north = bounds[0] - 0.05, bounds[1] - 0.05, bounds[2] + 0.05, bounds[3] + 0.05
    print(f"  London bbox: {south:.3f},{west:.3f} to {north:.3f},{east:.3f}")
    
    # Amenity types to fetch
    amenity_types = {
        "pub": "Pubs",
        "cafe": "Cafes", 
        "restaurant": "Restaurants",
        "bar": "Bars",
        "fast_food": "Fast Food",
    }
    
    all_amenities = {}
    
    for amenity_key, amenity_name in amenity_types.items():
        print(f"\nFetching {amenity_name}...")
        elements = fetch_amenities_for_bbox(south, west, north, east, amenity_key)
        
        # Extract coordinates
        points = []
        for el in elements:
            lat, lon = extract_coordinates(el)
            if lat and lon:
                points.append((lat, lon))
        
        all_amenities[amenity_key] = points
        print(f"  Found {len(points)} {amenity_name.lower()}")
        
        # Be nice to the API
        time.sleep(2)
    
    # Calculate counts per MSOA
    print("\n" + "=" * 40)
    print("Counting amenities per MSOA...")
    print("=" * 40)
    
    # Initialize columns
    for amenity_key in amenity_types.keys():
        gdf[f"{amenity_key}_count"] = 0
    
    # Count amenities in each MSOA
    for idx, row in gdf.iterrows():
        if idx % 100 == 0:
            print(f"  Processing MSOA {idx + 1}/{len(gdf)}...")
        
        geom = row.geometry
        for amenity_key, points in all_amenities.items():
            count = count_amenities_in_msoa(geom, points)
            gdf.at[idx, f"{amenity_key}_count"] = count
    
    # Calculate totals and density
    gdf["total_amenities"] = (
        gdf["pub_count"] + 
        gdf["cafe_count"] + 
        gdf["restaurant_count"] + 
        gdf["bar_count"] +
        gdf["fast_food_count"]
    )
    
    # Calculate area in km² for density
    gdf_projected = gdf.to_crs(epsg=27700)  # British National Grid
    gdf["area_km2"] = gdf_projected.geometry.area / 1_000_000
    gdf["amenity_density"] = (gdf["total_amenities"] / gdf["area_km2"]).round(1)
    
    # Lifestyle score (pubs + cafes + restaurants + bars, excluding fast food)
    gdf["lifestyle_amenities"] = (
        gdf["pub_count"] + 
        gdf["cafe_count"] + 
        gdf["restaurant_count"] + 
        gdf["bar_count"]
    )
    gdf["lifestyle_density"] = (gdf["lifestyle_amenities"] / gdf["area_km2"]).round(1)
    
    # Analysis
    print("\n" + "=" * 40)
    print("AMENITY ANALYSIS")
    print("=" * 40)
    
    se_london = gdf[gdf["is_se_london"] == True]
    rest_london = gdf[gdf["is_se_london"] == False]
    
    print(f"\n{'Metric':<30} {'SE London':>12} {'Rest':>12}")
    print("-" * 54)
    print(f"{'Total Pubs':<30} {se_london['pub_count'].sum():>12,} {rest_london['pub_count'].sum():>12,}")
    print(f"{'Total Cafes':<30} {se_london['cafe_count'].sum():>12,} {rest_london['cafe_count'].sum():>12,}")
    print(f"{'Total Restaurants':<30} {se_london['restaurant_count'].sum():>12,} {rest_london['restaurant_count'].sum():>12,}")
    print(f"{'Total Bars':<30} {se_london['bar_count'].sum():>12,} {rest_london['bar_count'].sum():>12,}")
    print(f"{'Avg Lifestyle Density/km²':<30} {se_london['lifestyle_density'].mean():>12.1f} {rest_london['lifestyle_density'].mean():>12.1f}")
    print(f"{'Avg Amenity Density/km²':<30} {se_london['amenity_density'].mean():>12.1f} {rest_london['amenity_density'].mean():>12.1f}")
    
    # Correlations
    print("\n" + "=" * 40)
    print("CORRELATIONS WITH AFFORDABILITY")
    print("=" * 40)
    
    corr_lifestyle = gdf["affordability_ratio"].corr(gdf["lifestyle_density"])
    corr_total = gdf["affordability_ratio"].corr(gdf["amenity_density"])
    corr_pubs = gdf["affordability_ratio"].corr(gdf["pub_count"])
    
    print(f"Affordability vs Lifestyle Density: {corr_lifestyle:.3f}")
    print(f"Affordability vs Total Amenity Density: {corr_total:.3f}")
    print(f"Affordability vs Pub Count: {corr_pubs:.3f}")
    print("(Positive = more amenities correlates with higher prices)")
    
    # Save updated GeoJSON
    output_path = DATA_DIR / "london_affordability_msoa.geojson"
    print(f"\nSaving to {output_path}...")
    gdf.to_file(output_path, driver="GeoJSON")
    
    # Update summary stats
    stats_path = DATA_DIR / "summary_stats_msoa.json"
    with open(stats_path, "r") as f:
        stats = json.load(f)
    
    stats["amenity_analysis"] = {
        "correlations": {
            "affordability_vs_lifestyle_density": round(corr_lifestyle, 3),
            "affordability_vs_amenity_density": round(corr_total, 3),
        },
        "se_london": {
            "total_pubs": int(se_london["pub_count"].sum()),
            "total_cafes": int(se_london["cafe_count"].sum()),
            "total_restaurants": int(se_london["restaurant_count"].sum()),
            "avg_lifestyle_density": round(se_london["lifestyle_density"].mean(), 1),
        },
        "rest_of_london": {
            "total_pubs": int(rest_london["pub_count"].sum()),
            "total_cafes": int(rest_london["cafe_count"].sum()),
            "total_restaurants": int(rest_london["restaurant_count"].sum()),
            "avg_lifestyle_density": round(rest_london["lifestyle_density"].mean(), 1),
        },
    }
    
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    
    print(f"Updated {stats_path}")
    print("\n" + "=" * 60)
    print("Complete! New fields added:")
    print("  - pub_count, cafe_count, restaurant_count, bar_count, fast_food_count")
    print("  - total_amenities, amenity_density")
    print("  - lifestyle_amenities, lifestyle_density")
    print("=" * 60)


if __name__ == "__main__":
    main()
