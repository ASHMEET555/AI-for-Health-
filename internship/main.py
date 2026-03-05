import json
from pathlib import Path
from data_manager import DataManager
from analyzer import ClinicalAnalyzer, DataQualityAnalyzer, ComparativeAnalyzer


def process_single_patient(patient_id: str, data_dir: str = 'Data') -> dict:
    manager = DataManager(data_dir)
    patient = manager.load_patient(patient_id)

    if not patient:
        print(f"Failed to load patient {patient_id}")
        return {}

    print(f"\nProcessing {patient_id}...")
    print(f"Available signals: {patient.get_available_signals()}")
    print(f"Available events: {patient.get_available_events()}")

    analyzer = ClinicalAnalyzer(patient)
    report = analyzer.generate_report()

    quality = DataQualityAnalyzer.get_data_quality_score(patient)
    missing = DataQualityAnalyzer.detect_missing_signals(patient)

    result = {
        'patient_id': patient_id,
        'clinical_report': report,
        'data_quality_score': quality,
        'missing_signals': missing
    }

    return result


def process_all_patients(data_dir: str = 'Data') -> dict:
    manager = DataManager(data_dir)
    loaded = manager.load_all_patients()

    print(f"Loaded {len(loaded)} patients: {loaded}\n")

    results = {
        'total_patients': len(loaded),
        'patients': {}
    }

    for patient_id in loaded:
        patient = manager.get_patient(patient_id)
        analyzer = ClinicalAnalyzer(patient)
        results['patients'][patient_id] = analyzer.generate_report()

    if len(manager.patients) > 1:
        comp_analyzer = ComparativeAnalyzer(manager.patients)
        results['comparative'] = {
            'ahi_comparison': comp_analyzer.compare_ahi(),
            'oxygen_comparison': comp_analyzer.compare_oxygen_levels()
        }

    return results


def save_results(results: dict, output_dir: str = 'Dataset'):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / 'analysis_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_file}")


def main():
    data_dir = 'Data'

    results = process_all_patients(data_dir)

    print("\n" + "="*50)
    print("ANALYSIS SUMMARY")
    print("="*50)

    for patient_id, report in results['patients'].items():
        print(f"\n{patient_id}:")
        if 'respiratory_events' in report:
            ahi = report['respiratory_events'].get('ahi', 0)
            severity = report['respiratory_events'].get('severity', 'Unknown')
            print(f"  AHI: {ahi} (Severity: {severity})")

        if 'oxygen_saturation' in report:
            spo2 = report['oxygen_saturation']
            print(f"  SpO2 - Mean: {spo2.get('mean')}%, Min: {spo2.get('min')}%")

    if 'comparative' in results:
        print("\n" + "-"*50)
        print("COMPARATIVE ANALYSIS")
        print("-"*50)
        print("\nAHI Comparison:")
        for patient, ahi in results['comparative']['ahi_comparison'].items():
            print(f"  {patient}: {ahi}")

    save_results(results)
    print("\nProcessing complete!")


if __name__ == '__main__':
    main()
