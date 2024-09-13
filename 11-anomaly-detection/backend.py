from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI()

# In-memory storage for time-series data and metadata associated with a process_id
database: Dict[str, Dict] = {}

class TimeSeriesData(BaseModel):
    time: str
    value: float

class TimeSeriesInput(BaseModel):
    process_id: str
    data: List[TimeSeriesData]
    anomaly: Optional[bool] = False


@app.put("/timeseries/{process_id}")
def create_or_update_timeseries(process_id: str, ts_input: TimeSeriesInput):
    try:
        database[process_id] = {
            "data": ts_input.data,  # Store the time series as-is
            "anomaly": ts_input.anomaly
        }
        return {"message": f"Time series data for process ID '{process_id}' stored or updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/timeseries/{process_id}", response_model=Dict)
def get_timeseries(process_id: str):
    try:
        if process_id not in database:
            raise HTTPException(status_code=404, detail=f"Time series data for process ID '{process_id}' not found.")
        
        record = database[process_id]
        
        return {
            "process_id": process_id,
            "data": record["data"],
            "anomaly": record["anomaly"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/timeseries/", response_model=Dict)
def list_timeseries(anomalies_only: bool = Query(False, description="Set to True to list only time series with anomalies")):
    try:
        if anomalies_only:
            filtered_timeseries = [{"process_id": process_id, "anomaly": record["anomaly"]} 
                                   for process_id, record in database.items() if record["anomaly"]]
        else:
            filtered_timeseries = [{"process_id": process_id, "anomaly": record["anomaly"]} 
                                   for process_id, record in database.items()]
        
        return {"timeseries": filtered_timeseries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/timeseries/{process_id}/anomaly", response_model=Dict)
def update_anomaly_status(process_id: str, anomaly: bool):
    try:
        if process_id not in database:
            raise HTTPException(status_code=404, detail=f"Time series data for process ID '{process_id}' not found.")
        
        database[process_id]["anomaly"] = anomaly
        
        return {"message": f"Anomaly status for process ID '{process_id}' updated to {anomaly}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/timeseries/{process_id}", response_model=Dict)
def delete_timeseries(process_id: str):
    try:
        if process_id not in database:
            raise HTTPException(status_code=404, detail=f"Time series data for process ID '{process_id}' not found.")
        
        del database[process_id]
        
        return {"message": f"Time series data for process ID '{process_id}' deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

