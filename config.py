"""
Configuration file for NavIC Comprehensive Monitoring System
Contains all constants, satellite data, and configuration parameters
"""

# Constants
MU = 398600.4418  # km^3/s^2
R_EARTH = 6371.0  # km
GEOSYNC_MEAN_MOTION = 1.002737909  # revolutions/day for perfect geostationary orbit

# NavIC Satellite NORAD IDs
NAVIK_SATS = {
    "IRNSS-1B": 39635,
    "IRNSS-1C": 40269,
    "IRNSS-1D": 40547,
    "IRNSS-1E": 41241,
    "IRNSS-1F": 41384,
    "IRNSS-1I": 43286,
    "NVS-01": 56759
}

# India's extreme geographical points for DOP analysis
INDIA_EXTREME_POINTS = {
    "Northernmost (Siachen Glacier)": (35.5, 77.0),
    "Southernmost (Indira Point)": (6.75, 93.85),
    "Easternmost (Kibithu)": (28.0, 97.0),
    "Westernmost (Guhar Moti)": (23.7, 68.1),
    "Capital (Delhi)": (28.7, 77.1)
}

# Japan's key geographical points for QZSS DOP analysis
JAPAN_KEY_POINTS = {
    "Northernmost (Hokkaido - Wakkanai)": (45.4, 141.7),
    "Southernmost (Okinawa - Ishigaki)": (24.3, 124.2),
    "Easternmost (Tokyo)": (35.7, 139.7),
    "Westernmost (Kyushu - Nagasaki)": (32.8, 129.9),
    "Capital (Tokyo)": (35.7, 139.7)
}

# China's key geographical points for BeiDou-3 DOP analysis
CHINA_KEY_POINTS = {
    "Northernmost (Mohe, Heilongjiang)": (53.5, 122.5),
    "Southernmost (Sansha, Hainan)": (16.8, 112.3),
    "Easternmost (Fuyuan, Heilongjiang)": (48.4, 134.7),
    "Westernmost (Wuqia, Xinjiang)": (39.7, 75.3),
    "Capital (Beijing)": (39.9, 116.4),
    "Shanghai": (31.2, 121.5),
    "Guangzhou": (23.1, 113.3),
    "Chengdu": (30.7, 104.1),
    "Urumqi (Xinjiang)": (43.8, 87.6),
    "Lhasa (Tibet)": (29.7, 91.1)
}

# NavIC service requirements (target longitudes and inclinations)
NAVIK_SERVICE_REQUIREMENTS = {
    "IRNSS-1B": {"longitude": 55.0, "inclination": 29.0},
    "IRNSS-1C": {"longitude": 83.0, "inclination": 5.0},
    "IRNSS-1D": {"longitude": 111.75, "inclination": 30.0},
    "IRNSS-1E": {"longitude": 111.75, "inclination": 29.0},
    "IRNSS-1F": {"longitude": 32.5, "inclination": 5.0},
    "IRNSS-1I": {"longitude": 55.0, "inclination": 29.0},
    "NVS-01": {"longitude": 129.5, "inclination": 5.0}
}

# QZSS Satellite NORAD IDs (fill correct NORAD_CAT_ID values)
QZSS_SATS = {
    "QZS-1R (Michibiki-1R)": 49336,
    "QZS-2 (Michibiki-2)": 42738,    
    "QZS-3 (Michibiki-3)": 42917,     
    "QZS-4 (Michibiki-4)": 42965,   
    "QZS-6 (Michibiki-6)": 62876      
}

# QZSS service/target requirements (per provided specifications)
# Semi-major axis 42164 km ±10 km, eccentricity < 0.099, period ≈ 23h56m
# IGSO trio: inclination 39–41°, argument of perigee 270° ±1°, central track 139°E ±5°
# GSO members: inclination 0°, QZS-3 at 127°E, QZS-6 at 90.5°E
QZSS_SERVICE_REQUIREMENTS = {
    "QZS-1R (Michibiki-1R)": {
        "type": "IGSO",
        "central_longitude_deg": 139.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg_range": (39.0, 41.0),
        "arg_perigee_deg": 270.0, "arg_perigee_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.099
    },
    "QZS-2 (Michibiki-2)": {
        "type": "IGSO",
        "central_longitude_deg": 139.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg_range": (39.0, 41.0),
        "arg_perigee_deg": 270.0, "arg_perigee_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.099
    },
    "QZS-4 (Michibiki-4)": {
        "type": "IGSO",
        "central_longitude_deg": 139.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg_range": (39.0, 41.0),
        "arg_perigee_deg": 270.0, "arg_perigee_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.099
    },
    "QZS-3 (Michibiki-3)": {
        "type": "GSO",
        "central_longitude_deg": 127.0, "longitude_tol_deg": 0.5,
        "inclination_target_deg": 0.0, "inclination_tol_deg": 0.5,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.099
    },
    "QZS-6 (Michibiki-6)": {
        "type": "GSO",
        "central_longitude_deg": 90.5, "longitude_tol_deg": 0.5,
        "inclination_target_deg": 0.0, "inclination_tol_deg": 0.5,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.099
    }
}

# Typical maintenance cadence for QZSS (about once every six months)
QZSS_MAINTENANCE_NOTE = "Orbit correction maneuvers occur roughly once every six months."

# BeiDou-3 Satellite NORAD IDs (IGSO and GEO satellites only)
# Note: NORAD IDs need to be filled in with actual values from Space-Track
BEIDOU3_SATS = {
    # IGSO Satellites (55° inclination)
    "Compass-IGSO1": 36828,    # BEIDOU-2 IGSO-1 / Compass-IGSO1. :contentReference[oaicite:1]{index=1}
    "Compass-IGSO2": 37256,    # BEIDOU-2 IGSO-2. :contentReference[oaicite:2]{index=2}
    "Compass-IGSO3": 37384,    # BEIDOU-2 IGSO-3. :contentReference[oaicite:3]{index=3}
    "Compass-IGSO4": 37763,    # BEIDOU-2 IGSO-4. :contentReference[oaicite:4]{index=4}
    "Compass-IGSO5": 37948,    # BEIDOU-2 IGSO-5. :contentReference[oaicite:5]{index=5}
    "Compass-IGSO6": 41434,    # BEIDOU-2 IGSO-6. :contentReference[oaicite:6]{index=6}
    "Compass-IGSO7": 43539,    # BEIDOU-2 IGSO-7. :contentReference[oaicite:7]{index=7}

    # GEO Satellites
    "Compass-G4": 37210,       # BEIDOU-2 G4 / Compass-G4 (GEO 160°E). :contentReference[oaicite:8]{index=8}
    "Compass-G5": 38091,       # BEIDOU-2 G5 / Compass-G5 (GEO 58.75°E). :contentReference[oaicite:9]{index=9}
    "Compass-G6": 38953,       # BEIDOU-2 G6 / Compass-G6 (GEO 80°E). :contentReference[oaicite:10]{index=10}
    "Compass-G7": 41586,       # BEIDOU-2 G7 / Compass-G7 (GEO 110.5°E). :contentReference[oaicite:11]{index=11}
    "Compass-G8": 44231,       # BEIDOU-2 G8 / Compass-G8 (launched 2019-05-17). :contentReference[oaicite:12]{index=12}
    "BeiDou-3 G1": 43683,      # BEIDOU-3 G1 (GEO). :contentReference[oaicite:13]{index=13}
    "BeiDou-3 G2": 45344,      # BEIDOU-3 G2 (GEO). :contentReference[oaicite:14]{index=14}
    "BeiDou-3 G3": 45807,      # BEIDOU-3 G3 (GEO). :contentReference[oaicite:15]{index=15}
    "BeiDou-3 G4": 56564,      # BEIDOU-3 G4 (GEO; launched 2023). :contentReference[oaicite:16]{index=16}

    # Additional IGSO satellites (BDS-3 generation)
    "BeiDou-3 I1": 44204,      # BEIDOU-3 IGSO-1. :contentReference[oaicite:17]{index=17}
    "BeiDou-3 I2": 44337,      # BEIDOU-3 IGSO-2. :contentReference[oaicite:18]{index=18}
    "BeiDou-3 I3": 44709,      # BEIDOU-3 IGSO-3. :contentReference[oaicite:19]{index=19}
}


# BeiDou-3 service requirements (IGSO and GEO specifications)
BEIDOU3_SERVICE_REQUIREMENTS = {
    # IGSO satellites at 118° E
    "Compass-IGSO1": {
        "type": "IGSO",
        "central_longitude_deg": 118.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg": 55.0, "inclination_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "Compass-IGSO2": {
        "type": "IGSO",
        "central_longitude_deg": 118.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg": 55.0, "inclination_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "Compass-IGSO3": {
        "type": "IGSO",
        "central_longitude_deg": 118.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg": 55.0, "inclination_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    
    # IGSO satellites at 95° E
    "Compass-IGSO4": {
        "type": "IGSO",
        "central_longitude_deg": 95.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg": 55.0, "inclination_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "Compass-IGSO5": {
        "type": "IGSO",
        "central_longitude_deg": 95.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg": 55.0, "inclination_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "Compass-IGSO6": {
        "type": "IGSO",
        "central_longitude_deg": 95.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg": 55.0, "inclination_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "Compass-IGSO7": {
        "type": "IGSO",
        "central_longitude_deg": 95.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg": 55.0, "inclination_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    
    # IGSO satellites at 120° E
    "BeiDou-3 I1": {
        "type": "IGSO",
        "central_longitude_deg": 120.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg": 55.0, "inclination_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "BeiDou-3 I2": {
        "type": "IGSO",
        "central_longitude_deg": 120.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg": 55.0, "inclination_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "BeiDou-3 I3": {
        "type": "IGSO",
        "central_longitude_deg": 120.0, "longitude_tol_deg": 5.0,
        "inclination_target_deg": 55.0, "inclination_tol_deg": 1.0,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    
    # GEO satellites
    "Compass-G4": {
        "type": "GEO",
        "central_longitude_deg": 160.0, "longitude_tol_deg": 0.5,
        "inclination_target_deg": 0.0, "inclination_tol_deg": 0.5,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "Compass-G5": {
        "type": "GEO",
        "central_longitude_deg": 58.75, "longitude_tol_deg": 0.5,
        "inclination_target_deg": 0.0, "inclination_tol_deg": 0.5,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "Compass-G6": {
        "type": "GEO",
        "central_longitude_deg": 80.0, "longitude_tol_deg": 0.5,
        "inclination_target_deg": 0.0, "inclination_tol_deg": 0.5,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "Compass-G7": {
        "type": "GEO",
        "central_longitude_deg": 110.5, "longitude_tol_deg": 0.5,
        "inclination_target_deg": 0.0, "inclination_tol_deg": 0.5,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "Compass-G8": {
        "type": "GEO",
        "central_longitude_deg": 140.0, "longitude_tol_deg": 0.5,
        "inclination_target_deg": 0.0, "inclination_tol_deg": 0.5,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "BeiDou-3 G1": {
        "type": "GEO",
        "central_longitude_deg": 144.2, "longitude_tol_deg": 0.5,
        "inclination_target_deg": 0.0, "inclination_tol_deg": 0.5,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "BeiDou-3 G2": {
        "type": "GEO",
        "central_longitude_deg": 80.0, "longitude_tol_deg": 0.5,
        "inclination_target_deg": 0.0, "inclination_tol_deg": 0.5,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "BeiDou-3 G3": {
        "type": "GEO",
        "central_longitude_deg": 110.5, "longitude_tol_deg": 0.5,
        "inclination_target_deg": 0.0, "inclination_tol_deg": 0.5,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    },
    "BeiDou-3 G4": {
        "type": "GEO",
        "central_longitude_deg": 160.0, "longitude_tol_deg": 0.5,
        "inclination_target_deg": 0.0, "inclination_tol_deg": 0.5,
        "sma_km": 42164.0, "sma_tol_km": 10.0,
        "ecc_max": 0.05
    }
}

# BeiDou-3 maintenance note
BEIDOU3_MAINTENANCE_NOTE = "BeiDou-3 IGSO and GEO satellites provide regional coverage over Asia-Pacific."

# Space-Track API configuration
LOGIN_URL = "https://www.space-track.org/ajaxauth/login"

# Inactive satellites (for DOP calculations)
# IRNSS-1B is operational, but IRNSS-1C, 1D, and 1E have non-functional atomic clocks
INACTIVE_SATELLITES = ["IRNSS-1C", "IRNSS-1D", "IRNSS-1E"]

# Default analysis parameters
DEFAULT_PARAMS = {
    "z_threshold": 3.5,
    "sma_threshold": 0.5,
    "inc_threshold": 0.01,
    "persist_window": 2,
    "inclination_tolerance": 1.0,
    "drift_tolerance_gso": 0.05,
    "min_maneuvers_per_month": 1,
    "max_maneuvers_per_month": 8,
    "maneuver_uniformity_threshold": 0.8,
    "elevation_mask_deg": 5,
    "timestep_minutes": 15,
    "prop_duration_days": 1.5
}

# DOP quality thresholds
DOP_QUALITY_THRESHOLDS = {
    "Excellent": 2,
    "Good": 4,
    "Moderate": 6,
    "Fair": 8,
    "Poor": float('inf')
}
