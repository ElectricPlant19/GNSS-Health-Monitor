# GNSS Constellation Monitoring System - Modular Architecture

This project provides comprehensive monitoring for multiple GNSS constellations including NavIC, QZSS, and BeiDou-3. It has been refactored from a monolithic structure into a clean, modular architecture for better maintainability and readability.

## 📁 Project Structure

```
HEALTH/
├── main_app.py              # Main Streamlit application
├── config.py                # Configuration and constants
├── spacetrack_api.py        # Space-Track API integration
├── drift_analysis.py        # Longitudinal drift calculations
├── maneuver_detection.py    # Orbital maneuver detection
├── health_assessment.py     # Comprehensive health scoring
├── dop_calculations.py      # DOP calculations and satellite positioning
├── visualization.py         # All plotting and visualization functions
└── README.md               # This documentation
```

## 🔧 Module Descriptions

### `config.py`
- **Purpose**: Centralized configuration and constants
- **Contains**: 
  - NavIC satellite NORAD IDs
  - QZSS satellite NORAD IDs
  - BeiDou-3 satellite NORAD IDs (IGSO and GEO only)
  - India's geographical points for DOP analysis
  - Japan's geographical points for DOP analysis
  - China's geographical points for DOP analysis
  - Service requirements and tolerances for each constellation
  - Default analysis parameters
  - DOP quality thresholds

### `spacetrack_api.py`
- **Purpose**: Space-Track.org API integration
- **Functions**:
  - `get_spacetrack_session()`: Authentication
  - `fetch_tle_json_cached()`: Cached GP history data
  - `fetch_multiple_tles()`: Latest TLE data
  - `fetch_and_classify_satellite()`: Complete satellite data processing

### `drift_analysis.py`
- **Purpose**: Longitudinal drift calculations and assessment
- **Functions**:
  - `calculate_longitudinal_drift()`: Convert mean motion to drift
  - `assess_drift_health()`: Health assessment based on drift
  - `calculate_drift_trend()`: Analyze drift trends over time
  - `get_drift_direction()`: Determine drift direction with emojis

### `maneuver_detection.py`
- **Purpose**: Statistical detection of orbital maneuvers
- **Functions**:
  - `detect_navik_maneuvers()`: Main maneuver detection algorithm
  - `rolling_median_safe()`: Robust rolling median calculation
  - `mad_zscore()`: Median Absolute Deviation z-score
  - `calculate_maneuver_uniformity()`: Maneuver spacing analysis

### `health_assessment.py`
- **Purpose**: Comprehensive satellite health scoring
- **Functions**:
  - `assess_satellite_health_with_drift()`: Complete health assessment including drift analysis
  - Integrates inclination control, maintenance activity, maneuver uniformity, and drift analysis

### `dop_calculations.py`
- **Purpose**: Dilution of Precision calculations and satellite positioning
- **Functions**:
  - `parse_tle_data()`: Parse TLE text into satellite objects
  - `calculate_satellite_position()`: Calculate satellite positions
  - `calculate_dop_for_location()`: DOP calculations for specific locations
  - `calculate_bounding_boxes()`: Ground track bounding box calculations
  - `get_dop_quality()`: DOP quality assessment

### `visualization.py`
- **Purpose**: All plotting and visualization functions
- **Functions**:
  - `plot_individual_satellites()`: Individual satellite plots
  - `plot_combined_drift()`: Combined drift comparison
  - `plot_bounding_boxes()`: Ground track visualizations
  - `plot_sky_plot()`: Azimuth-elevation sky plots
  - `plot_dop_over_time()`: DOP time series plots
  - `plot_drift_distribution()`: Drift distribution analysis
  - And more specialized plotting functions

### `main_app.py`
- **Purpose**: Main Streamlit application
- **Features**:
  - User interface and sidebar configuration
  - Data fetching and processing orchestration
  - Results display and visualization coordination
  - Session state management

## 🚀 Usage

### Running the Application
```bash
streamlit run main_app.py
```

### Supported Constellations
1. **NavIC (IRNSS)**: Indian Regional Navigation Satellite System
   - 7 satellites (3 GEO, 4 IGSO)
   - Coverage: India and surrounding regions
   - DOP analysis for 5 Indian locations

2. **QZSS (Michibiki)**: Quasi-Zenith Satellite System
   - 5 satellites (3 IGSO, 2 GEO)
   - Coverage: Japan and Asia-Pacific
   - DOP analysis for 5 Japanese locations

3. **BeiDou-3**: Chinese Navigation Satellite System
   - IGSO and GEO satellites only (10 IGSO, 9 GEO)
   - Coverage: Asia-Pacific regional service
   - DOP analysis for 10 Chinese locations
   - **Note**: NORAD IDs need to be populated in config.py

### Finding BeiDou-3 NORAD IDs
Run the helper script to find NORAD IDs:
```bash
python find_beidou_norad_ids.py
```

This will:
- Search Space-Track for BeiDou/Compass satellites
- Classify them as IGSO, GEO, or MEO
- Generate code for config.py
- Save results to CSV

### Key Features
- **Multi-Constellation Support**: NavIC, QZSS, and BeiDou-3
- **Modular Design**: Each module has a specific responsibility
- **Easy Maintenance**: Changes to one module don't affect others
- **Clear Dependencies**: Well-defined interfaces between modules
- **Reusable Components**: Functions can be imported and used independently
- **Comprehensive Documentation**: Each module is well-documented
- **Regional DOP Analysis**: Location-specific DOP calculations for each constellation

## 🔄 Migration from Monolithic Structure

The original `v4.py` file (1612 lines) has been split into:

1. **Configuration** → `config.py` (80 lines)
2. **API Integration** → `spacetrack_api.py` (120 lines)
3. **Drift Analysis** → `drift_analysis.py` (100 lines)
4. **Maneuver Detection** → `maneuver_detection.py` (150 lines)
5. **Health Assessment** → `health_assessment.py` (200 lines)
6. **DOP Calculations** → `dop_calculations.py` (180 lines)
7. **Visualization** → `visualization.py` (400 lines)
8. **Main Application** → `main_app.py` (500 lines)

**Total**: ~1730 lines across 8 focused modules vs. 1612 lines in 1 monolithic file

## 🎯 Benefits of Modular Architecture

1. **Maintainability**: Easier to locate and fix issues
2. **Readability**: Each module has a clear, focused purpose
3. **Testability**: Individual modules can be tested independently
4. **Reusability**: Functions can be imported and used in other projects
5. **Collaboration**: Multiple developers can work on different modules
6. **Documentation**: Each module is self-documenting
7. **Debugging**: Easier to isolate and debug specific functionality

## 📋 Dependencies

All modules maintain the same dependencies as the original:
- `streamlit`
- `numpy`
- `pandas`
- `plotly`
- `requests`
- `skyfield`
- `statistics`

## 🔧 Customization

Each module can be customized independently:
- **Configuration**: Modify `config.py` for different satellites or parameters
- **Analysis**: Adjust algorithms in respective analysis modules
- **Visualization**: Customize plots in `visualization.py`
- **UI**: Modify the main application interface in `main_app.py`

This modular structure makes the GNSS constellation monitoring system much more robust, readable, and maintainable while preserving all original functionality.

## 🛰️ BeiDou-3 Integration

### Overview
BeiDou-3 is China's third-generation satellite navigation system. This integration focuses on **IGSO and GEO satellites only** for regional Asia-Pacific coverage.

### Satellite Configuration
- **10 IGSO satellites**: 55° inclination at 95°E, 118°E, and 120°E
- **9 GEO satellites**: 0° inclination at various longitudes

### Service Requirements
- **IGSO**: 55° ± 1° inclination, 42,164 km ± 10 km semi-major axis
- **GEO**: 0° ± 0.5° inclination, 42,164 km ± 10 km semi-major axis

### Chinese Locations for DOP Analysis
1. Northernmost (Mohe, Heilongjiang): 53.5°N, 122.5°E
2. Southernmost (Sansha, Hainan): 16.8°N, 112.3°E
3. Easternmost (Fuyuan, Heilongjiang): 48.4°N, 134.7°E
4. Westernmost (Wuqia, Xinjiang): 39.7°N, 75.3°E
5. Capital (Beijing): 39.9°N, 116.4°E
6. Shanghai: 31.2°N, 121.5°E
7. Guangzhou: 23.1°N, 113.3°E
8. Chengdu: 30.7°N, 104.1°E
9. Urumqi (Xinjiang): 43.8°N, 87.6°E
10. Lhasa (Tibet): 29.7°N, 91.1°E

### Setup Instructions
1. Run `python find_beidou_norad_ids.py` to find NORAD IDs
2. Update `BEIDOU3_SATS` dictionary in `config.py` with actual NORAD IDs
3. Select "BeiDou-3" from constellation dropdown in the application
4. Enter Space-Track credentials and run analysis

### Documentation
See `BEIDOU3_INTEGRATION.md` for detailed integration guide and specifications.
