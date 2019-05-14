# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:19 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : report.py
# @Project : Automation-Framework
from jinja2 import Environment, FileSystemLoader
import yaml

class Report:
    def __init__(self, name='default', type='HTML', template='1'):
        self.name = name
        self.type = type
        self.template = template

    def generate(self,fdata):
        # print('generate html finished')

        env = Environment(loader=FileSystemLoader('./templates', encoding='utf-8'))
        information = {'Category': 'HPDM / HPWF / UWF /ThinUpdate/ ',
                       'Version': ' 1.0/ 1.0/ 1.0/ 1.0	',
                       'Start Time': ' 2018-5-14 14:58:27',
                       'Duration': ' 00:30:03	#仅保留秒',
                       'Note': '为了RC的最后一次的回归测试',
                       }
        ffdata = fdata['fdata']
        passCount = fdata['passCount']
        failCount = fdata['failCount']
        norunCount = fdata['norunCount']
        count = fdata['count']
        # total=[PassingRate,Pass,Fail,NoRun,Count]
        total = {'Passing rate': 100 * passCount / count, 'Pass': passCount, 'Fail': failCount, 'NoRun': norunCount,
                 'Count': count}

        data = [{'value': total['Pass'], 'name': 'Pass', 'itemStyle': {'color': '#5cb85c'}},
                {'value': total['Fail'], 'name': 'Fail', 'itemStyle': {'color': '#d9534f'}},
                # {'value': total['NoRun'], 'name': 'No Run', 'itemStyle': {'color': 'grey'}},
                ]
        template = env.get_template('tmp.html')
        html = template.render(information=information, fdata=ffdata, data=data, total=total,task_name=self.name,
                               encoding='utf-8')  # unicode string
        with open('../Report/'+self.name+'.html', 'w', encoding='utf-8') as f:
            f.write(html)

    def fdata(file='result.yaml'):
        passCount = 0
        failCount = 0
        norunCount = 0
        data_dict = {}
        test_list = []
        fdata = []
        f = open('result.yaml', encoding='utf-8')
        a = yaml.safe_load(f.read())
        for v in a.values():
            if v[-1] not in test_list:
                test_list.append(v[-1])
        # print(test_list)

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
    r=Report(name='task1')
    fdata=r.fdata()
    r.generate(fdata)

