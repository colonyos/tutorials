from pycolonies import Crypto
from pycolonies import colonies_client
import signal
import os
import uuid

class FaaSExecutor:
    def __init__(self):
        colonies, colonyname, colony_prvkey, _, _ = colonies_client()
        self.colonies = colonies
        self.colonyname = colonyname
        self.colony_prvkey = colony_prvkey
        self.executorname = "faas-executor" + uuid.uuid4().hex[:6]
        self.executortype = "faas-executor"

        crypto = Crypto()
        self.executor_prvkey = crypto.prvkey()
        self.executorid = crypto.id(self.executor_prvkey)

        self.register()
        
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
                                       "execute",  
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
                self.colonies.add_log(process.processid, "Executing function \n", self.executor_prvkey)

                if process.spec.funcname == "execute":
                    # parse function spec
                    function = process.spec.kwargs["function"] 
                    arg = process.spec.kwargs["arg"]

                    # fetch source code
                    source_code = self.colonies.download_data(self.colonyname, self.executor_prvkey, label="/faas", filename=function)
                    source_code_str = source_code.decode('utf-8')

                    # call the function
                    namespace = {}
                    exec(source_code_str, globals(), namespace)
                    f = namespace[function]
                    r = f(float(arg))

                    self.colonies.close(process.processid, [r], self.executor_prvkey)

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
    executor = FaaSExecutor()
    executor.start()
