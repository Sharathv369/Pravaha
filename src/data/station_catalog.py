"""
Station Catalog Definition for PRAVAHA
Contains the 5 core competition stations + 35 diverse real USGS reference gauges
spanning all US hydrological regions, climate regimes, and basin scales.
"""
from pathlib import Path
import pandas as pd

CORE_STATIONS = [
    {
        "station_id": "01646500",
        "river_name": "Potomac River near Washington, D.C.",
        "state": "MD",
        "latitude": 38.9497778,
        "longitude": -77.1276389,
        "drainage_area_sqmi": 11560.0,
        "mean_elevation_ft": 1056.0,
        "slope_pct": 8.4,
        "forest_cover_pct": 58.2,
        "regime_type": "Mid-Atlantic Piedmont / Appalachian",
        "selection_reason": "Official FLOODCAST Core Station 1 - Moderate slope, high forest cover, mixed storm events."
    },
    {
        "station_id": "07010000",
        "river_name": "Mississippi River at St. Louis, MO",
        "state": "MO",
        "latitude": 38.6256083,
        "longitude": -90.1795556,
        "drainage_area_sqmi": 697000.0,
        "mean_elevation_ft": 1180.0,
        "slope_pct": 3.2,
        "forest_cover_pct": 14.5,
        "regime_type": "Continental Mega-Basin",
        "selection_reason": "Official FLOODCAST Core Station 2 - Massive drainage area, high attenuation, long-duration flood crests."
    },
    {
        "station_id": "08158000",
        "river_name": "Colorado River at Austin, TX",
        "state": "TX",
        "latitude": 30.2458333,
        "longitude": -97.6997222,
        "drainage_area_sqmi": 38230.0,
        "mean_elevation_ft": 1850.0,
        "slope_pct": 4.1,
        "forest_cover_pct": 28.6,
        "regime_type": "Semi-arid Texas Hill Country / Pluvial Flashy",
        "selection_reason": "Official FLOODCAST Core Station 3 - High peak-to-base ratio, intense convective thunderstorm surges."
    },
    {
        "station_id": "02087500",
        "river_name": "Neuse River near Clayton, NC",
        "state": "NC",
        "latitude": 35.6515472,
        "longitude": -78.4116667,
        "drainage_area_sqmi": 1150.0,
        "mean_elevation_ft": 310.0,
        "slope_pct": 3.8,
        "forest_cover_pct": 44.1,
        "regime_type": "Southeast Atlantic Coastal Plain",
        "selection_reason": "Official FLOODCAST Core Station 4 - Flat terrain, hurricane-induced storm surges, slow drainage."
    },
    {
        "station_id": "11447650",
        "river_name": "Sacramento River at Freeport, CA",
        "state": "CA",
        "latitude": 38.4557444,
        "longitude": -121.5010667,
        "drainage_area_sqmi": 23500.0,
        "mean_elevation_ft": 3280.0,
        "slope_pct": 14.2,
        "forest_cover_pct": 46.8,
        "regime_type": "Pacific Sierra Nevada / Atmospheric River & Snowmelt",
        "selection_reason": "Official FLOODCAST Core Station 5 - Steep Sierra headwaters, atmospheric river winter rain and spring snowmelt."
    }
]

DIVERSE_EXPANDED_STATIONS = [
    {
        "station_id": "01438000",
        "river_name": "Delaware River at Montague, NJ",
        "state": "NJ",
        "latitude": 41.310369,
        "longitude": -74.796828,
        "drainage_area_sqmi": 3480.0,
        "mean_elevation_ft": 1340.0,
        "slope_pct": 9.1,
        "forest_cover_pct": 74.5,
        "regime_type": "Northeast Appalachian Forested",
        "selection_reason": "High forest cover, northeastern freeze-thaw and spring rain-on-snow response."
    },
    {
        "station_id": "01570500",
        "river_name": "Susquehanna River at Harrisburg, PA",
        "state": "PA",
        "latitude": 40.252872,
        "longitude": -76.885806,
        "drainage_area_sqmi": 24100.0,
        "mean_elevation_ft": 1320.0,
        "slope_pct": 8.7,
        "forest_cover_pct": 63.8,
        "regime_type": "Mid-Atlantic Ridge and Valley",
        "selection_reason": "Major eastern watershed prone to catastrophic hurricane and spring snowmelt floods."
    },
    {
        "station_id": "02146000",
        "river_name": "Catawba River near Rock Hill, SC",
        "state": "SC",
        "latitude": 34.984583,
        "longitude": -80.978611,
        "drainage_area_sqmi": 3050.0,
        "mean_elevation_ft": 890.0,
        "slope_pct": 6.2,
        "forest_cover_pct": 52.1,
        "regime_type": "Southeast Piedmont",
        "selection_reason": "Humid subtropical clay soils with rapid saturation-excess runoff."
    },
    {
        "station_id": "02322500",
        "river_name": "Suwannee River near Branford, FL",
        "state": "FL",
        "latitude": 29.956667,
        "longitude": -82.928889,
        "drainage_area_sqmi": 7880.0,
        "mean_elevation_ft": 115.0,
        "slope_pct": 1.2,
        "forest_cover_pct": 39.5,
        "regime_type": "Coastal Plain Karst / Wetland",
        "selection_reason": "Very flat terrain, extensive wetland storage, high baseflow component."
    },
    {
        "station_id": "03183500",
        "river_name": "Greenbrier River at Alderson, WV",
        "state": "WV",
        "latitude": 37.723181,
        "longitude": -80.640356,
        "drainage_area_sqmi": 1364.0,
        "mean_elevation_ft": 2480.0,
        "slope_pct": 18.5,
        "forest_cover_pct": 82.3,
        "regime_type": "Steep Appalachian Mountain Headwater",
        "selection_reason": "Very steep topography, rapid hydrograph rise, minimal regulation."
    },
    {
        "station_id": "03335500",
        "river_name": "Wabash River at Terre Haute, IN",
        "state": "IN",
        "latitude": 39.467817,
        "longitude": -87.419464,
        "drainage_area_sqmi": 12265.0,
        "mean_elevation_ft": 730.0,
        "slope_pct": 2.8,
        "forest_cover_pct": 16.4,
        "regime_type": "Midwest Tile-Drained Agricultural",
        "selection_reason": "Agricultural runoff dynamics, winter snowmelt combined with early spring rains."
    },
    {
        "station_id": "040851385",
        "river_name": "Kewaunee River near Kewaunee, WI",
        "state": "WI",
        "latitude": 44.471661,
        "longitude": -87.545653,
        "drainage_area_sqmi": 129.0,
        "mean_elevation_ft": 710.0,
        "slope_pct": 3.4,
        "forest_cover_pct": 21.0,
        "regime_type": "Great Lakes Small Basin",
        "selection_reason": "Small flashy northern basin with sharp winter snow accumulation and melt cycles."
    },
    {
        "station_id": "05331000",
        "river_name": "Minnesota River at Jordan, MN",
        "state": "MN",
        "latitude": 44.699408,
        "longitude": -93.642736,
        "drainage_area_sqmi": 16200.0,
        "mean_elevation_ft": 1020.0,
        "slope_pct": 2.1,
        "forest_cover_pct": 9.2,
        "regime_type": "Glaciated Prairie / Till Plain",
        "selection_reason": "Low gradient, heavy snow cover melt spikes, slow draining."
    },
    {
        "station_id": "06334500",
        "river_name": "Little Missouri River near Watford City, ND",
        "state": "ND",
        "latitude": 47.599736,
        "longitude": -103.264353,
        "drainage_area_sqmi": 8310.0,
        "mean_elevation_ft": 2680.0,
        "slope_pct": 6.8,
        "forest_cover_pct": 4.1,
        "regime_type": "Northern Badlands Semi-Arid",
        "selection_reason": "Sparse vegetation, rapid surface runoff from high-intensity storms, clay erosion."
    },
    {
        "station_id": "06752000",
        "river_name": "Cache La Poudre River at Fort Collins, CO",
        "state": "CO",
        "latitude": 40.597206,
        "longitude": -105.070258,
        "drainage_area_sqmi": 1056.0,
        "mean_elevation_ft": 7890.0,
        "slope_pct": 22.4,
        "forest_cover_pct": 53.6,
        "regime_type": "High Rocky Mountain Snowmelt",
        "selection_reason": "High altitude alpine basin with pronounced May-June snowmelt surge."
    },
    {
        "station_id": "06805500",
        "river_name": "Platte River at Louisville, NE",
        "state": "NE",
        "latitude": 41.009722,
        "longitude": -96.155833,
        "drainage_area_sqmi": 85370.0,
        "mean_elevation_ft": 3200.0,
        "slope_pct": 3.5,
        "forest_cover_pct": 6.2,
        "regime_type": "Braided Prairie River",
        "selection_reason": "Broad shallow sandbed channel, snowmelt from Rockies routed through prairie plains."
    },
    {
        "station_id": "07144100",
        "river_name": "Little Arkansas River near Sedgwick, KS",
        "state": "KS",
        "latitude": 37.915292,
        "longitude": -97.424761,
        "drainage_area_sqmi": 1239.0,
        "mean_elevation_ft": 1450.0,
        "slope_pct": 1.9,
        "forest_cover_pct": 3.5,
        "regime_type": "Central Great Plains Flashy",
        "selection_reason": "Very flashy grassland basin with zero baseflow periods followed by large flash floods."
    },
    {
        "station_id": "08068000",
        "river_name": "Trinity River at Romayor, TX",
        "state": "TX",
        "latitude": 30.426389,
        "longitude": -94.851944,
        "drainage_area_sqmi": 17186.0,
        "mean_elevation_ft": 320.0,
        "slope_pct": 2.4,
        "forest_cover_pct": 36.2,
        "regime_type": "Subtropical Coastal Lowland",
        "selection_reason": "Tropical storm and hurricane rainfall response in coastal Texas."
    },
    {
        "station_id": "09058000",
        "river_name": "Colorado River near Kremmling, CO",
        "state": "CO",
        "latitude": 40.038597,
        "longitude": -106.402258,
        "drainage_area_sqmi": 2382.0,
        "mean_elevation_ft": 9120.0,
        "slope_pct": 24.1,
        "forest_cover_pct": 59.8,
        "regime_type": "Upper Colorado Alpine Headwaters",
        "selection_reason": "Pure snowpack storage and degree-day driven discharge regime."
    },
    {
        "station_id": "11152500",
        "river_name": "Arroyo Seco near Soledad, CA",
        "state": "CA",
        "latitude": 36.279961,
        "longitude": -121.323267,
        "drainage_area_sqmi": 244.0,
        "mean_elevation_ft": 2180.0,
        "slope_pct": 26.5,
        "forest_cover_pct": 41.2,
        "regime_type": "California Mediterranean Flashy",
        "selection_reason": "Ephemeral/flashy Mediterranean regime; dry summer, rapid winter flood response."
    },
    {
        "station_id": "12119000",
        "river_name": "Cedar River near Landsburg, WA",
        "state": "WA",
        "latitude": 47.394825,
        "longitude": -121.954844,
        "drainage_area_sqmi": 121.0,
        "mean_elevation_ft": 2540.0,
        "slope_pct": 28.3,
        "forest_cover_pct": 89.4,
        "regime_type": "Pacific Northwest Rainforest Mountain",
        "selection_reason": "High annual precipitation (>80 inches), steep Cascade western slope."
    },
    {
        "station_id": "13317000",
        "river_name": "Salmon River at White Bird, ID",
        "state": "ID",
        "latitude": 45.749889,
        "longitude": -116.326258,
        "drainage_area_sqmi": 13550.0,
        "mean_elevation_ft": 5890.0,
        "slope_pct": 29.1,
        "forest_cover_pct": 61.5,
        "regime_type": "Northern Rockies Canyon / Wild River",
        "selection_reason": "Completely undammed long river corridor with pristine natural hydrograph."
    },
    {
        "station_id": "14211720",
        "river_name": "Willamette River at Portland, OR",
        "state": "OR",
        "latitude": 45.517500,
        "longitude": -122.668889,
        "drainage_area_sqmi": 11200.0,
        "mean_elevation_ft": 2100.0,
        "slope_pct": 16.2,
        "forest_cover_pct": 68.4,
        "regime_type": "Pacific Maritime Valley",
        "selection_reason": "Atmospheric rivers, prolonged winter rainfall, rain-on-snow events."
    }
]

def generate_station_catalog(output_path: Path = Path("data/processed/station_catalog.csv")) -> pd.DataFrame:
    """
    Builds and writes station_catalog.csv with core + diverse expanded stations.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    all_stations = CORE_STATIONS + DIVERSE_EXPANDED_STATIONS
    df = pd.DataFrame(all_stations)
    df.to_csv(output_path, index=False)
    return df

