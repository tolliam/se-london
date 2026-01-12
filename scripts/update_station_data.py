"""
Update transport data to include train stations (not just tube).

SE London has plenty of rail stations - measuring tube-only is unfair.
"""

import json
import geopandas as gpd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# Combined Tube + Overground + National Rail stations in London
# This is more representative of actual public transport access
ALL_RAIL_STATIONS = [
    # === TUBE STATIONS (selection of key ones) ===
    {"name": "Bank", "lat": 51.5133, "lon": -0.0886, "type": "tube"},
    {"name": "Liverpool Street", "lat": 51.5178, "lon": -0.0823, "type": "tube"},
    {"name": "Victoria", "lat": 51.4965, "lon": -0.1447, "type": "tube"},
    {"name": "Waterloo", "lat": 51.5036, "lon": -0.1143, "type": "tube"},
    {"name": "London Bridge", "lat": 51.5052, "lon": -0.0864, "type": "tube"},
    {"name": "Kings Cross", "lat": 51.5308, "lon": -0.1238, "type": "tube"},
    {"name": "Oxford Circus", "lat": 51.5152, "lon": -0.1418, "type": "tube"},
    {"name": "Brixton", "lat": 51.4627, "lon": -0.1145, "type": "tube"},
    {"name": "Stratford", "lat": 51.5416, "lon": -0.0042, "type": "tube"},
    {"name": "Canary Wharf", "lat": 51.5035, "lon": -0.0187, "type": "tube"},
    {"name": "North Greenwich", "lat": 51.5005, "lon": 0.0039, "type": "tube"},
    {"name": "Canada Water", "lat": 51.4982, "lon": -0.0502, "type": "tube"},
    {"name": "Bermondsey", "lat": 51.4979, "lon": -0.0637, "type": "tube"},
    {"name": "Stockwell", "lat": 51.4723, "lon": -0.1230, "type": "tube"},
    {"name": "Clapham Common", "lat": 51.4618, "lon": -0.1384, "type": "tube"},
    {"name": "Morden", "lat": 51.4022, "lon": -0.1948, "type": "tube"},
    {"name": "Wimbledon", "lat": 51.4214, "lon": -0.2064, "type": "tube"},
    {"name": "Barking", "lat": 51.5396, "lon": 0.0809, "type": "tube"},
    {"name": "Hammersmith", "lat": 51.4936, "lon": -0.2251, "type": "tube"},
    {"name": "Ealing Broadway", "lat": 51.5152, "lon": -0.3017, "type": "tube"},
    {"name": "Finsbury Park", "lat": 51.5642, "lon": -0.1065, "type": "tube"},
    {"name": "Highbury & Islington", "lat": 51.5460, "lon": -0.1036, "type": "tube"},
    
    # === SE LONDON RAIL STATIONS (the key ones missing from tube) ===
    # Greenwich/Lewisham area
    {"name": "Greenwich", "lat": 51.4781, "lon": -0.0149, "type": "rail"},
    {"name": "Deptford", "lat": 51.4789, "lon": -0.0259, "type": "rail"},
    {"name": "Lewisham", "lat": 51.4657, "lon": -0.0142, "type": "rail"},
    {"name": "Blackheath", "lat": 51.4658, "lon": 0.0089, "type": "rail"},
    {"name": "Westcombe Park", "lat": 51.4715, "lon": 0.0209, "type": "rail"},
    {"name": "Maze Hill", "lat": 51.4831, "lon": 0.0034, "type": "rail"},
    {"name": "Charlton", "lat": 51.4870, "lon": 0.0304, "type": "rail"},
    {"name": "Woolwich Dockyard", "lat": 51.4909, "lon": 0.0540, "type": "rail"},
    {"name": "Woolwich Arsenal", "lat": 51.4899, "lon": 0.0691, "type": "rail"},
    {"name": "Plumstead", "lat": 51.4872, "lon": 0.0858, "type": "rail"},
    {"name": "Abbey Wood", "lat": 51.4910, "lon": 0.1203, "type": "rail"},
    {"name": "Belvedere", "lat": 51.4921, "lon": 0.1514, "type": "rail"},
    {"name": "Erith", "lat": 51.4820, "lon": 0.1754, "type": "rail"},
    {"name": "Slade Green", "lat": 51.4673, "lon": 0.1907, "type": "rail"},
    {"name": "Dartford", "lat": 51.4470, "lon": 0.2191, "type": "rail"},
    
    # Bexley area
    {"name": "Bexleyheath", "lat": 51.4637, "lon": 0.0921, "type": "rail"},
    {"name": "Barnehurst", "lat": 51.4649, "lon": 0.1597, "type": "rail"},
    {"name": "Bexley", "lat": 51.4405, "lon": 0.1485, "type": "rail"},
    {"name": "Albany Park", "lat": 51.4354, "lon": 0.1277, "type": "rail"},
    {"name": "Sidcup", "lat": 51.4345, "lon": 0.1014, "type": "rail"},
    {"name": "New Eltham", "lat": 51.4378, "lon": 0.0701, "type": "rail"},
    {"name": "Eltham", "lat": 51.4505, "lon": 0.0524, "type": "rail"},
    {"name": "Kidbrooke", "lat": 51.4622, "lon": 0.0283, "type": "rail"},
    {"name": "Welling", "lat": 51.4647, "lon": 0.1013, "type": "rail"},
    {"name": "Falconwood", "lat": 51.4595, "lon": 0.0784, "type": "rail"},
    
    # Bromley area  
    {"name": "Bromley South", "lat": 51.3996, "lon": 0.0174, "type": "rail"},
    {"name": "Bromley North", "lat": 51.4087, "lon": 0.0172, "type": "rail"},
    {"name": "Bickley", "lat": 51.3882, "lon": 0.0448, "type": "rail"},
    {"name": "Petts Wood", "lat": 51.3886, "lon": 0.0743, "type": "rail"},
    {"name": "Orpington", "lat": 51.3739, "lon": 0.0988, "type": "rail"},
    {"name": "Chislehurst", "lat": 51.4050, "lon": 0.0573, "type": "rail"},
    {"name": "Elmstead Woods", "lat": 51.4175, "lon": 0.0442, "type": "rail"},
    {"name": "Sundridge Park", "lat": 51.4138, "lon": 0.0209, "type": "rail"},
    {"name": "Grove Park", "lat": 51.4302, "lon": 0.0222, "type": "rail"},
    {"name": "Hither Green", "lat": 51.4524, "lon": -0.0013, "type": "rail"},
    {"name": "Lee", "lat": 51.4500, "lon": 0.0139, "type": "rail"},
    {"name": "Mottingham", "lat": 51.4396, "lon": 0.0500, "type": "rail"},
    {"name": "Beckenham Junction", "lat": 51.4108, "lon": -0.0259, "type": "rail"},
    {"name": "Beckenham Hill", "lat": 51.4247, "lon": -0.0166, "type": "rail"},
    {"name": "Ravensbourne", "lat": 51.4145, "lon": -0.0166, "type": "rail"},
    {"name": "Shortlands", "lat": 51.4050, "lon": -0.0122, "type": "rail"},
    {"name": "Eden Park", "lat": 51.3903, "lon": -0.0281, "type": "rail"},
    {"name": "West Wickham", "lat": 51.3806, "lon": -0.0152, "type": "rail"},
    {"name": "Hayes (Kent)", "lat": 51.3762, "lon": 0.0101, "type": "rail"},
    
    # Lewisham/Catford area
    {"name": "Catford", "lat": 51.4446, "lon": -0.0252, "type": "rail"},
    {"name": "Catford Bridge", "lat": 51.4445, "lon": -0.0205, "type": "rail"},
    {"name": "Bellingham", "lat": 51.4345, "lon": -0.0248, "type": "rail"},
    {"name": "Lower Sydenham", "lat": 51.4252, "lon": -0.0402, "type": "rail"},
    {"name": "New Cross", "lat": 51.4764, "lon": -0.0326, "type": "rail"},
    {"name": "New Cross Gate", "lat": 51.4752, "lon": -0.0404, "type": "rail"},
    {"name": "Brockley", "lat": 51.4645, "lon": -0.0377, "type": "rail"},
    {"name": "Honor Oak Park", "lat": 51.4500, "lon": -0.0452, "type": "rail"},
    {"name": "Forest Hill", "lat": 51.4395, "lon": -0.0530, "type": "rail"},
    {"name": "Sydenham", "lat": 51.4275, "lon": -0.0546, "type": "rail"},
    {"name": "Penge East", "lat": 51.4193, "lon": -0.0543, "type": "rail"},
    {"name": "Penge West", "lat": 51.4177, "lon": -0.0610, "type": "rail"},
    {"name": "Anerley", "lat": 51.4124, "lon": -0.0655, "type": "rail"},
    {"name": "Norwood Junction", "lat": 51.3974, "lon": -0.0753, "type": "rail"},
    {"name": "Crystal Palace", "lat": 51.4181, "lon": -0.0724, "type": "rail"},
    
    # Southwark/Peckham area
    {"name": "Peckham Rye", "lat": 51.4700, "lon": -0.0694, "type": "rail"},
    {"name": "Queens Road Peckham", "lat": 51.4739, "lon": -0.0569, "type": "rail"},
    {"name": "South Bermondsey", "lat": 51.4877, "lon": -0.0531, "type": "rail"},
    {"name": "Denmark Hill", "lat": 51.4682, "lon": -0.0886, "type": "rail"},
    {"name": "East Dulwich", "lat": 51.4604, "lon": -0.0817, "type": "rail"},
    {"name": "North Dulwich", "lat": 51.4548, "lon": -0.0885, "type": "rail"},
    {"name": "Nunhead", "lat": 51.4676, "lon": -0.0528, "type": "rail"},
    {"name": "Crofton Park", "lat": 51.4552, "lon": -0.0356, "type": "rail"},
    {"name": "Elephant & Castle", "lat": 51.4943, "lon": -0.0986, "type": "rail"},
    {"name": "Loughborough Junction", "lat": 51.4676, "lon": -0.1001, "type": "rail"},
    
    # Croydon area
    {"name": "East Croydon", "lat": 51.3755, "lon": -0.0922, "type": "rail"},
    {"name": "West Croydon", "lat": 51.3786, "lon": -0.1025, "type": "rail"},
    {"name": "South Croydon", "lat": 51.3624, "lon": -0.0932, "type": "rail"},
    {"name": "Purley", "lat": 51.3377, "lon": -0.1134, "type": "rail"},
    {"name": "Purley Oaks", "lat": 51.3480, "lon": -0.0970, "type": "rail"},
    {"name": "Sanderstead", "lat": 51.3485, "lon": -0.0795, "type": "rail"},
    {"name": "Riddlesdown", "lat": 51.3323, "lon": -0.0998, "type": "rail"},
    {"name": "Coulsdon South", "lat": 51.3175, "lon": -0.1378, "type": "rail"},
    {"name": "Selhurst", "lat": 51.3899, "lon": -0.0886, "type": "rail"},
    {"name": "Thornton Heath", "lat": 51.3995, "lon": -0.1006, "type": "rail"},
    {"name": "Norbury", "lat": 51.4110, "lon": -0.1211, "type": "rail"},
    
    # Lambeth area (additional)
    {"name": "Streatham", "lat": 51.4251, "lon": -0.1310, "type": "rail"},
    {"name": "Streatham Common", "lat": 51.4186, "lon": -0.1365, "type": "rail"},
    {"name": "Streatham Hill", "lat": 51.4382, "lon": -0.1270, "type": "rail"},
    {"name": "Tulse Hill", "lat": 51.4397, "lon": -0.1050, "type": "rail"},
    {"name": "West Norwood", "lat": 51.4323, "lon": -0.1030, "type": "rail"},
    {"name": "Gipsy Hill", "lat": 51.4239, "lon": -0.0841, "type": "rail"},
    {"name": "Herne Hill", "lat": 51.4544, "lon": -0.0933, "type": "rail"},
    
    # === OTHER LONDON RAIL (for comparison) ===
    # North London
    {"name": "Finchley Road & Frognal", "lat": 51.5500, "lon": -0.1833, "type": "rail"},
    {"name": "Hampstead Heath", "lat": 51.5554, "lon": -0.1652, "type": "rail"},
    {"name": "Gospel Oak", "lat": 51.5554, "lon": -0.1517, "type": "rail"},
    {"name": "Kentish Town West", "lat": 51.5465, "lon": -0.1467, "type": "rail"},
    {"name": "Camden Road", "lat": 51.5418, "lon": -0.1391, "type": "rail"},
    {"name": "Hackney Central", "lat": 51.5468, "lon": -0.0556, "type": "rail"},
    {"name": "Hackney Downs", "lat": 51.5488, "lon": -0.0603, "type": "rail"},
    {"name": "Dalston Junction", "lat": 51.5462, "lon": -0.0754, "type": "rail"},
    {"name": "Dalston Kingsland", "lat": 51.5482, "lon": -0.0762, "type": "rail"},
    
    # West London
    {"name": "Richmond", "lat": 51.4632, "lon": -0.3013, "type": "rail"},
    {"name": "Kew Gardens", "lat": 51.4775, "lon": -0.2850, "type": "rail"},
    {"name": "Chiswick", "lat": 51.4677, "lon": -0.2678, "type": "rail"},
    {"name": "Barnes", "lat": 51.4681, "lon": -0.2403, "type": "rail"},
    {"name": "Putney", "lat": 51.4610, "lon": -0.2167, "type": "rail"},
    {"name": "Wandsworth Town", "lat": 51.4610, "lon": -0.1872, "type": "rail"},
    {"name": "Clapham Junction", "lat": 51.4641, "lon": -0.1702, "type": "rail"},
    {"name": "Battersea Park", "lat": 51.4772, "lon": -0.1481, "type": "rail"},
    {"name": "Queenstown Road", "lat": 51.4743, "lon": -0.1391, "type": "rail"},
    
    # East London
    {"name": "Forest Gate", "lat": 51.5490, "lon": 0.0247, "type": "rail"},
    {"name": "Manor Park", "lat": 51.5523, "lon": 0.0460, "type": "rail"},
    {"name": "Ilford", "lat": 51.5590, "lon": 0.0700, "type": "rail"},
    {"name": "Seven Kings", "lat": 51.5637, "lon": 0.0962, "type": "rail"},
    {"name": "Goodmayes", "lat": 51.5657, "lon": 0.1112, "type": "rail"},
    {"name": "Chadwell Heath", "lat": 51.5681, "lon": 0.1299, "type": "rail"},
    {"name": "Romford", "lat": 51.5751, "lon": 0.1827, "type": "rail"},
]


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


def calculate_nearest_station(lat, lon, station_list, station_type=None):
    """Find distance to nearest station, optionally filtered by type."""
    min_dist = float('inf')
    nearest = None
    nearest_type = None
    
    for station in station_list:
        if station_type and station.get("type") != station_type:
            continue
        dist = haversine_distance(lat, lon, station["lat"], station["lon"])
        if dist < min_dist:
            min_dist = dist
            nearest = station["name"]
            nearest_type = station.get("type", "unknown")
    
    return min_dist, nearest, nearest_type


def main():
    print("=" * 60)
    print("Updating: Tube Distance → Rail Station Distance")
    print("=" * 60)
    
    # Load MSOA data
    msoa_file = DATA_DIR / "london_affordability_msoa.geojson"
    print(f"Loading {msoa_file}...")
    gdf = gpd.read_file(msoa_file)
    print(f"  Loaded {len(gdf)} MSOAs")
    
    # Calculate centroids
    gdf["centroid"] = gdf.geometry.centroid
    gdf["centroid_lat"] = gdf["centroid"].y
    gdf["centroid_lon"] = gdf["centroid"].x
    
    # Separate tube-only stations for comparison
    tube_only = [s for s in ALL_RAIL_STATIONS if s["type"] == "tube"]
    
    print(f"\nStation counts:")
    print(f"  Tube stations: {len(tube_only)}")
    print(f"  All rail stations: {len(ALL_RAIL_STATIONS)}")
    
    # Calculate distances
    print("\nCalculating distances to nearest stations...")
    
    station_data = gdf.apply(
        lambda row: calculate_nearest_station(
            row["centroid_lat"], row["centroid_lon"], ALL_RAIL_STATIONS
        ),
        axis=1
    )
    
    gdf["station_distance_km"] = station_data.apply(lambda x: round(x[0], 2))
    gdf["nearest_station"] = station_data.apply(lambda x: x[1])
    gdf["nearest_station_type"] = station_data.apply(lambda x: x[2])
    gdf["has_station_nearby"] = gdf["station_distance_km"] < 1.5
    
    # Keep tube-only for comparison
    tube_data = gdf.apply(
        lambda row: calculate_nearest_station(
            row["centroid_lat"], row["centroid_lon"], tube_only
        ),
        axis=1
    )
    gdf["tube_distance_km"] = tube_data.apply(lambda x: round(x[0], 2))
    gdf["nearest_tube"] = tube_data.apply(lambda x: x[1])
    
    # Drop centroid
    gdf = gdf.drop(columns=["centroid"])
    
    # Analysis
    print("\n" + "=" * 40)
    print("COMPARISON: TUBE vs ALL RAIL")
    print("=" * 40)
    
    se_london = gdf[gdf["is_se_london"] == True]
    rest_london = gdf[gdf["is_se_london"] == False]
    
    print(f"\n{'Metric':<35} {'SE London':>12} {'Rest':>12}")
    print("-" * 59)
    print(f"{'Avg TUBE Distance (km)':<35} {se_london['tube_distance_km'].mean():>12.2f} {rest_london['tube_distance_km'].mean():>12.2f}")
    print(f"{'Avg ANY STATION Distance (km)':<35} {se_london['station_distance_km'].mean():>12.2f} {rest_london['station_distance_km'].mean():>12.2f}")
    print(f"{'% with Tube <1.5km':<35} {(se_london['tube_distance_km'] < 1.5).mean()*100:>11.1f}% {(rest_london['tube_distance_km'] < 1.5).mean()*100:>11.1f}%")
    print(f"{'% with ANY Station <1.5km':<35} {se_london['has_station_nearby'].mean()*100:>11.1f}% {rest_london['has_station_nearby'].mean()*100:>11.1f}%")
    
    # Correlations
    print("\n" + "=" * 40)
    print("CORRELATIONS WITH AFFORDABILITY")
    print("=" * 40)
    corr_tube = gdf["affordability_ratio"].corr(gdf["tube_distance_km"])
    corr_station = gdf["affordability_ratio"].corr(gdf["station_distance_km"])
    print(f"Affordability vs Tube Distance: {corr_tube:.3f}")
    print(f"Affordability vs Any Station Distance: {corr_station:.3f}")
    
    # Save
    output_path = DATA_DIR / "london_affordability_msoa.geojson"
    print(f"\nSaving to {output_path}...")
    gdf.to_file(output_path, driver="GeoJSON")
    
    # Update stats
    stats_path = DATA_DIR / "summary_stats_msoa.json"
    with open(stats_path, "r") as f:
        stats = json.load(f)
    
    stats["transport_analysis"]["station_comparison"] = {
        "se_london": {
            "avg_tube_distance_km": round(se_london["tube_distance_km"].mean(), 2),
            "avg_station_distance_km": round(se_london["station_distance_km"].mean(), 2),
            "pct_with_tube_nearby": round((se_london["tube_distance_km"] < 1.5).mean() * 100, 1),
            "pct_with_station_nearby": round(se_london["has_station_nearby"].mean() * 100, 1),
        },
        "rest_of_london": {
            "avg_tube_distance_km": round(rest_london["tube_distance_km"].mean(), 2),
            "avg_station_distance_km": round(rest_london["station_distance_km"].mean(), 2),
            "pct_with_tube_nearby": round((rest_london["tube_distance_km"] < 1.5).mean() * 100, 1),
            "pct_with_station_nearby": round(rest_london["has_station_nearby"].mean() * 100, 1),
        },
    }
    
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    
    print(f"Updated {stats_path}")
    print("\n" + "=" * 60)
    print("Complete! New fields:")
    print("  - station_distance_km (tube OR rail)")
    print("  - nearest_station, nearest_station_type")
    print("  - has_station_nearby")
    print("  - tube_distance_km (kept for comparison)")
    print("=" * 60)


if __name__ == "__main__":
    main()
