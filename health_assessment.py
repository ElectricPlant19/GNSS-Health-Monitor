"""
Health Assessment Module
Comprehensive health assessment for NavIC satellites including drift analysis
"""

import numpy as np
import pandas as pd
from datetime import timedelta
from config import NAVIK_SERVICE_REQUIREMENTS
from drift_analysis import assess_drift_health, calculate_drift_trend
from maneuver_detection import calculate_maneuver_uniformity


def analyze_maneuver_pattern(maneuver_events, observation_start, observation_end):
    """
    Dynamically analyze the maneuver pattern for a satellite.
    Analyzes E-W and N-S maneuvers separately as they serve different purposes.
    
    Args:
        maneuver_events: DataFrame of detected maneuvers with 'EPOCH', 'EW_MANEUVER', 'NS_MANEUVER' columns
        observation_start: Start date of observation period
        observation_end: End date of observation period
    
    Returns:
        dict: Pattern analysis including expected interval, last maneuver, and health metrics
    """
    if len(maneuver_events) == 0:
        return {
            'num_maneuvers': 0,
            'num_ew_maneuvers': 0,
            'num_ns_maneuvers': 0,
            'expected_interval_days': None,
            'ew_expected_interval_days': None,
            'ns_expected_interval_days': None,
            'median_interval_days': None,
            'last_maneuver_date': None,
            'last_ew_maneuver_date': None,
            'last_ns_maneuver_date': None,
            'days_since_last_maneuver': None,
            'days_since_last_ew': None,
            'days_since_last_ns': None,
            'is_overdue': False,
            'ew_is_overdue': False,
            'ns_is_overdue': False,
            'pattern_confidence': 'none',
            'maintenance_score': 0,
            'maintenance_status': 'No maneuvers detected'
        }
    
    # Separate E-W and N-S maneuvers
    ew_maneuvers = maneuver_events[maneuver_events.get('EW_MANEUVER', False) == True].copy() if 'EW_MANEUVER' in maneuver_events.columns else pd.DataFrame()
    ns_maneuvers = maneuver_events[maneuver_events.get('NS_MANEUVER', False) == True].copy() if 'NS_MANEUVER' in maneuver_events.columns else pd.DataFrame()
    
    num_ew = len(ew_maneuvers)
    num_ns = len(ns_maneuvers)
    
    # Helper function to analyze pattern for a specific maneuver type
    def analyze_type_pattern(maneuvers_df, maneuver_type_name):
        if len(maneuvers_df) == 0:
            return None, None, None, None, 'none'
        
        dates = pd.to_datetime(maneuvers_df['EPOCH']).sort_values().tolist()
        intervals = []
        if len(dates) >= 2:
            for i in range(1, len(dates)):
                intervals.append((dates[i] - dates[i-1]).days)
        
        if len(intervals) >= 2:
            median_int = np.median(intervals)
            mean_int = np.mean(intervals)
            std_int = np.std(intervals)
            expected_int = median_int
            if std_int / mean_int < 0.3:
                confidence = 'high'
            elif std_int / mean_int < 0.6:
                confidence = 'medium'
            else:
                confidence = 'low'
        elif len(intervals) == 1:
            expected_int = intervals[0]
            confidence = 'low'
        else:
            obs_days = (observation_end - observation_start).days
            expected_int = obs_days
            confidence = 'very_low'
        
        last_date = dates[-1]
        days_since = (observation_end - last_date).days
        is_overdue = days_since > (expected_int * 1.5)
        
        return expected_int, last_date, days_since, is_overdue, confidence
    
    # Analyze E-W pattern
    ew_expected, ew_last_date, ew_days_since, ew_overdue, ew_confidence = analyze_type_pattern(ew_maneuvers, "E-W")
    
    # Analyze N-S pattern
    ns_expected, ns_last_date, ns_days_since, ns_overdue, ns_confidence = analyze_type_pattern(ns_maneuvers, "N-S")
    
    # Overall pattern analysis (all maneuvers)
    maneuver_dates = pd.to_datetime(maneuver_events['EPOCH']).sort_values().tolist()
    num_maneuvers = len(maneuver_dates)
    
    intervals_days = []
    if num_maneuvers >= 2:
        for i in range(1, num_maneuvers):
            intervals_days.append((maneuver_dates[i] - maneuver_dates[i-1]).days)
    
    if len(intervals_days) >= 2:
        median_interval = np.median(intervals_days)
        mean_interval = np.mean(intervals_days)
        std_interval = np.std(intervals_days)
        expected_interval_days = median_interval
        if std_interval / mean_interval < 0.3:
            pattern_confidence = 'high'
        elif std_interval / mean_interval < 0.6:
            pattern_confidence = 'medium'
        else:
            pattern_confidence = 'low'
    elif len(intervals_days) == 1:
        expected_interval_days = intervals_days[0]
        median_interval = intervals_days[0]
        pattern_confidence = 'low'
    else:
        observation_days = (observation_end - observation_start).days
        expected_interval_days = observation_days
        median_interval = observation_days
        pattern_confidence = 'very_low'
    
    last_maneuver_date = maneuver_dates[-1]
    days_since_last = (observation_end - last_maneuver_date).days
    is_overdue = days_since_last > (expected_interval_days * 1.5)
    
    # Calculate combined maintenance score
    ew_score = 100
    ns_score = 100
    
    # E-W score (60% weight - more critical for station-keeping)
    if ew_expected is not None:
        if ew_overdue:
            overdue_ratio = ew_days_since / ew_expected
            if overdue_ratio > 3.0:
                ew_score = 0
            elif overdue_ratio > 2.0:
                ew_score = 30
            else:
                ew_score = 60
        else:
            recency_ratio = ew_days_since / ew_expected
            if recency_ratio < 0.5:
                ew_score = 100
            elif recency_ratio < 1.0:
                ew_score = 100
            else:
                ew_score = 90
        
        # Adjust for confidence
        if ew_confidence == 'very_low':
            ew_score = max(50, ew_score * 0.7)
        elif ew_confidence == 'low':
            ew_score = max(60, ew_score * 0.85)
    else:
        ew_score = 50  # No E-W maneuvers detected
    
    # N-S score (40% weight - less frequent but still important)
    if ns_expected is not None:
        if ns_overdue:
            overdue_ratio = ns_days_since / ns_expected
            if overdue_ratio > 3.0:
                ns_score = 0
            elif overdue_ratio > 2.0:
                ns_score = 30
            else:
                ns_score = 60
        else:
            recency_ratio = ns_days_since / ns_expected
            if recency_ratio < 0.5:
                ns_score = 100
            elif recency_ratio < 1.0:
                ns_score = 100
            else:
                ns_score = 90
        
        # Adjust for confidence
        if ns_confidence == 'very_low':
            ns_score = max(50, ns_score * 0.7)
        elif ns_confidence == 'low':
            ns_score = max(60, ns_score * 0.85)
    else:
        ns_score = 70  # No N-S maneuvers (less critical)
    
    # Combined maintenance score (weighted)
    maintenance_score = (ew_score * 0.6) + (ns_score * 0.4)
    
    # Build maintenance status message
    status_parts = []
    if ew_expected is not None:
        if ew_overdue:
            status_parts.append(f"E-W: OVERDUE ({ew_days_since} days, expected every {ew_expected:.0f} days)")
        else:
            status_parts.append(f"E-W: On schedule ({ew_days_since} days ago, every {ew_expected:.0f} days)")
    else:
        status_parts.append("E-W: No maneuvers detected")
    
    if ns_expected is not None:
        if ns_overdue:
            status_parts.append(f"N-S: OVERDUE ({ns_days_since} days, expected every {ns_expected:.0f} days)")
        else:
            status_parts.append(f"N-S: On schedule ({ns_days_since} days ago, every {ns_expected:.0f} days)")
    else:
        status_parts.append("N-S: No maneuvers detected")
    
    maintenance_status = " | ".join(status_parts)
    
    return {
        'num_maneuvers': num_maneuvers,
        'num_ew_maneuvers': num_ew,
        'num_ns_maneuvers': num_ns,
        'expected_interval_days': expected_interval_days,
        'ew_expected_interval_days': ew_expected,
        'ns_expected_interval_days': ns_expected,
        'median_interval_days': median_interval if len(intervals_days) > 0 else None,
        'last_maneuver_date': last_maneuver_date,
        'last_ew_maneuver_date': ew_last_date,
        'last_ns_maneuver_date': ns_last_date,
        'days_since_last_maneuver': days_since_last,
        'days_since_last_ew': ew_days_since,
        'days_since_last_ns': ns_days_since,
        'is_overdue': is_overdue,
        'ew_is_overdue': ew_overdue,
        'ns_is_overdue': ns_overdue,
        'pattern_confidence': pattern_confidence,
        'ew_confidence': ew_confidence,
        'ns_confidence': ns_confidence,
        'ew_score': ew_score,
        'ns_score': ns_score,
        'maintenance_score': maintenance_score,
        'maintenance_status': maintenance_status,
        'intervals': intervals_days if len(intervals_days) > 0 else None
    }


def assess_satellite_health_with_drift(sat_name, sat_df, maneuver_events, inc_tolerance, 
                                       min_man_per_month, max_man_per_month, uniformity_threshold,
                                       drift_tolerance_gso=0.05, service_requirements=None,
                                       pattern_maneuvers=None, pattern_df=None):
    """
    Comprehensive health assessment for a satellite including drift analysis.
    
    Args:
        pattern_maneuvers: Maneuvers from last year's data for pattern analysis (optional)
        pattern_df: Last year's dataframe for pattern analysis (optional)
    """
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
    
    observation_start = sat_df['EPOCH'].min()
    observation_end = sat_df['EPOCH'].max()
    observation_days = (observation_end - observation_start).days
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
    
    # ========== DYNAMIC MANEUVER PATTERN ANALYSIS ==========
    # Use last year's data for pattern analysis if available, otherwise use selected range
    if pattern_maneuvers is not None and pattern_df is not None:
        pattern_obs_start = pattern_df['EPOCH'].min()
        pattern_obs_end = pattern_df['EPOCH'].max()
        pattern_analysis = analyze_maneuver_pattern(pattern_maneuvers, pattern_obs_start, pattern_obs_end)
    else:
        # Fallback to selected range if pattern data not available
        pattern_analysis = analyze_maneuver_pattern(maneuver_events, observation_start, observation_end)
    
    # Use the dynamically determined maintenance score
    maintenance_score = pattern_analysis['maintenance_score']
    maintenance_status = pattern_analysis['maintenance_status']
    expected_interval_days = pattern_analysis['expected_interval_days']
    days_since_last = pattern_analysis['days_since_last_maneuver']
    pattern_confidence = pattern_analysis['pattern_confidence']
    
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
    
    # Dynamic maintenance remarks based on learned pattern (E-W and N-S separate)
    remarks.append(f"📊 {maintenance_status}")
    
    # E-W specific remarks
    ew_expected = pattern_analysis.get('ew_expected_interval_days')
    ew_days_since = pattern_analysis.get('days_since_last_ew')
    ew_confidence = pattern_analysis.get('ew_confidence')
    ew_overdue = pattern_analysis.get('ew_is_overdue')
    
    if ew_expected is not None:
        if ew_confidence == 'high':
            remarks.append(f"✅ E-W: Consistent pattern (every {ew_expected:.0f} days)")
        elif ew_confidence in ['medium', 'low']:
            remarks.append(f"ℹ️ E-W: Variable pattern (confidence: {ew_confidence})")
        
        if ew_overdue:
            remarks.append(f"🔴 E-W maneuver overdue by {ew_days_since - ew_expected:.0f} days")
        elif ew_days_since is not None:
            next_ew = ew_expected - ew_days_since
            if next_ew > 0:
                remarks.append(f"⏱️ Next E-W maneuver expected in ~{next_ew:.0f} days")
    
    # N-S specific remarks
    ns_expected = pattern_analysis.get('ns_expected_interval_days')
    ns_days_since = pattern_analysis.get('days_since_last_ns')
    ns_confidence = pattern_analysis.get('ns_confidence')
    ns_overdue = pattern_analysis.get('ns_is_overdue')
    
    if ns_expected is not None:
        if ns_confidence == 'high':
            remarks.append(f"✅ N-S: Consistent pattern (every {ns_expected:.0f} days)")
        elif ns_confidence in ['medium', 'low']:
            remarks.append(f"ℹ️ N-S: Variable pattern (confidence: {ns_confidence})")
        
        if ns_overdue:
            remarks.append(f"🔴 N-S maneuver overdue by {ns_days_since - ns_expected:.0f} days")
        elif ns_days_since is not None:
            next_ns = ns_expected - ns_days_since
            if next_ns > 0:
                remarks.append(f"⏱️ Next N-S maneuver expected in ~{next_ns:.0f} days")
    
    # Uniformity remarks
    if uniformity_cov is not None:
        if uniformity_cov <= uniformity_threshold:
            remarks.append("Regular maneuver pattern detected")
        else:
            remarks.append("Irregular maneuver spacing")
    
    if std_inclination < 0.1:
        remarks.append("Stable orbital parameters")
    
    # Get current altitude if available
    current_altitude = None
    if 'altitude_km' in sat_df.columns and not sat_df['altitude_km'].isna().all():
        current_altitude = sat_df['altitude_km'].iloc[-1]
    
    # Extract pattern details for display
    ew_expected = pattern_analysis.get('ew_expected_interval_days')
    ns_expected = pattern_analysis.get('ns_expected_interval_days')
    ew_days_since = pattern_analysis.get('days_since_last_ew')
    ns_days_since = pattern_analysis.get('days_since_last_ns')
    ew_confidence = pattern_analysis.get('ew_confidence', 'none')
    ns_confidence = pattern_analysis.get('ns_confidence', 'none')
    
    return {
        'Satellite': sat_name,
        'Type': sat_type,
        'Health Status': f"{status_color} {health_status}",
        'Overall Score': round(overall_score, 1),
        'Target Incl. (°)': target_inclination if target_inclination is not None else "N/A",
        'Mean Incl. (°)': round(mean_inclination, 3),
        'Incl. Dev. (°)': round(inc_deviation, 3) if inc_deviation is not None else "N/A",
        'Altitude (km)': round(current_altitude, 1) if current_altitude is not None else "N/A",
        'Mean Drift (°/day)': round(mean_drift, 4) if mean_drift is not None else "N/A",
        'Current Drift (°/day)': round(current_drift, 4) if current_drift is not None else "N/A",
        'Drift Status': f"{drift_color} {drift_status}",
        'Maneuvers/Month': round(maneuvers_per_month, 2),
        'Expected Interval (days)': round(expected_interval_days, 0) if expected_interval_days is not None else "N/A",
        'Days Since Last': days_since_last if days_since_last is not None else "N/A",
        'Pattern Confidence': pattern_confidence.replace('_', ' ').title(),
        'EW Maneuvers': int(maneuver_events['EW_MANEUVER'].sum()) if 'EW_MANEUVER' in maneuver_events.columns else 0,
        'NS Maneuvers': int(maneuver_events['NS_MANEUVER'].sum()) if 'NS_MANEUVER' in maneuver_events.columns else 0,
        'EW Expected Interval (days)': round(ew_expected, 0) if ew_expected is not None else "N/A",
        'NS Expected Interval (days)': round(ns_expected, 0) if ns_expected is not None else "N/A",
        'EW Days Since Last': ew_days_since if ew_days_since is not None else "N/A",
        'NS Days Since Last': ns_days_since if ns_days_since is not None else "N/A",
        'EW Pattern Confidence': ew_confidence.replace('_', ' ').title(),
        'NS Pattern Confidence': ns_confidence.replace('_', ' ').title(),
        'Uniformity (CoV)': round(uniformity_cov, 3) if uniformity_cov else "N/A",
        'Remarks': " | ".join(remarks),
        'Pattern Analysis Period': f"{pattern_obs_start.strftime('%Y-%m-%d')} to {pattern_obs_end.strftime('%Y-%m-%d')}" if pattern_maneuvers is not None else "Selected date range"
    }
