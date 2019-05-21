from multiprocessing import Pipe
from Framework_Kernel import configuration_engine
from Framework_Kernel import assemble_engine
from Framework_Kernel import execution_engine
from Framework_Kernel import log
import time
import threading
import msvcrt


def readinput(timeout):
    start_time = time.time()
    input = ''
    while True:
        if msvcrt.kbhit():
            byte_arr = msvcrt.getche()
            if ord(byte_arr) == 13:  # enter_key
                break
            elif ord(byte_arr) >= 32:  # space_char
                input += "".join(map(chr, byte_arr))
        if len(input) == 0 and (time.time() - start_time) > timeout:
            # print("timing out, nothing input.")
            break
    print('')
    if len(input) > 0:
        return input
    else:
        return None


def operation():
    global status_flag, assemble, exe, pipe, deploy_list, build_list, lock,conf

    while True:
        log.log("current assemble status is {}".format(assemble.status.is_alive()))
        log.log("current exe status is {}".format(exe.status.is_alive()))
        log.log("assemble auto restart status is {}".format(status_flag[0]))
        log.log("exe auto restart status is {}".format(status_flag[1]))
        log.log("please select operation")
        log.log("01:stop assembly")
        log.log("02:stop execute")
        log.log("03:start assembly")
        log.log("04:start execute")
        log.log("05:restart assembly")
        log.log("06:restart execute")
        ans = readinput(10)
        if ans:
            if ans == "01":
                log.log("stop assembly")
                if assemble.status.is_alive():
                    assemble.status.terminate()
                else:
                    log.log("assembly already stop ,no need again")
                status_flag[0] = False
            elif ans == "02":
                log.log("stop execute")
                if exe.status.is_alive():
                    exe.status.terminate()
                else:
                    log.log("exe already stop ,no need again")
                status_flag[1] = False
            elif ans == "03":
                if not assemble.status.is_alive():
                    log.log("start assembly")
                    assemble = assemble_engine.AssembleEngine(pipe[0], build_list)
                    assemble.start()
                else:
                    log.log("assembly  already running ,no need again")
                status_flag[0] = True
            elif ans == "04":
                if not exe.status.is_alive():
                    log.log("start execute")
                    exe = execution_engine.ExecutionEngine(deploy_list, pipe[1])
                    exe.start()
                else:
                    log.log("execute already running ,no need again")
                status_flag[1] = True
            elif ans == "05":
                log.log("restart assembly")
                assemble.status.terminate()
                assemble = assemble_engine.AssembleEngine(pipe[0], build_list)
                assemble.start()
                status_flag[0] = True
            elif ans == "06":
                log.log("restart execute")
                exe.status.terminate()
                exe = execution_engine.ExecutionEngine(deploy_list, pipe[1])
                exe.start()
                status_flag[1] = True
            elif ans == "07":
                log.log("restart config")
                assemble.status.terminate()
                exe.status.terminate()
                conf = configuration_engine.ConfigurationEngine()
                conf.start(build_list, deploy_list)
                assemble = assemble_engine.AssembleEngine(pipe[0], build_list)
                assemble.start()
                exe = execution_engine.ExecutionEngine(deploy_list, pipe[1])
                exe.start()
            else:
                log.log("unknow input,please retry")


if __name__ == '__main__':
    pipe = Pipe()
    log = log.Log(name='framework')
    log.log('Begin to start controller')
    print('=================Begin to start controller===================')
    build_list = []
    deploy_list = []
    log.log('start configuration engine')
    conf = configuration_engine.ConfigurationEngine()
    conf.start(build_list, deploy_list)
    log.log("configurator  finished")
    print('==============start assemble engine======================')
    log.log('start assemble engine')
    assemble = assemble_engine.AssembleEngine(pipe[0], build_list)
    assemble.start()
    log.log('assemble finished')
    print('=================start execution engine=====================')
    log.log('start execution engine')
    exe = execution_engine.ExecutionEngine(deploy_list, pipe[1])
    exe.start()
    log.log('execution finished')

    time.sleep(5)
    """restart flag for asssembly and execution ,default is True"""
    status_flag = [True, True]

    """lock for operate engine"""
    lock = True
    watch_thread = threading.Thread(target=operation, args=())
    watch_thread.start()

    while True:
        time.sleep(5)
        if status_flag[0]:
            log.log("assembly engine pid {} current status is {}".format(assemble.status.pid,
                                                                         str(assemble.status.is_alive())))
            if not assemble.status.is_alive():
                assemble = assemble_engine.AssembleEngine(pipe[0], build_list)
                assemble.start()
                if assemble.status.is_alive():
                    log.log("restart assembly success")
                else:
                    log.log("restart assembly fail")

        if status_flag[1]:
            log.log("execution engine pid {} current status is {}".format(exe.status.pid,
                                                                          str(exe.status.is_alive())))
            if not exe.status.is_alive():
                exe = execution_engine.ExecutionEngine(deploy_list, pipe[1])
                exe.start()
                if exe.status.is_alive():
                    log.log("restart execution success")
                else:
                    log.log("restart execution fail")
