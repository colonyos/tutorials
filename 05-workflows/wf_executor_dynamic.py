from pycolonies import Crypto, FuncSpec, Conditions, colonies_client
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
                    insert = True 
                    for i in range (2):
                        processid = process.processid
                        processgraphid = process.processgraphid

                        processgraph = self.colonies.get_processgraph(processgraphid, self.executor_prvkey)
                        sum_process = self.colonies.find_process("sum_node", processgraph.processids, self.executor_prvkey)
                    
                        funcspec = FuncSpec(
                            funcname="square",
                            nodename="square_node" + str(i),
                            args=[2],
                            conditions = Conditions(
                                colonyname=self.colonyname,
                                executortype="wf-executor",
                                dependencies=["gen_node"]
                            )
                        )

                        self.colonies.add_child(processgraphid, processid, sum_process.processid, funcspec, "square_node", insert, self.executor_prvkey) 
                        insert = False
                        
                    self.colonies.close(process.processid, [1, 1], self.executor_prvkey)
                elif process.spec.funcname == "square":
                    s = int(process.spec.args[0]) ** 2
                    self.colonies.close(process.processid, [s], self.executor_prvkey)
                elif process.spec.funcname == "sum":
                    total = sum(process.input)
                    self.colonies.close(process.processid, [total], self.executor_prvkey)
                else:
                    self.colonies.fail(process.processid, ["Unknown function"], self.executor_prvkey)
            except Exception as err:
                print("ERROR")
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
