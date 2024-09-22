from pycolonies import Crypto
from pycolonies import colonies_client
import signal
import os
import requests
import numpy as np
from scipy.stats import entropy
import pandas as pd
import string
import random

class AnomalyDetectorExecutor:
    def __init__(self):
        colonies, colonyname, colony_prvkey, _, _ = colonies_client()
        self.colonies = colonies
        self.colonyname = colonyname
        self.colony_prvkey = colony_prvkey
    
        ## generate a 5 long unique id
        id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

        self.executorname = "anomaly-executor-" + id
        self.executortype = "anomaly-executor"

        reference_df = self.generate_single_sample()
        self.reference_wave = reference_df['normal_wave'].values

        crypto = Crypto()
        self.executor_prvkey = crypto.prvkey()
        self.executorid = crypto.id(self.executor_prvkey)

        self.register()
        
    def fetch_time_series(self, db, ts_id):
        url = f"{db}/timeseries/{ts_id}"
        response = requests.get(url)
    
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch time series. Status code: {response.status_code}")

    def update_anomaly_status(self, db, ts_id, anomaly_status):
        url = f"{db}/timeseries/{ts_id}/anomaly"

        params = {"anomaly": anomaly_status, "process_id": "5678"}
        response = requests.patch(url, params=params)

        if response.status_code == 200:
            print(f"Database updated successfully. Timeseries ID: {ts_id}, Anomaly: {anomaly_status}, Process ID: 5678")
        else:
            print(f"Failed to update the database. Status code: {response.status_code}")
            print(f"Response: {response.text}")

    def convert_to_dataframe(self, time_series_data):
        time_series = time_series_data['data']

        df = pd.DataFrame(time_series)

        return df

    def compute_histogram(self, data, bins=50):
        hist, bin_edges = np.histogram(data, bins=bins, density=True)
        hist = hist + 1e-10  # Avoid division by zero
        return hist, bin_edges

    def compute_kl_divergence(self, p, q):
        return entropy(p, q)

    def detect_anomaly(self, sample_wave, kl_threshold=0.010199148586751076):
        sample_hist, _ = self.compute_histogram(sample_wave)
        reference_hist, _ = self.compute_histogram(self.reference_wave)
        kl_div = self.compute_kl_divergence(reference_hist, sample_hist)
        anomaly_detected = kl_div > kl_threshold

        return anomaly_detected, kl_div
    
    def generate_single_sample(self, duration=1, sampling_rate=1000, frequency=50, amplitude=230,anomaly_probability=0.0001, 
                               anomaly_duration=100, anomaly_drop=0.2):
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

    def register(self):
        executor = {
            "executorname": self.executorname,
            "executorid": self.executorid,
            "colonyname": self.colonyname,
            "executortype": self.executortype
        }
        
        try:
            executor = self.colonies.add_executor(executor, self.colony_prvkey)
            self.colonies.approve_executor(self.colonyname, self.executorname, self.colony_prvkey)
            
            self.colonies.add_function(self.colonyname, 
                                       self.executorname, 
                                       "anomaly",  
                                       self.executor_prvkey)
        except Exception as err:
            print(err)
            os._exit(0)
        
        print("Executor", self.executorname, "registered")
        
    def start(self):
        while (True):
            try:
                process = self.colonies.assign(self.colonyname, 10, self.executor_prvkey)
                print("Process", process.processid, "is assigned to executor")
                if process.spec.funcname == "anomaly":
                    ts_ids = process.spec.args
                    db = process.spec.kwargs["db"]
                    print("DB:", db)
                    print("TS IDs:", ts_ids)
                    
                    for ts_id in ts_ids:
                        logMsg = f"Checking anomalies in time series with ID: {ts_ids}"
                        self.colonies.add_log(process.processid, logMsg, self.executor_prvkey)
                        logMsg = f"Fetching time series data with ID: {ts_id} from database {db}"
                        self.colonies.add_log(process.processid, logMsg, self.executor_prvkey)
                        time_series_data = self.fetch_time_series(db, ts_id)
                        
                        logMsg = f"Converting time series data to dataframe"
                        self.colonies.add_log(process.processid, logMsg, self.executor_prvkey)
                        df = self.convert_to_dataframe(time_series_data)

                        logMsg = f"Detecting anomalies in time series with ID: {ts_id}"
                        self.colonies.add_log(process.processid, logMsg, self.executor_prvkey)
                        sample_wave = df['value'].values
                        anomaly_detected, kl_divergence = self.detect_anomaly(sample_wave)
    
                        if anomaly_detected:
                            logMsg = f"Anomaly detected! KL Divergence: {kl_divergence}, time series ID: {ts_id}"
                            print(logMsg)
                            self.colonies.add_log(process.processid, logMsg, self.executor_prvkey)
                            self.update_anomaly_status(db, ts_id, True)
                        else:
                            logMsg = f"No anomaly detected. KL Divergence: {kl_divergence}, time series ID: {ts_id}"
                            print(logMsg)
                            self.colonies.add_log(process.processid, logMsg, self.executor_prvkey)
                            self.update_anomaly_status(db, ts_id, False)
                        
                    self.colonies.close(process.processid, [], self.executor_prvkey)
    
            except Exception as err:
                print(err)
                pass

    def unregister(self):
        self.colonies.remove_executor(self.colonyname, self.executorname, self.colony_prvkey)
        print("Executor", self.executorname, "unregistered")
        os._exit(0)

def sigint_handler(signum, frame):
    executor.unregister()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    executor = AnomalyDetectorExecutor()
    executor.start()
