from pathlib import Path
from typing import Dict, List, Optional, Any
import json
from parser import parse_file
from processor import SignalProcessor, EventProcessor


class PatientData:
    def __init__(self, patient_id: str, data_dir: str):
        self.patient_id = patient_id
        self.data_dir = Path(data_dir)
        self.signals = {}
        self.events = {}
        self.metadata = {}

    def load(self) -> bool:
        patient_path = self.data_dir / self.patient_id
        if not patient_path.exists():
            return False

        for file_path in patient_path.glob('*.txt'):
            signal_name = file_path.stem.lower()

            data = parse_file(str(file_path))

            if 'event' in signal_name:
                processor = EventProcessor(data['events'])
                self.events[signal_name] = {
                    'raw': data['events'],
                    'processor': processor,
                    'metadata': data['metadata']
                }
            else:
                processor = SignalProcessor(data['data'], data['metadata'])
                self.signals[signal_name] = {
                    'raw': data['data'],
                    'processor': processor,
                    'metadata': data['metadata']
                }

        self.metadata = self._extract_session_metadata()
        return True

    def _extract_session_metadata(self) -> Dict[str, Any]:
        metadata = {}
        if self.signals:
            first_signal = next(iter(self.signals.values()))
            metadata['start_time'] = first_signal['metadata'].get('Start Time')

        return metadata

    def get_signal(self, signal_name: str) -> Optional[SignalProcessor]:
        signal_key = self._find_key(signal_name, self.signals)
        if signal_key:
            return self.signals[signal_key]['processor']
        return None

    def get_events(self, event_name: str) -> Optional[EventProcessor]:
        event_key = self._find_key(event_name, self.events)
        if event_key:
            return self.events[event_key]['processor']
        return None

    def _find_key(self, name: str, data_dict: Dict) -> Optional[str]:
        name_lower = name.lower()
        for key in data_dict.keys():
            if name_lower in key:
                return key
        return None

    def get_available_signals(self) -> List[str]:
        return list(self.signals.keys())

    def get_available_events(self) -> List[str]:
        return list(self.events.keys())

    def export_to_dict(self) -> Dict[str, Any]:
        result = {
            'patient_id': self.patient_id,
            'metadata': self.metadata,
            'signals': {}
        }

        for sig_name, sig_data in self.signals.items():
            stats = sig_data['processor'].get_statistics()
            result['signals'][sig_name] = {
                'metadata': sig_data['metadata'],
                'statistics': stats
            }

        return result

    def export_to_json(self, output_file: str):
        data = self.export_to_dict()
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)


class DataManager:
    def __init__(self, data_dir: str = 'internship/Data'):
        self.data_dir = Path(data_dir)
        self.patients = {}

    def load_patient(self, patient_id: str) -> Optional[PatientData]:
        patient = PatientData(patient_id, str(self.data_dir))
        if patient.load():
            self.patients[patient_id] = patient
            return patient
        return None

    def load_all_patients(self) -> List[str]:
        loaded = []
        for patient_dir in self.data_dir.iterdir():
            if patient_dir.is_dir():
                patient_id = patient_dir.name
                if self.load_patient(patient_id):
                    loaded.append(patient_id)
        return loaded

    def get_patient(self, patient_id: str) -> Optional[PatientData]:
        return self.patients.get(patient_id)

    def get_all_patients(self) -> Dict[str, PatientData]:
        return self.patients

    def export_all_patients(self, output_dir: str):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for patient_id, patient in self.patients.items():
            output_file = output_path / f"{patient_id}_data.json"
            patient.export_to_json(str(output_file))
