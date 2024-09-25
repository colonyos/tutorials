from pycolonies import func_spec, Conditions, FuncSpec, Workflow
from pycolonies import colonies_client

colonies, colonyname, colony_prvkey, executor_name, prvkey = colonies_client()

gen_func_spec = FuncSpec(
    funcname="gen",
    nodename="gen_node",
    conditions = Conditions(
        colonyname=colonyname,
        executortype="wf-executor"
    )
)

sum_func_spec = FuncSpec(
    funcname="sum",
    nodename="sum_node",
    conditions = Conditions(
        colonyname=colonyname,
        executortype="wf-executor",
        dependencies=["gen_node"]
    )
)

wf = Workflow(colonyname=colonyname) 
wf.functionspecs.append(gen_func_spec)
wf.functionspecs.append(sum_func_spec)

processgraph = colonies.submit_workflow(wf, prvkey)
print("Workflow", processgraph.processgraphid, "submitted")

process = colonies.find_process("sum_node", processgraph.processids, prvkey)
process = colonies.wait(process, 100, prvkey)
print(process.output[0])
