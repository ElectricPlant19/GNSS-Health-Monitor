"""
DOP (Dilution of Precision) Calculation Module
Handles DOP calculations and satellite position computations
"""

import numpy as np
import statistics
from datetime import datetime, timedelta
from datetime import timezone
from skyfield.api import load, EarthSatellite, wgs84
from config import NAVIK_SATS


def parse_tle_data(tle_text, sat_dict):
    """Parse TLE text and create satellite objects"""
    ts = load.timescale()
    satellites = {}
    
    lines = tle_text.strip().split('\n')
    
    for i in range(0, len(lines), 3):
        if i + 2 >= len(lines):
            break
        
        name = lines[i].strip()
        line1 = lines[i + 1].strip()
        line2 = lines[i + 2].strip()
        
        try:
            norad_id = int(line1[2:7])
            sat_name = None
            for s_name, s_id in sat_dict.items():
                if s_id == norad_id:
                    sat_name = s_name
                    break
            
            if sat_name:
                satellite = EarthSatellite(line1, line2, sat_name, ts)
                satellites[sat_name] = satellite
        except (ValueError, IndexError):
            continue
    
    return satellites


def calculate_satellite_position(satellite, time, observer_location):
    """Calculate satellite position relative to observer"""
    try:
        difference = satellite - observer_location
        topocentric = difference.at(time)
        alt, az, distance = topocentric.altaz()
        
        return {
            'altitude': alt.degrees,
            'azimuth': az.degrees,
            'distance': distance.km,
            'elevation': alt.degrees
        }
    except Exception:
        return None


def calculate_design_matrix(satellite_positions, observer_lat, observer_lon, elevation_mask_deg=5):
    """Calculate the geometry matrix (design matrix) for DOP calculation.
    
    Uses standard GNSS convention with line-of-sight unit vectors in ENU (East-North-Up) frame.
    The design matrix H contains unit vectors pointing FROM observer TO satellite.
    
    For each satellite:
    - East component:  sin(azimuth) * cos(elevation)
    - North component: cos(azimuth) * cos(elevation)  
    - Up component:    sin(elevation)
    - Clock bias:      1
    """
    H = []
    
    for pos in satellite_positions:
        if pos is None:
            continue
            
        if pos['elevation'] > elevation_mask_deg:
            az_rad = np.radians(pos['azimuth'])
            el_rad = np.radians(pos['elevation'])
            
            # Line-of-sight unit vector in ENU (East-North-Up) coordinates
            # East component
            e = np.sin(az_rad) * np.cos(el_rad)
            # North component
            n = np.cos(az_rad) * np.cos(el_rad)
            # Up component
            u = np.sin(el_rad)
            
            # Design matrix row: [East, North, Up, clock_bias]
            H.append([e, n, u, 1])
    
    return np.array(H) if H else np.array([]).reshape(0, 4)


def calculate_dop_values(H):
    """Calculate various DOP values from the design matrix.
    
    DOP calculation:
    1. Compute H^T * H
    2. Invert to get Q = (H^T * H)^-1
    3. DOP values are square roots of diagonal elements and sums
    
    Returns:
        dict: DOP values (GDOP, PDOP, HDOP, VDOP, TDOP) or None if calculation fails
    """
    if len(H) < 4:
        return None
    
    try:
        HTH = np.dot(H.T, H)
        
        # Check for numerical stability using condition number
        cond = np.linalg.cond(HTH)
        if cond > 1e10:  # Matrix is ill-conditioned
            return None
        
        # Check determinant (should be non-zero for invertibility)
        det = np.linalg.det(HTH)
        if abs(det) < 1e-10:  # Essentially singular
            return None
            
        Q = np.linalg.inv(HTH)
        
        # Verify Q is positive definite (all diagonal elements should be positive)
        if not all(Q[i,i] > 0 for i in range(4)):
            return None
        
        dop = {
            'GDOP': float(np.sqrt(np.trace(Q))),
            'PDOP': float(np.sqrt(Q[0,0] + Q[1,1] + Q[2,2])),
            'HDOP': float(np.sqrt(Q[0,0] + Q[1,1])),
            'VDOP': float(np.sqrt(Q[2,2])),
            'TDOP': float(np.sqrt(Q[3,3])),
        }
        
        # Sanity check: GDOP should be >= PDOP >= HDOP and VDOP
        if dop['GDOP'] < dop['PDOP'] - 0.001:  # Small tolerance for numerical errors
            return None
        
        return dop
    except (np.linalg.LinAlgError, ValueError, FloatingPointError):
        return None


def calculate_dop_for_location(satellites_dict, lat, lon, time, elevation_mask_deg=5):
    """Calculate DOP for a specific location and time"""
    ts = load.timescale()
    t = ts.utc(time.year, time.month, time.day, time.hour, time.minute, time.second)
    
    observer = wgs84.latlon(lat, lon)
    
    satellite_positions = []
    visible_sats = []
    
    for sat_name, sat_obj in satellites_dict.items():
        pos = calculate_satellite_position(sat_obj, t, observer)
        if pos:
            satellite_positions.append(pos)
            if pos['elevation'] > elevation_mask_deg:
                visible_sats.append(sat_name)
    
    H = calculate_design_matrix(satellite_positions, lat, lon, elevation_mask_deg)
    dop = calculate_dop_values(H)
    
    return dop, visible_sats, satellite_positions


def get_geo_box_vectorized(satellite, epoch, timestep_minutes, prop_duration_days):
    """Calculate geographic bounding box for satellite propagation."""
    if epoch.tzinfo is None:
        epoch = epoch.replace(tzinfo=timezone.utc)
    
    t1 = epoch
    t2 = t1 + timedelta(days=prop_duration_days)
    delta_t = (t2 - t1).seconds + 24*3600*(t2 - t1).days
    n_steps = int(delta_t / (timestep_minutes * 60)) + 1
    
    time_offsets = np.arange(1, n_steps-1) * (60 * timestep_minutes)
    time_offsets = time_offsets.tolist()
    epochs = [t1 + timedelta(seconds=t) for t in time_offsets]
    
    ts = load.timescale()
    ts_times = [ts.from_datetime(t) for t in epochs]
    
    positions = [satellite.at(t) for t in ts_times]
    
    lat_lon = [wgs84.latlon_of(pos) for pos in positions]
    latitudes = [ll[0].degrees for ll in lat_lon]
    longitudes = [ll[1].degrees for ll in lat_lon]
    
    return {
        'epochs': epochs,
        'latitudes': latitudes,
        'longitudes': longitudes,
        'min_lon': min(longitudes),
        'max_lon': max(longitudes),
        'mean_lon': statistics.mean(longitudes),
        'min_lat': min(latitudes),
        'max_lat': max(latitudes),
        'mean_lat': statistics.mean(latitudes)
    }


def calculate_bounding_boxes(satellites_dict, reference_time, timestep_minutes=15, prop_duration_days=1.5):
    """Calculate bounding boxes for all satellites."""
    import streamlit as st
    
    bounding_boxes = {}
    
    for sat_name, sat_obj in satellites_dict.items():
        try:
            box_data = get_geo_box_vectorized(sat_obj, reference_time, timestep_minutes, prop_duration_days)
            bounding_boxes[sat_name] = box_data
        except Exception as e:
            st.warning(f"Could not calculate bounding box for {sat_name}: {str(e)}")
            continue
    
    return bounding_boxes


def get_dop_quality(gdop_value):
    """Get DOP quality assessment based on GDOP value."""
    from config import DOP_QUALITY_THRESHOLDS
    
    for quality, threshold in DOP_QUALITY_THRESHOLDS.items():
        if gdop_value < threshold:
            return quality
    return "Poor"
