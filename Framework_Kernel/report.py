# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:19 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : report.py
# @Project : Automation-Framework
from jinja2 import Environment, FileSystemLoader
from Framework_Kernel.log import execution_log
# from Framework_Kernel.analyzer import Analyzer
from Framework_Kernel.analyzer import framework_settings
import yaml
import os
import shutil
import pandas
from Framework_Kernel.error_handler import ErrorMsg, ErrorLevel, ErrorHandler, EngineCode


class Report:
    def __init__(self, task):
        self.settings = self.__load_settings()
        self.__template_folder = self.settings['template_folder']
        self.__template_name = self.settings['template_name']
        self.__static_src = self.settings['static_src']
        self.__name = task.get_name()
        self.task = task
        self.__uut_list = task.get_uut_list()
        self.__start_time = task.start_time
        self.__end_time = task.end_time
        self.__test_report_root = os.path.join(os.getcwd(), 'Report\\' + task.folder_name)
        self.__load_uut_result()
        self.__data_by_uut = self.__generate_table('uut_name')
        self.__data_by_case = self.__generate_table('case_name')
        self.total = {
            'Passing rate': '%.2f' % (100 * self.__data_by_uut['passCount'] / self.__data_by_uut['count']),
            'Pass': self.__data_by_uut['passCount'],
            'Fail': self.__data_by_uut['failCount'],
            'NoRun': self.__data_by_uut['norunCount'],
            'Count': self.__data_by_uut['count']
        }
        self.pie_chart_data = [
            {
                'value': self.total['Pass'],
                'name': 'Pass',
                'itemStyle': {'color': '#5cb85c'}
            },
            {
                'value': self.total['Fail'],
                'name': 'Fail',
                'itemStyle': {'color': '#d9534f'}
            },
        ]
        self.framework_version = '1.0'
        self.script_version = '1.0'

    def __load_settings(self):
        report_settings = framework_settings['report_settings']
        return report_settings

    # generate html
    def generate(self):
        env = Environment(loader=FileSystemLoader(
            os.path.join(os.getcwd(), self.__template_folder), encoding='utf-8'))
        template = env.get_template(self.__template_name)
        html = template.render(task_name=self.__name,
                               framework_version=self.framework_version,
                               script_version=self.script_version,
                               start=self.__start_time,
                               end=self.__end_time,
                               final_data=self.__data_by_uut['final_data'],
                               final_data_2=self.__data_by_case['final_data'],
                               data=self.pie_chart_data,
                               total=self.total,
                               encoding='utf-8')  # unicode string
        with open(self.__test_report_root + '\\' + self.__name + '.html', 'w', encoding='utf-8') as f:
            f.write(html)
        # copy static folder
        if self.__get_src_files():
            execution_log.info('generate {}.html finished'.format(self.__name))
        return self.__test_report_root

    def __get_src_files(self):
        static_path = os.path.join(os.getcwd(), self.__static_src)
        if os.path.exists(self.__test_report_root + '\\' + 'static'):
            shutil.rmtree(self.__test_report_root + '\\' + 'static')
            execution_log.info('Target static folder exist, remove the old folder')
        shutil.copytree(static_path, self.__test_report_root + '\\' + 'static')
        execution_log.info('Copy static folder to report folder finished')
        return True

    def __generate_table(self, key_name):
        test_result_file = os.path.join(self.__test_report_root, 'result.yaml')
        with open(test_result_file, 'r') as f:
            source_data = yaml.safe_load(f)
        df_raw = pandas.DataFrame(source_data)
        # remove the unnecessary column
        df_new = df_raw[[key_name, 'result']]
        table_raw = pandas.pivot_table(df_new, index=key_name, columns='result', aggfunc=len, fill_value=0, margins=True)
        # Turn index to new column
        table_raw[key_name] = table_raw.index
        table_format = table_raw[[key_name, 'pass', 'fail']]
        # raw_data: list:[[key_name, 'pass_count', 'fail_count'], [key_name, 'pass_count', 'fail_count'], ...]
        raw_data = table_format.values.tolist()
        final_data = []
        data_dict = {}
        current_case_list = []
        # exclude last item: All
        for item in raw_data[:-1]:
            for each_result in source_data:
                if item[0] == each_result[key_name]:
                    current_case_list.append(each_result)
            final_data.append([item[0], current_case_list, item[1], item[2], 0, item[1] + item[2]])
        # get last item in list
        total_item = raw_data.pop()
        data_dict['final_data'] = final_data
        data_dict['passCount'] = total_item[1]
        data_dict['failCount'] = total_item[2]
        data_dict['norunCount'] = 0
        data_dict['count'] = total_item[1] + total_item[2]
        return data_dict

    # get all uut result
    def __load_uut_result(self):
        result = []
        if not os.path.exists(self.__test_report_root):
            os.makedirs(self.__test_report_root)
        result_file = os.path.join(self.__test_report_root, 'result.yaml')
        for i in self.__uut_list:
            uut_result_file = os.path.join(self.__test_report_root, '{}\\test_report\\{}.yaml'.format(i.get_ip(), i.get_ip()))
            if not os.path.exists(uut_result_file):
                empty_result = [{
                    'uut_name': i.get_ip(),
                    'case_name': 'No result return',
                    'steps': [],
                    'result': 'fail'
                },{
                    'uut_name': i.get_ip(),
                    'case_name': 'No result return',
                    'steps': [],
                    'result': 'pass'
                }]
                result.extend(empty_result)
                """
                error handle for execute fail
                """
                error_msg_instance = ErrorMsg(EngineCode().execute_engine, ErrorLevel().mark_task,
                                              "execute task {} fail on uut {}".format(self.__name, i.get_ip()))
                error_handle_instance = ErrorHandler(error_msg_instance)
                error_handle_instance.handle(task=self.task, state="unknown", mail_receiver=self.task.get_email())
                continue
            with open(uut_result_file, encoding='utf-8') as f:
                empty_result = yaml.safe_load(f.read())
                result.extend(empty_result)
        with open(result_file, 'w', encoding='utf-8') as g:
            yaml.dump(result, g)
        return result

    @staticmethod
    def remove_report_folder(task_report_path):
        shutil.rmtree(task_report_path)
