import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from data_manager import PatientData
from analyzer import ClinicalAnalyzer


class Visualizer:
    def __init__(self, output_dir: str = 'Visualizations'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_oxygen_saturation(self, patient: PatientData, save: bool = True):
        spo2_processor = patient.get_signal('spo2')
        if not spo2_processor:
            return

        timestamps, values = spo2_processor.get_raw_data()
        if len(values) == 0:
            return

        fig, ax = plt.subplots(figsize=(12, 4))
        x = np.arange(len(values))
        ax.plot(x, values, linewidth=0.5)
        ax.set_xlabel('Time Points')
        ax.set_ylabel('SpO2 (%)')
        ax.set_title(f'{patient.patient_id} - Oxygen Saturation')
        ax.grid(alpha=0.3)

        if save:
            self._save_figure(fig, f'{patient.patient_id}_spo2.png')
        return fig

    def plot_flow_signal(self, patient: PatientData, save: bool = True):
        flow_processor = patient.get_signal('flow')
        if not flow_processor:
            return

        timestamps, values = flow_processor.get_raw_data()
        if len(values) == 0:
            return

        fig, ax = plt.subplots(figsize=(12, 4))
        x = np.arange(len(values))
        ax.plot(x, values, linewidth=0.5, color='green')
        ax.set_xlabel('Time Points')
        ax.set_ylabel('Flow')
        ax.set_title(f'{patient.patient_id} - Respiratory Flow')
        ax.grid(alpha=0.3)

        if save:
            self._save_figure(fig, f'{patient.patient_id}_flow.png')
        return fig

    def plot_sleep_stages(self, patient: PatientData, save: bool = True):
        stage_counts = {}
        
        for event_key in patient.events.keys():
            if 'sleep' in event_key or 'profil' in event_key:
                events = patient.events[event_key]['raw']
                for event in events:
                    if 'value' in event:
                        stage = event['value']
                        stage_counts[stage] = stage_counts.get(stage, 0) + 1
        
        if not stage_counts:
            return None

        fig, ax = plt.subplots(figsize=(10, 5))
        stages = list(stage_counts.keys())
        counts = list(stage_counts.values())
        
        colors = {'Wake': 'red', 'N1': 'orange', 'N2': 'yellow', 'N3': 'green', 
                  'N4': 'blue', 'REM': 'purple', 'Movement': 'gray'}
        bar_colors = [colors.get(s, 'lightblue') for s in stages]

        ax.bar(stages, counts, color=bar_colors, edgecolor='black', linewidth=0.5)
        ax.set_ylabel('Count', fontsize=11)
        ax.set_xlabel('Sleep Stage', fontsize=11)
        ax.set_title(f'{patient.patient_id} - Sleep Stages Distribution', fontsize=12, fontweight='bold')
        ax.tick_params(axis='x', rotation=45, labelsize=10)
        ax.grid(axis='y', alpha=0.3)

        if save:
            self._save_figure(fig, f'{patient.patient_id}_sleep_stages.png')
        return fig

    def plot_respiratory_events(self, patient: PatientData, save: bool = True):
        event_counts = {}
        
        for event_key in patient.events.keys():
            if 'event' in event_key and 'sleep' not in event_key:
                events = patient.events[event_key]['raw']
                for event in events:
                    if 'event_type' in event:
                        evt_type = event['event_type']
                        event_counts[evt_type] = event_counts.get(evt_type, 0) + 1
        
        if not event_counts:
            return None

        fig, ax = plt.subplots(figsize=(10, 5))
        events = list(event_counts.keys())
        counts = list(event_counts.values())

        colors = {'Obstructive Apnea': 'darkred', 'Central Apnea': 'red', 
                  'Mixed Apnea': 'orange', 'Hypopnea': 'coral'}
        bar_colors = [colors.get(e, 'lightcoral') for e in events]

        ax.barh(events, counts, color=bar_colors, edgecolor='black', linewidth=0.5)
        ax.set_xlabel('Count', fontsize=11)
        ax.set_title(f'{patient.patient_id} - Respiratory Events', fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        if save:
            self._save_figure(fig, f'{patient.patient_id}_events.png')
        return fig

    def plot_comparison_ahi(self, ahi_data: dict, save: bool = True):
        fig, ax = plt.subplots(figsize=(10, 4))
        patients = list(ahi_data.keys())
        ahi_values = list(ahi_data.values())

        colors = ['green' if v < 5 else 'yellow' if v < 15 else 'orange' if v < 30 else 'red'
                  for v in ahi_values]

        ax.bar(patients, ahi_values, color=colors)
        ax.set_ylabel('AHI Index')
        ax.set_title('AHI Comparison Across Patients')
        ax.axhline(y=5, color='green', linestyle='--', alpha=0.5, label='Normal (5)')
        ax.axhline(y=15, color='yellow', linestyle='--', alpha=0.5, label='Mild (15)')
        ax.axhline(y=30, color='red', linestyle='--', alpha=0.5, label='Severe (30)')
        ax.legend()

        if save:
            self._save_figure(fig, 'ahi_comparison.png')
        return fig

    def generate_patient_report(self, patient: PatientData):
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.25, 
                              top=0.93, bottom=0.07, left=0.08, right=0.95)

        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_on_axis(ax1, patient, 'oxygen')

        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_on_axis(ax2, patient, 'flow')

        ax3 = fig.add_subplot(gs[1, :])
        self._plot_on_axis(ax3, patient, 'stages')

        ax4 = fig.add_subplot(gs[2, :])
        self._plot_on_axis(ax4, patient, 'events')

        fig.suptitle(f'{patient.patient_id} - Comprehensive Sleep Study Report', 
                     fontsize=16, fontweight='bold')
        self._save_figure(fig, f'{patient.patient_id}_report.png')
        return fig

    def _plot_on_axis(self, ax, patient: PatientData, plot_type: str):
        if plot_type == 'oxygen':
            spo2_processor = patient.get_signal('spo2')
            if spo2_processor:
                _, values = spo2_processor.get_raw_data()
                if len(values) > 0:
                    ax.plot(values, linewidth=0.6, color='#1f77b4')
                    ax.set_ylabel('SpO2 (%)', fontsize=10)
                    ax.set_xlabel('Time Points', fontsize=10)
                    ax.set_title('Oxygen Saturation', fontsize=11, fontweight='bold')
                    ax.grid(alpha=0.3, linewidth=0.5)
                    ax.set_ylim([0, max(100, max(values) if len(values) > 0 else 100)])
                else:
                    ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
        elif plot_type == 'flow':
            flow_processor = patient.get_signal('flow')
            if flow_processor:
                _, values = flow_processor.get_raw_data()
                if len(values) > 0:
                    ax.plot(values, linewidth=0.7, color='#2ca02c')
                    ax.set_ylabel('Flow', fontsize=10)
                    ax.set_xlabel('Time Points', fontsize=10)
                    ax.set_title('Respiratory Flow', fontsize=11, fontweight='bold')
                    ax.grid(alpha=0.3, linewidth=0.5)
                    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.3)
                else:
                    ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
        elif plot_type == 'stages':
            stage_counts = {}
            for event_key in patient.events.keys():
                if 'sleep' in event_key or 'profil' in event_key:
                    events = patient.events[event_key]['raw']
                    for event in events:
                        if 'value' in event:
                            stage = event['value']
                            stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            if stage_counts:
                stages = list(stage_counts.keys())
                counts = list(stage_counts.values())
                colors_map = {'Wake': 'red', 'N1': 'orange', 'N2': 'yellow', 'N3': 'green', 
                              'N4': 'blue', 'REM': 'purple', 'Movement': 'gray'}
                bar_colors = [colors_map.get(s, 'lightblue') for s in stages]
                ax.bar(stages, counts, color=bar_colors, edgecolor='black', linewidth=0.5)
                ax.set_ylabel('Count', fontsize=10)
                ax.set_title('Sleep Stages Distribution', fontsize=11, fontweight='bold')
                ax.tick_params(axis='x', rotation=45, labelsize=9)
                ax.grid(axis='y', alpha=0.3)
            else:
                ax.text(0.5, 0.5, 'No Sleep Stage Data', ha='center', va='center', transform=ax.transAxes, fontsize=10)
        elif plot_type == 'events':
            event_counts = {}
            for event_key in patient.events.keys():
                if 'event' in event_key and 'sleep' not in event_key:
                    events = patient.events[event_key]['raw']
                    for event in events:
                        if 'event_type' in event:
                            evt_type = event['event_type']
                            event_counts[evt_type] = event_counts.get(evt_type, 0) + 1
            
            if event_counts:
                events = list(event_counts.keys())
                counts = list(event_counts.values())
                colors_map = {'Obstructive Apnea': 'darkred', 'Central Apnea': 'red', 
                              'Mixed Apnea': 'orange', 'Hypopnea': 'coral'}
                bar_colors = [colors_map.get(e, 'lightcoral') for e in events]
                ax.barh(events, counts, color=bar_colors, edgecolor='black', linewidth=0.5)
                ax.set_xlabel('Count', fontsize=10)
                ax.set_title('Respiratory Events', fontsize=11, fontweight='bold')
                ax.grid(axis='x', alpha=0.3)
            else:
                ax.text(0.5, 0.5, 'No Events Detected', ha='center', va='center', transform=ax.transAxes, fontsize=10)

    def _save_figure(self, fig, filename: str):
        output_file = self.output_dir / filename
        fig.savefig(output_file, dpi=100, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved: {output_file}")
