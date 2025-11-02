"""
Main NavIC Comprehensive Monitoring Application
Streamlit-based interface for satellite monitoring and analysis
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
from datetime import timezone
from skyfield.api import load

# Import our modular components
from config import (
    NAVIK_SATS, INDIA_EXTREME_POINTS, JAPAN_KEY_POINTS, CHINA_KEY_POINTS, INACTIVE_SATELLITES, DEFAULT_PARAMS,
    QZSS_SATS, QZSS_SERVICE_REQUIREMENTS,
    BEIDOU3_SATS, BEIDOU3_SERVICE_REQUIREMENTS
)
from spacetrack_api import fetch_and_classify_satellite, fetch_multiple_tles
from drift_analysis import assess_drift_health, get_drift_direction
from maneuver_detection import detect_navik_maneuvers
from health_assessment import assess_satellite_health_with_drift
from dop_calculations import parse_tle_data, calculate_dop_for_location, get_dop_quality
from visualization import (
    plot_individual_satellites, plot_combined_drift, plot_bounding_boxes,
    plot_sky_plot, plot_dop_over_time, plot_combined_inclination,
    plot_combined_altitude, plot_drift_distribution, plot_drift_vs_altitude,
    plot_constellation_coverage
)

# Initialize timescale globally
ts = load.timescale()

# Streamlit Configuration
st.set_page_config(page_title="GNSS Health Monitor", layout="wide")
st.title("🛰️ GNSS Health Monitor")

# ==================== SIDEBAR CONFIGURATION ====================

# Sidebar Configuration
st.sidebar.header("🔐 Space-Track Credentials")
username = st.sidebar.text_input("Username", value="", type="default")
password = st.sidebar.text_input("Password", value="", type="password")

st.sidebar.header("📅 Date Range")
start_date = st.sidebar.date_input("Start date", value=date(2025, 1, 1))
end_date = st.sidebar.date_input("End date", value=date(2025, 10, 1))
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

daily_only = st.sidebar.checkbox("Keep only one TLE per day (first entry)", value=True)

st.sidebar.header("⚙️ Analysis Parameters")
with st.sidebar.expander("Maneuver Detection", expanded=False):
    z_threshold = st.number_input("Z-Score Threshold", min_value=1.0, max_value=10.0, 
                                  value=DEFAULT_PARAMS["z_threshold"], step=0.5)
    sma_threshold = st.number_input("SMA Change Threshold (km)", min_value=0.1, 
                                    max_value=5.0, value=DEFAULT_PARAMS["sma_threshold"], step=0.1)
    inc_threshold = st.number_input("Inclination Change Threshold (degrees)", 
                                    min_value=0.001, max_value=0.1, value=DEFAULT_PARAMS["inc_threshold"], 
                                    step=0.001, format="%.3f")
    persist_window = st.number_input("Persistence Window", min_value=1, max_value=10, 
                                     value=DEFAULT_PARAMS["persist_window"], step=1)

with st.sidebar.expander("Health Assessment", expanded=False):
    inclination_tolerance = st.number_input("Inclination Tolerance (degrees)", 
                                           min_value=0.1, max_value=5.0, value=DEFAULT_PARAMS["inclination_tolerance"], step=0.1)
    drift_tolerance_gso = st.number_input("GSO Drift Tolerance (deg/day)", 
                                          min_value=0.01, max_value=0.5, value=DEFAULT_PARAMS["drift_tolerance_gso"], 
                                          step=0.01, format="%.2f")
    min_maneuvers_per_month = st.number_input("Min Maneuvers/Month", min_value=0, 
                                              max_value=10, value=DEFAULT_PARAMS["min_maneuvers_per_month"], step=1)
    max_maneuvers_per_month = st.number_input("Max Maneuvers/Month", min_value=1, 
                                              max_value=20, value=DEFAULT_PARAMS["max_maneuvers_per_month"], step=1)
    maneuver_uniformity_threshold = st.number_input("Maneuver Uniformity Threshold (CoV)", 
                                                   min_value=0.1, max_value=2.0, 
                                                   value=DEFAULT_PARAMS["maneuver_uniformity_threshold"], step=0.1)

# Constellation selection
st.sidebar.header("🛰️ Constellation")
constellation = st.sidebar.selectbox("Select constellation", ["NavIC", "QZSS", "BeiDou-3"], index=0)

# DOP Settings
st.sidebar.header("📡 DOP Settings")
elevation_mask_deg = st.sidebar.slider("Elevation Mask (°)", min_value=0, max_value=30, 
                                       value=DEFAULT_PARAMS["elevation_mask_deg"], step=1)
use_custom_location = st.sidebar.checkbox("Use custom DOP location", value=False)
custom_lat = 28.7  # Default value
custom_lon = 77.1  # Default value
if use_custom_location:
    custom_lat = st.sidebar.number_input("Latitude (°)", min_value=-90.0, max_value=90.0, 
                                         value=28.7, step=0.1, format="%.3f")
    custom_lon = st.sidebar.number_input("Longitude (°)", min_value=-180.0, max_value=180.0, 
                                         value=77.1, step=0.1, format="%.3f")

# Per-constellation configuration
if constellation == "NavIC":
    SAT_DICT = NAVIK_SATS
    SERVICE_REQS = None  # default in health module
    system_label = "NavIC"
    LOCATION_POINTS = INDIA_EXTREME_POINTS
    include_inactive_sats = st.sidebar.checkbox(
        "Include inactive satellites (IRNSS-1C, 1D, 1E) in DOP", value=False
    )
elif constellation == "QZSS":
    SAT_DICT = QZSS_SATS
    SERVICE_REQS = QZSS_SERVICE_REQUIREMENTS
    system_label = "QZSS"
    LOCATION_POINTS = JAPAN_KEY_POINTS
    include_inactive_sats = False
    st.sidebar.caption("QZSS: orbit correction roughly every six months.")
else:  # BeiDou-3
    SAT_DICT = BEIDOU3_SATS
    SERVICE_REQS = BEIDOU3_SERVICE_REQUIREMENTS
    system_label = "BeiDou-3"
    LOCATION_POINTS = CHINA_KEY_POINTS
    include_inactive_sats = False
    st.sidebar.caption("BeiDou-3: IGSO and GEO satellites for Asia-Pacific regional coverage.")

# Update page title for selected constellation
st.title(f"🛰️ GNSS Health Monitor - {system_label}")

# ==================== MAIN ANALYSIS ====================

# Main Analysis Button
if st.button("🚀 Fetch Data & Run Analysis", type="primary"):
    if not username or not password:
        st.error("❌ Please enter Space-Track username and password in the sidebar.")
    else:
        with st.spinner("🔄 Fetching satellite data..."):
            all_dfs = []
            errors = {}
            
            for sat_name, norad in SAT_DICT.items():
                try:
                    if norad is None:
                        raise ValueError(f"NORAD ID not set for {sat_name}. Please update QZSS_SATS in config.py.")
                    df = fetch_and_classify_satellite(
                        norad_id=int(norad),
                        start_date=start_date_str,
                        end_date=end_date_str,
                        username=username,
                        password=password,
                        igso_min=10,
                        deviation_tol=0.3
                    )

                    df['EPOCH'] = pd.to_datetime(df['EPOCH'])
                    df = df.sort_values('EPOCH').reset_index(drop=True)

                    if daily_only:
                        df['date'] = df['EPOCH'].dt.date
                        df = df.sort_values('EPOCH').groupby('date', as_index=False).first()
                        df['EPOCH'] = pd.to_datetime(df['EPOCH'])

                    df['satellite'] = sat_name

                    if 'mean_inclination' not in df.columns:
                        df['mean_inclination'] = df['INCLINATION'].mean()

                    all_dfs.append(df)

                except Exception as e:
                    errors[sat_name] = str(e)

            if errors:
                st.warning("⚠️ Some satellites failed to fetch:")
                for s, msg in errors.items():
                    st.write(f"- **{s}**: {msg}")

            if not all_dfs:
                st.error("❌ No data fetched for any satellite.")
            else:
                df_all = pd.concat(all_dfs, ignore_index=True, sort=False)
                
                # Store in session state
                st.session_state['df_all'] = df_all
                st.session_state['analysis_complete'] = True
                st.session_state['errors'] = errors
                
                st.success("✅ Data fetched successfully! Scroll down to see results.")

# ==================== RESULTS DISPLAY ====================

# Display results if analysis is complete
if st.session_state.get('analysis_complete', False):
    df_all = st.session_state['df_all']
    
    # ==================== HEALTH ASSESSMENT (MAIN) ====================
    st.header(f"🏥 {system_label} Satellite Health Assessment")
    
    maneuver_summary = []
    all_maneuvers_df = pd.DataFrame()
    health_assessments = []
    
    for sat_name in sorted(df_all['satellite'].unique()):
        sat_df = df_all[df_all['satellite'] == sat_name].copy()
        
        sat_detected = detect_navik_maneuvers(
            sat_df,
            sma_col='SEMIMAJOR_AXIS',
            inc_col='INCLINATION',
            z_thresh=z_threshold,
            sma_abs_thresh_km=sma_threshold,
            inc_abs_thresh_deg=inc_threshold,
            persist_window=int(persist_window)
        )
        
        ew_maneuvers = int(sat_detected['EW_MANEUVER'].sum()) if 'EW_MANEUVER' in sat_detected.columns else 0
        ns_maneuvers = int(sat_detected['NS_MANEUVER'].sum()) if 'NS_MANEUVER' in sat_detected.columns else 0
        
        maneuver_events = sat_detected[sat_detected['MANEUVER']].copy()
        maneuver_events['satellite'] = sat_name
        all_maneuvers_df = pd.concat([all_maneuvers_df, maneuver_events], ignore_index=True)
        
        maneuver_summary.append({
            'Satellite': sat_name,
            'E-W Maneuvers': ew_maneuvers,
            'N-S Maneuvers': ns_maneuvers,
            'Total Maneuvers': ew_maneuvers + ns_maneuvers,
            'Observation Period (days)': (sat_df['EPOCH'].max() - sat_df['EPOCH'].min()).days
        })
        
        health_data = assess_satellite_health_with_drift(
            sat_name, sat_df, maneuver_events,
            inclination_tolerance, min_maneuvers_per_month,
            max_maneuvers_per_month, maneuver_uniformity_threshold,
            drift_tolerance_gso, service_requirements=SERVICE_REQS
        )
        health_assessments.append(health_data)
    
    health_df = pd.DataFrame(health_assessments)
    
    st.dataframe(
        health_df[[
            'Satellite', 'Type', 'Health Status', 'Overall Score', 
            'Target Incl. (°)', 'Mean Incl. (°)', 'Incl. Dev. (°)',
            'Mean Drift (°/day)', 'Drift Status',
            'Maneuvers/Month', 'EW Maneuvers', 'NS Maneuvers'
        ]],
        hide_index=True,
        use_container_width=True
    )
    
    with st.expander("📋 View Detailed Health Remarks"):
        for _, row in health_df.iterrows():
            st.markdown(f"### {row['Satellite']} ({row['Type']}) - {row['Health Status']}")
            st.markdown(f"**Overall Score:** {row['Overall Score']}/100")
            st.markdown("**Remarks:**")
            for remark in row['Remarks'].split(' | '):
                st.markdown(f"- {remark}")
            st.markdown("---")
    
    st.divider()
    
    # ==================== ADDITIONAL ANALYSIS (EXPANDABLE) ====================
    
    # Longitudinal Drift Analysis
    with st.expander("🌍 Longitudinal Drift Analysis", expanded=False):
        drift_summary = []
        for sat_name in sorted(df_all['satellite'].unique()):
            sat_df = df_all[df_all['satellite'] == sat_name].copy()
            
            if 'LonDrift_deg_per_day' in sat_df.columns:
                mean_drift = sat_df['LonDrift_deg_per_day'].mean()
                current_drift = sat_df['LonDrift_deg_per_day'].iloc[-1]
                std_drift = sat_df['LonDrift_deg_per_day'].std()
                
                # Determine satellite type
                mean_incl = sat_df['INCLINATION'].mean()
                if 0.0 < mean_incl < 10.0:
                    sat_type = 'GSO'
                else:
                    sat_type = 'IGSO'
                
                drift_assessment = assess_drift_health(mean_drift, sat_type, drift_tolerance_gso)
                
                drift_direction = get_drift_direction(mean_drift)
                
                drift_summary.append({
                    'Satellite': sat_name,
                    'Type': sat_type,
                    'Mean Drift (°/day)': round(mean_drift, 4),
                    'Current Drift (°/day)': round(current_drift, 4),
                    'Std Dev (°/day)': round(std_drift, 4),
                    'Direction': drift_direction,
                    'Drift Status': f"{drift_assessment['drift_color']} {drift_assessment['drift_status']}",
                    'Drift Score': round(drift_assessment['drift_score'], 1)
                })
        
        drift_summary_df = pd.DataFrame(drift_summary)
        st.dataframe(drift_summary_df, hide_index=True, use_container_width=True)
        st.caption(f"**GSO Drift Tolerance:** ±{drift_tolerance_gso}°/day | Positive = Eastward, Negative = Westward")
    
    # Satellite Classification
    with st.expander("🔍 Satellite Classification Summary", expanded=False):
        sat_summary = []
        for sat_name in sorted(df_all['satellite'].unique()):
            sub = df_all[df_all['satellite'] == sat_name]
            mean_incl = sub['INCLINATION'].mean() if not sub.empty else float('nan')
            mean_alt = sub['altitude_km'].mean() if not sub.empty and 'altitude_km' in sub.columns else float('nan')
            mean_drift = sub['LonDrift_deg_per_day'].mean() if 'LonDrift_deg_per_day' in sub.columns else float('nan')
            
            if 0.0 < mean_incl < 10.0:
                sat_type = 'GSO'
            elif mean_incl >= 10.0:
                sat_type = 'IGSO'
            else:
                sat_type = 'Unclassified'
            
            sat_summary.append({
                'Satellite': sat_name,
                'Mean Inclination (°)': round(mean_incl, 3) if not sub.empty else None,
                'Mean Altitude (km)': round(mean_alt, 2) if not pd.isna(mean_alt) else None,
                'Mean Drift (°/day)': round(mean_drift, 4) if not pd.isna(mean_drift) else None,
                'Classified Type': sat_type
            })
        sat_summary_df = pd.DataFrame(sat_summary)
        st.dataframe(sat_summary_df, hide_index=True, use_container_width=True)
    
    # Maneuver Summary
    with st.expander("🛠️ Maneuver Detection Summary", expanded=False):
        maneuver_summary_df = pd.DataFrame(maneuver_summary)
        st.caption(f"Detection settings: Z-score ≥ {z_threshold}, SMA ≥ {sma_threshold} km, Inclination ≥ {inc_threshold}°, Window = {int(persist_window)}")
        st.dataframe(maneuver_summary_df, hide_index=True, use_container_width=True)
    
    # ==================== DOP ANALYSIS (EXPANDABLE) ====================
    with st.expander("📡 Dilution of Precision (DOP) Analysis", expanded=False):
        try:
            norad_ids = [nid for nid in SAT_DICT.values() if nid is not None]
            tle_data = fetch_multiple_tles(norad_ids, username, password)
            
            if not tle_data:
                st.error("❌ Failed to fetch TLE data for DOP calculations")
            else:
                satellites = parse_tle_data(tle_data, SAT_DICT)
                
                if len(satellites) == 0:
                    st.error("❌ No satellites parsed from TLE data")
                else:
                    # Filter out inactive satellites if toggle is off
                    original_count = len(satellites)
                    if system_label == "NavIC" and not include_inactive_sats:
                        satellites = {name: sat for name, sat in satellites.items() if name not in INACTIVE_SATELLITES}
                        inactive_count = original_count - len(satellites)
                        if inactive_count > 0:
                            st.info(f"📋 Excluding {inactive_count} inactive satellites (IRNSS-1C, 1D, 1E) from DOP calculations")
                    
                    st.success(f"✅ Successfully loaded {len(satellites)} satellites for DOP calculations")
                    
                    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
                    st.caption(f"Calculation Time (UTC): {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    dop_results = []
                    last_sat_positions = None
                    last_location_meta = None
                    
                    if use_custom_location:
                        lat, lon = float(custom_lat), float(custom_lon)
                        location_name = f"Custom ({lat:.3f}, {lon:.3f})"
                        dop, visible_sats, sat_positions = calculate_dop_for_location(
                            satellites, lat, lon, current_time, elevation_mask_deg=elevation_mask_deg
                        )
                        last_sat_positions = sat_positions
                        last_location_meta = {'name': location_name, 'lat': lat, 'lon': lon}
                        
                        if dop:
                            quality = get_dop_quality(dop['GDOP'])
                            
                            dop_results.append({
                                'Location': location_name,
                                'Latitude': lat,
                                'Longitude': lon,
                                'Visible Sats': len(visible_sats),
                                'GDOP': round(dop['GDOP'], 2),
                                'PDOP': round(dop['PDOP'], 2),
                                'HDOP': round(dop['HDOP'], 2),
                                'VDOP': round(dop['VDOP'], 2),
                                'TDOP': round(dop['TDOP'], 2),
                                'Quality': quality
                            })
                        else:
                            dop_results.append({
                                'Location': location_name,
                                'Latitude': lat,
                                'Longitude': lon,
                                'Visible Sats': len(visible_sats),
                                'GDOP': None,
                                'PDOP': None,
                                'HDOP': None,
                                'VDOP': None,
                                'TDOP': None,
                                'Quality': 'N/A'
                            })
                    else:
                        for location_name, (lat, lon) in LOCATION_POINTS.items():
                            dop, visible_sats, sat_positions = calculate_dop_for_location(
                                satellites, lat, lon, current_time, elevation_mask_deg=elevation_mask_deg
                            )
                            
                            if dop:
                                quality = get_dop_quality(dop['GDOP'])
                                
                                dop_results.append({
                                    'Location': location_name,
                                    'Latitude': lat,
                                    'Longitude': lon,
                                    'Visible Sats': len(visible_sats),
                                    'GDOP': round(dop['GDOP'], 2),
                                    'PDOP': round(dop['PDOP'], 2),
                                    'HDOP': round(dop['HDOP'], 2),
                                    'VDOP': round(dop['VDOP'], 2),
                                    'TDOP': round(dop['TDOP'], 2),
                                    'Quality': quality
                                })
                            else:
                                dop_results.append({
                                    'Location': location_name,
                                    'Latitude': lat,
                                    'Longitude': lon,
                                    'Visible Sats': len(visible_sats),
                                    'GDOP': None,
                                    'PDOP': None,
                                    'HDOP': None,
                                    'VDOP': None,
                                    'TDOP': None,
                                    'Quality': 'N/A'
                                })
                    
                    dop_df = pd.DataFrame(dop_results)
                    st.dataframe(dop_df, hide_index=True, use_container_width=True)
                    
                    st.caption("**DOP Quality Guide:** Excellent: <2 | Good: 2-4 | Moderate: 4-6 | Fair: 6-8 | Poor: >8")
                    st.caption(f"Elevation mask: {elevation_mask_deg}°")
                    
                    # Store for plotting
                    st.session_state['satellites_dop'] = satellites
                    st.session_state['dop_results'] = dop_results
                    st.session_state['current_time'] = current_time
                    st.session_state['elevation_mask_deg'] = elevation_mask_deg
                    if last_sat_positions is not None and last_location_meta is not None:
                        st.session_state['last_sat_positions'] = last_sat_positions
                        st.session_state['last_location_meta'] = last_location_meta
                    
                    # Display constellation coverage map
                    # Commented out for now
                    # st.divider()
                    # plot_constellation_coverage(
                    #     satellites, 
                    #     current_time, 
                    #     LOCATION_POINTS, 
                    #     system_label=system_label,
                    #     elevation_mask_deg=elevation_mask_deg
                    # )
                    
        except Exception as e:
            st.error(f"❌ Error during DOP analysis: {str(e)}")
    
    # ==================== VISUALIZATIONS (EXPANDABLE) ====================
    with st.expander("📊 Visualizations & Plots", expanded=False):
        show_plots = st.button("🎨 Generate All Plots", type="primary")
        
        if show_plots or st.session_state.get('show_plots', False):
            st.session_state['show_plots'] = True
            
            # Individual satellite plots
            plot_individual_satellites(df_all)
            
            # Combined drift plot
            plot_combined_drift(df_all, system_label=system_label)
            
            # Satellite bounding box plots
            if st.session_state.get('satellites_dop') and st.session_state.get('current_time'):
                satellites = st.session_state['satellites_dop']
                reference_time = st.session_state['current_time']
                
                plot_bounding_boxes(satellites, reference_time)
            else:
                st.info("Bounding box plots require DOP analysis data. Please ensure DOP analysis completed successfully.")
            
            # Azimuth-Elevation Sky Plot
            if st.session_state.get('satellites_dop') and st.session_state.get('current_time'):
                satellites = st.session_state['satellites_dop']
                current_time = st.session_state['current_time']
                elevation_mask = st.session_state.get('elevation_mask_deg', elevation_mask_deg)
                
                # Let user select location for sky plot
                if use_custom_location:
                    sky_plot_lat = custom_lat
                    sky_plot_lon = custom_lon
                    sky_plot_name = f"Custom ({sky_plot_lat:.3f}, {sky_plot_lon:.3f})"
                else:
                    sky_plot_location = st.selectbox("Select Location for Sky Plot", list(LOCATION_POINTS.keys()))
                    sky_plot_lat, sky_plot_lon = LOCATION_POINTS[sky_plot_location]
                    sky_plot_name = sky_plot_location
                
                # Calculate satellite positions for selected location
                with st.spinner(f"Calculating satellite positions for {sky_plot_name}..."):
                    dop, visible_sats, sat_positions = calculate_dop_for_location(
                        satellites, sky_plot_lat, sky_plot_lon, current_time, 
                        elevation_mask_deg=elevation_mask
                    )
                    loc_meta = {'name': sky_plot_name, 'lat': sky_plot_lat, 'lon': sky_plot_lon}
                    
                    plot_sky_plot(satellites, sat_positions, loc_meta, elevation_mask)

            # DOP Over Last 30 Days Plot
            if st.session_state.get('satellites_dop') and st.session_state.get('dop_results'):
                satellites = st.session_state['satellites_dop']
                
                if use_custom_location:
                    selected_location = None
                else:
                    location_options = list(LOCATION_POINTS.keys())
                    selected_location = st.selectbox("Select Location for DOP Time Series", location_options)
                
                if use_custom_location or selected_location:
                    plot_dop_over_time(satellites, use_custom_location, custom_lat, custom_lon, 
                                      elevation_mask_deg, selected_location, LOCATION_POINTS)
            
            # Combined plots
            plot_combined_inclination(df_all, system_label=system_label)
            plot_combined_altitude(df_all, system_label=system_label)
            plot_drift_distribution(df_all)
            plot_drift_vs_altitude(df_all)

else:
    st.info("👆 Select a constellation and click the button in the sidebar to start the analysis")
    st.markdown("""
    ### Welcome to GNSS Constellation Monitoring System
    
    This application provides comprehensive monitoring and analysis for multiple GNSS constellations including **NavIC**, **QZSS**, and **BeiDou-3**:
    
    - **🌍 Longitudinal Drift Analysis**: Track east-west drift for station-keeping assessment
    - **🏥 Enhanced Health Assessment**: Comprehensive health scoring including drift considerations
    - **🔍 Satellite Classification**: GSO/IGSO classification based on inclination
    - **🛠️ Advanced Maneuver Detection**: Detects both E-W and N-S orbital correction maneuvers
    - **📡 DOP Analysis**: Dilution of Precision calculations for regional locations
    - **📊 Rich Visualizations**: Time series plots for inclination, altitude, drift, and DOP values
    
    **Supported Constellations:**
    - **NavIC (IRNSS)**: 7 satellites with DOP analysis for 5 Indian locations
    - **QZSS (Michibiki)**: 5 satellites with DOP analysis for 5 Japanese locations
    - **BeiDou-3**: IGSO & GEO satellites with DOP analysis for 10 Chinese locations
    
    **Key Features:**
    - **Drift Monitoring**: Calculate longitudinal drift based on mean motion deviation from geosynchronous rate
    - **Drift Direction**: Identify eastward (positive) or westward (negative) drift patterns
    - **Station-Keeping Health**: Assess GSO satellites' ability to maintain their assigned longitude
    - **Maneuver Correlation**: Link drift changes to station-keeping maneuvers
    
    **To get started:**
    1. Select a constellation from the sidebar (NavIC, QZSS, or BeiDou-3)
    2. Enter your Space-Track credentials in the sidebar
    3. Select the date range for analysis
    4. Adjust analysis parameters if needed (including drift tolerance)
    5. Click "Fetch Data & Run Analysis"
    
    **Understanding Drift:**
    - **Zero drift (0°/day)**: Perfect geostationary orbit
    - **Positive drift**: Satellite moving eastward (orbiting faster than Earth)
    - **Negative drift**: Satellite moving westward (orbiting slower than Earth)
    - **GSO tolerance**: Typically ±0.05°/day for good station-keeping
    """)
