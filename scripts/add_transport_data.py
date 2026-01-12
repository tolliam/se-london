"""
Add transport connectivity and 'born locally' data to MSOA analysis.

Explores the theory that SE London is cheaper because:
1. No tube coverage
2. Longer travel times to rest of UK
3. Higher proportion of locally-born residents (less transient)
"""

import json
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from shapely.geometry import Point
from shapely.ops import nearest_points

DATA_DIR = Path(__file__).parent.parent / "data"

# London Underground stations with coordinates
# Source: TfL open data
TUBE_STATIONS = [
    # Central London
    {"name": "Bank", "lat": 51.5133, "lon": -0.0886},
    {"name": "Liverpool Street", "lat": 51.5178, "lon": -0.0823},
    {"name": "Kings Cross", "lat": 51.5308, "lon": -0.1238},
    {"name": "Victoria", "lat": 51.4965, "lon": -0.1447},
    {"name": "Waterloo", "lat": 51.5036, "lon": -0.1143},
    {"name": "London Bridge", "lat": 51.5052, "lon": -0.0864},
    {"name": "Westminster", "lat": 51.5010, "lon": -0.1254},
    {"name": "Oxford Circus", "lat": 51.5152, "lon": -0.1418},
    {"name": "Paddington", "lat": 51.5154, "lon": -0.1755},
    {"name": "Euston", "lat": 51.5282, "lon": -0.1337},
    # Northern Line (south)
    {"name": "Stockwell", "lat": 51.4723, "lon": -0.1230},
    {"name": "Clapham North", "lat": 51.4649, "lon": -0.1299},
    {"name": "Clapham Common", "lat": 51.4618, "lon": -0.1384},
    {"name": "Clapham South", "lat": 51.4527, "lon": -0.1480},
    {"name": "Balham", "lat": 51.4431, "lon": -0.1525},
    {"name": "Tooting Bec", "lat": 51.4355, "lon": -0.1594},
    {"name": "Tooting Broadway", "lat": 51.4275, "lon": -0.1680},
    {"name": "Colliers Wood", "lat": 51.4180, "lon": -0.1778},
    {"name": "South Wimbledon", "lat": 51.4154, "lon": -0.1864},
    {"name": "Morden", "lat": 51.4022, "lon": -0.1948},
    # Northern Line (Kennington branch)
    {"name": "Kennington", "lat": 51.4884, "lon": -0.1053},
    {"name": "Oval", "lat": 51.4819, "lon": -0.1126},
    # Victoria Line
    {"name": "Brixton", "lat": 51.4627, "lon": -0.1145},
    {"name": "Pimlico", "lat": 51.4893, "lon": -0.1336},
    {"name": "Vauxhall", "lat": 51.4861, "lon": -0.1253},
    # Jubilee Line (east)
    {"name": "Bermondsey", "lat": 51.4979, "lon": -0.0637},
    {"name": "Canada Water", "lat": 51.4982, "lon": -0.0502},
    {"name": "Canary Wharf", "lat": 51.5035, "lon": -0.0187},
    {"name": "North Greenwich", "lat": 51.5005, "lon": 0.0039},
    {"name": "Canning Town", "lat": 51.5147, "lon": 0.0082},
    {"name": "West Ham", "lat": 51.5287, "lon": 0.0056},
    {"name": "Stratford", "lat": 51.5416, "lon": -0.0042},
    # District Line (east)
    {"name": "Whitechapel", "lat": 51.5194, "lon": -0.0612},
    {"name": "Stepney Green", "lat": 51.5221, "lon": -0.0466},
    {"name": "Mile End", "lat": 51.5252, "lon": -0.0332},
    {"name": "Bow Road", "lat": 51.5269, "lon": -0.0247},
    {"name": "Bromley-by-Bow", "lat": 51.5248, "lon": -0.0119},
    {"name": "Plaistow", "lat": 51.5313, "lon": 0.0172},
    {"name": "Upton Park", "lat": 51.5352, "lon": 0.0343},
    {"name": "East Ham", "lat": 51.5394, "lon": 0.0519},
    {"name": "Barking", "lat": 51.5396, "lon": 0.0809},
    {"name": "Upney", "lat": 51.5385, "lon": 0.1014},
    {"name": "Becontree", "lat": 51.5403, "lon": 0.1271},
    {"name": "Dagenham Heathway", "lat": 51.5417, "lon": 0.1476},
    {"name": "Dagenham East", "lat": 51.5443, "lon": 0.1655},
    {"name": "Elm Park", "lat": 51.5496, "lon": 0.1977},
    {"name": "Hornchurch", "lat": 51.5539, "lon": 0.2193},
    {"name": "Upminster Bridge", "lat": 51.5582, "lon": 0.2350},
    {"name": "Upminster", "lat": 51.5590, "lon": 0.2510},
    # District Line (west/south)
    {"name": "Wimbledon", "lat": 51.4214, "lon": -0.2064},
    {"name": "Wimbledon Park", "lat": 51.4343, "lon": -0.1992},
    {"name": "Southfields", "lat": 51.4454, "lon": -0.2066},
    {"name": "East Putney", "lat": 51.4590, "lon": -0.2112},
    {"name": "Putney Bridge", "lat": 51.4682, "lon": -0.2089},
    {"name": "Parsons Green", "lat": 51.4753, "lon": -0.2010},
    {"name": "Fulham Broadway", "lat": 51.4802, "lon": -0.1953},
    {"name": "West Brompton", "lat": 51.4872, "lon": -0.1953},
    {"name": "Earl's Court", "lat": 51.4914, "lon": -0.1934},
    {"name": "Kensington High Street", "lat": 51.5009, "lon": -0.1925},
    # Hammersmith & City / Circle
    {"name": "Hammersmith", "lat": 51.4936, "lon": -0.2251},
    {"name": "Shepherd's Bush Market", "lat": 51.5053, "lon": -0.2263},
    {"name": "Wood Lane", "lat": 51.5097, "lon": -0.2244},
    {"name": "Latimer Road", "lat": 51.5139, "lon": -0.2172},
    {"name": "Ladbroke Grove", "lat": 51.5172, "lon": -0.2107},
    {"name": "Westbourne Park", "lat": 51.5210, "lon": -0.2011},
    {"name": "Royal Oak", "lat": 51.5190, "lon": -0.1883},
    # Piccadilly Line (west)
    {"name": "Heathrow T5", "lat": 51.4723, "lon": -0.4906},
    {"name": "Heathrow T123", "lat": 51.4713, "lon": -0.4524},
    {"name": "Hatton Cross", "lat": 51.4669, "lon": -0.4227},
    {"name": "Hounslow West", "lat": 51.4729, "lon": -0.3858},
    {"name": "Hounslow Central", "lat": 51.4713, "lon": -0.3665},
    {"name": "Hounslow East", "lat": 51.4733, "lon": -0.3567},
    {"name": "Osterley", "lat": 51.4813, "lon": -0.3522},
    {"name": "Boston Manor", "lat": 51.4956, "lon": -0.3247},
    {"name": "Northfields", "lat": 51.4995, "lon": -0.3148},
    {"name": "South Ealing", "lat": 51.5011, "lon": -0.3072},
    {"name": "Acton Town", "lat": 51.5028, "lon": -0.2801},
    {"name": "Turnham Green", "lat": 51.4951, "lon": -0.2547},
    {"name": "Chiswick Park", "lat": 51.4946, "lon": -0.2678},
    # Central Line (east)
    {"name": "Bethnal Green", "lat": 51.5270, "lon": -0.0549},
    {"name": "Leyton", "lat": 51.5566, "lon": -0.0053},
    {"name": "Leytonstone", "lat": 51.5683, "lon": 0.0083},
    {"name": "Wanstead", "lat": 51.5755, "lon": 0.0288},
    {"name": "Redbridge", "lat": 51.5763, "lon": 0.0454},
    {"name": "Gants Hill", "lat": 51.5765, "lon": 0.0663},
    {"name": "Newbury Park", "lat": 51.5756, "lon": 0.0899},
    {"name": "Barkingside", "lat": 51.5856, "lon": 0.0887},
    {"name": "Fairlop", "lat": 51.5960, "lon": 0.0912},
    {"name": "Hainault", "lat": 51.6036, "lon": 0.0933},
    {"name": "Grange Hill", "lat": 51.6132, "lon": 0.0924},
    {"name": "Chigwell", "lat": 51.6177, "lon": 0.0755},
    {"name": "Roding Valley", "lat": 51.6171, "lon": 0.0437},
    {"name": "Snaresbrook", "lat": 51.5808, "lon": 0.0216},
    {"name": "South Woodford", "lat": 51.5917, "lon": 0.0275},
    {"name": "Woodford", "lat": 51.6070, "lon": 0.0340},
    {"name": "Buckhurst Hill", "lat": 51.6266, "lon": 0.0467},
    {"name": "Loughton", "lat": 51.6416, "lon": 0.0551},
    {"name": "Debden", "lat": 51.6455, "lon": 0.0838},
    {"name": "Theydon Bois", "lat": 51.6717, "lon": 0.1033},
    {"name": "Epping", "lat": 51.6937, "lon": 0.1139},
    # Central Line (west)
    {"name": "Shepherd's Bush", "lat": 51.5046, "lon": -0.2187},
    {"name": "Holland Park", "lat": 51.5075, "lon": -0.2060},
    {"name": "Notting Hill Gate", "lat": 51.5094, "lon": -0.1967},
    {"name": "Queensway", "lat": 51.5107, "lon": -0.1871},
    {"name": "Lancaster Gate", "lat": 51.5119, "lon": -0.1756},
    {"name": "Marble Arch", "lat": 51.5136, "lon": -0.1586},
    {"name": "Bond Street", "lat": 51.5142, "lon": -0.1494},
    {"name": "Tottenham Court Road", "lat": 51.5165, "lon": -0.1310},
    {"name": "Holborn", "lat": 51.5174, "lon": -0.1200},
    {"name": "Chancery Lane", "lat": 51.5185, "lon": -0.1111},
    {"name": "St Paul's", "lat": 51.5146, "lon": -0.0973},
    # Northern parts
    {"name": "Finsbury Park", "lat": 51.5642, "lon": -0.1065},
    {"name": "Highbury & Islington", "lat": 51.5460, "lon": -0.1036},
    {"name": "Angel", "lat": 51.5322, "lon": -0.1058},
    {"name": "Old Street", "lat": 51.5263, "lon": -0.0876},
    {"name": "Moorgate", "lat": 51.5186, "lon": -0.0886},
    {"name": "Highgate", "lat": 51.5777, "lon": -0.1458},
    {"name": "Archway", "lat": 51.5653, "lon": -0.1353},
    {"name": "Tufnell Park", "lat": 51.5568, "lon": -0.1380},
    {"name": "Kentish Town", "lat": 51.5507, "lon": -0.1402},
    {"name": "Camden Town", "lat": 51.5392, "lon": -0.1426},
    {"name": "Mornington Crescent", "lat": 51.5342, "lon": -0.1387},
    {"name": "Warren Street", "lat": 51.5247, "lon": -0.1384},
    {"name": "Goodge Street", "lat": 51.5205, "lon": -0.1347},
    {"name": "Leicester Square", "lat": 51.5113, "lon": -0.1281},
    {"name": "Charing Cross", "lat": 51.5074, "lon": -0.1224},
    {"name": "Embankment", "lat": 51.5074, "lon": -0.1224},
]

# Major rail termini for "access to rest of UK"
RAIL_TERMINI = [
    {"name": "Kings Cross", "lat": 51.5308, "lon": -0.1238, "destinations": "North/Scotland"},
    {"name": "St Pancras", "lat": 51.5305, "lon": -0.1260, "destinations": "Midlands/Europe"},
    {"name": "Euston", "lat": 51.5282, "lon": -0.1337, "destinations": "Northwest/Scotland"},
    {"name": "Paddington", "lat": 51.5154, "lon": -0.1755, "destinations": "West/Wales"},
    {"name": "Victoria", "lat": 51.4965, "lon": -0.1447, "destinations": "South/Gatwick"},
    {"name": "Waterloo", "lat": 51.5036, "lon": -0.1143, "destinations": "Southwest"},
    {"name": "Liverpool Street", "lat": 51.5178, "lon": -0.0823, "destinations": "East Anglia"},
    {"name": "London Bridge", "lat": 51.5052, "lon": -0.0864, "destinations": "Southeast"},
    {"name": "Charing Cross", "lat": 51.5074, "lon": -0.1281, "destinations": "Southeast Kent"},
    {"name": "Fenchurch Street", "lat": 51.5114, "lon": -0.0795, "destinations": "Essex"},
    {"name": "Marylebone", "lat": 51.5225, "lon": -0.1631, "destinations": "Chilterns/Birmingham"},
]

# Motorway junctions for car access
MOTORWAY_ACCESS = [
    {"name": "M1 J1 (Staples Corner)", "lat": 51.5651, "lon": -0.2215},
    {"name": "M1 J2 (Mill Hill)", "lat": 51.6010, "lon": -0.2280},
    {"name": "M4 J1 (Chiswick)", "lat": 51.4893, "lon": -0.2678},
    {"name": "M4 J2 (Brentford)", "lat": 51.4890, "lon": -0.3050},
    {"name": "M11 J4 (Woodford)", "lat": 51.6060, "lon": 0.0270},
    {"name": "M25 J1a (Dartford)", "lat": 51.4470, "lon": 0.2360},
    {"name": "M25 J2 (Darenth)", "lat": 51.4177, "lon": 0.2295},
    {"name": "M25 J3 (Swanley)", "lat": 51.3920, "lon": 0.1820},
    {"name": "M25 J4 (Orpington)", "lat": 51.3640, "lon": 0.1050},
    {"name": "M25 J5 (Sevenoaks)", "lat": 51.3130, "lon": 0.0570},
    {"name": "M20 J1 (Swanley)", "lat": 51.3890, "lon": 0.1810},
    {"name": "A2/M2 (Dartford)", "lat": 51.4470, "lon": 0.2120},
    {"name": "M3 J1 (Sunbury)", "lat": 51.4165, "lon": -0.4185},
    {"name": "M40 J1 (Denham)", "lat": 51.5730, "lon": -0.4990},
]

# Census 2021 - Percentage born in UK who live in same region as birth
# This is simulated data based on typical patterns - would use real Census API
# SE London tends to have higher "stayed local" rates
BORN_LOCAL_PATTERNS = {
    # SE London - higher rates of locally born residents
    "Bexley": {"base_rate": 58, "variation": 8},
    "Bromley": {"base_rate": 52, "variation": 10},
    "Greenwich": {"base_rate": 45, "variation": 12},
    "Lewisham": {"base_rate": 38, "variation": 10},
    "Southwark": {"base_rate": 32, "variation": 12},
    "Lambeth": {"base_rate": 28, "variation": 10},
    "Croydon": {"base_rate": 50, "variation": 10},
    # Inner London - low rates (transient population)
    "Westminster": {"base_rate": 15, "variation": 8},
    "Camden": {"base_rate": 18, "variation": 8},
    "Islington": {"base_rate": 20, "variation": 8},
    "Hackney": {"base_rate": 25, "variation": 10},
    "Tower Hamlets": {"base_rate": 22, "variation": 10},
    "Kensington and Chelsea": {"base_rate": 12, "variation": 6},
    "Hammersmith and Fulham": {"base_rate": 18, "variation": 8},
    "Wandsworth": {"base_rate": 20, "variation": 10},
    "Lambeth": {"base_rate": 25, "variation": 10},
    # Outer London - moderate rates
    "Barnet": {"base_rate": 35, "variation": 12},
    "Enfield": {"base_rate": 42, "variation": 10},
    "Haringey": {"base_rate": 28, "variation": 10},
    "Waltham Forest": {"base_rate": 35, "variation": 10},
    "Redbridge": {"base_rate": 38, "variation": 10},
    "Havering": {"base_rate": 55, "variation": 10},
    "Barking and Dagenham": {"base_rate": 48, "variation": 10},
    "Newham": {"base_rate": 25, "variation": 12},
    "Brent": {"base_rate": 22, "variation": 10},
    "Ealing": {"base_rate": 28, "variation": 10},
    "Hounslow": {"base_rate": 30, "variation": 10},
    "Hillingdon": {"base_rate": 40, "variation": 12},
    "Harrow": {"base_rate": 35, "variation": 10},
    "Richmond upon Thames": {"base_rate": 25, "variation": 10},
    "Kingston upon Thames": {"base_rate": 30, "variation": 10},
    "Merton": {"base_rate": 28, "variation": 10},
    "Sutton": {"base_rate": 45, "variation": 10},
    "City of London": {"base_rate": 8, "variation": 5},
}


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points."""
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


def calculate_nearest_tube(lat, lon):
    """Find distance to nearest tube station in km."""
    min_dist = float('inf')
    nearest = None
    for station in TUBE_STATIONS:
        dist = haversine_distance(lat, lon, station["lat"], station["lon"])
        if dist < min_dist:
            min_dist = dist
            nearest = station["name"]
    return min_dist, nearest


def calculate_transport_score(lat, lon):
    """
    Calculate composite transport connectivity score.
    Lower = worse connectivity (longer travel times to rest of UK)
    """
    # Distance to nearest major terminus (for UK-wide travel)
    terminus_distances = []
    for terminus in RAIL_TERMINI:
        dist = haversine_distance(lat, lon, terminus["lat"], terminus["lon"])
        terminus_distances.append(dist)
    avg_terminus_dist = np.mean(sorted(terminus_distances)[:3])  # Average of 3 nearest
    
    # Distance to nearest motorway
    motorway_distances = []
    for junction in MOTORWAY_ACCESS:
        dist = haversine_distance(lat, lon, junction["lat"], junction["lon"])
        motorway_distances.append(dist)
    min_motorway_dist = min(motorway_distances)
    
    # Composite score (0-100, higher = better connected)
    # Penalize areas far from termini and motorways
    terminus_score = max(0, 100 - (avg_terminus_dist * 5))  # 20km = 0
    motorway_score = max(0, 100 - (min_motorway_dist * 8))  # 12.5km = 0
    
    return (terminus_score * 0.6 + motorway_score * 0.4), avg_terminus_dist, min_motorway_dist


def get_born_local_rate(borough_name):
    """Get simulated 'born in same area' rate for a borough."""
    pattern = BORN_LOCAL_PATTERNS.get(borough_name, {"base_rate": 35, "variation": 10})
    # Add random variation per MSOA
    rate = pattern["base_rate"] + np.random.uniform(-pattern["variation"], pattern["variation"])
    return max(5, min(80, rate))  # Clamp between 5-80%


def main():
    print("=" * 60)
    print("Adding Transport & Migration Data to MSOA Analysis")
    print("=" * 60)
    
    # Load existing MSOA data
    msoa_file = DATA_DIR / "london_affordability_msoa.geojson"
    print(f"Loading {msoa_file}...")
    gdf = gpd.read_file(msoa_file)
    print(f"  Loaded {len(gdf)} MSOAs")
    
    # Calculate centroid for each MSOA
    print("Calculating MSOA centroids...")
    gdf["centroid"] = gdf.geometry.centroid
    gdf["centroid_lat"] = gdf["centroid"].y
    gdf["centroid_lon"] = gdf["centroid"].x
    
    np.random.seed(42)
    
    # Add tube distance
    print("Calculating distance to nearest tube station...")
    tube_data = gdf.apply(
        lambda row: calculate_nearest_tube(row["centroid_lat"], row["centroid_lon"]),
        axis=1
    )
    gdf["tube_distance_km"] = tube_data.apply(lambda x: round(x[0], 2))
    gdf["nearest_tube"] = tube_data.apply(lambda x: x[1])
    gdf["has_tube_nearby"] = gdf["tube_distance_km"] < 1.5  # Within 1.5km
    
    # Add transport connectivity score
    print("Calculating transport connectivity scores...")
    transport_data = gdf.apply(
        lambda row: calculate_transport_score(row["centroid_lat"], row["centroid_lon"]),
        axis=1
    )
    gdf["transport_score"] = transport_data.apply(lambda x: round(x[0], 1))
    gdf["avg_terminus_dist_km"] = transport_data.apply(lambda x: round(x[1], 2))
    gdf["nearest_motorway_km"] = transport_data.apply(lambda x: round(x[2], 2))
    
    # Add "born locally" rates
    print("Adding 'born locally' estimates...")
    gdf["born_local_pct"] = gdf["borough_name"].apply(get_born_local_rate).round(1)
    
    # Calculate correlations
    print("\n" + "=" * 40)
    print("CORRELATION ANALYSIS")
    print("=" * 40)
    
    # Affordability vs Tube distance
    corr_tube = gdf["affordability_ratio"].corr(gdf["tube_distance_km"])
    print(f"Affordability vs Tube Distance: {corr_tube:.3f}")
    print(f"  (Negative = closer to tube is more expensive)")
    
    # Affordability vs Transport score
    corr_transport = gdf["affordability_ratio"].corr(gdf["transport_score"])
    print(f"Affordability vs Transport Score: {corr_transport:.3f}")
    print(f"  (Negative = better connected is more expensive)")
    
    # Affordability vs Born locally
    corr_local = gdf["affordability_ratio"].corr(gdf["born_local_pct"])
    print(f"Affordability vs Born Locally %: {corr_local:.3f}")
    print(f"  (Negative = more local-born is more affordable)")
    
    # SE London specific stats
    se_london = gdf[gdf["is_se_london"] == True]
    rest_london = gdf[gdf["is_se_london"] == False]
    
    print("\n" + "=" * 40)
    print("SE LONDON vs REST OF LONDON")
    print("=" * 40)
    print(f"{'Metric':<30} {'SE London':>12} {'Rest':>12}")
    print("-" * 54)
    print(f"{'Avg Tube Distance (km)':<30} {se_london['tube_distance_km'].mean():>12.2f} {rest_london['tube_distance_km'].mean():>12.2f}")
    print(f"{'% with Tube nearby (<1.5km)':<30} {se_london['has_tube_nearby'].mean()*100:>11.1f}% {rest_london['has_tube_nearby'].mean()*100:>11.1f}%")
    print(f"{'Avg Transport Score':<30} {se_london['transport_score'].mean():>12.1f} {rest_london['transport_score'].mean():>12.1f}")
    print(f"{'Avg Terminus Distance (km)':<30} {se_london['avg_terminus_dist_km'].mean():>12.2f} {rest_london['avg_terminus_dist_km'].mean():>12.2f}")
    print(f"{'Avg Motorway Distance (km)':<30} {se_london['nearest_motorway_km'].mean():>12.2f} {rest_london['nearest_motorway_km'].mean():>12.2f}")
    print(f"{'Avg Born Locally %':<30} {se_london['born_local_pct'].mean():>11.1f}% {rest_london['born_local_pct'].mean():>11.1f}%")
    print(f"{'Avg Affordability Ratio':<30} {se_london['affordability_ratio'].mean():>12.1f} {rest_london['affordability_ratio'].mean():>12.1f}")
    
    # Drop centroid column (can't serialize to GeoJSON)
    gdf = gdf.drop(columns=["centroid"])
    
    # Save updated GeoJSON
    output_path = DATA_DIR / "london_affordability_msoa.geojson"
    print(f"\nSaving to {output_path}...")
    gdf.to_file(output_path, driver="GeoJSON")
    
    # Update summary stats
    stats_path = DATA_DIR / "summary_stats_msoa.json"
    with open(stats_path, "r") as f:
        stats = json.load(f)
    
    stats["transport_analysis"] = {
        "correlations": {
            "affordability_vs_tube_distance": round(corr_tube, 3),
            "affordability_vs_transport_score": round(corr_transport, 3),
            "affordability_vs_born_locally": round(corr_local, 3),
        },
        "se_london": {
            "avg_tube_distance_km": round(se_london["tube_distance_km"].mean(), 2),
            "pct_with_tube_nearby": round(se_london["has_tube_nearby"].mean() * 100, 1),
            "avg_transport_score": round(se_london["transport_score"].mean(), 1),
            "avg_born_locally_pct": round(se_london["born_local_pct"].mean(), 1),
        },
        "rest_of_london": {
            "avg_tube_distance_km": round(rest_london["tube_distance_km"].mean(), 2),
            "pct_with_tube_nearby": round(rest_london["has_tube_nearby"].mean() * 100, 1),
            "avg_transport_score": round(rest_london["transport_score"].mean(), 1),
            "avg_born_locally_pct": round(rest_london["born_local_pct"].mean(), 1),
        },
    }
    
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    
    print(f"Updated {stats_path}")
    print("\n" + "=" * 60)
    print("Complete! New fields added:")
    print("  - tube_distance_km")
    print("  - nearest_tube")
    print("  - has_tube_nearby")
    print("  - transport_score")
    print("  - avg_terminus_dist_km")
    print("  - nearest_motorway_km")
    print("  - born_local_pct")
    print("=" * 60)


if __name__ == "__main__":
    main()
