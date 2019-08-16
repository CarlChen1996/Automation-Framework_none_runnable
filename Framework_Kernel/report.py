# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:19 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : report.py
# @Project : Automation-Framework
import zipfile

from jinja2 import Environment, FileSystemLoader
from Framework_Kernel.log import execution_log, assemble_log
import yaml
import os
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
import shutil


class Report:
    def __init__(
            self,
            name,
            uut_list,
            type='HTML',
            template='1',
    ):
        self.__name = name
        self.__type = type
        self.__template = template
        self.__uut_list = uut_list
        self.__result()
        self.__data = self.__final_data()
        self.__data_2 = self.__final_data_2()

    # generate html
    def generate(self):
        env = Environment(loader=FileSystemLoader(os.path.join(os.getcwd(), 'Report\\templates'), encoding='utf-8'))
        information = {
            'Category': 'TEST ',
            'Version': ' 1.0',
            'Start Time': ' 2018-5-14 14:58:27',
            'Duration': ' 00:30:03',
            'Note': '为了RC的最后一次回归测试',
        }
        # total=[PassingRate,Pass,Fail,NoRun,Count]
        self.total = {
            'Passing rate': '%.2f' % (100 * self.__data['passCount'] / self.__data['count']),
            'Pass': self.__data['passCount'],
            'Fail': self.__data['failCount'],
            'NoRun': self.__data['norunCount'],
            'Count': self.__data['count']
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
            # {'value': total['NoRun'], 'name': 'No Run', 'itemStyle': {'color': 'grey'}},
        ]
        template = env.get_template('template_1.html')
        html = template.render(information=information,
                               final_data=self.__data['final_data'],
                               final_data_2=self.__data_2['final_data_2'],
                               data=data,
                               total=self.total,
                               task_name=self.__name,
                               encoding='utf-8')  # unicode string
        task_folder_path = os.path.join(os.getcwd(), 'Report\\' + self.__name)
        with open(task_folder_path + '\\' + self.__name + '.html',
                  'w',
                  encoding='utf-8') as f:
            f.write(html)

        # copy static folder
        static_path = os.path.join(os.getcwd(), 'Report\\templates\\static')
        if not os.path.exists(task_folder_path + '\\' + 'static'):
            shutil.copytree(static_path, task_folder_path + '\\' + 'static')
            execution_log.info('copy static folder finished')
        else:
            execution_log.info('target folder exist, copy static folder failed')
        execution_log.info('generate {}.html finished'.format(self.__name))
        return task_folder_path

    # group by uut
    def __final_data(self):

        file = os.path.join(os.getcwd(), 'Report\\{}\\result.yaml'.format(self.__name))
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
            # print(test_uut_list)
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
        file = os.path.join(os.getcwd(), 'Report\\{}\\result.yaml'.format(self.__name))
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
            # print(test_uut_list)

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
        result_file = os.path.join(os.getcwd(), 'Report\\{}\\result.yaml'.format(self.__name))
        for i in self.__uut_list:
            uut_result_file = os.path.join(os.getcwd(),
                                           'Report\\{}\\{}\\test_report\\{}.yaml'.format(self.__name, i.get_ip(),
                                                                                         i.get_ip()))
            if not os.path.exists(uut_result_file):
                if not os.path.exists(os.path.dirname(result_file)):
                    os.makedirs(os.path.dirname(result_file))
                a = [{'uut_name': i, 'case_name': 'Error', 'steps': [], 'result': 'Fail'}]
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


if __name__ == '__main__':
    # debug in this module should change os.getcwd() to os.path.dirname(os.getcwd()) and i.get_ip() to i
    # uut_list = ['15.83.248.208', '15.83.250.20', '15.15.15.15',]
    # r = Report(name='task_2',uut_list=uut_list)
    # r.generate()
    # e = Email('carl.chen@hp.com')
    # e.zip_result_package(r.generate(), 'task_1')
    # zip_result_package(r'E:\PycharmProjects\Automation-Framework\Report\task_1','task_1.zip')
    #
    # e=Email(receiver=['carl.chen@hp.com'],attachments_rar='E:\\PycharmProjects\\test\\log_module\\task_1.rar')
    # e.send()
    e = Email(['carl.chen@hp.com'])
    e.send_message()
    # pass
