#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from data_manager import DataManager
from analyzer import ClinicalAnalyzer, DataQualityAnalyzer, ComparativeAnalyzer
from visualizer import Visualizer
from utils import DataExporter, DataValidator, ReportGenerator


def run_full_pipeline(data_dir: str = 'Data', output_dir: str = 'Dataset'):
    print("\n" + "="*60)
    print("AI FOR HEALTH - SRIP 2026 PIPELINE")
    print("="*60 + "\n")

    manager = DataManager(data_dir)
    loaded = manager.load_all_patients()

    if not loaded:
        print(f"No patients found in {data_dir}")
        return

    print(f"Loaded {len(loaded)} patients: {loaded}\n")

    results = {
        'total_patients': len(loaded),
        'patients': {},
        'quality_metrics': {},
        'validation': {}
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for patient_id in loaded:
        patient = manager.get_patient(patient_id)

        print(f"\nAnalyzing {patient_id}...")

        analyzer = ClinicalAnalyzer(patient)
        report = analyzer.generate_report()
        results['patients'][patient_id] = report

        quality = DataQualityAnalyzer.get_data_quality_score(patient)
        results['quality_metrics'][patient_id] = quality

        validation = DataValidator.validate_patient_data(patient)
        results['validation'][patient_id] = validation

        DataExporter.export_to_csv(patient, str(output_path))
        DataExporter.export_events_to_csv(patient, str(output_path))

        print(f"  - Data Quality: {quality}%")
        print(f"  - Signals found: {len(patient.get_available_signals())}")
        print(f"  - Events found: {len(patient.get_available_events())}")

        if 'respiratory_events' in report:
            ahi = report['respiratory_events'].get('ahi', 0)
            severity = report['respiratory_events'].get('severity', 'Unknown')
            print(f"  - AHI: {ahi} ({severity})")

    if len(manager.patients) > 1:
        comp_analyzer = ComparativeAnalyzer(manager.patients)
        results['comparative'] = {
            'ahi_comparison': comp_analyzer.compare_ahi(),
            'oxygen_comparison': comp_analyzer.compare_oxygen_levels()
        }

    json_file = output_path / 'analysis_results.json'
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {json_file}")

    DataExporter.export_statistics_to_csv(
        manager,
        str(output_path / 'signal_statistics.csv')
    )

    ReportGenerator.generate_text_report(
        manager,
        str(output_path / 'analysis_report.txt')
    )

    ReportGenerator.generate_html_report(
        manager,
        str(output_path / 'analysis_report.html')
    )

    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)

    for patient_id, report in results['patients'].items():
        print(f"\n{patient_id}:")
        if 'respiratory_events' in report:
            events = report['respiratory_events']
            print(f"  AHI: {events.get('ahi', 0)}")
            print(f"  Severity: {events.get('severity', 'Unknown')}")
            print(f"  Total Events: {events.get('total_events', 0)}")

        if 'oxygen_saturation' in report:
            spo2 = report['oxygen_saturation']
            print(f"  SpO2 Mean: {spo2.get('mean', 0)}%")
            print(f"  SpO2 Min: {spo2.get('min', 0)}%")

    print("\n" + "="*60 + "\n")


def run_visualization_pipeline(data_dir: str = 'Data', output_dir: str = 'Visualizations'):
    print(f"\nGenerating visualizations...")

    manager = DataManager(data_dir)
    loaded = manager.load_all_patients()

    if not loaded:
        print("No patients to visualize")
        return

    visualizer = Visualizer(output_dir)

    for patient_id in loaded:
        patient = manager.get_patient(patient_id)
        print(f"  Visualizing {patient_id}...")
        visualizer.plot_oxygen_saturation(patient)
        visualizer.plot_flow_signal(patient)
        visualizer.plot_sleep_stages(patient)
        visualizer.plot_respiratory_events(patient)
        visualizer.generate_patient_report(patient)

    print(f"Visualizations saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Sleep Apnea Analysis Pipeline')
    parser.add_argument('--data', default='Data', help='Data directory path')
    parser.add_argument('--output', default='Dataset', help='Output directory path')
    parser.add_argument('--viz', action='store_true', help='Generate visualizations')
    parser.add_argument('--viz-only', action='store_true', help='Only generate visualizations')

    args = parser.parse_args()

    if args.viz_only:
        run_visualization_pipeline(args.data, 'Visualizations')
    else:
        run_full_pipeline(args.data, args.output)
        if args.viz:
            run_visualization_pipeline(args.data, 'Visualizations')


if __name__ == '__main__':
    main()
