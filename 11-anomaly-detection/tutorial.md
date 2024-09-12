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
| ----- | ---------- -| ------------- | ---------- | 
| 0.001	| 325  	      | 325	          | 0          |
| 0.002 | 324	      | 324	          | 0          |
| 0.003	| 322	      | 58	          | 1          |
| 0.004	| 319	      | 55	          | 1          |
| 0.005	| 315	      | 315	          | 0          |

In this table, the Abnormal Wave column shows the effect of an anomaly at time 0.003s and 0.004s, where the voltage dropped significantly. The corresponding entries in the Anomaly Label column are set to 1 to indicate the presence of an anomaly.

Below is a picture showing several anomalies where the power has dropped.

<img src="anomalies.png">




```bash
TODO
```
