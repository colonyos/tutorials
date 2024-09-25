import inspect
from pycolonies import colonies_client

def convert(celsius):
    return (celsius * 9/5) + 32

colonies, colonyname, colony_prvkey, executor_name, prvkey = colonies_client()
source_code = inspect.getsource(convert)
colonies.upload_data(colonyname, prvkey, filename="convert", data=source_code.encode('utf-8'), label="/faas")
