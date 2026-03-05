import numpy as np
from datetime import datetime
from typing import List, Tuple, Dict, Any


class SignalProcessor:
    def __init__(self, data: List[Dict], metadata: Dict):
        self.data = data
        self.metadata = metadata
        self.timestamps = []
        self.values = []
        self._parse_signal()

    def _parse_signal(self):
        for point in self.data:
            try:
                ts = point['timestamp']
                val = float(point['value'])
                self.timestamps.append(ts)
                self.values.append(val)
            except (ValueError, KeyError):
                continue

    def normalize(self) -> Tuple[List[str], np.ndarray]:
        if len(self.values) == 0:
            return self.timestamps, np.array([])

        arr = np.array(self.values, dtype=np.float32)
        mean = np.mean(arr)
        std = np.std(arr)

        if std != 0:
            normalized = (arr - mean) / std
        else:
            normalized = arr - mean

        return self.timestamps, normalized

    def smooth(self, window_size: int = 5) -> Tuple[List[str], np.ndarray]:
        if len(self.values) < window_size:
            return self.timestamps, np.array(self.values, dtype=np.float32)

        kernel = np.ones(window_size, dtype=np.float32) / window_size
        arrval = np.array(self.values, dtype=np.float32)
        smoothed = np.convolve(arrval, kernel, mode='same')

        return self.timestamps, smoothed

    def detect_outliers(self, threshold: float = 3.0) -> List[int]:
        if len(self.values) == 0:
            return []
        
        arr = np.array(self.values, dtype=np.float32)
        mean = np.mean(arr)
        std = np.std(arr)

        outliers = []
        if std != 0:
            for i, val in enumerate(arr):
                if abs((val - mean) / std) > threshold:
                    outliers.append(i)

        return outliers

    def get_statistics(self) -> Dict[str, float]:
        arr = np.array(self.values, dtype=np.float32)
        if len(arr) == 0:
            return {
                'mean': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'median': 0,
                'count': 0
            }
        return {
            'mean': float(np.mean(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'median': float(np.median(arr)),
            'count': len(arr)
        }

    def resample(self, target_rate: float) -> Tuple[List[str], np.ndarray]:
        current_rate = self._get_sample_rate()
        if current_rate == 0:
            return self.timestamps, np.array(self.values)

        ratio = target_rate / current_rate
        new_length = int(len(self.values) * ratio)

        if new_length <= 1:
            return self.timestamps, np.array(self.values)

        indices = np.linspace(0, len(self.values) - 1, new_length)
        resampled = np.interp(indices, np.arange(len(self.values)), self.values)

        new_timestamps = [self.timestamps[0] if not self.timestamps else '']
        return new_timestamps, resampled

    def _get_sample_rate(self) -> float:
        try:
            rate_str = self.metadata.get('Sample Rate', '1')
            return float(rate_str)
        except (ValueError, TypeError):
            return 1.0

    def get_raw_data(self) -> Tuple[List[str], np.ndarray]:
        return self.timestamps, np.array(self.values, dtype=np.float32)


class EventProcessor:
    def __init__(self, events: List[Dict]):
        self.events = events

    def count_by_type(self) -> Dict[str, int]:
        counts = {}
        for event in self.events:
            event_type = event.get('event_type', 'Unknown')
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts

    def count_by_stage(self) -> Dict[str, int]:
        counts = {}
        for event in self.events:
            stage = event.get('sleep_stage', 'Unknown')
            counts[stage] = counts.get(stage, 0) + 1
        return counts

    def get_apnea_index(self, total_hours: float) -> float:
        apnea_events = sum(1 for e in self.events
                          if 'apnea' in e.get('event_type', '').lower())
        if total_hours == 0:
            return 0
        return apnea_events / total_hours

    def get_hypopnea_index(self, total_hours: float) -> float:
        hypopnea_events = sum(1 for e in self.events
                             if 'hypopnea' in e.get('event_type', '').lower())
        if total_hours == 0:
            return 0
        return hypopnea_events / total_hours

    def get_ahi(self, total_hours: float) -> float:
        apnea_idx = self.get_apnea_index(total_hours)
        hypopnea_idx = self.get_hypopnea_index(total_hours)
        return apnea_idx + hypopnea_idx
