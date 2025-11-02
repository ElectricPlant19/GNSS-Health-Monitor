"""
Visualization Module
Handles all plotting and visualization functions for the NavIC monitoring system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, timezone
from config import INACTIVE_SATELLITES
from dop_calculations import calculate_dop_for_location, calculate_bounding_boxes


def plot_individual_satellites(df_all):
    """Plot individual satellite data (inclination, altitude, drift)."""
    st.subheader("Individual Satellite Plots")
    
    for sat_name in sorted(df_all['satellite'].unique()):
        sat_df = df_all[df_all['satellite'] == sat_name].copy()
        
        st.markdown(f"### {sat_name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_incl = px.line(
                sat_df,
                x='EPOCH',
                y='INCLINATION',
                markers=True,
                title=f"{sat_name} - Inclination Over Time",
                labels={'EPOCH': 'Epoch', 'INCLINATION': 'Inclination (°)'},
                hover_data=['INCLINATION', 'type']
            )
            fig_incl.update_traces(line_color='#636EFA')
            fig_incl.update_layout(hovermode='x unified', showlegend=False)
            st.plotly_chart(fig_incl, use_container_width=True)
        
        with col2:
            if 'altitude_km' in sat_df.columns and not sat_df['altitude_km'].isna().all():
                fig_alt = px.line(
                    sat_df,
                    x='EPOCH',
                    y='altitude_km',
                    markers=True,
                    title=f"{sat_name} - Altitude Above Surface",
                    labels={'EPOCH': 'Epoch', 'altitude_km': 'Altitude (km)'}
                )
                fig_alt.update_traces(line_color='#EF553B')
                fig_alt.update_layout(hovermode='x unified', showlegend=False)
                st.plotly_chart(fig_alt, use_container_width=True)
            else:
                st.info(f"No altitude data available for {sat_name}")
        
        # Drift plot
        if 'LonDrift_deg_per_day' in sat_df.columns and not sat_df['LonDrift_deg_per_day'].isna().all():
            fig_drift = px.line(
                sat_df,
                x='EPOCH',
                y='LonDrift_deg_per_day',
                markers=True,
                title=f"{sat_name} - Longitudinal Drift Over Time",
                labels={'EPOCH': 'Epoch', 'LonDrift_deg_per_day': 'Drift (°/day)'}
            )
            fig_drift.update_traces(line_color='#00CC96')
            fig_drift.update_layout(hovermode='x unified', showlegend=False)
            
            # Add zero line for reference
            fig_drift.add_hline(y=0, line_dash="dash", line_color="gray", 
                               annotation_text="Zero Drift", annotation_position="right")
            
            st.plotly_chart(fig_drift, use_container_width=True)
        
        st.markdown("---")


def plot_combined_drift(df_all, system_label="NavIC"):
    """Plot combined drift comparison for all satellites."""
    if 'LonDrift_deg_per_day' in df_all.columns:
        st.subheader("All Satellites - Drift Comparison")
        fig_all_drift = px.line(
            df_all[df_all['LonDrift_deg_per_day'].notna()],
            x='EPOCH',
            y='LonDrift_deg_per_day',
            color='satellite',
            markers=False,
            title=f"All {system_label} Satellites - Longitudinal Drift Over Time",
            labels={'EPOCH': 'Epoch', 'LonDrift_deg_per_day': 'Drift (°/day)', 'satellite': 'Satellite'}
        )
        fig_all_drift.add_hline(y=0, line_dash="dash", line_color="white", 
                               annotation_text="Zero Drift", annotation_position="right")
        fig_all_drift.update_layout(hovermode='x unified', height=500)
        st.plotly_chart(fig_all_drift, use_container_width=True)


def plot_bounding_boxes(satellites, reference_time, timestep_minutes=15, prop_duration_days=1.5):
    """Plot satellite ground track bounding boxes."""
    st.subheader("🗺️ Satellite Ground Track Bounding Boxes")
    st.caption("Shows the geographic coverage area for each satellite over the next 1.5 days")
    
    with st.spinner("Calculating satellite ground tracks..."):
        bounding_boxes = calculate_bounding_boxes(
            satellites, 
            reference_time, 
            timestep_minutes=timestep_minutes, 
            prop_duration_days=prop_duration_days
        )
        
        if bounding_boxes:
            for sat_name, box_data in bounding_boxes.items():
                st.markdown(f"#### {sat_name} Ground Track")
                
                fig = go.Figure()
                
                fig.add_trace(go.Scattergeo(
                    lon=box_data['longitudes'],
                    lat=box_data['latitudes'],
                    mode='lines+markers',
                    name=sat_name,
                    marker=dict(size=3),
                    line=dict(width=2)
                ))
                
                box_lons = [
                    box_data['min_lon'], box_data['max_lon'], 
                    box_data['max_lon'], box_data['min_lon'], 
                    box_data['min_lon']
                ]
                box_lats = [
                    box_data['min_lat'], box_data['min_lat'], 
                    box_data['max_lat'], box_data['max_lat'], 
                    box_data['min_lat']
                ]
                
                fig.add_trace(go.Scattergeo(
                    lon=box_lons,
                    lat=box_lats,
                    mode='lines',
                    name='Bounding Box',
                    line=dict(color='red', width=2, dash='dash')
                ))
                
                fig.add_trace(go.Scattergeo(
                    lon=[box_data['mean_lon']],
                    lat=[box_data['mean_lat']],
                    mode='markers',
                    name='Center',
                    marker=dict(size=10, color='red', symbol='x')
                ))
                
                fig.update_geos(
                    projection_type="natural earth",
                    showland=True,
                    landcolor="lightgray",
                    showocean=True,
                    oceancolor="lightblue",
                    showcountries=True,
                    countrycolor="white",
                    showlakes=True,
                    lakecolor="lightblue",
                    center=dict(lon=box_data['mean_lon'], lat=box_data['mean_lat']),
                    projection_scale=3
                )
                
                fig.update_layout(
                    title=f"{sat_name} - Geographic Coverage (1.5 days)",
                    height=500,
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Longitude Range", 
                             f"{box_data['min_lon']:.2f}° to {box_data['max_lon']:.2f}°")
                with col2:
                    st.metric("Latitude Range", 
                             f"{box_data['min_lat']:.2f}° to {box_data['max_lat']:.2f}°")
                with col3:
                    st.metric("Center Position", 
                             f"({box_data['mean_lat']:.2f}°, {box_data['mean_lon']:.2f}°)")
                
                st.markdown("---")
            
            plot_combined_ground_tracks(bounding_boxes)
        else:
            st.warning("No bounding box data available for plotting.")


def plot_combined_ground_tracks(bounding_boxes, system_label="NavIC"):
    """Plot combined ground tracks for all satellites."""
    st.markdown("#### All Satellites - Combined Ground Tracks")
    
    fig_combined = go.Figure()
    
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692']
    
    for idx, (sat_name, box_data) in enumerate(bounding_boxes.items()):
        color = colors[idx % len(colors)]
        
        fig_combined.add_trace(go.Scattergeo(
            lon=box_data['longitudes'],
            lat=box_data['latitudes'],
            mode='lines',
            name=sat_name,
            line=dict(width=2, color=color),
            showlegend=True
        ))
    
    fig_combined.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="lightgray",
        showocean=True,
        oceancolor="lightblue",
        showcountries=True,
        countrycolor="white",
        showlakes=True,
        lakecolor="lightblue",
        center=dict(lon=80, lat=20),
        projection_scale=2
    )
    
    fig_combined.update_layout(
        title=f"All {system_label} Satellites - Combined Ground Tracks",
        height=600,
        showlegend=True
    )
    
    st.plotly_chart(fig_combined, use_container_width=True)


def plot_sky_plot(satellites, sat_positions, location_meta, elevation_mask_deg):
    """Plot azimuth-elevation sky plot."""
    # Note: Title is now set in main_app.py, so we don't duplicate it here
    
    # Prepare polar coordinates: r = 90 - elevation (so zenith at center), theta = azimuth
    az_list = []
    r_list = []
    names = []
    elev_list = []
    hover_text = []
    
    for name, pos in zip([s for s in satellites.keys()], sat_positions):
        if pos is None:
            continue
        if pos['elevation'] > elevation_mask_deg:
            az_list.append(pos['azimuth'])
            r_list.append(max(0, 90 - pos['elevation']))
            names.append(name)
            elev_list.append(pos['elevation'])
            hover_text.append(
                f"<b>{name}</b><br>" +
                f"Azimuth: {pos['azimuth']:.1f}°<br>" +
                f"Elevation: {pos['elevation']:.1f}°<br>" +
                f"Distance: {pos['distance']:.0f} km"
            )
    
    if len(az_list) > 0:
        fig_sky = go.Figure()
        
        # Color code by elevation (higher elevation = darker color)
        fig_sky.add_trace(go.Scatterpolar(
            r=r_list,
            theta=az_list,
            mode='markers+text',
            text=names,
            textposition='top center',
            hovertext=hover_text,
            hoverinfo='text',
            marker=dict(
                size=12,
                color=elev_list,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title="Elevation (°)",
                    thickness=15,
                    len=0.7
                ),
                line=dict(width=1, color='white')
            ),
            textfont=dict(size=9)
        ))
        
        fig_sky.update_layout(
            title=dict(
                text=f"Sky Plot at {location_meta['name']}<br><sub>Elevation mask: {elevation_mask_deg}° | {len(names)} visible satellites</sub>",
                x=0.5,
                xanchor='center'
            ),
            polar=dict(
                radialaxis=dict(
                    range=[0, 90], 
                    tickvals=[0, 30, 60, 90], 
                    ticktext=['Zenith (90°)', '60°', '30°', f'Horizon ({elevation_mask_deg}°)'],
                    showline=True,
                    linewidth=2
                ),
                angularaxis=dict(
                    direction='clockwise', 
                    rotation=90,
                    tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                    ticktext=['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
                ),
                bgcolor='rgba(240, 240, 240, 0.3)'
            ),
            showlegend=False,
            height=600,
            margin=dict(t=80, b=40)
        )
        
        st.plotly_chart(fig_sky, use_container_width=True)
        
        # Add summary table
        st.caption(f"**Location:** {location_meta['name']} ({location_meta['lat']:.3f}°, {location_meta['lon']:.3f}°)")
        
    else:
        st.info(f"No satellites above the {elevation_mask_deg}° elevation mask at this time for {location_meta['name']}.")


def plot_dop_over_time(satellites, use_custom_location, custom_lat, custom_lon, 
                      elevation_mask_deg, selected_location=None, location_points=None):
    """Plot DOP values over the last 30 days."""
    st.subheader("📡 DOP Over Last 30 Days")
    
    if use_custom_location:
        lat, lon = float(custom_lat), float(custom_lon)
        timeseries_location_name = f"Custom ({lat:.3f}, {lon:.3f})"
    else:
        if selected_location and location_points:
            lat, lon = location_points[selected_location]
            timeseries_location_name = selected_location
        else:
            st.warning("Please select a location for DOP time series")
            return
    
    with st.spinner(f"Calculating DOP over time for {timeseries_location_name}..."):
        current_time = datetime.now(timezone.utc)
        time_points = []
        gdop_values = []
        pdop_values = []
        hdop_values = []
        vdop_values = []
        visible_sat_counts = []
        
        for hours in range(0, 30*24, 6):
            calc_time = current_time - timedelta(hours=hours)
            dop, visible_sats, _ = calculate_dop_for_location(
                satellites, lat, lon, calc_time, elevation_mask_deg=elevation_mask_deg
            )
            
            time_points.append(calc_time)
            visible_sat_counts.append(len(visible_sats))
            
            if dop:
                gdop_values.append(dop['GDOP'])
                pdop_values.append(dop['PDOP'])
                hdop_values.append(dop['HDOP'])
                vdop_values.append(dop['VDOP'])
            else:
                gdop_values.append(None)
                pdop_values.append(None)
                hdop_values.append(None)
                vdop_values.append(None)
        
        # Reverse all lists to show chronological order (oldest to newest)
        time_points.reverse()
        gdop_values.reverse()
        pdop_values.reverse()
        hdop_values.reverse()
        vdop_values.reverse()
        visible_sat_counts.reverse()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(f'DOP Values Over Last 30 Days - {timeseries_location_name}', 
                          'Visible Satellites Count'),
            vertical_spacing=0.15
        )
        
        fig.add_trace(
            go.Scatter(x=time_points, y=gdop_values, name='GDOP', 
                     line=dict(color='#636EFA')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=time_points, y=pdop_values, name='PDOP', 
                     line=dict(color='#EF553B')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=time_points, y=hdop_values, name='HDOP', 
                     line=dict(color='#00CC96')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=time_points, y=vdop_values, name='VDOP', 
                     line=dict(color='#AB63FA')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=time_points, y=visible_sat_counts, name='Visible Satellites',
                     line=dict(color='#FFA15A'), fill='tozeroy'),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="DOP Value", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=2, col=1)
        
        fig.update_layout(height=800, showlegend=True, hovermode='x unified')
        
        st.plotly_chart(fig, use_container_width=True)


def plot_combined_inclination(df_all, system_label="NavIC"):
    """Plot combined inclination comparison for all satellites."""
    st.subheader("📈 All Satellites - Inclination Comparison")
    fig_all_incl = px.line(
        df_all,
        x='EPOCH',
        y='INCLINATION',
        color='satellite',
        markers=False,
        title=f"All {system_label} Satellites - Inclination Over Time",
        labels={'EPOCH': 'Epoch', 'INCLINATION': 'Inclination (°)', 'satellite': 'Satellite'}
    )
    fig_all_incl.update_layout(hovermode='x unified', height=500)
    st.plotly_chart(fig_all_incl, use_container_width=True)


def plot_combined_altitude(df_all, system_label="NavIC"):
    """Plot combined altitude comparison for all satellites."""
    if 'altitude_km' in df_all.columns and not df_all['altitude_km'].isna().all():
        st.subheader("🛰️ All Satellites - Altitude Comparison")
        fig_all_alt = px.line(
            df_all[df_all['altitude_km'].notna()],
            x='EPOCH',
            y='altitude_km',
            color='satellite',
            markers=False,
            title=f"All {system_label} Satellites - Altitude Over Time",
            labels={'EPOCH': 'Epoch', 'altitude_km': 'Altitude (km)', 'satellite': 'Satellite'}
        )
        fig_all_alt.update_layout(hovermode='x unified', height=500)
        st.plotly_chart(fig_all_alt, use_container_width=True)


def plot_drift_distribution(df_all):
    """Plot drift distribution analysis."""
    if 'LonDrift_deg_per_day' in df_all.columns:
        st.subheader("📊 Drift Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram of drift values
            fig_hist = px.histogram(
                df_all[df_all['LonDrift_deg_per_day'].notna()],
                x='LonDrift_deg_per_day',
                color='satellite',
                title="Drift Distribution by Satellite",
                labels={'LonDrift_deg_per_day': 'Drift (°/day)', 'count': 'Frequency'},
                nbins=50,
                marginal="box"
            )
            fig_hist.update_layout(height=500)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Box plot of drift by satellite type
            df_all_with_type = df_all.copy()
            df_all_with_type['sat_type'] = df_all_with_type['INCLINATION'].apply(
                lambda x: 'GSO' if (0.0 < x < 10.0) else ('IGSO' if x >= 10.0 else 'Unclassified')
            )
            
            fig_box = px.box(
                df_all_with_type[df_all_with_type['LonDrift_deg_per_day'].notna()],
                x='sat_type',
                y='LonDrift_deg_per_day',
                color='sat_type',
                title="Drift Distribution by Satellite Type",
                labels={'LonDrift_deg_per_day': 'Drift (°/day)', 'sat_type': 'Satellite Type'}
            )
            fig_box.add_hline(y=0, line_dash="dash", line_color="gray")
            fig_box.update_layout(height=500)
            st.plotly_chart(fig_box, use_container_width=True)


def plot_drift_vs_altitude(df_all):
    """Plot drift vs altitude correlation."""
    if 'LonDrift_deg_per_day' in df_all.columns and 'altitude_km' in df_all.columns:
        st.subheader("🔬 Drift vs Altitude Correlation")
        
        fig_scatter = px.scatter(
            df_all[(df_all['LonDrift_deg_per_day'].notna()) & (df_all['altitude_km'].notna())],
            x='altitude_km',
            y='LonDrift_deg_per_day',
            color='satellite',
            title="Longitudinal Drift vs Altitude",
            labels={'altitude_km': 'Altitude (km)', 'LonDrift_deg_per_day': 'Drift (°/day)'},
            hover_data=['EPOCH', 'INCLINATION']
        )
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="gray", 
                             annotation_text="Zero Drift", annotation_position="right")
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)


def plot_constellation_coverage(satellites, current_time, location_points, system_label="GNSS", elevation_mask_deg=5):
    """
    Plot geographic coverage/field of view for a GNSS constellation.
    Shows satellite ground tracks, footprints, and coverage areas.
    
    Args:
        satellites: Dictionary of satellite objects from skyfield
        current_time: Current time for position calculation (datetime or Skyfield Time)
        location_points: Dictionary of location names and (lat, lon) tuples
        system_label: Name of the constellation (NavIC, QZSS, BeiDou-3)
        elevation_mask_deg: Minimum elevation angle for visibility
    """
    import numpy as np
    from skyfield.api import wgs84, load
    from datetime import datetime
    
    st.subheader(f"🌍 {system_label} Constellation Coverage Map")
    
    # Convert datetime to Skyfield Time if needed
    if isinstance(current_time, datetime):
        ts = load.timescale()
        skyfield_time = ts.from_datetime(current_time)
        display_time = current_time
    else:
        skyfield_time = current_time
        display_time = skyfield_time.utc_datetime()
    
    # Create figure
    fig = go.Figure()
    
    # Add world map coastlines
    fig.update_geos(
        projection_type="natural earth",
        showland=True,
        landcolor="rgb(243, 243, 243)",
        coastlinecolor="rgb(204, 204, 204)",
        showocean=True,
        oceancolor="rgb(230, 245, 255)",
        showcountries=True,
        countrycolor="rgb(204, 204, 204)"
    )
    
    # Calculate satellite positions and footprints
    sat_positions = []
    colors = px.colors.qualitative.Plotly
    
    for idx, (sat_name, sat) in enumerate(satellites.items()):
        try:
            # Get satellite position
            geocentric = sat.at(skyfield_time)
            subpoint = wgs84.subpoint(geocentric)
            
            lat = subpoint.latitude.degrees
            lon = subpoint.longitude.degrees
            alt_km = subpoint.elevation.km
            
            sat_positions.append({
                'name': sat_name,
                'lat': lat,
                'lon': lon,
                'alt_km': alt_km
            })
            
            # Calculate satellite footprint (visibility circle)
            # Earth radius in km
            earth_radius = 6371.0
            
            # Calculate the angular radius of visibility from satellite altitude
            # For a satellite at height h, the horizon angle from Earth center is:
            # cos(theta) = R / (R + h), where R is Earth radius
            
            # Maximum visibility angle (horizon to horizon)
            cos_max_angle = earth_radius / (earth_radius + alt_km)
            max_angle_rad = np.arccos(cos_max_angle)
            
            # Adjust for elevation mask
            if elevation_mask_deg > 0:
                # Reduce the coverage angle based on elevation mask
                # The grazing angle at horizon is 90°, subtract elevation mask
                elevation_rad = np.radians(elevation_mask_deg)
                # Adjust the maximum angle
                adjusted_angle_rad = max_angle_rad - elevation_rad
                footprint_radius_deg = np.degrees(adjusted_angle_rad)
            else:
                footprint_radius_deg = np.degrees(max_angle_rad)
            
            # Create circle points for footprint using proper spherical geometry
            circle_points = 64
            angles = np.linspace(0, 2*np.pi, circle_points)
            
            # Convert to radians
            lat_rad = np.radians(lat)
            lon_rad = np.radians(lon)
            radius_rad = np.radians(footprint_radius_deg)
            
            footprint_lats = []
            footprint_lons = []
            
            for angle in angles:
                # Use spherical trigonometry to calculate points on circle
                # Formula for points on a small circle on a sphere
                new_lat = np.arcsin(
                    np.sin(lat_rad) * np.cos(radius_rad) +
                    np.cos(lat_rad) * np.sin(radius_rad) * np.cos(angle)
                )
                
                new_lon = lon_rad + np.arctan2(
                    np.sin(angle) * np.sin(radius_rad) * np.cos(lat_rad),
                    np.cos(radius_rad) - np.sin(lat_rad) * np.sin(new_lat)
                )
                
                # Convert back to degrees
                footprint_lats.append(np.degrees(new_lat))
                footprint_lons.append(np.degrees(new_lon))
            
            # Close the circle
            footprint_lats.append(footprint_lats[0])
            footprint_lons.append(footprint_lons[0])
            
            # Add footprint circle
            color = colors[idx % len(colors)]
            fig.add_trace(go.Scattergeo(
                lon=footprint_lons,
                lat=footprint_lats,
                mode='lines',
                line=dict(width=1.5, color=color),
                name=f"{sat_name} Footprint",
                showlegend=True,
                hoverinfo='skip'
            ))
            
            # Add satellite position marker
            fig.add_trace(go.Scattergeo(
                lon=[lon],
                lat=[lat],
                mode='markers+text',
                marker=dict(size=12, color=color, symbol='star'),
                text=[sat_name.split('-')[-1] if '-' in sat_name else sat_name[:4]],
                textposition="top center",
                textfont=dict(size=9, color=color),
                name=sat_name,
                showlegend=False,
                hovertemplate=f"<b>{sat_name}</b><br>" +
                             f"Lat: {lat:.2f}°<br>" +
                             f"Lon: {lon:.2f}°<br>" +
                             f"Alt: {alt_km:.0f} km<br>" +
                             "<extra></extra>"
            ))
            
        except Exception as e:
            st.warning(f"Could not calculate position for {sat_name}: {str(e)}")
            continue
    
    # Add location points
    if location_points:
        loc_lats = []
        loc_lons = []
        loc_names = []
        
        for name, (lat, lon) in location_points.items():
            loc_lats.append(lat)
            loc_lons.append(lon)
            loc_names.append(name)
        
        fig.add_trace(go.Scattergeo(
            lon=loc_lons,
            lat=loc_lats,
            mode='markers+text',
            marker=dict(size=8, color='red', symbol='circle'),
            text=loc_names,
            textposition="bottom center",
            textfont=dict(size=8, color='darkred'),
            name="Key Locations",
            showlegend=True,
            hovertemplate="<b>%{text}</b><br>" +
                         "Lat: %{lat:.2f}°<br>" +
                         "Lon: %{lon:.2f}°<br>" +
                         "<extra></extra>"
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"{system_label} Satellite Coverage at {display_time.strftime('%Y-%m-%d %H:%M UTC')}<br>" +
                 f"<sub>Footprints show visibility area (elevation mask: {elevation_mask_deg}°)</sub>",
            x=0.5,
            xanchor='center'
        ),
        height=600,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)"
        ),
        margin=dict(l=0, r=0, t=80, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display satellite position summary
    if sat_positions:
        st.caption(f"**{len(sat_positions)} satellites** displayed with their ground tracks and visibility footprints.")
        
        with st.expander("📊 View Satellite Position Details"):
            pos_df = pd.DataFrame(sat_positions)
            pos_df = pos_df.round({'lat': 2, 'lon': 2, 'alt_km': 0})
            pos_df.columns = ['Satellite', 'Latitude (°)', 'Longitude (°)', 'Altitude (km)']
            st.dataframe(pos_df, hide_index=True, use_container_width=True)
