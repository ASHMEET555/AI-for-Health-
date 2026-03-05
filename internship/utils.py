import csv
import json
from pathlib import Path
from typing import Dict, List, Any
from data_manager import DataManager, PatientData


class DataExporter:
    @staticmethod
    def export_to_csv(patient: PatientData, output_dir: str = 'Dataset'):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for sig_name, sig_data in patient.signals.items():
            processor = sig_data['processor']
            timestamps, values = processor.get_raw_data()

            csv_file = output_path / f"{patient.patient_id}_{sig_name}.csv"
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'value'])
                for ts, val in zip(timestamps, values):
                    writer.writerow([ts, val])

    @staticmethod
    def export_events_to_csv(patient: PatientData, output_dir: str = 'Dataset'):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for event_name, event_data in patient.events.items():
            events = event_data['raw']

            csv_file = output_path / f"{patient.patient_id}_{event_name}.csv"
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['time_range', 'duration', 'event_type', 'sleep_stage'])
                for event in events:
                    writer.writerow([
                        event.get('time_range', ''),
                        event.get('duration', ''),
                        event.get('event_type', ''),
                        event.get('sleep_stage', '')
                    ])

    @staticmethod
    def export_statistics_to_csv(manager: DataManager, output_file: str):
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        patients = manager.get_all_patients()
        with open(output_path, 'w', newline='') as f:
            fieldnames = ['patient_id', 'signal_name', 'mean', 'std', 'min', 'max', 'count']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for patient_id, patient in patients.items():
                for sig_name, sig_data in patient.signals.items():
                    processor = sig_data['processor']
                    stats = processor.get_statistics()

                    writer.writerow({
                        'patient_id': patient_id,
                        'signal_name': sig_name,
                        'mean': round(stats['mean'], 2),
                        'std': round(stats['std'], 2),
                        'min': round(stats['min'], 2),
                        'max': round(stats['max'], 2),
                        'count': stats['count']
                    })


class DataValidator:
    @staticmethod
    def validate_signal(processor, min_samples: int = 1000) -> Dict[str, Any]:
        stats = processor.get_statistics()
        return {
            'has_data': stats['count'] > 0,
            'sufficient_samples': stats['count'] >= min_samples,
            'data_points': stats['count'],
            'mean': round(stats['mean'], 2),
            'std': round(stats['std'], 2)
        }

    @staticmethod
    def validate_patient_data(patient: PatientData) -> Dict[str, Any]:
        validation = {
            'patient_id': patient.patient_id,
            'signals': {},
            'events': {}
        }

        for sig_name, sig_data in patient.signals.items():
            validation['signals'][sig_name] = DataValidator.validate_signal(sig_data['processor'])

        for event_name, event_data in patient.events.items():
            event_count = len(event_data['raw'])
            validation['events'][event_name] = {
                'has_events': event_count > 0,
                'event_count': event_count
            }

        return validation


class ReportGenerator:
    @staticmethod
    def generate_text_report(manager: DataManager, output_file: str):
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write("AI FOR HEALTH - SLEEP APNEA ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n\n")

            patients = manager.get_all_patients()
            f.write(f"Total Patients Analyzed: {len(patients)}\n")
            f.write(f"Patient IDs: {', '.join(patients.keys())}\n\n")

            for patient_id, patient in patients.items():
                f.write(f"\nPATIENT: {patient_id}\n")
                f.write("-" * 60 + "\n")

                validation = DataValidator.validate_patient_data(patient)
                f.write(f"Available Signals: {list(validation['signals'].keys())}\n")
                f.write(f"Available Events: {list(validation['events'].keys())}\n\n")

                for sig_name, sig_validation in validation['signals'].items():
                    f.write(f"  {sig_name}:\n")
                    f.write(f"    Data Points: {sig_validation['data_points']}\n")
                    f.write(f"    Mean: {sig_validation['mean']}\n")
                    f.write(f"    Std Dev: {sig_validation['std']}\n")

                f.write("\n")

    @staticmethod
    def generate_html_report(manager: DataManager, output_file: str):
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sleep Apnea Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                .patient { border: 1px solid #ddd; padding: 15px; margin: 10px 0; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
            </style>
        </head>
        <body>
            <h1>Sleep Apnea Analysis Report</h1>
        """

        patients = manager.get_all_patients()
        for patient_id, patient in patients.items():
            validation = DataValidator.validate_patient_data(patient)

            html_content += f"""
            <div class="patient">
                <h2>{patient_id}</h2>
                <table>
                    <tr>
                        <th>Signal</th>
                        <th>Data Points</th>
                        <th>Mean</th>
                        <th>Std Dev</th>
                    </tr>
            """

            for sig_name, sig_validation in validation['signals'].items():
                html_content += f"""
                    <tr>
                        <td>{sig_name}</td>
                        <td>{sig_validation['data_points']}</td>
                        <td>{sig_validation['mean']}</td>
                        <td>{sig_validation['std']}</td>
                    </tr>
                """

            html_content += """
                </table>
            </div>
            """

        html_content += """
        </body>
        </html>
        """

        with open(output_path, 'w') as f:
            f.write(html_content)
