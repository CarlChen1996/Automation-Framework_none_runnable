# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:19 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : report.py
# @Project : Automation-Framework
from jinja2 import Environment, FileSystemLoader
from Framework_Kernel.log import Log
import yaml
import os
log = Log('report')


class Report:
    def __init__(
            self,
            name,
            uut_list,
            type='HTML',
            template='1',
    ):
        self.name = name
        self.type = type
        self.template = template
        self.uut_list = uut_list
        self.data = self.final_data()

    def generate(self):
        # print('generate html finished')
        # print(self.script_list)

        env = Environment(loader=FileSystemLoader(os.path.join(os.getcwd(),'Report\\templates'), encoding='utf-8'))
        information = {
            'Category': 'TEST ',
            'Version': ' 1.0',
            'Start Time': ' 2018-5-14 14:58:27',
            'Duration': ' 00:30:03',
            'Note': '为了RC的最后一次回归测试',
        }

        report_data = self.data['final_data']
        passCount = self.data['passCount']
        failCount = self.data['failCount']
        norunCount = self.data['norunCount']
        count = self.data['count']
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
                               data=data,
                               total=total,
                               task_name=self.name,
                               encoding='utf-8')  # unicode string
        filepath = os.path.join(os.getcwd(), 'Report\\' + self.name + '\\'+self.name+'.html')
        with open(filepath,
                  'w',
                  encoding='utf-8') as f:
            f.write(html)
        log.log('generate {}.html finished'.format(self.name))

    def final_data(self):
        self.result()
        file = os.path.join(os.getcwd(), 'Report\\{}\\result.yaml'.format(self.name))
        passed_case_number = 0
        failed_case_number = 0
        norun_case_number = 0
        data_dict = {}
        test_project_list = []
        final_data = []
        f = open(file, encoding='utf-8')
        a = yaml.safe_load(f.read())

        for v in a:
            if v[0] not in test_project_list:
                test_project_list.append(v[0])

        for l in test_project_list:
            # project, case[], pass, fail, norun, total
            final_data.append([l, [], 0, 0, 0, 0])
        # print(test_project_list)
        for v in a:
            # print(v)
            for k in final_data:
                if v[0] == k[0]:
                    index = final_data.index(k)
                    final_data[index][1].append(v)
                    if v[-1] == 'Pass':
                        final_data[index][2] += 1
                        passed_case_number += 1
                    if v[-1] == 'Fail':
                        final_data[index][3] += 1
                        failed_case_number += 1
                    if v[-1] == 'Norun':
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

    def result(self):
        result = []
        for i in self.uut_list:
            with open(os.path.join(os.getcwd(),
                                   'Report\\{}\\{}\\{}.yaml'.format(self.name, i.hostname, i.hostname)), encoding='utf-8') as f:
                a = yaml.safe_load(f.read())
                result.extend(a)
        with open(os.path.join(os.getcwd(),
                               'Report\\{}\\result.yaml'.format(self.name)), 'w', encoding='utf-8') as g:
            yaml.dump(result, g)
            # print(g)


class Email:
    def __init__(self):
        pass

    def send(self,
             receiver='',
             sender='',
             subject='',
             content='',
             attachments=''):
        self.receiver = receiver
        self.sender = sender
        self.sender = subject
        self.sender = content
        self.sender = attachments
        print('send email')
        os.path.dirname(os.getcwd())
if __name__ == '__main__':
    # if debug in this module should change os.getcwd() to os.path.dirname(os.getcwd())
    uut_list = [{'hostname':'uut_1'}, {'hostname':'uut_2'}]
    r = Report(name='task_1',uut_list=uut_list)
    r.generate()
