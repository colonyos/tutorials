from pycolonies import Crypto
from pycolonies import colonies_client
import signal
import os
import random

class PythonExecutor:
    def __init__(self):
        colonies, colonyname, colony_prvkey, _, _ = colonies_client()
        self.colonies = colonies
        self.colonyname = colonyname
        self.colony_prvkey = colony_prvkey
        self.executorname = "wf-executor"
        self.executortype = "wf-executor"

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
                                       "gen",  
                                       self.executor_prvkey)
            
            self.colonies.add_function(self.colonyname, 
                                       self.executorname, 
                                       "sum",  
                                       self.executor_prvkey)
        except Exception as err:
            print(err)
            os._exit(0)
        
        print("Executor", self.executorname, "registered")
        
    def start(self):
        while (True):
            try:
                process = self.colonies.assign(self.colonyname, 10, self.executor_prvkey)

                if process.spec.funcname == "gen":
                    rand_num = [random.randint(1, 100) for i in range(5)]
                    self.colonies.close(process.processid, rand_num, self.executor_prvkey)
                elif process.spec.funcname == "sum":
                    total = sum(process.input)
                    self.colonies.close(process.processid, [total], self.executor_prvkey)
                else:
                    self.colonies.fail(process.processid, ["Unknown function"], self.executor_prvkey)
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
    executor = PythonExecutor()
    executor.start()
