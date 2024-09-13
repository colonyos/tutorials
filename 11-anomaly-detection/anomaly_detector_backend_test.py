import requests
import pandas as pd
import numpy as np
from scipy.stats import entropy

def fetch_time_series(process_id):
    url = f"http://127.0.0.1:8000/timeseries/{process_id}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch time series. Status code: {response.status_code}")

def convert_to_dataframe(time_series_data):
    time_series = time_series_data['data']
    
    df = pd.DataFrame(time_series)
    
    return df

reference_wave_global = None

def set_reference_wave(reference_wave):
    global reference_wave_global
    reference_wave_global = reference_wave

def compute_histogram(data, bins=50):
    hist, bin_edges = np.histogram(data, bins=bins, density=True)
    hist = hist + 1e-10  # Avoid division by zero
    return hist, bin_edges

def compute_kl_divergence(p, q):
    return entropy(p, q)

def detect_anomaly(sample_wave, kl_threshold=0.010199148586751076):
    global reference_wave_global

    if reference_wave_global is None:
        raise ValueError("Reference wave has not been set. Use 'set_reference_wave()' to set the reference.")

    sample_hist, _ = compute_histogram(sample_wave)
    reference_hist, _ = compute_histogram(reference_wave_global)
    kl_div = compute_kl_divergence(reference_hist, sample_hist)
    anomaly_detected = kl_div > kl_threshold

    return anomaly_detected, kl_div

def generate_single_sample(duration=1, sampling_rate=1000, frequency=50, amplitude=230,
                           anomaly_probability=0.0001, anomaly_duration=100, anomaly_drop=0.2):
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
        elif labels[i] == 0:
            in_anomaly = False

    data = {
        'time': time,
        'normal_wave': normal_wave,
        'anomaly_wave': anomaly_wave,
        'is_anomaly': labels
    }

    return pd.DataFrame(data)

def update_anomaly_status(process_id, anomaly_status):
    url = f"http://127.0.0.1:8000/timeseries/{process_id}/anomaly"
    
    params = {"anomaly": anomaly_status}
    response = requests.patch(url, params=params)
    
    if response.status_code == 200:
        print(f"Database updated successfully. Process ID: {process_id}, Anomaly: {anomaly_status}")
    else:
        print(f"Failed to update the database. Status code: {response.status_code}")
        print(f"Response: {response.text}")

try:
    process_id = "1234"
    time_series_data = fetch_time_series(process_id)
    
    df = convert_to_dataframe(time_series_data)
    
    reference_df = generate_single_sample()
    reference_wave = reference_df['normal_wave'].values
    set_reference_wave(reference_wave)
    
    sample_wave = df['value'].values  # Assuming 'value' column contains the wave data

    anomaly_detected, kl_divergence = detect_anomaly(sample_wave)
    
    if anomaly_detected:
        print(f"Anomaly detected! KL Divergence: {kl_divergence}")
        update_anomaly_status(process_id, True)
    else:
        print(f"No anomaly detected. KL Divergence: {kl_divergence}")
        update_anomaly_status(process_id, False)

except Exception as e:
    print(e)
