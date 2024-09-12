import numpy as np
import pandas as pd
from scipy.stats import entropy

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

sample_df = generate_single_sample(duration=1, sampling_rate=1000, frequency=50, amplitude=230, 
                                   anomaly_probability=0.001, anomaly_duration=100, anomaly_drop=0.2)

reference_wave = sample_df['normal_wave'].values
set_reference_wave(reference_wave)

sample_wave = sample_df['anomaly_wave'].values
anomaly_detected, kl_divergence = detect_anomaly(sample_wave)

print(f"Anomaly detected: {anomaly_detected}")
print(f"KL Divergence: {kl_divergence}")
