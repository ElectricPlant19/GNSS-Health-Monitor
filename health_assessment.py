"""
Health Assessment Module
Comprehensive health assessment for NavIC satellites including drift analysis
"""

import numpy as np
import pandas as pd
from config import NAVIK_SERVICE_REQUIREMENTS
from drift_analysis import assess_drift_health, calculate_drift_trend
from maneuver_detection import calculate_maneuver_uniformity


def assess_satellite_health_with_drift(sat_name, sat_df, maneuver_events, inc_tolerance, 
                                       min_man_per_month, max_man_per_month, uniformity_threshold,
                                       drift_tolerance_gso=0.05, service_requirements=None):
    """Comprehensive health assessment for a satellite including drift analysis."""
    requirements_map = service_requirements if service_requirements is not None else NAVIK_SERVICE_REQUIREMENTS
    requirements = requirements_map.get(sat_name, {})
    
    # Handle different inclination formats (NavIC uses "inclination", QZSS uses different keys)
    target_inclination = None
    if "inclination" in requirements:
        target_inclination = requirements["inclination"]
    elif "inclination_target_deg" in requirements:
        target_inclination = requirements["inclination_target_deg"]
    elif "inclination_target_deg_range" in requirements:
        # For IGSO satellites with inclination range, use the midpoint
        inc_range = requirements["inclination_target_deg_range"]
        target_inclination = (inc_range[0] + inc_range[1]) / 2.0
    
    mean_inclination = sat_df['INCLINATION'].mean()
    std_inclination = sat_df['INCLINATION'].std()
    
    # Determine satellite type
    if 0.0 < mean_inclination < 10.0:
        sat_type = 'GSO'
    elif mean_inclination >= 10.0:
        sat_type = 'IGSO'
    else:
        sat_type = 'Unclassified'
    
    observation_days = (sat_df['EPOCH'].max() - sat_df['EPOCH'].min()).days
    observation_months = observation_days / 30.0
    
    num_maneuvers = len(maneuver_events)
    maneuvers_per_month = num_maneuvers / observation_months if observation_months > 0 else 0
    
    # Detect if this is QZSS (service_requirements is not None and not NavIC)
    is_qzss = service_requirements is not None and requirements.get('type') in ['IGSO', 'GSO']
    
    # Inclination score with stability consideration
    if target_inclination is not None:
        inc_deviation = abs(mean_inclination - target_inclination)
        
        # Penalize high standard deviation (unstable inclination)
        inc_stability_penalty = min(20, std_inclination * 10)
        
        inc_score = max(0, 100 - (inc_deviation / inc_tolerance) * 100 - inc_stability_penalty)
    else:
        inc_score = None
        inc_deviation = None
    
    # Maintenance score with better scaling
    # QZSS has different maintenance cadence (every 6 months) vs NavIC (monthly)
    if is_qzss:
        # For QZSS IGSO: expect ~0.17 maneuvers/month (1 every 6 months)
        # For QZSS GSO: more frequent maneuvers are normal due to station-keeping requirements
        if sat_type == 'GSO':
            # GSO satellites need more frequent corrections
            qzss_min = 0.1  # At least 1 maneuver every 10 months
            qzss_max = 2.0  # GSO can have up to ~2 maneuvers/month normally
        else:
            # IGSO satellites (standard QZSS cadence)
            qzss_min = 0.1  # At least 1 maneuver every 10 months
            qzss_max = 0.5  # More than 1 every 2 months might indicate issues
        
        if maneuvers_per_month < qzss_min:
            maintenance_score = max(0, 30 + (maneuvers_per_month / qzss_min) * 40)
        elif maneuvers_per_month > qzss_max:
            excess_maneuvers = maneuvers_per_month - qzss_max
            penalty = min(40, excess_maneuvers / qzss_max * 60)
            maintenance_score = 100 - penalty
        else:
            maintenance_score = 100
    else:
        # NavIC maintenance scoring (original logic)
        if maneuvers_per_month < min_man_per_month:
            maintenance_score = max(0, 30 + (maneuvers_per_month / min_man_per_month) * 40)
        elif maneuvers_per_month > max_man_per_month:
            # Penalize excessive maneuvers (potential issues)
            excess_maneuvers = maneuvers_per_month - max_man_per_month
            penalty = min(40, excess_maneuvers / max_man_per_month * 60)
            maintenance_score = 100 - penalty
        else:
            maintenance_score = 100
    
    # Uniformity score with better weighting
    if num_maneuvers >= 2:
        maneuver_dates = pd.to_datetime(maneuver_events['EPOCH']).tolist()
        uniformity_cov = calculate_maneuver_uniformity(maneuver_dates)
        
        if uniformity_cov is not None and uniformity_cov <= uniformity_threshold:
            uniformity_score = 100
        elif uniformity_cov is not None:
            # Gradual degradation instead of abrupt
            excess = uniformity_cov - uniformity_threshold
            max_penalty = 50
            penalty = min(max_penalty, (excess / uniformity_threshold) * max_penalty)
            uniformity_score = 100 - penalty
        else:
            uniformity_score = 50
    else:
        uniformity_score = 50 if num_maneuvers == 1 else 0
        uniformity_cov = None
    
    # Enhanced DRIFT ANALYSIS
    if 'LonDrift_deg_per_day' in sat_df.columns:
        mean_drift = sat_df['LonDrift_deg_per_day'].mean()
        std_drift = sat_df['LonDrift_deg_per_day'].std()
        current_drift = sat_df['LonDrift_deg_per_day'].iloc[-1]
        
        # Calculate drift trend
        drift_trend = calculate_drift_trend(sat_df)
        
        # Base drift assessment
        drift_assessment = assess_drift_health(mean_drift, sat_type, drift_tolerance_gso)
        drift_score = drift_assessment['drift_score']
        drift_status = drift_assessment['drift_status']
        drift_color = drift_assessment['drift_color']
        
        # Stability penalty: penalize high standard deviation in drift (unstable station-keeping)
        if sat_type == 'GSO':
            drift_stability = std_drift / drift_tolerance_gso
            if drift_stability > 2:
                stability_penalty = min(30, (drift_stability - 2) * 10)
                drift_score = max(0, drift_score - stability_penalty)
        elif sat_type == 'IGSO':
            drift_stability = std_drift / 2.0
            if drift_stability > 1:
                stability_penalty = min(20, (drift_stability - 1) * 10)
                drift_score = max(0, drift_score - stability_penalty)
        
        # Trend analysis bonus/penalty
        if drift_trend > 0.01:  # Drift magnitude increasing
            drift_score = max(0, drift_score - 10)
        elif drift_trend < -0.01:  # Drift magnitude decreasing (improving)
            drift_score = min(100, drift_score + 5)
        
    else:
        mean_drift = None
        std_drift = None
        current_drift = None
        drift_score = None
        drift_status = "N/A"
        drift_color = "⚪"
        drift_trend = None
    
    # Calculate overall score with drift consideration
    if inc_score is not None and drift_score is not None:
        overall_score = (inc_score * 0.35 + maintenance_score * 0.25 + 
                        uniformity_score * 0.15 + drift_score * 0.25)
    elif inc_score is not None:
        overall_score = (inc_score * 0.5 + maintenance_score * 0.3 + uniformity_score * 0.2)
    elif drift_score is not None:
        overall_score = (maintenance_score * 0.4 + uniformity_score * 0.2 + drift_score * 0.4)
    else:
        overall_score = (maintenance_score * 0.6 + uniformity_score * 0.4)
    
    if overall_score >= 85:
        health_status = "Excellent"
        status_color = "🟢"
    elif overall_score >= 70:
        health_status = "Good"
        status_color = "🟡"
    elif overall_score >= 50:
        health_status = "Fair"
        status_color = "🟠"
    else:
        health_status = "Needs Attention"
        status_color = "🔴"
    
    remarks = []
    
    # Inclination remarks
    if inc_score is not None and inc_deviation is not None:
        if inc_deviation <= inc_tolerance * 0.3:
            remarks.append(f"Excellent inclination control (±{inc_deviation:.2f}°)")
        elif inc_deviation <= inc_tolerance:
            remarks.append(f"Inclination within tolerance (±{inc_deviation:.2f}°)")
        else:
            remarks.append(f"⚠️ Inclination deviation exceeds tolerance ({inc_deviation:.2f}°)")
    
    # Enhanced drift remarks for both GSO and IGSO
    if drift_score is not None:
        if sat_type == 'GSO':
            if drift_status == "Excellent":
                remarks.append(f"Excellent station-keeping ({drift_color} drift: {abs(mean_drift):.3f}°/day)")
            elif drift_status == "Good":
                remarks.append(f"Good drift control ({drift_color} {abs(mean_drift):.3f}°/day)")
            elif drift_status == "Fair":
                remarks.append(f"⚠️ Moderate drift detected ({drift_color} {abs(mean_drift):.3f}°/day)")
            elif drift_status == "Poor":
                remarks.append(f"⚠️ High drift - requires correction ({drift_color} {abs(mean_drift):.3f}°/day)")
            else:
                remarks.append(f"🔴 Critical drift - immediate attention needed ({abs(mean_drift):.3f}°/day)")
            
            # Add drift direction
            if mean_drift > 0:
                remarks.append(f"Drifting EASTWARD at {abs(mean_drift):.3f}°/day")
            elif mean_drift < 0:
                remarks.append(f"Drifting WESTWARD at {abs(mean_drift):.3f}°/day")
        elif sat_type == 'IGSO':
            if drift_status == "Normal":
                remarks.append(f"Normal IGSO drift ({drift_color} {abs(mean_drift):.3f}°/day)")
            elif drift_status == "Elevated":
                remarks.append(f"⚠️ Elevated IGSO drift ({drift_color} {abs(mean_drift):.3f}°/day)")
            else:
                remarks.append(f"⚠️ High IGSO drift ({drift_color} {abs(mean_drift):.3f}°/day)")
        
        # Enhanced remarks about drift stability and trend
        if drift_trend is not None:
            if drift_trend > 0.01:
                remarks.append(f"📈 Drift magnitude increasing (trend: +{drift_trend:.3f}°/day)")
            elif drift_trend < -0.01:
                remarks.append(f"📉 Drift magnitude decreasing (trend: {drift_trend:.3f}°/day)")
        
        if sat_type == 'GSO' and std_drift is not None:
            if std_drift > drift_tolerance_gso:
                remarks.append(f"⚠️ Unstable drift (std dev: {std_drift:.3f}°/day)")
            elif std_drift > drift_tolerance_gso * 0.5:
                remarks.append(f"Moderate drift variability (std dev: {std_drift:.3f}°/day)")
    
    # Maintenance remarks - adjusted for QZSS vs NavIC
    if is_qzss:
        # QZSS: Different thresholds for GSO vs IGSO
        if sat_type == 'GSO':
            # GSO satellites need more frequent station-keeping
            if maneuvers_per_month < 0.1:
                remarks.append(f"⚠️ Low maintenance activity ({maneuvers_per_month:.2f}/month, ~{maneuvers_per_month*12:.1f}/year)")
            elif maneuvers_per_month > 2.0:
                remarks.append(f"⚠️ Very high correction frequency ({maneuvers_per_month:.2f}/month, ~{maneuvers_per_month*12:.1f}/year)")
            else:
                # Normal for QZSS GSO
                remarks.append(f"Active station-keeping ({maneuvers_per_month:.2f}/month, ~{maneuvers_per_month*12:.1f}/year)")
        else:
            # IGSO satellites: ~1 maneuver every 6 months is normal
            if maneuvers_per_month < 0.1:
                remarks.append(f"⚠️ Low maintenance activity ({maneuvers_per_month:.2f}/month, ~{maneuvers_per_month*12:.1f}/year)")
            elif maneuvers_per_month > 0.5:
                remarks.append(f"⚠️ High correction frequency ({maneuvers_per_month:.2f}/month, ~{maneuvers_per_month*12:.1f}/year)")
            else:
                # Normal for QZSS IGSO
                remarks.append(f"Normal maintenance cadence ({maneuvers_per_month:.2f}/month, ~{maneuvers_per_month*12:.1f}/year)")
    else:
        # NavIC maintenance remarks (original logic)
        if maneuvers_per_month < min_man_per_month:
            remarks.append(f"⚠️ Low maintenance activity ({maneuvers_per_month:.1f}/month)")
        elif maneuvers_per_month > max_man_per_month:
            remarks.append(f"⚠️ High correction frequency ({maneuvers_per_month:.1f}/month)")
        else:
            remarks.append(f"Active maintenance ({maneuvers_per_month:.1f} maneuvers/month)")
    
    # Uniformity remarks
    if uniformity_cov is not None:
        if uniformity_cov <= uniformity_threshold:
            remarks.append("Regular maneuver pattern detected")
        else:
            remarks.append("Irregular maneuver spacing")
    
    if std_inclination < 0.1:
        remarks.append("Stable orbital parameters")
    
    return {
        'Satellite': sat_name,
        'Type': sat_type,
        'Health Status': f"{status_color} {health_status}",
        'Overall Score': round(overall_score, 1),
        'Target Incl. (°)': target_inclination if target_inclination is not None else "N/A",
        'Mean Incl. (°)': round(mean_inclination, 3),
        'Incl. Dev. (°)': round(inc_deviation, 3) if inc_deviation is not None else "N/A",
        'Mean Drift (°/day)': round(mean_drift, 4) if mean_drift is not None else "N/A",
        'Current Drift (°/day)': round(current_drift, 4) if current_drift is not None else "N/A",
        'Drift Status': f"{drift_color} {drift_status}",
        'Maneuvers/Month': round(maneuvers_per_month, 2),
        'EW Maneuvers': int(maneuver_events['EW_MANEUVER'].sum()) if 'EW_MANEUVER' in maneuver_events.columns else 0,
        'NS Maneuvers': int(maneuver_events['NS_MANEUVER'].sum()) if 'NS_MANEUVER' in maneuver_events.columns else 0,
        'Uniformity (CoV)': round(uniformity_cov, 3) if uniformity_cov else "N/A",
        'Remarks': " | ".join(remarks)
    }
