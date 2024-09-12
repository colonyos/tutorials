from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

# Initialize FastAPI app
app = FastAPI()

# In-memory storage for time series data and metadata (associated with a process_id)
database: Dict[str, Dict] = {}

# Define the request model for inserting/updating time series data
class TimeSeriesInput(BaseModel):
    process_id: str  # Unique identifier for the process
    data: List[Dict]  # List of dictionaries, each containing 'time' and 'value'
    anomaly: Optional[bool] = False  # Metadata: whether it contains an anomaly

# Endpoint to store time series data along with metadata (based on process_id)
@app.post("/store/")
def store(ts_input: TimeSeriesInput):
    try:
        # Store the time series data and metadata (process_id, anomaly status) in the database
        database[ts_input.process_id] = {
            "data": ts_input.data,  # Store the time series as-is (time-value pairs)
            "anomaly": ts_input.anomaly
        }
        return {"message": f"Time series data for process ID '{ts_input.process_id}' stored successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to retrieve time series data and its metadata by process_id
@app.get("/get_timeseries/{process_id}")
def get_timeseries(process_id: str):
    try:
        # Check if the time series data exists in the database
        if process_id not in database:
            raise HTTPException(status_code=404, detail=f"Time series data for process ID '{process_id}' not found.")
        
        # Retrieve the time series data and metadata
        record = database[process_id]
        
        return {
            "process_id": process_id,
            "data": record["data"],
            "anomaly": record["anomaly"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to list all stored time series data and their metadata
@app.get("/list_timeseries/")
def list_timeseries():
    try:
        return {"timeseries": [{"process_id": process_id, "anomaly": record["anomaly"]} for process_id, record in database.items()]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to update the metadata (anomaly status) of a stored time series by process_id
@app.put("/update_timeseries/{process_id}")
def update_timeseries(process_id: str, anomaly: bool):
    try:
        # Check if the time series data exists in the database
        if process_id not in database:
            raise HTTPException(status_code=404, detail=f"Time series data for process ID '{process_id}' not found.")
        
        # Update the anomaly status
        database[process_id]["anomaly"] = anomaly
        
        return {"message": f"Time series data for process ID '{process_id}' updated successfully with anomaly status {anomaly}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to delete a time series by process_id
@app.delete("/delete_timeseries/{process_id}")
def delete_timeseries(process_id: str):
    try:
        # Check if the time series data exists in the database
        if process_id not in database:
            raise HTTPException(status_code=404, detail=f"Time series data for process ID '{process_id}' not found.")
        
        # Delete the time series data from memory
        del database[process_id]
        
        return {"message": f"Time series data for process ID '{process_id}' deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the application using Uvicorn (FastAPI's server)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

