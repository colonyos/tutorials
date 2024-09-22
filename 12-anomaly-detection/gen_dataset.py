import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Define parameters for the 230V AC time series
duration = 100  # 1 second duration
time_resolution = 0.001  # 0.1 millisecond resolution for high fidelity
time = np.arange(0, duration, time_resolution)  # time from 0 to 1 second
anomaly_probability = 0.00009

frequency = 50  # 50 Hz frequency
amplitude = 230 * np.sqrt(2)  # Peak amplitude for 230V RMS (~325V)

# Generate the normal sinusoidal wave
normal_wave = amplitude * np.sin(2 * np.pi * frequency * time)

anomaly_wave = np.copy(normal_wave)
labels = np.zeros_like(time, dtype=int)  # 0 for normal, 1 for anomaly

# Generate anomalies
in_anomaly = False
for i in range(len(time)):
    if np.random.rand() < anomaly_probability and not in_anomaly:
        # Create an anomaly at this point: e.g., a sudden drop in voltage for a short duration
        end_index = min(i + 100, len(time))  # The anomaly will last for a small time period (100 points)
        anomaly_wave[i:end_index] = anomaly_wave[i:end_index] * 0.2  # 80% dip in voltage
        labels[i:end_index] = 1  # Mark as anomaly
        in_anomaly = True  # Set flag to indicate an anomaly is in progress
    elif labels[i] == 0:  # Reset flag when anomaly ends
        in_anomaly = False

# Create the dataset
data = {
    'time': time,
    'normal_wave': normal_wave,
    'anomaly_wave': anomaly_wave,
    'is_anomaly': labels
}

df = pd.DataFrame(data)

# Save the dataset to CSV
csv_file_path = "dataset.csv"
df.to_csv(csv_file_path, index=False)
