from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI()

database: Dict[str, Dict] = {}

class TimeSeriesData(BaseModel):
    time: str
    value: float

class TimeSeriesInput(BaseModel):
    ts_id: str
    process_id: str
    data: List[TimeSeriesData]
    anomaly: Optional[bool] = False


@app.put("/timeseries/{ts_id}")
def create_or_update_timeseries(ts_id: str, ts_input: TimeSeriesInput):
    try:
        database[ts_id] = {
            "data": ts_input.data,  # Store the time series as-is
            "anomaly": ts_input.anomaly
        }
        return {"message": f"Time series data for time series ID '{ts_id}' stored or updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/timeseries/{ts_id}", response_model=Dict)
def get_timeseries(ts_id: str):
    try:
        if ts_id not in database:
            raise HTTPException(status_code=404, detail=f"Time series data for time series ID '{ts_id}' not found.")
        
        record = database[ts_id]
        
        return {
            "ts_id": ts_id,
            "data": record["data"],
            "anomaly": record["anomaly"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/timeseries/", response_model=Dict)
def list_timeseries(anomalies: bool = Query(False, description="Set to True to list only time series with anomalies")):
    try:
        if anomalies:
            filtered_timeseries = [{"ts_id": ts_id, "process_id": record.get("process_id", None), "anomaly": record["anomaly"]}
                                   for ts_id, record in database.items() if record["anomaly"]]
        else:
            filtered_timeseries = [{"ts_id": ts_id, "process_id": record.get("process_id", None), "anomaly": record["anomaly"]}
                                   for ts_id, record in database.items() if not record["anomaly"]]

        return {"timeseries": filtered_timeseries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/timeseries/{ts_id}/anomaly", response_model=Dict)
def update_anomaly_status(ts_id: str, anomaly: bool, process_id: str):
    try:
        if ts_id not in database:
            raise HTTPException(status_code=404, detail=f"Time series data for time series ID '{ts_id}' not found.")

        database[ts_id]["anomaly"] = anomaly
        database[ts_id]["process_id"] = process_id

        return {"message": f"Anomaly status for time series ID '{ts_id}' updated to {anomaly} and process_id set to {process_id}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/timeseries/{ts_id}", response_model=Dict)
def delete_timeseries(ts_id: str):
    try:
        if ts_id not in database:
            raise HTTPException(status_code=404, detail=f"Time series data for time series ID '{ts_id}' not found.")
        
        del database[ts_id]
        
        return {"message": f"Time series data for time series ID '{ts_id}' deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

