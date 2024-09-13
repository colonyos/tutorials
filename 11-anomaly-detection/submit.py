import numpy as np
import pandas as pd
import requests
import os

from pycolonies import func_spec
from pycolonies import colonies_client

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

def submit_job(is_id, db):
    colonies, colonyname, _, _, prvkey = colonies_client()

    f = func_spec(func="anomaly", 
                  args=[is_id, ts_id],
                  kwargs={
                    "db": db,
                  },
                  colonyname=colonyname, 
                  executortype="anomaly-executor")

    process = colonies.submit_func_spec(f, prvkey)
    print("Process", process.processid, "submitted")

if __name__ == '__main__':
    print("-> Generating sample data")
    sample_df = generate_single_sample(duration=1, sampling_rate=1000, frequency=50, amplitude=230,
                                     anomaly_probability=0.001, anomaly_duration=100, anomaly_drop=0.2)
    time_series_data = [{"time": str(row['time']), "value": row['anomaly_wave']} for _, row in sample_df.iterrows()]

    ts_id = random_data = os.urandom(32).hex()
    print("-> Adding time series with ID:", ts_id, "to the database")

    db = "http://127.0.0.1:8000"
    url = db + "/timeseries/" + ts_id

    payload = {
      "ts_id": ts_id,
      "process_id": "",  # A unique identifier for the time series
      "data": time_series_data,
      "anomaly": False  # Set as False since we are not detecting anomalies here
    }

    response = requests.put(url, json=payload)

    if response.status_code == 200:
        print("Sample waveform stored successfully.")
    else:
        print(f"Failed to store the waveform. Status code: {response.status_code}")
        print(f"Response: {response.text}")


    print("-> Submitting ColonyOS function spec")
    submit_job(ts_id, db)
