from multiprocessing import Pipe
from Framework_Kernel.log import controller_log
from Framework_Kernel import configuration_engine
from Framework_Kernel import assemble_engine
from Framework_Kernel import execution_engine
from Framework_Kernel.error_handler import ERROR_MSG,ERROR_LEVEL,ErrorHandler,ENGINE_CODE
from Common_Library.functions import get_keyboard_input
from multiprocessing import Process
import threading
import time


def run_with_manual_mode():
    is_framework_configured = False
    controller_log.info(
        "This is the manual operation mode, framework must be configured before continue"
    )
    controller_log.info(
        "++++++++++++++++++++++++++ manual mode first selection+++++++++++++++++++++++++++++++"
    )
    controller_log.info(
        "+++++++++++++++++++++++ 01:start config +++++++++++++++++++++++")
    controller_log.info(
        "+++++++++++++++++++++++ 99:exit +++++++++++++++++++++++++")
    manual_mode_first_selection = get_keyboard_input(60)
    controller_log.info(run_mode)
    while True:
        if manual_mode_first_selection == "01":  # start config engine
            controller_log.info("start config")
            instance_config_engine.start()
            controller_log.info("config pid is {}".format(
                instance_config_engine.status.pid))
            is_framework_configured = True
            break
        elif manual_mode_first_selection == "99":
            controller_log.info(
                "User select to stop or no selection within a certain time, program exit"
            )
            break
        else:
            controller_log.info(
                "Unknown run mode, please select the valid run mode from the list"
            )
            manual_mode_first_selection = get_keyboard_input(60)

    while is_framework_configured:
        controller_log.info(
            "Framework has been configured, please continue with the operation"
        )
        controller_log.info(
            "++++++++++++++++++++++++++ manual mode second selection+++++++++++++++++++++++++++++++"
        )
        controller_log.info(
            "+++++++++++++++++++++++ 01:start assembly +++++++++++++++++++++++"
        )
        controller_log.info(
            "+++++++++++++++++++++++ 02:start execution +++++++++++++++++++++++"
        )
        controller_log.info(
            "+++++++++++++++++++++++ 03:stop assembly +++++++++++++++++++++++")
        controller_log.info(
            "+++++++++++++++++++++++ 04:stop execution +++++++++++++++++++++++"
        )
        controller_log.info(
            "+++++++++++++++++++++++ 99:exit - this will stop all engines  +++++++++++++++++++++++"
        )
        manual_mode_second_selection = get_keyboard_input(600)
        controller_log.info(run_mode)
        if manual_mode_second_selection == "01":  # start assemble
            controller_log.info("start assembly")
            thread_start_assemble = threading.Thread(
                target=instance_assemble_engine.start())
            thread_start_assemble.start()
            controller_log.info("assemble pid is {}".format(
                instance_assemble_engine.status.pid))
        elif manual_mode_second_selection == "02":
            controller_log.info("start execution")
            instance_execution_engine.start()
            controller_log.info("execute pid is {}".format(
                instance_execution_engine.status.pid))
        elif manual_mode_second_selection == "03":
            controller_log.info("stop assembly")
            instance_assemble_engine.stop()
        elif manual_mode_second_selection == "04":
            controller_log.info("stop execute")
            instance_execution_engine.stop()
        elif manual_mode_second_selection == "99":
            controller_log.info(
                "User select to stop or no selection within a certain time, program exit"
            )
            break
        else:
            controller_log.info(
                "Unknown run mode, please select the valid mode from the list")


def run_with_auto_mode():
    controller_log.info("Framework will be initialized automatically")
    controller_log.info('start configuration engine')
    instance_config_engine.start()
    controller_log.info("configurator  finished")
    print('==============start assemble engine======================')
    controller_log.info('start assemble engine')

    while not instance_config_engine.list_status:
        time.sleep(5)
        controller_log.info('Server list not ready, wait for 5 seconds')
    instance_assemble_engine.start()
    controller_log.info('assemble finished')
    print('=================start execution engine=====================')
    controller_log.info('start execution engine')
    instance_execution_engine.start()
    controller_log.info('execution finished')
    watch_assemble_thread = threading.Thread(target=keep_assemble_alive,
                                             name="watch_assemble_thread",
                                             args=())
    watch_assemble_thread.start()
    watch_executor_thread = threading.Thread(target=keep_executor_alive,
                                             name="watch_executor_thread",
                                             args=())
    watch_executor_thread.start()


def keep_assemble_alive():
    while True:
        time.sleep(5)
        if not isinstance(instance_assemble_engine.status, Process):
            error_msg_instance = ERROR_MSG(ENGINE_CODE().controller,
                                           ERROR_LEVEL().reset_engine,
                                           'reset assemble_engine for process instance check fail')
            error_handle_instance = ErrorHandler(error_msg_instance)
            error_handle_instance.handle(engine=instance_assemble_engine)
            # instance_assemble_engine.start()
        if not instance_assemble_engine.status.is_alive():
            error_msg_instance = ERROR_MSG(ENGINE_CODE().controller,
                                           ERROR_LEVEL().reset_engine,
                                           'reset assemble_engine for process alive check fail')
            error_handle_instance = ErrorHandler(error_msg_instance)
            error_handle_instance.handle(engine=instance_assemble_engine)

            # instance_assemble_engine.start()
        #     if instance_assemble_engine.status.is_alive():
        #         controller_log.info(
        #             "[watch_assemble_thread] start assemble engine successfully"
        #         )
        #     else:
        #         controller_log.info(
        #             "[watch_assemble_thread] can't start assemble engine")
        # controller_log.info(
        #     "[watch_assemble_thread] assemble engine pid {} current status is {}"
        #     .format(instance_assemble_engine.status.pid,
        #             str(instance_assemble_engine.status.is_alive())))


def keep_executor_alive():
    while True:
        time.sleep(5)
        if not isinstance(instance_execution_engine.status, Process):
            error_msg_instance = ERROR_MSG(ENGINE_CODE().controller,
                                           ERROR_LEVEL().reset_engine,
                                           'reset execution_engine for process instance check fail')
            error_handle_instance = ErrorHandler(error_msg_instance)
            error_handle_instance.handle(engine=instance_execution_engine)
            # instance_execution_engine.start()
        if not instance_execution_engine.status.is_alive():
            error_msg_instance = ERROR_MSG(ENGINE_CODE().controller,
                                           ERROR_LEVEL().reset_engine,
                                           'reset execution_engine for process alive check fail')
            error_handle_instance = ErrorHandler(error_msg_instance)
            error_handle_instance.handle(engine=instance_execution_engine)
        #     instance_execution_engine.start()
        #     if instance_execution_engine.status.is_alive():
        #         controller_log.info(
        #             "[watch_executor_thread] start execution engine successfully"
        #         )
        #     else:
        #         controller_log.info(
        #             "[watch_executor_thread] can't start execution engine")
        # controller_log.info(
        #     "[watch_executor_thread] execution engine pid {} current status is {}"
        #     .format(instance_execution_engine.status.pid,
        #             str(instance_execution_engine.status.is_alive())))


if __name__ == '__main__':
    pipe = Pipe()
    controller_log.info('Begin to start controller')

    instance_config_engine = configuration_engine.ConfigurationEngine()
    build_server_list = instance_config_engine.build_server_list
    deploy_list = instance_config_engine.deploy_server_list
    instance_assemble_engine = assemble_engine.AssembleEngine(
        pipe[0], build_server_list)
    instance_execution_engine = execution_engine.ExecutionEngine(
        deploy_list, pipe[1])
    controller_log.info(
        "++++++++++++++++++++++++++ Select mode+++++++++++++++++++++++++++++++"
    )
    controller_log.info(
        "+++++++++++++++++++++++ 01:manual +++++++++++++++++++++++")
    controller_log.info(
        "+++++++++++++++++++++++ 02:auto,default +++++++++++++++++")
    controller_log.info(
        "+++++++++++++++++++++++ 99:exit +++++++++++++++++++++++++")
    run_mode = get_keyboard_input(60)
    controller_log.info(run_mode)
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
            controller_log.info(
                "User select to stop or no selection within a certain time, program exit"
            )
            break
        else:
            controller_log.info(
                "Unknown run mode, please select the valid run mode from the list"
            )
            run_mode = get_keyboard_input(60)
