import numpy as np
import pandas as pd
import requests
import json

def generate_single_sample(duration=1, sampling_rate=1000, frequency=50, amplitude=230,
                           anomaly_probability=0.1, anomaly_duration=100, anomaly_drop=0.2):
    time = np.arange(0, duration, 1/sampling_rate)

    normal_wave = amplitude * np.sqrt(2) * np.sin(2 * np.pi * frequency * time)
    anomaly_wave = np.copy(normal_wave)
    labels = np.zeros_like(time, dtype=int)

    in_anomaly = False
    for i in range(len(time)):
        if np.random.rand() < anomaly_probability and not in_anomaly:
            end_index = min(i + anomaly_duration, len(time))
            anomaly_wave[i:end_index] = anomaly_wave[i:end_index] * anomaly_drop
            labels[i:end_index] = 1
            in_anomaly = True
            print("Anomaly detected at index:", i)
        elif labels[i] == 0:
            in_anomaly = False

    data = {
        'time': time,
        'normal_wave': normal_wave,
        'anomaly_wave': anomaly_wave,
        'is_anomaly': labels
    }

    return pd.DataFrame(data)


sample_df = generate_single_sample(duration=1, sampling_rate=1000, frequency=50, amplitude=230,
                                   anomaly_probability=0.001, anomaly_duration=100, anomaly_drop=0.2)

time_series_data = [{"time": str(row['time']), "value": row['anomaly_wave']} for _, row in sample_df.iterrows()]

url = "http://127.0.0.1:8000/timeseries/1234"  

payload = {
    "ts_id": "1234",  # A unique identifier for the time series
    "process_id": "", # Not currently definied
    "data": time_series_data,
    "anomaly": False  # Set as False since we are not detecting anomalies here
}

response = requests.put(url, json=payload)

if response.status_code == 200:
    print("Sample waveform stored successfully.")
else:
    print(f"Failed to store the waveform. Status code: {response.status_code}")
    print(f"Response: {response.text}")

