from multiprocessing import Pipe
from Framework_Kernel import configuration_engine
from Framework_Kernel import assemble_engine
from Framework_Kernel import execution_engine
from Framework_Kernel import log
from Common_Library.functions import get_keyboard_input
import threading
import time


def run_with_manual_mode():
    is_framework_configured = False
    log.log("This is the manual operation mode, framework must be configured before continue")
    log.log(
        "++++++++++++++++++++++++++ manual mode first selection+++++++++++++++++++++++++++++++"
    )
    log.log("+++++++++++++++++++++++ 01:start config +++++++++++++++++++++++")
    log.log("+++++++++++++++++++++++ 99:exit +++++++++++++++++++++++++")
    manual_mode_first_selection = get_keyboard_input(60)
    log.log(run_mode)
    while True:
        if manual_mode_first_selection == "01":  # start config engine
            log.log("start config")
            instance_config_engine.start(build_server_list, deploy_list)
            log.log("config pid is {}".format(instance_config_engine.status.pid))
            is_framework_configured = True
            break
        elif manual_mode_first_selection == "99":
            log.log(
                "User select to stop or no selection within a certain time, program exit"
            )
            break
        else:
            log.log("Unknow run mode, please select the valid run mode from the list")
            manual_mode_first_selection = get_keyboard_input(60)

    while is_framework_configured:
        log.log("Framework has been configured, please continue with the operation")
        log.log(
            "++++++++++++++++++++++++++ manual mode second selection+++++++++++++++++++++++++++++++"
        )
        log.log("+++++++++++++++++++++++ 01:start assembly +++++++++++++++++++++++")
        log.log("+++++++++++++++++++++++ 02:start execution +++++++++++++++++++++++")
        log.log("+++++++++++++++++++++++ 03:stop assembly +++++++++++++++++++++++")
        log.log("+++++++++++++++++++++++ 04:stop execution +++++++++++++++++++++++")
        log.log("+++++++++++++++++++++++ 99:exit - this will stop all engines  +++++++++++++++++++++++")
        manual_mode_second_selection = get_keyboard_input(600)
        log.log(run_mode)
        if manual_mode_second_selection == "01":    # start assemble
            log.log("start assembly")
            thread_start_assemble = threading.Thread(target=instance_assemble_engine.start())
            thread_start_assemble.start()
            log.log("assemble pid is {}".format(instance_assemble_engine.status.pid))
        elif manual_mode_second_selection == "02":
            log.log("start execution")
            instance_execution_engine.start()
            log.log("execute pid is {}".format(instance_execution_engine.status.pid))
        elif manual_mode_second_selection == "03":
            log.log("stop assembly")
            instance_assemble_engine.stop()
        elif manual_mode_second_selection == "04":
            log.log("stop execute")
            instance_execution_engine.stop()
        elif manual_mode_second_selection == "99":
            log.log(
                "User select to stop or no selection within a certain time, program exit"
            )
            break
        else:
            log.log("Unknow run mode, please select the valid mode from the list")


def run_with_auto_mode():
    log.log("Framework will be initialized automatically")
    log.log('start configuration engine')
    instance_config_engine.start(build_server_list, deploy_list)
    log.log("configurator  finished")
    print('==============start assemble engine======================')
    log.log('start assemble engine')
    instance_assemble_engine.start()
    log.log('assemble finished')
    print(
        '=================start execution engine=====================')
    log.log('start execution engine')
    instance_execution_engine.start()
    log.log('execution finished')
    watch_assemble_thread = threading.Thread(
        target=keep_assemble_alive, name="watch_assemble_thread", args=())
    watch_assemble_thread.start()
    watch_executor_thread = threading.Thread(
        target=keep_executor_alive, name="watch_executor_thread", args=())
    watch_executor_thread.start()


def keep_assemble_alive():
    while True:
        time.sleep(5)
        log.log("[watch_assemble_thread] assemble engine pid {} current status is {}"
                .format(instance_assemble_engine.status.pid, str(instance_assemble_engine.status.is_alive())))
        if not instance_assemble_engine.status.is_alive():
            instance_assemble_engine.start()
            if instance_assemble_engine.status.is_alive():
                log.log(
                    "[watch_assemble_thread] start assemble engine successfully"
                )
            else:
                log.log("[watch_assemble_thread] can't start assemble engine")


def keep_executor_alive():
    while True:
        time.sleep(5)
        log.log("[watch_executor_thread] execution engine pid {} current status is {}"
                .format(instance_execution_engine.status.pid, str(instance_execution_engine.status.is_alive())))
        if not instance_execution_engine.status.is_alive():
            instance_execution_engine.start()
            if instance_execution_engine.status.is_alive():
                log.log(
                    "[watch_executor_thread] start execution engine successfully"
                )
            else:
                log.log("[watch_executor_thread] can't start execution engine")


if __name__ == '__main__':
    pipe = Pipe()
    log = log.Log(name='framework')
    log.log('Begin to start controller')
    build_server_list = []
    deploy_list = []
    instance_config_engine = configuration_engine.ConfigurationEngine()
    instance_assemble_engine = assemble_engine.AssembleEngine(pipe[0], build_server_list)
    instance_execution_engine = execution_engine.ExecutionEngine(deploy_list, pipe[1])
    log.log(
        "++++++++++++++++++++++++++ Select mode+++++++++++++++++++++++++++++++"
    )
    log.log("+++++++++++++++++++++++ 01:manual +++++++++++++++++++++++")
    log.log("+++++++++++++++++++++++ 02:auto,default +++++++++++++++++")
    log.log("+++++++++++++++++++++++ 99:exit +++++++++++++++++++++++++")
    run_mode = get_keyboard_input(60)
    log.log(run_mode)
    while True:
        if run_mode == "01":  # manual mode
            temp_thread = threading.Thread(target=run_with_manual_mode)
            temp_thread.start()
            break
        elif run_mode == "02":  # auto mode, default
            temp_thread = threading.Thread(target=run_with_auto_mode)
            temp_thread.start()
            break
        elif run_mode == "99":
            log.log(
                "User select to stop or no selection within a certain time, program exit"
            )
            break
        else:
            log.log("Unknow run mode, please select the valid run mode from the list")
            run_mode = get_keyboard_input(60)
