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
    # print('')
    if len(input) > 0:
        return input
    else:
        return None


def operation():
    global assemble, exe, pipe, deploy_list, build_list, conf
    flags = [False, False]
    config_flag = False
    log.log("please select operation")
    log.log("00:start config")
    log.log("01:start assembly")
    log.log("02:start execute")
    log.log("03:stop assembly")
    log.log("04:stop execute")
    log.log("05:restart assembly")
    log.log("06:restart execute")
    log.log("07:restart all")
    log.log("08:stop all")
    log.log("09:daemon")
    while True:
        ans = readinput(10)
        if ans:
            if ans == "00":
                log.log("start config")
                conf.start(build_list, deploy_list)
                config_flag = True
                log.log("config pid is {}".format(conf.status.pid))
            if ans == "07":
                log.log("restart all")
                if flags[0]:
                    assemble.stop()
                if flags[1]:
                    exe.stop()
                conf.start(build_list, deploy_list)
                config_flag = True
                flags[0] = True
                flags[1] = True
                assemble.start()
                exe.start()
                log.log("config pid is {}".format(conf.status.pid))
                log.log("assemble pid is {}".format(assemble.status.pid))
                log.log("execute pid is {}".format(exe.status.pid))
            elif config_flag:
                if ans == "01":
                    log.log("start assembly")
                    assemble.start()
                    flags[0] = True
                    log.log("assemble pid is {}".format(assemble.status.pid))
                elif ans == "02":
                    log.log("start execute")
                    exe.start()
                    flags[1] = True
                    log.log("execute pid is {}".format(exe.status.pid))
                elif ans == "03":
                    if flags[0]:
                        log.log("stop assembly")
                        assemble.stop()
                    else:
                        log.log("assemble process not run and can not stop")
                elif ans == "04":
                    if flags[1]:
                        log.log("stop execute")
                        exe.stop()
                    else:
                        log.log("execute process not run and can not stop")

                elif ans == "05":
                    if flags[0]:
                        assemble.stop()
                    log.log("restart assembly")
                    assemble.start()
                    flags[0] = True
                    log.log("assemble pid is {}".format(assemble.status.pid))
                elif ans == "06":
                    if flags[1]:
                        exe.stop()
                    log.log("restart execute")
                    exe.start()
                    flags[1] = True
                    log.log("execute pid is {}".format(exe.status.pid))
                elif ans == "08":
                    if flags[1]:
                        exe.stop()
                    if flags[0]:
                        assemble.stop()
                    log.log("stop all")
                elif ans == "09":
                    if flags[0] & flags[1]:
                        log.log("start daemon")
                        while True:
                            log.log(
                                "[daemon]assembly engine pid {} is {}".format(
                                    assemble.status.pid,
                                    str(assemble.status.is_alive())))
                            if not assemble.status.is_alive():
                                assemble.start()
                                if assemble.status.is_alive():
                                    log.log("restart assembly success")
                                else:
                                    log.log("restart assembly fail")

                            log.log("[daemon]execution engine pid {}  is {}".
                                    format(exe.status.pid,
                                           str(exe.status.is_alive())))
                            if not exe.status.is_alive():
                                exe.start()
                                if exe.status.is_alive():
                                    log.log("restart execution success")
                                else:
                                    log.log("restart execution fail")
                            log.log("input break to exit daemon")
                            s = readinput(5)
                            if s == "break":
                                log.log("exit daemon")
                                log.log("please select operation")
                                log.log("00:start config")
                                log.log("01:start assembly")
                                log.log("02:start execute")
                                log.log("03:stop assembly")
                                log.log("04:stop execute")
                                log.log("05:restart assembly")
                                log.log("06:restart execute")
                                log.log("07:restart all")
                                log.log("08:stop all")
                                log.log("09:daemon")
                                break
                    else:
                        log.log(
                            "[daemon]assembly and execution must be alive before daemon"
                        )

            else:
                log.log("config has not been run")


if __name__ == '__main__':
    pipe = Pipe()
    log = log.Log(name='framework')
    log.log('Begin to start controller')
    print('=================Begin to start controller===================')
    build_list = []
    deploy_list = []
    conf = configuration_engine.ConfigurationEngine()
    assemble = assemble_engine.AssembleEngine(pipe[0], build_list)
    exe = execution_engine.ExecutionEngine(deploy_list, pipe[1])
    log.log(
        "++++++++++++++++++++++++ Select mode+++++++++++++++++++++++++++++++++"
    )
    log.log("+++++++++++++++++++++++ 01:manual +++++++++++++++++++++++")
    log.log("+++++++++++++++++++++++ 02:auto,default +++++++++++++++++++++++")
    choice = readinput(100)

    if choice == "01":
        watch_thread = threading.Thread(target=operation)
        watch_thread.start()
    elif choice == "02":
        log.log('start configuration engine')
        conf.start(build_list, deploy_list)
        log.log("configurator  finished")
        print('==============start assemble engine======================')
        log.log('start assemble engine')
        assemble.start()
        log.log('assemble finished')
        print('=================start execution engine=====================')
        log.log('start execution engine')
        exe.start()
        log.log('execution finished')

        while True:
            time.sleep(5)
            log.log("assembly engine pid {} current status is {}".format(
                assemble.status.pid, str(assemble.status.is_alive())))
            if not assemble.status.is_alive():
                assemble.start()
                if assemble.status.is_alive():
                    log.log("restart assembly success")
                else:
                    log.log("restart assembly fail")

            log.log("execution engine pid {} current status is {}".format(
                exe.status.pid, str(exe.status.is_alive())))
            if not exe.status.is_alive():
                exe.start()
                if exe.status.is_alive():
                    log.log("restart execution success")
                else:
                    log.log("restart execution fail")
    else:
        log.log("nothing select ,exit")
