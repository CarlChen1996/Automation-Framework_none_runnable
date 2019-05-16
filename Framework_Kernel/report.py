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
    def __init__(self, name, script_list, type='HTML', template='1',):
        self.name = name
        self.type = type
        self.template = template
        self.script_list = script_list
        self.data = self.fdata()

    def generate(self):
        # print('generate html finished')
        # print(self.script_list)

        env = Environment(loader=FileSystemLoader(os.path.join(os.getcwd(), 'Framework_Kernel/templates'),
                                                  encoding='utf-8'))
        information = {'Category': 'HPDM / HPWF / UWF /ThinUpdate/ ',
                       'Version': ' 1.0/ 1.0/ 1.0/ 1.0	',
                       'Start Time': ' 2018-5-14 14:58:27',
                       'Duration': ' 00:30:03',
                       'Note': '为了RC的最后一次回归测试',
                       }

        ffdata = self.data['fdata']
        passCount = self.data['passCount']
        failCount = self.data['failCount']
        norunCount = self.data['norunCount']
        count = self.data['count']
        # total=[PassingRate,Pass,Fail,NoRun,Count]
        total = {'Passing rate': '%.2f' % (100 * passCount / count),
                 'Pass': passCount,
                 'Fail': failCount,
                 'NoRun': norunCount,
                 'Count': count}

        data = [{'value': total['Pass'], 'name': 'Pass', 'itemStyle': {'color': '#5cb85c'}},
                {'value': total['Fail'], 'name': 'Fail', 'itemStyle': {'color': '#d9534f'}},
                # {'value': total['NoRun'], 'name': 'No Run', 'itemStyle': {'color': 'grey'}},
                ]
        template = env.get_template('tmp.html')
        html = template.render(information=information, fdata=ffdata, data=data, total=total, task_name=self.name,
                               encoding='utf-8')  # unicode string
        with open(os.path.join(os.getcwd(), 'Report\\'+self.name+'.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        log.log('generate {}.html finished'.format(self.name))

    def fdata(self):
        file = os.path.join(os.getcwd(), 'Framework_Kernel\\{}_result.yaml'.format(self.name))
        passCount = 0
        failCount = 0
        norunCount = 0
        data_dict = {}
        test_list = []
        fdata = []
        f = open(file, encoding='utf-8')
        a = yaml.safe_load(f.read())
        # print(list(a.values()))

        for v in list(a.values()):
            # print(v[0])
            v[0] = self.script_list[list(a.values()).index(v)].get_name()
            # for s in self.script_list:
            #     v[0]=s.get_name()
            if v[-1] not in test_list:
                test_list.append(v[-1])
        # print(test_list)
        # for s in self.script_list:
        #     print(s.get_name())

        for l in test_list:
            fdata.append([l, [], 0, 0, 0, 0])
        # print(fdata)

        for v in a.values():
            for l in fdata:
                if v[-1] == l[0]:
                    index = fdata.index(l)
                    fdata[index][1].append(v)
                    if v[-2] == 'Pass':
                        fdata[index][2] += 1
                        passCount += 1
                    if v[-2] == 'Fail':
                        fdata[index][3] += 1
                        failCount += 1
                    if v[-2] == 'Norun':
                        fdata[index][4] += 1
                        norunCount += 1
                    fdata[index][5] += 1
        count = passCount + failCount + norunCount
        data_dict['fdata'] = fdata
        data_dict['passCount'] = passCount
        data_dict['failCount'] = failCount
        data_dict['norunCount'] = norunCount
        data_dict['count'] = count
        return data_dict


class Email:
    def __init__(self):
        pass

    def send(self,
             receiver='',
             sender='',
             subject='',
             content='',
             attanchments=''):
        self.receiver = receiver
        self.sender = sender
        self.sender = subject
        self.sender = content
        self.sender = attanchments
        print('send email')


if __name__ == '__main__':
    r = Report(name='task1')
    fdata = r.fdata()
    r.generate(fdata)