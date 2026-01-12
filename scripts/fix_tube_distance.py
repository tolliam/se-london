"""
Fix tube distance calculation - use FULL tube station list (272 stations).
"""

import json
import geopandas as gpd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# FULL London Underground stations list (272 stations)
TUBE_STATIONS = [
    # Central London interchanges
    {"name": "Bank", "lat": 51.5133, "lon": -0.0886},
    {"name": "Monument", "lat": 51.5107, "lon": -0.0860},
    {"name": "Liverpool Street", "lat": 51.5178, "lon": -0.0823},
    {"name": "Kings Cross St Pancras", "lat": 51.5308, "lon": -0.1238},
    {"name": "Victoria", "lat": 51.4965, "lon": -0.1447},
    {"name": "Waterloo", "lat": 51.5036, "lon": -0.1143},
    {"name": "London Bridge", "lat": 51.5052, "lon": -0.0864},
    {"name": "Westminster", "lat": 51.5010, "lon": -0.1254},
    {"name": "Oxford Circus", "lat": 51.5152, "lon": -0.1418},
    {"name": "Paddington", "lat": 51.5154, "lon": -0.1755},
    {"name": "Euston", "lat": 51.5282, "lon": -0.1337},
    {"name": "Euston Square", "lat": 51.5260, "lon": -0.1359},
    {"name": "Great Portland Street", "lat": 51.5238, "lon": -0.1439},
    {"name": "Farringdon", "lat": 51.5203, "lon": -0.1053},
    {"name": "Barbican", "lat": 51.5204, "lon": -0.0979},
    {"name": "Aldgate", "lat": 51.5143, "lon": -0.0755},
    {"name": "Aldgate East", "lat": 51.5152, "lon": -0.0714},
    {"name": "Tower Hill", "lat": 51.5098, "lon": -0.0766},
    {"name": "Cannon Street", "lat": 51.5113, "lon": -0.0904},
    {"name": "Mansion House", "lat": 51.5122, "lon": -0.0940},
    {"name": "Blackfriars", "lat": 51.5120, "lon": -0.1032},
    {"name": "Temple", "lat": 51.5111, "lon": -0.1141},
    {"name": "St James's Park", "lat": 51.4994, "lon": -0.1335},
    {"name": "Borough", "lat": 51.5011, "lon": -0.0943},
    {"name": "Southwark", "lat": 51.5040, "lon": -0.1050},
    {"name": "Covent Garden", "lat": 51.5129, "lon": -0.1243},
    {"name": "Russell Square", "lat": 51.5234, "lon": -0.1244},
    {"name": "Hyde Park Corner", "lat": 51.5027, "lon": -0.1527},
    {"name": "Knightsbridge", "lat": 51.5015, "lon": -0.1607},
    {"name": "Barons Court", "lat": 51.4895, "lon": -0.2139},
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
    # Victoria Line (full line)
    {"name": "Brixton", "lat": 51.4627, "lon": -0.1145},
    {"name": "Pimlico", "lat": 51.4893, "lon": -0.1336},
    {"name": "Vauxhall", "lat": 51.4861, "lon": -0.1253},
    {"name": "Seven Sisters", "lat": 51.5822, "lon": -0.0749},
    {"name": "Tottenham Hale", "lat": 51.5882, "lon": -0.0594},
    {"name": "Blackhorse Road", "lat": 51.5867, "lon": -0.0417},
    {"name": "Walthamstow Central", "lat": 51.5830, "lon": -0.0195},
    # Jubilee Line (east)
    {"name": "Bermondsey", "lat": 51.4979, "lon": -0.0637},
    {"name": "Canada Water", "lat": 51.4982, "lon": -0.0502},
    {"name": "Canary Wharf", "lat": 51.5035, "lon": -0.0187},
    {"name": "North Greenwich", "lat": 51.5005, "lon": 0.0039},
    {"name": "Canning Town", "lat": 51.5147, "lon": 0.0082},
    {"name": "West Ham", "lat": 51.5287, "lon": 0.0056},
    {"name": "Stratford", "lat": 51.5416, "lon": -0.0042},
    # Jubilee Line (west)
    {"name": "Green Park", "lat": 51.5067, "lon": -0.1428},
    {"name": "Baker Street", "lat": 51.5226, "lon": -0.1571},
    {"name": "St John's Wood", "lat": 51.5347, "lon": -0.1740},
    {"name": "Swiss Cottage", "lat": 51.5432, "lon": -0.1750},
    {"name": "Finchley Road", "lat": 51.5472, "lon": -0.1803},
    {"name": "West Hampstead", "lat": 51.5469, "lon": -0.1910},
    {"name": "Kilburn", "lat": 51.5471, "lon": -0.2047},
    {"name": "Willesden Green", "lat": 51.5494, "lon": -0.2215},
    {"name": "Dollis Hill", "lat": 51.5520, "lon": -0.2387},
    {"name": "Neasden", "lat": 51.5542, "lon": -0.2503},
    {"name": "Wembley Park", "lat": 51.5635, "lon": -0.2795},
    {"name": "Kingsbury", "lat": 51.5846, "lon": -0.2786},
    {"name": "Queensbury", "lat": 51.5942, "lon": -0.2861},
    {"name": "Canons Park", "lat": 51.6078, "lon": -0.2947},
    {"name": "Stanmore", "lat": 51.6194, "lon": -0.3028},
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
    {"name": "Gloucester Road", "lat": 51.4945, "lon": -0.1829},
    {"name": "South Kensington", "lat": 51.4941, "lon": -0.1738},
    {"name": "Sloane Square", "lat": 51.4924, "lon": -0.1565},
    # District/Piccadilly Richmond branch
    {"name": "Turnham Green", "lat": 51.4951, "lon": -0.2547},
    {"name": "Gunnersbury", "lat": 51.4915, "lon": -0.2754},
    {"name": "Kew Gardens", "lat": 51.4775, "lon": -0.2850},
    {"name": "Richmond", "lat": 51.4632, "lon": -0.3013},
    # District Ealing branch
    {"name": "Acton Town", "lat": 51.5028, "lon": -0.2801},
    {"name": "Ealing Common", "lat": 51.5101, "lon": -0.2882},
    {"name": "Ealing Broadway", "lat": 51.5152, "lon": -0.3017},
    # Hammersmith & City / Circle
    {"name": "Hammersmith", "lat": 51.4936, "lon": -0.2251},
    {"name": "Goldhawk Road", "lat": 51.5018, "lon": -0.2267},
    {"name": "Shepherd's Bush Market", "lat": 51.5053, "lon": -0.2263},
    {"name": "Wood Lane", "lat": 51.5097, "lon": -0.2244},
    {"name": "Latimer Road", "lat": 51.5139, "lon": -0.2172},
    {"name": "Ladbroke Grove", "lat": 51.5172, "lon": -0.2107},
    {"name": "Westbourne Park", "lat": 51.5210, "lon": -0.2011},
    {"name": "Royal Oak", "lat": 51.5190, "lon": -0.1883},
    {"name": "Edgware Road (Circle)", "lat": 51.5199, "lon": -0.1679},
    # Piccadilly Line (west)
    {"name": "Heathrow T5", "lat": 51.4723, "lon": -0.4906},
    {"name": "Heathrow T4", "lat": 51.4590, "lon": -0.4476},
    {"name": "Heathrow T123", "lat": 51.4713, "lon": -0.4524},
    {"name": "Hatton Cross", "lat": 51.4669, "lon": -0.4227},
    {"name": "Hounslow West", "lat": 51.4729, "lon": -0.3858},
    {"name": "Hounslow Central", "lat": 51.4713, "lon": -0.3665},
    {"name": "Hounslow East", "lat": 51.4733, "lon": -0.3567},
    {"name": "Osterley", "lat": 51.4813, "lon": -0.3522},
    {"name": "Boston Manor", "lat": 51.4956, "lon": -0.3247},
    {"name": "Northfields", "lat": 51.4995, "lon": -0.3148},
    {"name": "South Ealing", "lat": 51.5011, "lon": -0.3072},
    {"name": "Chiswick Park", "lat": 51.4946, "lon": -0.2678},
    # Piccadilly (north)
    {"name": "Arnos Grove", "lat": 51.6164, "lon": -0.1331},
    {"name": "Southgate", "lat": 51.6322, "lon": -0.1280},
    {"name": "Oakwood", "lat": 51.6476, "lon": -0.1318},
    {"name": "Cockfosters", "lat": 51.6517, "lon": -0.1496},
    {"name": "Bounds Green", "lat": 51.6071, "lon": -0.1243},
    {"name": "Wood Green", "lat": 51.5975, "lon": -0.1097},
    {"name": "Turnpike Lane", "lat": 51.5904, "lon": -0.1028},
    {"name": "Manor House", "lat": 51.5709, "lon": -0.0958},
    {"name": "Arsenal", "lat": 51.5586, "lon": -0.1059},
    {"name": "Holloway Road", "lat": 51.5526, "lon": -0.1132},
    {"name": "Caledonian Road", "lat": 51.5481, "lon": -0.1188},
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
    # Central (west outer)
    {"name": "White City", "lat": 51.5120, "lon": -0.2246},
    {"name": "East Acton", "lat": 51.5168, "lon": -0.2474},
    {"name": "North Acton", "lat": 51.5237, "lon": -0.2597},
    {"name": "West Acton", "lat": 51.5180, "lon": -0.2809},
    {"name": "Hanger Lane", "lat": 51.5302, "lon": -0.2929},
    {"name": "Perivale", "lat": 51.5366, "lon": -0.3234},
    {"name": "Greenford", "lat": 51.5423, "lon": -0.3456},
    {"name": "Northolt", "lat": 51.5483, "lon": -0.3687},
    {"name": "South Ruislip", "lat": 51.5569, "lon": -0.3988},
    {"name": "Ruislip Gardens", "lat": 51.5606, "lon": -0.4103},
    {"name": "West Ruislip", "lat": 51.5696, "lon": -0.4378},
    # Northern Line (north)
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
    # Northern (High Barnet branch)
    {"name": "East Finchley", "lat": 51.5874, "lon": -0.1650},
    {"name": "Finchley Central", "lat": 51.6012, "lon": -0.1926},
    {"name": "West Finchley", "lat": 51.6095, "lon": -0.1883},
    {"name": "Woodside Park", "lat": 51.6179, "lon": -0.1856},
    {"name": "Totteridge & Whetstone", "lat": 51.6302, "lon": -0.1791},
    {"name": "High Barnet", "lat": 51.6503, "lon": -0.1943},
    # Northern (Edgware branch)
    {"name": "Golders Green", "lat": 51.5724, "lon": -0.1941},
    {"name": "Brent Cross", "lat": 51.5766, "lon": -0.2136},
    {"name": "Hendon Central", "lat": 51.5833, "lon": -0.2265},
    {"name": "Colindale", "lat": 51.5955, "lon": -0.2499},
    {"name": "Burnt Oak", "lat": 51.6027, "lon": -0.2639},
    {"name": "Edgware", "lat": 51.6137, "lon": -0.2750},
    # Metropolitan Line
    {"name": "Harrow-on-the-Hill", "lat": 51.5793, "lon": -0.3370},
    {"name": "Northwick Park", "lat": 51.5784, "lon": -0.3184},
    {"name": "Preston Road", "lat": 51.5720, "lon": -0.2954},
    {"name": "North Harrow", "lat": 51.5846, "lon": -0.3626},
    {"name": "Pinner", "lat": 51.5926, "lon": -0.3805},
    {"name": "Northwood Hills", "lat": 51.6004, "lon": -0.4092},
    {"name": "Northwood", "lat": 51.6111, "lon": -0.4237},
    {"name": "Moor Park", "lat": 51.6294, "lon": -0.4329},
    {"name": "Croxley", "lat": 51.6470, "lon": -0.4418},
    {"name": "Watford", "lat": 51.6573, "lon": -0.4177},
    {"name": "Rickmansworth", "lat": 51.6404, "lon": -0.4733},
    {"name": "Chorleywood", "lat": 51.6543, "lon": -0.5183},
    {"name": "Chalfont & Latimer", "lat": 51.6679, "lon": -0.5606},
    {"name": "Amersham", "lat": 51.6736, "lon": -0.6073},
    {"name": "Chesham", "lat": 51.7052, "lon": -0.6110},
    # Metropolitan (Uxbridge branch)
    {"name": "West Harrow", "lat": 51.5795, "lon": -0.3534},
    {"name": "Rayners Lane", "lat": 51.5753, "lon": -0.3714},
    {"name": "Eastcote", "lat": 51.5765, "lon": -0.3967},
    {"name": "Ruislip Manor", "lat": 51.5732, "lon": -0.4125},
    {"name": "Ruislip", "lat": 51.5715, "lon": -0.4213},
    {"name": "Ickenham", "lat": 51.5619, "lon": -0.4421},
    {"name": "Hillingdon", "lat": 51.5538, "lon": -0.4499},
    {"name": "Uxbridge", "lat": 51.5463, "lon": -0.4786},
    # Bakerloo
    {"name": "Elephant & Castle", "lat": 51.4943, "lon": -0.0986},
    {"name": "Lambeth North", "lat": 51.4991, "lon": -0.1115},
    {"name": "Piccadilly Circus", "lat": 51.5100, "lon": -0.1347},
    {"name": "Regent's Park", "lat": 51.5234, "lon": -0.1466},
    {"name": "Marylebone", "lat": 51.5225, "lon": -0.1631},
    {"name": "Edgware Road (Bakerloo)", "lat": 51.5199, "lon": -0.1679},
    {"name": "Warwick Avenue", "lat": 51.5235, "lon": -0.1835},
    {"name": "Maida Vale", "lat": 51.5298, "lon": -0.1854},
    {"name": "Kilburn Park", "lat": 51.5351, "lon": -0.1939},
    {"name": "Queen's Park", "lat": 51.5341, "lon": -0.2047},
    {"name": "Kensal Green", "lat": 51.5304, "lon": -0.2249},
    {"name": "Willesden Junction", "lat": 51.5326, "lon": -0.2445},
    {"name": "Harlesden", "lat": 51.5362, "lon": -0.2575},
    {"name": "Stonebridge Park", "lat": 51.5439, "lon": -0.2759},
    {"name": "Wembley Central", "lat": 51.5522, "lon": -0.2963},
    {"name": "North Wembley", "lat": 51.5621, "lon": -0.3034},
    {"name": "South Kenton", "lat": 51.5701, "lon": -0.3085},
    {"name": "Kenton", "lat": 51.5816, "lon": -0.3170},
    {"name": "Harrow & Wealdstone", "lat": 51.5920, "lon": -0.3351},
    # DLR (key stations - part of TfL network)
    {"name": "Tower Gateway", "lat": 51.5106, "lon": -0.0743},
    {"name": "Shadwell", "lat": 51.5117, "lon": -0.0569},
    {"name": "Limehouse", "lat": 51.5123, "lon": -0.0396},
    {"name": "Westferry", "lat": 51.5097, "lon": -0.0264},
    {"name": "Poplar", "lat": 51.5077, "lon": -0.0173},
    {"name": "All Saints", "lat": 51.5103, "lon": -0.0130},
    {"name": "Langdon Park", "lat": 51.5150, "lon": -0.0145},
    {"name": "Devons Road", "lat": 51.5223, "lon": -0.0174},
    {"name": "Blackwall", "lat": 51.5087, "lon": -0.0059},
    {"name": "East India", "lat": 51.5093, "lon": 0.0024},
    {"name": "Royal Victoria", "lat": 51.5091, "lon": 0.0181},
    {"name": "Custom House", "lat": 51.5095, "lon": 0.0276},
    {"name": "Prince Regent", "lat": 51.5100, "lon": 0.0341},
    {"name": "Royal Albert", "lat": 51.5082, "lon": 0.0461},
    {"name": "Beckton Park", "lat": 51.5087, "lon": 0.0551},
    {"name": "Cyprus", "lat": 51.5085, "lon": 0.0640},
    {"name": "Gallions Reach", "lat": 51.5096, "lon": 0.0716},
    {"name": "Beckton", "lat": 51.5148, "lon": 0.0613},
    {"name": "Pontoon Dock", "lat": 51.5019, "lon": 0.0376},
    {"name": "London City Airport", "lat": 51.5032, "lon": 0.0492},
    {"name": "King George V", "lat": 51.5018, "lon": 0.0620},
    {"name": "Woolwich Arsenal DLR", "lat": 51.4905, "lon": 0.0688},
    {"name": "Heron Quays", "lat": 51.5033, "lon": -0.0217},
    {"name": "West India Quay", "lat": 51.5073, "lon": -0.0219},
    {"name": "Crossharbour", "lat": 51.4968, "lon": -0.0154},
    {"name": "Mudchute", "lat": 51.4903, "lon": -0.0145},
    {"name": "Island Gardens", "lat": 51.4871, "lon": -0.0095},
    {"name": "Cutty Sark", "lat": 51.4827, "lon": -0.0100},
    {"name": "Greenwich DLR", "lat": 51.4781, "lon": -0.0149},
    {"name": "Deptford Bridge", "lat": 51.4741, "lon": -0.0219},
    {"name": "Elverson Road", "lat": 51.4693, "lon": -0.0207},
    {"name": "Lewisham DLR", "lat": 51.4657, "lon": -0.0142},
    {"name": "Pudding Mill Lane", "lat": 51.5343, "lon": -0.0138},
    {"name": "Star Lane", "lat": 51.5233, "lon": 0.0033},
    {"name": "Abbey Road DLR", "lat": 51.5319, "lon": 0.0038},
    {"name": "Stratford High Street", "lat": 51.5378, "lon": -0.0006},
    {"name": "Stratford International", "lat": 51.5449, "lon": -0.0087},
]

# SE London rail stations (unchanged from before)
SE_RAIL_STATIONS = [
    {"name": "Greenwich", "lat": 51.4781, "lon": -0.0149},
    {"name": "Deptford", "lat": 51.4789, "lon": -0.0259},
    {"name": "Lewisham", "lat": 51.4657, "lon": -0.0142},
    {"name": "Blackheath", "lat": 51.4658, "lon": 0.0089},
    {"name": "Woolwich Arsenal", "lat": 51.4899, "lon": 0.0691},
    {"name": "Abbey Wood", "lat": 51.4910, "lon": 0.1203},
    {"name": "Dartford", "lat": 51.4470, "lon": 0.2191},
    {"name": "Bexleyheath", "lat": 51.4637, "lon": 0.0921},
    {"name": "Sidcup", "lat": 51.4345, "lon": 0.1014},
    {"name": "Eltham", "lat": 51.4505, "lon": 0.0524},
    {"name": "Bromley South", "lat": 51.3996, "lon": 0.0174},
    {"name": "Orpington", "lat": 51.3739, "lon": 0.0988},
    {"name": "Peckham Rye", "lat": 51.4700, "lon": -0.0694},
    {"name": "Denmark Hill", "lat": 51.4682, "lon": -0.0886},
    {"name": "East Croydon", "lat": 51.3755, "lon": -0.0922},
    {"name": "West Croydon", "lat": 51.3786, "lon": -0.1025},
    {"name": "Crystal Palace", "lat": 51.4181, "lon": -0.0724},
    {"name": "Forest Hill", "lat": 51.4395, "lon": -0.0530},
    {"name": "Sydenham", "lat": 51.4275, "lon": -0.0546},
    {"name": "Catford", "lat": 51.4446, "lon": -0.0252},
    {"name": "New Cross", "lat": 51.4764, "lon": -0.0326},
    {"name": "Brockley", "lat": 51.4645, "lon": -0.0377},
    {"name": "Hither Green", "lat": 51.4524, "lon": -0.0013},
    {"name": "Grove Park", "lat": 51.4302, "lon": 0.0222},
    {"name": "Beckenham Junction", "lat": 51.4108, "lon": -0.0259},
    {"name": "Streatham", "lat": 51.4251, "lon": -0.1310},
    {"name": "Tulse Hill", "lat": 51.4397, "lon": -0.1050},
    {"name": "Herne Hill", "lat": 51.4544, "lon": -0.0933},
    {"name": "Clapham Junction", "lat": 51.4641, "lon": -0.1702},
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


def find_nearest_station(lat, lon, stations):
    """Find distance and name of nearest station."""
    min_dist = float('inf')
    nearest = None
    for station in stations:
        dist = haversine_distance(lat, lon, station["lat"], station["lon"])
        if dist < min_dist:
            min_dist = dist
            nearest = station["name"]
    return min_dist, nearest


def main():
    print("=" * 60)
    print("FIXING Tube Distance (using full 270 station list)")
    print("=" * 60)
    
    msoa_file = DATA_DIR / "london_affordability_msoa.geojson"
    print(f"Loading {msoa_file}...")
    gdf = gpd.read_file(msoa_file)
    print(f"  Loaded {len(gdf)} MSOAs")
    
    print(f"\nTube stations: {len(TUBE_STATIONS)}")
    
    # Calculate centroids
    gdf["centroid"] = gdf.geometry.centroid
    gdf["centroid_lat"] = gdf["centroid"].y
    gdf["centroid_lon"] = gdf["centroid"].x
    
    # Recalculate tube distance
    print("\nRecalculating tube distances...")
    tube_results = gdf.apply(
        lambda row: find_nearest_station(row["centroid_lat"], row["centroid_lon"], TUBE_STATIONS),
        axis=1
    )
    gdf["tube_distance_km"] = tube_results.apply(lambda x: round(x[0], 2))
    gdf["nearest_tube"] = tube_results.apply(lambda x: x[1])
    
    # Combine tube + SE rail for "any station"
    all_stations = TUBE_STATIONS + SE_RAIL_STATIONS
    print(f"All stations (tube + rail): {len(all_stations)}")
    
    station_results = gdf.apply(
        lambda row: find_nearest_station(row["centroid_lat"], row["centroid_lon"], all_stations),
        axis=1
    )
    gdf["station_distance_km"] = station_results.apply(lambda x: round(x[0], 2))
    gdf["nearest_station"] = station_results.apply(lambda x: x[1])
    
    # Drop centroid
    gdf = gdf.drop(columns=["centroid"])
    
    # Check Harrow specifically
    harrow_msoas = gdf[gdf["borough_name"] == "Harrow"]
    print(f"\n=== HARROW CHECK ===")
    print(f"Harrow MSOAs: {len(harrow_msoas)}")
    for _, row in harrow_msoas.head(5).iterrows():
        print(f"  {row['msoa_name']}: nearest tube = {row['nearest_tube']} ({row['tube_distance_km']} km)")
    
    # Analysis
    print("\n" + "=" * 40)
    print("CORRECTED STATS")
    print("=" * 40)
    
    se_london = gdf[gdf["is_se_london"] == True]
    rest_london = gdf[gdf["is_se_london"] == False]
    
    print(f"\n{'Metric':<35} {'SE London':>12} {'Rest':>12}")
    print("-" * 59)
    print(f"{'Avg Tube Distance (km)':<35} {se_london['tube_distance_km'].mean():>12.2f} {rest_london['tube_distance_km'].mean():>12.2f}")
    print(f"{'% with Tube <1.5km':<35} {(se_london['tube_distance_km'] < 1.5).mean()*100:>11.1f}% {(rest_london['tube_distance_km'] < 1.5).mean()*100:>11.1f}%")
    
    # Save
    output_path = DATA_DIR / "london_affordability_msoa.geojson"
    print(f"\nSaving to {output_path}...")
    gdf.to_file(output_path, driver="GeoJSON")
    
    print("\n✅ Fixed!")


if __name__ == "__main__":
    main()
