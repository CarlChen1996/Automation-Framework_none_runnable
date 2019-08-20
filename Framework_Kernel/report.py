# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:19 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : report.py
# @Project : Automation-Framework
from jinja2 import Environment, FileSystemLoader
from Framework_Kernel.log import execution_log
from Framework_Kernel.analyzer import Analyzer
import yaml
import os
import shutil


class Report:
    def __init__(self, task):
        self.settings = self.__load_settings()
        self.__name = task.get_name()
        self.__template_folder = self.settings['template_folder']
        self.__template_name = self.settings['template_name']
        self.__static_src = self.settings['static_src']
        self.__uut_list = task.get_uut_list()
        self.__result()
        self.__data = self.__final_data()
        self.__data_2 = self.__final_data_2()
        self.framework_version = '1.0'
        self.script_version = '1.0'
        self.start_time = task.start_time
        self.end_time = task.end_time

    def __load_settings(self):
        config_file = os.path.join(os.getcwd(), r'.\Configuration\config_framework_list.yml')
        analyer = Analyzer()
        report_settings = analyer.analyze_file(config_file)['report_settings']
        return report_settings

    # generate html
    def generate(self):
        env = Environment(loader=FileSystemLoader(
            os.path.join(os.getcwd(), self.__template_folder), encoding='utf-8'))
        self.total = {
            'Passing rate':
            '%.2f' % (100 * self.__data['passCount'] / self.__data['count']),
            'Pass':
            self.__data['passCount'],
            'Fail':
            self.__data['failCount'],
            'NoRun':
            self.__data['norunCount'],
            'Count':
            self.__data['count']
        }
        # the canvas data
        data = [
            {
                'value': self.total['Pass'],
                'name': 'Pass',
                'itemStyle': {
                    'color': '#5cb85c'
                }
            },
            {
                'value': self.total['Fail'],
                'name': 'Fail',
                'itemStyle': {
                    'color': '#d9534f'
                }
            },
        ]
        template = env.get_template(self.__template_name)
        html = template.render(task_name=self.__name,
                               framework_version=self.framework_version,
                               script_version=self.script_version,
                               start=self.start_time,
                               end=self.end_time,
                               final_data=self.__data['final_data'],
                               final_data_2=self.__data_2['final_data_2'],
                               data=data,
                               total=self.total,
                               encoding='utf-8')  # unicode string
        task_folder_path = os.path.join(os.getcwd(), 'Report\\' + self.__name)
        with open(task_folder_path + '\\' + self.__name + '.html',
                  'w',
                  encoding='utf-8') as f:
            f.write(html)

        # copy static folder
        static_path = os.path.join(os.getcwd(), self.__static_src)
        if not os.path.exists(task_folder_path + '\\' + 'static'):
            shutil.copytree(static_path, task_folder_path + '\\' + 'static')
            execution_log.info('copy static folder finished')
        else:
            execution_log.info(
                'target folder exist, copy static folder failed')
        execution_log.info('generate {}.html finished'.format(self.__name))
        return task_folder_path

    # group by uut
    def __final_data(self):

        file = os.path.join(os.getcwd(),
                            'Report\\{}\\result.yaml'.format(self.__name))
        passed_case_number = 0
        failed_case_number = 0
        norun_case_number = 0
        data_dict = {}
        test_uut_list = []
        final_data = []
        with open(file, encoding='utf-8') as f:
            source_data = yaml.safe_load(f)

            for each_result in source_data:
                if each_result['uut_name'] not in test_uut_list:
                    test_uut_list.append(each_result['uut_name'])

            for uut_name in test_uut_list:
                # [uut, case[], pass, fail, norun, total]
                final_data.append([uut_name, [], 0, 0, 0, 0])
            for each_result in source_data:
                # k = [uut_name , [], 0, 0, 0, 0]
                for each_uut_result in final_data:
                    if each_result['uut_name'] == each_uut_result[0]:
                        index = final_data.index(each_uut_result)
                        final_data[index][1].append(each_result)
                        if each_result['result'].upper() == 'PASS':
                            final_data[index][2] += 1
                            passed_case_number += 1
                        if each_result['result'].upper() == 'FAIL':
                            final_data[index][3] += 1
                            failed_case_number += 1
                        if each_result['result'].upper() == 'NORUN':
                            final_data[index][4] += 1
                            norun_case_number += 1
                        final_data[index][5] += 1
            total_case_number = passed_case_number + failed_case_number + norun_case_number
            data_dict['final_data'] = final_data
            data_dict['passCount'] = passed_case_number
            data_dict['failCount'] = failed_case_number
            data_dict['norunCount'] = norun_case_number
            data_dict['count'] = total_case_number
        return data_dict

    # group by case
    def __final_data_2(self):
        file = os.path.join(os.getcwd(),
                            'Report\\{}\\result.yaml'.format(self.__name))
        passed_case_number = 0
        failed_case_number = 0
        norun_case_number = 0
        data_dict_2 = {}
        test_case_list = []
        final_data_2 = []
        with open(file, encoding='utf-8') as f:
            source_data = yaml.safe_load(f)

            for each_result in source_data:
                if each_result['case_name'] not in test_case_list:
                    test_case_list.append(each_result['case_name'])

            for case_name in test_case_list:
                # [case_name, uut[], pass, fail, norun, total]
                final_data_2.append([case_name, [], 0, 0, 0, 0])
            for each_result in source_data:
                # print(each_result)
                for each_case_result in final_data_2:
                    if each_result['case_name'] == each_case_result[0]:
                        index = final_data_2.index(each_case_result)
                        final_data_2[index][1].append(each_result)
                        if each_result['result'].upper() == 'PASS':
                            final_data_2[index][2] += 1
                            passed_case_number += 1
                        if each_result['result'].upper() == 'FAIL':
                            final_data_2[index][3] += 1
                            failed_case_number += 1
                        if each_result['result'].upper() == 'NORUN':
                            final_data_2[index][4] += 1
                            norun_case_number += 1
                        final_data_2[index][5] += 1
            total_case_number = passed_case_number + failed_case_number + norun_case_number
            data_dict_2['final_data_2'] = final_data_2
            data_dict_2['passCount'] = passed_case_number
            data_dict_2['failCount'] = failed_case_number
            data_dict_2['norunCount'] = norun_case_number
            data_dict_2['count'] = total_case_number
        return data_dict_2

    # get all uut result
    def __result(self):
        result = []
        result_file = os.path.join(
            os.getcwd(), 'Report\\{}\\result.yaml'.format(self.__name))
        for i in self.__uut_list:
            uut_result_file = os.path.join(
                os.getcwd(), 'Report\\{}\\{}\\test_report\\{}.yaml'.format(
                    self.__name, i.get_ip(), i.get_ip()))
            if not os.path.exists(uut_result_file):
                if not os.path.exists(os.path.dirname(result_file)):
                    os.makedirs(os.path.dirname(result_file))
                a = [{
                    'uut_name': i,
                    'case_name': 'Error',
                    'steps': [],
                    'result': 'Fail'
                }]
                result.extend(a)
                continue
            with open(uut_result_file, encoding='utf-8') as f:
                a = yaml.safe_load(f.read())
                result.extend(a)

        with open(result_file, 'w', encoding='utf-8') as g:
            yaml.dump(result, g)
            # print(g)

    @staticmethod
    def remove_report_folder(task_report_path):
        shutil.rmtree(task_report_path)
