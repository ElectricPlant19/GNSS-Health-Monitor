# 🛰️ GNSS Constellation Health Monitoring System

A comprehensive real-time monitoring and analysis system for multiple Global Navigation Satellite System (GNSS) constellations including **NavIC (IRNSS)**, **QZSS (Michibiki)**, and **BeiDou-3**. This application provides satellite health assessment, orbital drift analysis, maneuver detection, and Dilution of Precision (DOP) calculations through an interactive Streamlit web interface.

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [What the Application Does](#-what-the-application-does)
- [Configuration & Customization](#-configuration--customization)
- [Troubleshooting](#-troubleshooting)
- [Additional Documentation](#-additional-documentation)

## 🌟 Key Features

- **Multi-Constellation Support**: Monitor NavIC, QZSS, and BeiDou-3 satellites
- **Real-Time Health Assessment**: Comprehensive health scoring based on orbital parameters
- **Longitudinal Drift Analysis**: Track east-west drift for station-keeping assessment
- **Maneuver Detection**: Automated detection of orbital correction maneuvers (E-W and N-S)
- **DOP Calculations**: Dilution of Precision analysis for regional locations
- **Interactive Visualizations**: Rich time-series plots and sky plots
- **Modular Architecture**: Clean, maintainable codebase with separated concerns

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
streamlit run main_app.py

# 3. Open browser at http://localhost:8501

# 4. Enter Space-Track credentials and start analyzing!
```

**First time user?** Register for free at [Space-Track.org](https://www.space-track.org/auth/createAccount)

## 📁 Project Structure

```
heath_monitor/
├── main_app.py                    # Main Streamlit application (entry point)
├── config.py                      # Configuration and constants
├── spacetrack_api.py              # Space-Track API integration
├── drift_analysis.py              # Longitudinal drift calculations
├── maneuver_detection.py          # Orbital maneuver detection
├── health_assessment.py           # Comprehensive health scoring
├── dop_calculations.py            # DOP calculations and satellite positioning
├── visualization.py               # All plotting and visualization functions
├── find_beidou_norad_ids.py       # Helper script to find BeiDou NORAD IDs
├── requirements.txt               # Python dependencies
├── README.md                      # This documentation
├── BEIDOU3_INTEGRATION.md         # BeiDou-3 integration guide
├── BEIDOU3_SUMMARY.md             # BeiDou-3 constellation overview
└── DOP_FIX_EXPLANATION.md         # DOP calculation methodology
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

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Space-Track.org account (free registration at https://www.space-track.org/auth/createAccount)

### Installation

1. **Clone or download the repository**
   ```bash
   cd heath_monitor
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install required dependencies**
   ```bash
   pip install streamlit numpy pandas plotly requests skyfield
   ```

   Or create a `requirements.txt` file with:
   ```
   streamlit>=1.28.0
   numpy>=1.24.0
   pandas>=2.0.0
   plotly>=5.17.0
   requests>=2.31.0
   skyfield>=1.46
   ```
   Then install:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Streamlit server**
   ```bash
   streamlit run main_app.py
   ```

2. **Access the application**
   - The application will automatically open in your default browser
   - Default URL: http://localhost:8501
   - If it doesn't open automatically, navigate to the URL shown in the terminal

3. **Configure the application**
   - Enter your Space-Track.org credentials in the sidebar
   - Select a constellation (NavIC, QZSS, or BeiDou-3)
   - Choose date range for analysis
   - Adjust analysis parameters as needed
   - Click "Fetch Data & Run Analysis"

### Example Workflow

```
1. Launch Application
   └─> streamlit run main_app.py

2. Configure Settings (Sidebar)
   ├─> Enter Space-Track credentials
   ├─> Select constellation: NavIC
   ├─> Set date range: 2025-01-01 to 2025-10-01
   └─> Keep default parameters

3. Run Analysis
   └─> Click "Fetch Data & Run Analysis"

4. View Results
   ├─> Health Assessment Table (main view)
   ├─> Expand "Longitudinal Drift Analysis"
   ├─> Expand "DOP Analysis"
   └─> Expand "Visualizations & Plots"

5. Generate Plots
   └─> Click "Generate All Plots" in Visualizations section
```

### Supported Constellations

| Constellation | Satellites | Coverage | DOP Locations | Status |
|---------------|------------|----------|---------------|--------|
| **NavIC (IRNSS)** | 7 (3 GEO, 4 IGSO) | India & surrounding regions | 5 Indian cities | ✅ Fully configured |
| **QZSS (Michibiki)** | 5 (3 IGSO, 2 GEO) | Japan & Asia-Pacific | 5 Japanese cities | ✅ Fully configured |
| **BeiDou-3** | 19 (10 IGSO, 9 GEO) | Asia-Pacific regional | 10 Chinese cities | ⚠️ Requires NORAD ID setup |

**NavIC Locations**: New Delhi, Mumbai, Chennai, Kolkata, Bangalore  
**QZSS Locations**: Tokyo, Osaka, Sapporo, Fukuoka, Naha  
**BeiDou-3 Locations**: Beijing, Shanghai, Guangzhou, Chengdu, Urumqi, Lhasa, Mohe, Sansha, Fuyuan, Wuqia

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

## 📊 What the Application Does

### Health Assessment
- **Inclination Control**: Monitors satellite inclination deviation from target values
- **Drift Analysis**: Calculates longitudinal drift for station-keeping assessment
- **Maneuver Tracking**: Detects and counts orbital correction maneuvers
- **Overall Health Score**: Comprehensive 0-100 scoring system based on multiple parameters

### Orbital Analysis
- **Longitudinal Drift**: Calculates drift rate in degrees per day
- **Drift Direction**: Identifies eastward (positive) or westward (negative) drift
- **Altitude Monitoring**: Tracks semi-major axis and altitude variations
- **Inclination Trends**: Monitors inclination changes over time

### DOP Analysis
- **GDOP**: Geometric Dilution of Precision
- **PDOP**: Position Dilution of Precision
- **HDOP**: Horizontal Dilution of Precision
- **VDOP**: Vertical Dilution of Precision
- **TDOP**: Time Dilution of Precision
- **Regional Coverage**: Location-specific calculations for each constellation

### Visualizations
- Individual satellite time-series plots (inclination, altitude, drift)
- Combined constellation comparison plots
- Sky plots (azimuth-elevation diagrams)
- Ground track bounding boxes
- DOP time-series over 30 days
- Drift distribution analysis

## 📈 Understanding the Output

### Health Status Indicators

| Status | Score Range | Color | Meaning |
|--------|-------------|-------|---------|
| 🟢 Healthy | 80-100 | Green | Excellent orbital control, within all tolerances |
| 🟡 Marginal | 60-79 | Yellow | Some parameters outside ideal range, monitoring needed |
| 🟠 Degraded | 40-59 | Orange | Multiple issues detected, corrective action recommended |
| 🔴 Critical | 0-39 | Red | Significant orbital deviations, immediate attention required |

### Key Metrics Explained

**Inclination Deviation**: Difference between current and target inclination
- **Good**: < 0.5°
- **Acceptable**: 0.5° - 1.0°
- **Poor**: > 1.0°

**Longitudinal Drift** (for GSO satellites):
- **Good**: ±0.05°/day
- **Acceptable**: ±0.05° - 0.10°/day
- **Poor**: > ±0.10°/day

**Maneuvers per Month**:
- **Typical**: 1-8 maneuvers
- **Too Few**: < 1 (insufficient station-keeping)
- **Too Many**: > 8 (possible instability)

**DOP Values**:
- **Excellent**: < 2
- **Good**: 2-4
- **Moderate**: 4-6
- **Fair**: 6-8
- **Poor**: > 8

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

| Package | Version | Purpose |
|---------|---------|---------|
| `streamlit` | ≥1.28.0 | Web application framework |
| `numpy` | ≥1.24.0 | Numerical computations |
| `pandas` | ≥2.0.0 | Data manipulation and analysis |
| `plotly` | ≥5.17.0 | Interactive visualizations |
| `requests` | ≥2.31.0 | HTTP requests to Space-Track API |
| `skyfield` | ≥1.46 | Satellite position calculations |

## 🔧 Configuration & Customization

### Analysis Parameters

You can customize various analysis parameters through the sidebar:

**Maneuver Detection:**
- Z-Score Threshold (default: 3.0)
- SMA Change Threshold in km (default: 0.5)
- Inclination Change Threshold in degrees (default: 0.005)
- Persistence Window (default: 2)

**Health Assessment:**
- Inclination Tolerance in degrees (default: 1.0)
- GSO Drift Tolerance in deg/day (default: 0.05)
- Min/Max Maneuvers per Month (default: 1-8)
- Maneuver Uniformity Threshold (default: 0.8)

**DOP Settings:**
- Elevation Mask (0-30°, default: 5°)
- Custom location option for DOP calculations

### Module Customization

Each module can be modified independently:
- **`config.py`**: Add new satellites, modify NORAD IDs, change service requirements
- **`drift_analysis.py`**: Adjust drift calculation algorithms
- **`maneuver_detection.py`**: Modify detection thresholds and algorithms
- **`health_assessment.py`**: Customize health scoring logic
- **`visualization.py`**: Create new plots or modify existing ones
- **`main_app.py`**: Customize UI layout and workflow

## 🐛 Troubleshooting

### Common Issues

**Issue: "Failed to fetch TLE data"**
- Verify Space-Track credentials are correct
- Check internet connection
- Ensure NORAD IDs in `config.py` are valid

**Issue: "No satellites parsed from TLE data"**
- Check if NORAD IDs are set (not `None`) in `config.py`
- For BeiDou-3, run `find_beidou_norad_ids.py` first

**Issue: "Module not found" errors**
- Ensure all Python files are in the same directory
- Verify all dependencies are installed: `pip list`

**Issue: Application won't start**
- Check Python version: `python --version` (should be 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

**Issue: Slow performance**
- Reduce date range for analysis
- Enable "Keep only one TLE per day" option
- Close other browser tabs running Streamlit

### Getting Help

- Check existing documentation in `BEIDOU3_INTEGRATION.md` and `DOP_FIX_EXPLANATION.md`
- Review Space-Track API documentation: https://www.space-track.org/documentation
- Verify satellite NORAD IDs at: https://celestrak.org/

## 📖 Additional Documentation

- **`BEIDOU3_INTEGRATION.md`**: Detailed BeiDou-3 integration guide
- **`BEIDOU3_SUMMARY.md`**: BeiDou-3 constellation overview
- **`DOP_FIX_EXPLANATION.md`**: DOP calculation methodology

## 🔒 Security Notes

- Never commit Space-Track credentials to version control
- Credentials are stored only in session state (not persisted)
- Consider using environment variables for production deployments

## 🎯 Use Cases

- **Satellite Operators**: Monitor constellation health and plan maneuvers
- **Researchers**: Analyze orbital dynamics and station-keeping strategies
- **Navigation Engineers**: Assess DOP values for service quality
- **Students**: Learn about GNSS constellations and orbital mechanics

## 📝 License & Credits

This project uses data from Space-Track.org, which requires free registration. The application is built with open-source libraries and follows modular design principles for maintainability and extensibility.

---

## 🎓 Technical Background

### Data Sources
- **TLE Data**: Two-Line Element sets from Space-Track.org
- **Orbital Calculations**: Skyfield library for precise satellite positioning
- **Time Series Analysis**: Statistical methods for maneuver detection

### Algorithms
- **Drift Calculation**: Based on mean motion deviation from geosynchronous rate (1.00273790935 rev/day)
- **Maneuver Detection**: MAD (Median Absolute Deviation) z-score method with persistence filtering
- **Health Scoring**: Multi-factor weighted scoring system (0-100 scale)
- **DOP Calculation**: Standard geometric dilution of precision using satellite-observer geometry

### Performance
- Typical analysis time: 30-60 seconds for 9 months of data
- Memory usage: ~500MB for full constellation analysis
- Supports concurrent analysis of multiple satellites

---

## 🚀 Future Enhancements

Potential improvements and features:
- [ ] Add GPS, GLONASS, and Galileo constellation support
- [ ] Export analysis results to PDF reports
- [ ] Real-time alerting for critical health status changes
- [ ] Historical trend comparison across multiple time periods
- [ ] Machine learning for anomaly detection
- [ ] API endpoint for programmatic access
- [ ] Multi-user support with saved configurations

---

**Made with ❤️ for GNSS monitoring and analysis**

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
