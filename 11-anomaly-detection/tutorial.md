# Getting started
In this tutorial, we are going to develop a simple anomaly detection service that identifies irregularities in time-series data. Specifically, we will focus on detecting anomalies in a continuous signal, in particilar we are going to detect anomalies in voltage measurements.

To begin, we need to create a time-series dataset that simulates the behavior of a 50Hz AC power signal (230V). The dataset will consist of a continuous sinusoidal wave, representing the normal operation of the system, and occasional anomalies injected randomly to simulate sudden voltage drops.

We’ll start by writing a Python script to generate this synthetic dataset. The script will create a normal sinusoidal wave and inject anomalies based on a given probability and duration. 

Below is the explanation of the key parameters:

* **duration**: The total time in seconds for the dataset.
* **sampling_rate**: The number of samples collected per second.
* **frequency**: The frequency of the sinusoidal wave, which for a standard power signal is typically 50 Hz.
* **amplitude**: The peak amplitude of the signal in volts, which corresponds to the RMS value of the power supply (e.g., 230V).
* **anomaly_probability**: The probability of injecting an anomaly at any given point. A lower probability will result in fewer anomalies.
* **anomaly_duration**: The duration of the anomaly, in terms of the number of samples. This controls how long each anomaly lasts.
* **anomaly_drop**: The percentage drop in voltage during the anomaly (e.g., a value of 0.2 will simulate an 80% voltage drop).

The resulting dataset will contain three main columns:

* **time**: The time index for each sample.
* **normal_wave**: The sinusoidal wave timeseries representing normal operation.
* **anomaly_wave**: The wave timeseries with injected anomalies.
* **is_anomaly**: A label indicating if the sample contains an anomaly (1) or not (0).

Below is an example of the dataset:

| time  | normal_wave | abnormal_wave | is_anomaly |
|-------|-------------|---------------|------------|
| 0.001 | 325         | 325           | 0          |
| 0.002 | 324         | 324           | 0          |
| 0.003 | 322         | 258           | 1          |
| 0.004 | 319         | 255           | 1          |
| 0.005 | 315         | 315           | 0          |

In this table, the abnormal wave column shows the effect of an anomaly at time 0.003s and 0.004s, where the voltage dropped significantly. The corresponding entries in the anomaly label column are set to 1 to indicate the presence of an anomaly. Below is a picture showing 2 anomalies where the power has dropped.
<img src="anomalies.png">

To generate the dataset, run:
```bash
python gen_dataset.py
```

The script will create a file, called *dataset.csv*.

## Detecting anomalies
We are going to use a very simple method to detect anomalies based on **Kullback-Leibler (KL) divergence**. KL divergence measures how one probability distribution differs from a reference distribution, thus making useful to detect anomalies in time-series data.

In our case, we will treat the normal signal as our reference distribution and the potentially anomalous signal as the second distribution. By comparing these two distributions, we can 
calculate how much the abnormal signal deviates from what we expect under normal conditions.

## KL divergence
The KL divergence between two probability distributions *P* (the reference distribution) and *Q* (the observed distribution) is calculated as follows:

<img src="kl_div.png" width="300">

Where:
- *P(i)* is the probability of the signal in the normal distribution at bin *i*,
- *Q(i)* is the probability of the signal in the abnormal distribution at bin  *i*,
- *log P(i)/Q(i)* measures the divergence between the two distributions for each bin.

KL divergence essentially tells us how much information is lost when one distribution (the normal signal) is used to approximate another distribution (the abnormal signal). A higher KL divergence value means that the abnormal signal is significantly different from the normal one, and this difference could be indicative of an anomaly. By setting a threshold, we can define a boundary that distinguishes normal behavior from anomalous behavior. If the KL divergence value exceeds this threshold, it indicates that the difference between the normal and abnormal signals is significant enough to be considered an anomaly. 

Run the Python script below to calculate a suitable threshold value based on the training dataset.

```bash
python3 kl_div.py
```

<img src="kl_div_res.png">

```bash
Anomaly detection threshold (KL Divergence): 0.010199148586751076
Accuracy: 1.0000
Precision: 1.0000
Recall: 1.0000
F1-Score: 1.0000
```

F1-Score of 1.0000 indicates perfect precision and recall, meaning the model did not make any classification errors. Also, 0.010199148586751076 seems to be a good threshold.
The code below generates a sample and then tests if it contains an anomaly. 


```python
import numpy as np
import pandas as pd
from scipy.stats import entropy

reference_wave_global = None

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
```

The next step is to split the code into several components: one where the client generates a sample, and another where a job is created and sent to an executor that performs anomaly detection.
Let's create a simple 
