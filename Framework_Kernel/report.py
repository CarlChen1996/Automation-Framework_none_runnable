# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:19 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : report.py
# @Project : Automation-Framework
import zipfile

from jinja2 import Environment, FileSystemLoader
from Framework_Kernel.log import execution_log
import yaml
import os
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header


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

    def generate(self):
        # print('generate html finished')
        # print(self.script_list)

        env = Environment(loader=FileSystemLoader(os.path.join(os.getcwd(), 'Report\\templates'), encoding='utf-8'))
        information = {
            'Category': 'TEST ',
            'Version': ' 1.0',
            'Start Time': ' 2018-5-14 14:58:27',
            'Duration': ' 00:30:03',
            'Note': '为了RC的最后一次回归测试',
        }

        report_data = self.__data['final_data']
        report_data_2 = self.__data_2['final_data_2']
        passCount = self.__data['passCount']
        failCount = self.__data['failCount']
        norunCount = self.__data['norunCount']
        count = self.__data['count']
        # total=[PassingRate,Pass,Fail,NoRun,Count]
        total = {
            'Passing rate': '%.2f' % (100 * passCount / count),
            'Pass': passCount,
            'Fail': failCount,
            'NoRun': norunCount,
            'Count': count

        }

        data = [
            {
                'value': total['Pass'],
                'name': 'Pass',
                'itemStyle': {
                    'color': '#5cb85c'
                }
            },
            {
                'value': total['Fail'],
                'name': 'Fail',
                'itemStyle': {
                    'color': '#d9534f'
                }
            },
            # {'value': total['NoRun'], 'name': 'No Run', 'itemStyle': {'color': 'grey'}},
        ]
        template = env.get_template('tmp.html')
        html = template.render(information=information,
                               final_data=report_data,
                               final_data_2=report_data_2,
                               data=data,
                               total=total,
                               task_name=self.__name,
                               encoding='utf-8')  # unicode string
        filepath = os.path.join(os.getcwd(), 'Report\\' + self.__name)
        with open(filepath + '\\'+self.__name+'.html',
                  'w',
                  encoding='utf-8') as f:
            f.write(html)
        static_path = os.path.join(os.getcwd(),'Report\\templates\\static')
        shutil.copytree(static_path, filepath+'\\'+'static')
        execution_log.info('generate {}.html finished'.format(self.__name))
        return filepath
    def __final_data(self):

        file = os.path.join(os.getcwd(), 'Report\\{}\\result.yaml'.format(self.__name))
        passed_case_number = 0
        failed_case_number = 0
        norun_case_number = 0
        data_dict = {}
        test_uut_list = []
        final_data = []
        f = open(file, encoding='utf-8')
        a = yaml.safe_load(f.read())

        for v in a:
            if v['uut_name'] not in test_uut_list:
                test_uut_list.append(v['uut_name'])

        for uut_name in test_uut_list:
            # project, case[], pass, fail, norun, total
            final_data.append([uut_name, [], 0, 0, 0, 0])
        # print(test_uut_list)

        for v in a:
            # print(v)
            for k in final_data:
                if v['uut_name'] == k[0]:
                    index = final_data.index(k)
                    final_data[index][1].append(v)
                    if v['result'] == 'Pass':
                        final_data[index][2] += 1
                        passed_case_number += 1
                    if v['result'] == 'Fail':
                        final_data[index][3] += 1
                        failed_case_number += 1
                    if v['result'] == 'Norun':
                        final_data[index][4] += 1
                        norun_case_number += 1
                    final_data[index][5] += 1
        total_case_number = passed_case_number + failed_case_number + norun_case_number
        data_dict['final_data'] = final_data
        data_dict['passCount'] = passed_case_number
        data_dict['failCount'] = failed_case_number
        data_dict['norunCount'] = norun_case_number
        data_dict['count'] = total_case_number
        # print('-------------------------????????????---')
        # print(data_dict)
        # print('-------------------------????????????---')
        return data_dict

    def __final_data_2(self):
        file = os.path.join(os.getcwd(), 'Report\\{}\\result.yaml'.format(self.__name))
        passed_case_number = 0
        failed_case_number = 0
        norun_case_number = 0
        data_dict_2 = {}
        test_case_list = []
        final_data_2 = []
        f = open(file, encoding='utf-8')
        a = yaml.safe_load(f.read())

        for v in a:
            if v['case_name'] not in test_case_list:
                test_case_list.append(v['case_name'])

        for case_name in test_case_list:
            # project, case[], pass, fail, norun, total
            final_data_2.append([case_name, [], 0, 0, 0, 0])
        # print(test_uut_list)

        for v in a:
            # print(v)
            for k in final_data_2:
                if v['case_name'] == k[0]:
                    index = final_data_2.index(k)
                    final_data_2[index][1].append(v)
                    if v['result'] == 'Pass':
                        final_data_2[index][2] += 1
                        passed_case_number += 1
                    if v['result'] == 'Fail':
                        final_data_2[index][3] += 1
                        failed_case_number += 1
                    if v['result'] == 'Norun':
                        final_data_2[index][4] += 1
                        norun_case_number += 1
                    final_data_2[index][5] += 1
        total_case_number = passed_case_number + failed_case_number + norun_case_number
        data_dict_2['final_data_2'] = final_data_2
        data_dict_2['passCount'] = passed_case_number
        data_dict_2['failCount'] = failed_case_number
        data_dict_2['norunCount'] = norun_case_number
        data_dict_2['count'] = total_case_number
        # print('-------------------------????????????---')
        # print(data_dict_2)
        # print('-------------------------????????????---')
        return data_dict_2

    def __result(self):
        result = []
        for i in self.__uut_list:
            with open(os.path.join(os.getcwd(),
                                   'Report\\{}\\{}\\test_report\\{}.yaml'.format(self.__name, i.get_ip(), i.get_ip())), encoding='utf-8') as f:
                a = yaml.safe_load(f.read())
                result.extend(a)
        with open(os.path.join(os.getcwd(),
                               'Report\\{}\\result.yaml'.format(self.__name)), 'w', encoding='utf-8') as g:
            yaml.dump(result, g)
            # print(g)


class Email:
    def __init__(self, receiver, ):
        self.receiver = receiver
        self.smtpserver = '15.73.212.81'
        self.sender = 'carl.chen@hp.com'
        self.subject = Header('Report email test', 'utf-8').encode()

    def zip_result_package(self, result_path, name):
        result_path = result_path
        self.send_file_name = name+'.zip'
        self.send_file = result_path + '.zip'
        """
        压缩指定文件夹
        :param result_path: 目标文件夹路径
        :param send_file: 压缩文件保存路径+xxxx.zip
        :return: 无
        """
        zip = zipfile.ZipFile(self.send_file, "w", zipfile.ZIP_DEFLATED)
        for path, dirnames, filenames in os.walk(result_path):
            # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
            fpath = path.replace(result_path, '')

            for filename in filenames:
                zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
        zip.close()

    def send(self,):
        msg = MIMEMultipart('mixed')
        msg['Subject'] = self.subject
        msg['From'] = self.sender
        msg['To'] = ";".join(self.receiver)
        #正文
        text = """Hi,\n\nYour test has been completed, please refer to the attachment for details.\n\nBest regards"""
        text_plain = MIMEText(text, 'plain', 'utf-8')
        msg.attach(text_plain)
        #附件
        sendfile = open(self.send_file, 'rb').read()
        text_attachment = MIMEText(sendfile, 'base64', 'utf-8')
        text_attachment["Content-Disposition"] = 'attachment; filename="{}"'.format(self.send_file_name)
        msg.attach(text_attachment)
        try:
            smtp = smtplib.SMTP()
            smtp.connect(self.smtpserver, 25)
            smtp.sendmail(self.sender, self.receiver, msg.as_string())
            execution_log.info('send email success')
            smtp.quit()
        except smtplib.SMTPException as e:
            print("Error: %s" % e)

if __name__ == '__main__':
    # debug in this module should change os.getcwd() to os.path.dirname(os.getcwd())
    # uut_list = [{'hostname':'15.83.250.1'}, {'hostname':'15.83.250.2'}]
    # r = Report(name='task_1',uut_list=uut_list)
    # r.generate()
    # zip_result_package(r'E:\PycharmProjects\Automation-Framework\Report\task_1','task_1.zip')

    # e=Email(receiver=['carl.chen@hp.com'],attachments_rar='E:\\PycharmProjects\\test\\log_module\\task_1.rar')
    # e.send()
    pass