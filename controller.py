from multiprocessing import Pipe
from multiprocessing import Process
from multiprocessing import Pipe
import threading
from time import ctime
import time
import os
from Framework_Kernel import configuration_engine
from Framework_Kernel import assemble_engine
from Framework_Kernel import execution_engine
from Framework_Kernel import log


if __name__ == '__main__':
    pipe = Pipe()
    log = log.Log(name='framework')
    log.log('Begin to start controller')
    print('====================================')

    build_list = []
    deploy_list = []

    log.log('start configuration engine')
    conf = configuration_engine.ConfigurationEngine()
    conf.start(build_list, deploy_list)
    log.log("configurator  finished")
    print('====================================')
    log.log('start assemble engine')
    assemble = assemble_engine.AssembleEngine(pipe[0], build_list)
    assemble.new_process()
    log.log('assemble finished')
    print('======================================')
    log.log('start execution engine')
    exe = execution_engine.ExecutionEngine(deploy_list, pipe[1])
    exe.start()
    log.log('execution finished')
    # while True:
    #     time.sleep(3)
    #     log.log("configuration engine current status is {}".format(str(conf.status.is_alive())))
    #     if not conf.status.is_alive():
    #         conf.start(build_list, deploy_list)
    #         print("restart config success")
    #     log.log("configuration engine current status is {}".format(str(conf.status.is_alive())))
    #     if not conf.status.is_alive():
    #         conf.start(build_list, deploy_list)
    #         print("restart config success")
    #     log.log("configuration engine current status is {}".format(str(conf.status.is_alive())))
    #     if not conf.status.is_alive():
    #         conf.start(build_list, deploy_list)
    #         print("restart config success")