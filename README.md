# Sleep Apnea Analysis System

Comprehensive data processing and analysis pipeline for sleep study signals from the SRIP 2026 AI for Health project.

## Project Structure

```
internship/
├── Data/                 # Raw signal data (organized by patient)
├── Dataset/             # Processed and exported data
├── Visualizations/      # Generated plots and reports
├── parser.py           # Signal and event parsing
├── processor.py        # Signal processing and analysis
├── data_manager.py     # Data loading and organization
├── analyzer.py         # Clinical analysis and insights
├── visualizer.py       # Plotting and visualization
├── utils.py            # Data export and reporting utilities
├── main.py             # Main analysis script
├── visualize.py        # Visualization script
├── pipeline.py         # Complete processing pipeline
└── requirements.txt    # Python dependencies
```

## Features

### Data Processing
- Parse multiple signal types (Flow, SpO2, Thoracic, Sleep Profile, Events)
- Automatic metadata extraction
- Signal normalization and filtering
- Outlier detection and handling

### Clinical Analysis
- Apnea-Hypopnea Index (AHI) calculation
- Sleep stage distribution analysis
- Oxygen saturation metrics
- Respiratory event classification
- OSA severity classification

### Data Management
- Multi-patient data loading
- Organized signal and event access
- Statistical analysis
- Data quality assessment

### Visualizations
- Time-series signal plots
- Sleep stage distribution charts
- Respiratory event histograms
- Comprehensive patient reports
- Multi-patient comparisons

### Export Formats
- JSON (analysis results)
- CSV (signals, events, statistics)
- HTML (summary reports)
- PNG (visualizations)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Full Pipeline
```bash
python pipeline.py --data Data --output Dataset --viz
```

### Analysis Only
```bash
python main.py
```

### Visualizations Only
```bash
python pipeline.py --viz-only
```

### Custom Paths
```bash
python pipeline.py --data path/to/data --output path/to/output
```

## Data Format

### Signal Files
```
Signal Type: [TYPE]
Start Time: [DATETIME]
Sample Rate: [RATE]
Length: [COUNT]
Unit: [UNIT]

Data:
[TIMESTAMP]; [VALUE]
[TIMESTAMP]; [VALUE]
...
```

### Event Files
```
Signal ID: [ID]
Start Time: [DATETIME]
Unit: [UNIT]
Signal Type: [TYPE]

[TIME_RANGE]; [DURATION]; [EVENT_TYPE]; [SLEEP_STAGE]
[TIME_RANGE]; [DURATION]; [EVENT_TYPE]; [SLEEP_STAGE]
...
```

## Supported Signal Types

- **Flow**: Respiratory flow signals
- **SPO2**: Oxygen saturation (%)
- **Thorac**: Thoracic movement
- **Sleep Profile**: Sleep stage classifications
- **Flow Events**: Breathing event detections

## Output Files

### Dataset Directory
- `analysis_results.json` - Complete analysis results
- `signal_statistics.csv` - Statistics for all signals
- `analysis_report.txt` - Text summary report
- `analysis_report.html` - HTML summary report
- `[PATIENT]_[SIGNAL].csv` - Individual signal data

### Visualizations Directory
- `[PATIENT]_spo2.png` - SpO2 time series
- `[PATIENT]_flow.png` - Flow signal
- `[PATIENT]_sleep_stages.png` - Sleep stage distribution
- `[PATIENT]_events.png` - Respiratory events
- `[PATIENT]_report.png` - Comprehensive patient report

## Key Metrics

### AHI (Apnea-Hypopnea Index)
- Normal: AHI < 5
- Mild: 5 ≤ AHI < 15
- Moderate: 15 ≤ AHI < 30
- Severe: AHI ≥ 30

### SpO2 Metrics
- Mean oxygen saturation
- Minimum oxygen saturation
- Desaturation events
- Standard deviation

### Sleep Analysis
- Stage distribution
- Total sleep time
- Sleep efficiency metrics

## Requirements

- Python 3.8+
- numpy
- pandas
- scipy
- matplotlib
- seaborn

## License

SRIP 2026 - AI for Health
