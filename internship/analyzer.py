from typing import Dict, List, Any, Tuple
from data_manager import PatientData
import numpy as np


class ClinicalAnalyzer:
    def __init__(self, patient: PatientData):
        self.patient = patient

    def analyze_oxygen_saturation(self) -> Dict[str, Any]:
        spo2_processor = self.patient.get_signal('spo2')
        if not spo2_processor:
            return {}

        stats = spo2_processor.get_statistics()
        outliers = spo2_processor.detect_outliers(threshold=2.5)

        return {
            'mean': round(stats['mean'], 2),
            'min': round(stats['min'], 2),
            'max': round(stats['max'], 2),
            'std': round(stats['std'], 2),
            'desaturation_events': len(outliers),
            'total_points': stats['count']
        }

    def analyze_sleep_stages(self) -> Dict[str, Any]:
        for event_key in self.patient.events.keys():
            if 'sleep' in event_key or 'profil' in event_key:
                sleep_data = self.patient.events[event_key]
                events = sleep_data['raw']
                
                stage_counts = {}
                for event in events:
                    if 'value' in event:
                        stage = event['value']
                        stage_counts[stage] = stage_counts.get(stage, 0) + 1
                
                if stage_counts:
                    return {
                        'stage_distribution': stage_counts,
                        'total_events': sum(stage_counts.values())
                    }
        
        return {
            'stage_distribution': {},
            'total_events': 0
        }

    def analyze_respiratory_events(self) -> Dict[str, Any]:
        events_processor = self.patient.get_events('event')
        if not events_processor:
            return {}

        event_counts = events_processor.count_by_type()
        total_hours = 8.0

        return {
            'event_types': event_counts,
            'total_events': sum(event_counts.values()),
            'apnea_index': round(events_processor.get_apnea_index(total_hours), 2),
            'hypopnea_index': round(events_processor.get_hypopnea_index(total_hours), 2),
            'ahi': round(events_processor.get_ahi(total_hours), 2),
            'severity': self._classify_osa_severity(events_processor.get_ahi(total_hours))
        }

    def analyze_thoracic_movement(self) -> Dict[str, Any]:
        thorac_processor = self.patient.get_signal('thorac')
        if not thorac_processor:
            return {}

        stats = thorac_processor.get_statistics()
        return {
            'mean': round(stats['mean'], 2),
            'std': round(stats['std'], 2),
            'activity_level': 'Normal' if stats['std'] > 10 else 'Low',
            'variability': round(stats['std'], 2)
        }

    def analyze_flow_signal(self) -> Dict[str, Any]:
        flow_processor = self.patient.get_signal('flow')
        if not flow_processor:
            return {}

        stats = flow_processor.get_statistics()
        return {
            'mean': round(stats['mean'], 2),
            'std': round(stats['std'], 2),
            'breathing_pattern': 'Regular' if stats['std'] < 30 else 'Irregular'
        }

    def _classify_osa_severity(self, ahi: float) -> str:
        if ahi < 5:
            return 'Normal'
        elif ahi < 15:
            return 'Mild'
        elif ahi < 30:
            return 'Moderate'
        else:
            return 'Severe'

    def generate_report(self) -> Dict[str, Any]:
        return {
            'patient_id': self.patient.patient_id,
            'oxygen_saturation': self.analyze_oxygen_saturation(),
            'sleep_stages': self.analyze_sleep_stages(),
            'respiratory_events': self.analyze_respiratory_events(),
            'thoracic_movement': self.analyze_thoracic_movement(),
            'flow_signal': self.analyze_flow_signal()
        }


class DataQualityAnalyzer:
    @staticmethod
    def check_signal_completeness(patient: PatientData) -> Dict[str, float]:
        completeness = {}
        for sig_name, sig_data in patient.signals.items():
            processor = sig_data['processor']
            stats = processor.get_statistics()
            completeness[sig_name] = stats['count']
        return completeness

    @staticmethod
    def detect_missing_signals(patient: PatientData) -> List[str]:
        expected = ['flow', 'spo2', 'thorac', 'sleep', 'event']
        available = set()

        for sig_name in patient.get_available_signals() + patient.get_available_events():
            for exp in expected:
                if exp in sig_name.lower():
                    available.add(exp)

        missing = set(expected) - available
        return list(missing)

    @staticmethod
    def get_data_quality_score(patient: PatientData) -> float:
        missing_count = len(DataQualityAnalyzer.detect_missing_signals(patient))
        max_signals = 5
        score = ((max_signals - missing_count) / max_signals) * 100
        return round(score, 2)


class ComparativeAnalyzer:
    def __init__(self, patients: Dict[str, PatientData]):
        self.patients = patients

    def compare_ahi(self) -> Dict[str, float]:
        results = {}
        for patient_id, patient in self.patients.items():
            analyzer = ClinicalAnalyzer(patient)
            report = analyzer.analyze_respiratory_events()
            results[patient_id] = report.get('ahi', 0)
        return results

    def compare_oxygen_levels(self) -> Dict[str, Dict[str, float]]:
        results = {}
        for patient_id, patient in self.patients.items():
            analyzer = ClinicalAnalyzer(patient)
            spo2_data = analyzer.analyze_oxygen_saturation()
            results[patient_id] = {
                'mean': spo2_data.get('mean', 0),
                'min': spo2_data.get('min', 0)
            }
        return results
