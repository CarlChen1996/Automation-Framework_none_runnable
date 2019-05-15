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

log.log('start configuration engine')
conf = configuration_engine.ConfigurationEngine()
conf.start(build_list, deploy_list)
log.log( "configurator  finished")
print('====================================')
log.log('start assemble engine')
assemble = assemble_engine.AssembleEngine()
assemble.tasklist = task_list
assemble.start(build_list)
log.log('assemble finished')
print('======================================')
log.log('start execution engine')
exe = execution_engine.ExecutionEngine()
exe.start(deploy_list, task_list)
log.log('execution finished')
