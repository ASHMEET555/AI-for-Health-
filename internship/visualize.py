from data_manager import DataManager
from visualizer import Visualizer


def generate_visualizations(data_dir: str = 'Data', output_dir: str = 'Visualizations'):
    manager = DataManager(data_dir)
    loaded = manager.load_all_patients()

    if not loaded:
        print("No patients to visualize")
        return

    visualizer = Visualizer(output_dir)

    print(f"Generating visualizations for {len(loaded)} patients...\n")

    for patient_id in loaded:
        patient = manager.get_patient(patient_id)

        print(f"Processing {patient_id}...")
        visualizer.plot_oxygen_saturation(patient)
        visualizer.plot_flow_signal(patient)
        visualizer.plot_sleep_stages(patient)
        visualizer.plot_respiratory_events(patient)
        visualizer.generate_patient_report(patient)

    print("\nVisualization complete!")


if __name__ == '__main__':
    generate_visualizations()
