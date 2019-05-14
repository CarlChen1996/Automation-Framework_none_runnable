from Framework_Kernel import configuration_engine
from Framework_Kernel import assemble_engine
from Framework_Kernel import execution_engine

task_list = []
build_list = []
deploy_list = []
conf = configuration_engine.ConfigurationEngine()
conf.start(build_list, deploy_list)
assemble = assemble_engine.AssembleEngine()
task_list = assemble.start(build_list)
exe = execution_engine.ExecutionEngine()
exe.start(deploy_list, task_list)
