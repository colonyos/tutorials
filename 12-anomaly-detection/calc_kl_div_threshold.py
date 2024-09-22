import numpy as np
import pandas as pd
from scipy.stats import entropy
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Function to find the zero crossings of a signal
def find_zero_crossings(signal):
    zero_crossings = np.where(np.diff(np.sign(signal)))[0]
    return zero_crossings

# Function to trim the signal to start and end at zero crossings
def trim_to_zero_crossings(signal):
    zero_crossings = find_zero_crossings(signal)
    if len(zero_crossings) >= 2:
        return signal[zero_crossings[0]:zero_crossings[-1]]
    else:
        return signal

# Load the dataset
df = pd.read_csv('dataset.csv')

# Define the chunk size (1 second = 1000 samples)
sampling_rate = 1000
chunk_size = sampling_rate  # 1 second chunk size

# Prepare 1-second chunks of the normal_wave and trim to zero crossings
window_size = chunk_size
step_size = 1000  # 1-second overlap
normal_chunks = []
for i in range(0, len(df) - window_size, step_size):
    chunk = df['normal_wave'].iloc[i:i + window_size].values
    trimmed_chunk = trim_to_zero_crossings(chunk)
    normal_chunks.append(trimmed_chunk)

# Prepare 1-second chunks of the anomaly_wave and trim to zero crossings
anomaly_chunks = []
for i in range(0, len(df) - window_size, step_size):
    chunk = df['anomaly_wave'].iloc[i:i + window_size].values
    trimmed_chunk = trim_to_zero_crossings(chunk)
    anomaly_chunks.append(trimmed_chunk)

# Function to compute the probability distribution from a histogram
def compute_histogram(data, bins=50):
    hist, bin_edges = np.histogram(data, bins=bins, density=True)
    hist = hist + 1e-10  # Avoid division by zero
    return hist, bin_edges

# Function to compute KL divergence
def compute_kl_divergence(p, q):
    return entropy(p, q)

# Estimate the distribution of the normal wave (using the first chunk as reference)
normal_wave = normal_chunks[0]  # Taking the first chunk as an example
p_hist, p_bins = compute_histogram(normal_wave)

# Compute the KL divergence for each chunk of the anomaly wave
kl_divergences = []
for anomaly_wave in anomaly_chunks:
    q_hist, q_bins = compute_histogram(anomaly_wave)
    kl_div = compute_kl_divergence(p_hist, q_hist)
    kl_divergences.append(kl_div)

# Set a threshold for anomaly detection (e.g., mean + 2 standard deviations)
kl_threshold = np.mean(kl_divergences) + 0.1 * np.std(kl_divergences)
print(f"Anomaly detection threshold (KL Divergence): {kl_threshold}")

# Detect anomalies based on KL divergence
anomaly_predictions = np.array(kl_divergences) > kl_threshold

# Aggregate ground truth for each chunk (taking max of 'is_anomaly' in each chunk)
ground_truth_chunks = []
for i in range(0, len(df) - window_size, step_size):
    chunk_ground_truth = df['is_anomaly'].iloc[i:i + window_size].values
    ground_truth_chunks.append(np.max(chunk_ground_truth))  # Take max value in chunk (1 if any anomaly)

# Convert ground truth to numpy array for consistency
ground_truth_chunks = np.array(ground_truth_chunks)

# Calculate accuracy, precision, recall, and F1-score
accuracy = accuracy_score(ground_truth_chunks, anomaly_predictions)
precision = precision_score(ground_truth_chunks, anomaly_predictions)
recall = recall_score(ground_truth_chunks, anomaly_predictions)
f1 = f1_score(ground_truth_chunks, anomaly_predictions)

# Print the evaluation metrics
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1-Score: {f1:.4f}")

# Plot the KL divergence and the ground truth 'is_anomaly' labels
plt.figure(figsize=(12, 6))

# Plot KL divergence
plt.subplot(2, 1, 1)
plt.plot(kl_divergences, label='KL Divergence', color='b')
plt.axhline(y=kl_threshold, color='r', linestyle='--', label='Threshold')
plt.title('KL Divergence Over Chunks')
plt.xlabel('Chunk Index')
plt.ylabel('KL Divergence')
plt.legend()

# Plot the ground truth anomalies
plt.subplot(2, 1, 2)
plt.plot(ground_truth_chunks, label='True Anomalies', color='g')
plt.title('Ground Truth Anomalies (is_anomaly)')
plt.xlabel('Chunk Index')
plt.ylabel('Anomaly (0 or 1)')
plt.legend()

plt.tight_layout()
plt.show()

# Display the number of detected anomalies
print(f"Detected {np.sum(anomaly_predictions)} anomalies out of {len(kl_divergences)} chunks.")
