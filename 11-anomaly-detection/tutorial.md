# Getting started
In this tutorial, we are going to develop a simple anomaly detection service that identifies irregularities or unexpected patterns in time-series data. Specifically, we will focus on detecting anomalies in a continuous signal, such as voltage measurements in a power grid, or sensor data from IoT devices. 

We'll begin by creating a time-series dataset that simulates the behavior of a 50Hz AC power signal (e.g., a typical 230V power supply). The dataset will consist of a continuous sinusoidal wave, representing the normal operation of the system, and occasional anomalies injected randomly to simulate sudden voltage drops.

We’ll start by writing a Python script to generate this synthetic dataset. The script will create a normal sinusoidal wave and inject anomalies based on a given probability and duration. 
Below is the explanation of the key parameters:

* **duration**: The total time in seconds for the dataset.
* **sampling_rate**: The number of samples collected per second (for a high-fidelity signal, 1000 samples per second is typical).
* **frequency**: The frequency of the sinusoidal wave, which for a standard power signal is typically 50 Hz.
* **amplitude**: The peak amplitude of the signal in volts, which corresponds to the RMS value of the power supply (e.g., 230V for a typical power grid).
* **anomaly_probability**: The probability of injecting an anomaly at any given point. A lower probability will result in fewer anomalies.
* **anomaly_duration**: The duration of the anomaly, in terms of the number of samples. This controls how long each anomaly lasts.
* **anomaly_drop**: The percentage drop in voltage during the anomaly (e.g., a value of 0.2 will simulate an 80% voltage drop).

The resulting dataset will contain three main columns:

* **time**: The time index for each sample.
* **normal_wave**: The sinusoidal wave representing normal operation.
* **anomaly_wave**: The wave with injected anomalies.
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

Certainly! Here's the expanded text with the equation in Markdown format:

## Detecting anomalies
We are going to use a very simple method to detect anomalies based on **Kullback-Leibler (KL) divergence**, a fundamental concept from information theory. KL divergence measures how one probability distribution differs from a reference distribution, making it a powerful tool for anomaly detection in time-series data.

In our case, we will treat the normal signal as our reference distribution and the potentially anomalous signal as the second distribution. By comparing these two distributions, we can quantify how much the abnormal signal deviates from what we expect under normal conditions.

### KL Divergence Formula

The KL divergence between two probability distributions \( P \) (the reference distribution) and \( Q \) (the observed distribution) is calculated as follows:

\[
D_{\text{KL}}(P \parallel Q) = \sum_i P(i) \log \frac{P(i)}{Q(i)}
\]

Where:
- \( P(i) \) is the probability of the signal in the normal distribution at bin \( i \),
- \( Q(i) \) is the probability of the signal in the abnormal distribution at bin \( i \),
- \( \log \frac{P(i)}{Q(i)} \) measures the divergence between the two distributions for each bin.

KL divergence essentially tells us how much information is lost when one distribution (the normal signal) is used to approximate another distribution (the abnormal signal). A higher KL divergence value means that the abnormal signal is significantly different from the normal one, and this difference could be indicative of an anomaly.

### How KL Divergence Works for Anomaly Detection

We will calculate the KL divergence between the normal signal and the abnormal signal over short time windows (or "chunks"). For each chunk, if the KL divergence exceeds a pre-defined threshold, we will flag that section of the signal as anomalous. The threshold will be set based on empirical testing or domain knowledge about what constitutes a significant deviation.

### Steps to Implement KL Divergence Anomaly Detection:

1. **Generate the Normal and Abnormal Signals**:
   First, we generate the synthetic dataset as described earlier, consisting of normal and abnormal waves, along with an anomaly label.

2. **Calculate Histograms**:
   For both the normal and abnormal signals, we calculate their probability distributions by creating histograms. These histograms represent the distribution of signal values over a period of time.

3. **Compute KL Divergence**:
   For each chunk of the time series, we compute the KL divergence between the normal wave's histogram and the abnormal wave's histogram. This will give us a measure of how much the two signals differ in that particular window.

4. **Compare to Threshold**:
   If the KL divergence value for any given chunk exceeds the threshold, we flag that chunk as containing an anomaly. If the KL divergence remains below the threshold, the chunk is considered normal.

### Advantages of Using KL Divergence:

- **Simplicity**: KL divergence is straightforward to compute and interpret. It requires only basic statistical knowledge, making it a lightweight and effective method for anomaly detection in many cases.
- **Flexibility**: The method works well across different domains, from detecting voltage drops in power systems to monitoring sensor data in industrial settings.
- **Threshold-based**: The approach allows for tuning the sensitivity of the anomaly detection system by adjusting the KL divergence threshold. A lower threshold will catch more anomalies but might also lead to more false positives, while a higher threshold will be stricter, reducing false positives but potentially missing subtle anomalies.

This approach provides a simple yet powerful way to detect anomalies in time-series data without needing complex machine learning models or large datasets. As we proceed through the tutorial, we will implement and test this method, starting with calculating the KL divergence and then fine-tuning our threshold to achieve effective anomaly detection.

--- 

You can now copy this text into your Markdown file, and it should render properly with the equation and explanation.




```bash
TODO
```
