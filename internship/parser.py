import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import os


class SignalParser:
    SAMPLE_RATE = 100
    
    def __init__(self, filepath: str, sample_data: bool = True):
        self.filepath = Path(filepath)
        self.metadata = {}
        self.data = []
        self.sample_data = sample_data
        self.file_size = os.path.getsize(filepath)
        self.sample_interval = 1

    def parse(self) -> Dict[str, Any]:
        with open(self.filepath, 'r', encoding='utf-8', buffering=65536) as f:
            self._extract_metadata_stream(f)
            self._extract_data_stream(f)

        return {
            'metadata': self.metadata,
            'data': self.data
        }

    def _extract_metadata_stream(self, f):
        f.seek(0)
        for _ in range(10):
            line = f.readline()
            if not line:
                break
            if ':' in line:
                key, value = line.split(':', 1)
                self.metadata[key.strip()] = value.strip()
            if line.strip() == 'Data:':
                break
        
        if self.sample_data and self.file_size > 10 * 1024 * 1024:
            total_lines = int(self.metadata.get('Length', 1000))
            self.sample_interval = max(1, total_lines // self.SAMPLE_RATE)

    def _extract_data_stream(self, f):
        f.seek(0)
        data_start = False
        line_count = 0

        for line in f:
            if line.strip() == 'Data:':
                data_start = True
                continue
            if not data_start or not line.strip():
                continue

            if self.sample_data and line_count % self.sample_interval != 0:
                line_count += 1
                continue
            
            self._parse_data_line(line)
            line_count += 1

    def _parse_data_line(self, line: str):
        line = line.strip()
        if not line:
            return

        if ';' in line:
            parts = [p.strip() for p in line.split(';')]
            if len(parts) >= 2:
                timestamp = parts[0]
                value = parts[1]

                if len(parts) > 2:
                    extra = ';'.join(parts[2:])
                    self.data.append({
                        'timestamp': timestamp,
                        'value': value,
                        'event_info': extra
                    })
                else:
                    self.data.append({
                        'timestamp': timestamp,
                        'value': value
                    })


class EventParser:
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.metadata = {}
        self.events = []

    def parse(self) -> Dict[str, Any]:
        with open(self.filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        self._extract_metadata(lines)
        self._extract_events(lines)

        return {
            'metadata': self.metadata,
            'events': self.events
        }

    def _extract_metadata(self, lines: List[str]):
        for line in lines[:10]:
            if ':' in line and not '-' in line[:30]:
                key, value = line.split(':', 1)
                self.metadata[key.strip()] = value.strip()

    def _extract_events(self, lines: List[str]):
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if '-' in line and ';' in line:
                try:
                    parts = [p.strip() for p in line.split(';')]
                    if len(parts) >= 3:
                        time_range = parts[0]
                        duration = parts[1]
                        event_type = parts[2]
                        stage = parts[3] if len(parts) > 3 else 'Unknown'

                        self.events.append({
                            'time_range': time_range,
                            'duration': duration,
                            'event_type': event_type,
                            'sleep_stage': stage
                        })
                except:
                    continue
            elif ';' in line:
                try:
                    parts = [p.strip() for p in line.split(';')]
                    if len(parts) >= 2:
                        timestamp = parts[0]
                        value = parts[1]
                        self.events.append({
                            'timestamp': timestamp,
                            'value': value
                        })
                except:
                    continue


def parse_file(filepath: str, sample_large: bool = True) -> Dict[str, Any]:
    name = Path(filepath).stem.lower()

    if 'event' in name or 'sleep' in name or 'profil' in name:
        parser = EventParser(filepath)
    else:
        parser = SignalParser(filepath, sample_data=sample_large)

    return parser.parse()
