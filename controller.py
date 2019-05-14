from Framework_Kernel import configuration_engine
from Framework_Kernel import assemble_engine
from Framework_Kernel import execution_engine
from Framework_Kernel import log

log = log.Log(name='framework')
log.log('Begin to start controller')
print('====================================')
task_list = []
build_list = []
deploy_list = []
log.log('Begin to init configuration engine')
conf = configuration_engine.ConfigurationEngine()
conf.start(build_list, deploy_list)
print('====================================')
assemble = assemble_engine.AssembleEngine()
task_list = assemble.start(build_list, task_list)
print('======================================')
exe = execution_engine.ExecutionEngine()
exe.start(deploy_list, task_list)
