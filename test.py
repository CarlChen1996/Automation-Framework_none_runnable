# -*- coding: utf-8 -*-
# @Time    : 5/15/2019 2:12 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : test.py
# @Project : Automation-Framework
from multiprocessing import Process
from multiprocessing import Pipe
import threading
from time import ctime
import time
import os

class Configuration:
    def __init__(self,):
        self.config = Process(target=self.configuration, name='framework_configuration', args=())

    def configuration(self):
        time.sleep(3)
        print('config finished')

    def start_c(self):
        self.config.start()
        self.config.join()


class Assemblr:

    def __init__(self, pipe):
        self.pipe = pipe
        self.assembler = Process(target=self.assemble_q, name='framework_assembler', args=())
        self.a_q_list=[]

    def assemble_q(self):
        threads = []
        t1 = threading.Thread(target=self.thred_1, args=())
        threads.append(t1)
        t2 = threading.Thread(target=self.thred_2, args=())
        threads.append(t2)
        for t in threads:
            t.setDaemon(True)
            t.start()
            # t.join()
        t.join()
        print(" [process1]all thread finish at %s" % ctime())

    def thred_1(self):
        i = 1
        while True:
            self.a_q_list.append(i)
            print('[thred_1] append {} into a_q_list'.format(i))
            print('[thred_1] a_q_list now is {}'.format(self.a_q_list))
            time.sleep(1)
            i += 1

    def thred_2(self):
        while True:
            l=self.a_q_list[:]
            print('[thred_2] now is build {}'.format(l[0]))
            print("[thred_2] now send {}".format(l[0]))
            self.pipe.send(l[0])
            print("[thred_2] remove {} from a_q_list".format(l[0]))
            self.a_q_list.remove(l[0])
            print('[thred_2] a_q_list now is {}'.format(self.a_q_list))
            time.sleep(2)

    def start_p(self):
        self.assembler.start()
        # self.assembler.join()

class Execute:

    def __init__(self, pipe):
        self.pipe = pipe
        self.executor = Process(target=self.execute_q, name='framework_executor', args=())
        self.e_q_list = []

    def execute_q(self):
        threads_2 = []
        t3 = threading.Thread(target=self.thred_3, args=())
        threads_2.append(t3)
        t4 = threading.Thread(target=self.thred_4, args=())
        threads_2.append(t4)
        for tt in threads_2:
            tt.setDaemon(True)
            tt.start()
            # t.join()
        tt.join()
        print(" [process1]all thread finish at %s" % ctime())


    def thred_3(self):
        while not False:
            receive = self.pipe.recv()
            print("[thred_3] receive: {}".format(receive))
            self.e_q_list.append(receive)
            print('[thred_3] append {} to e_q_list'.format(receive))
            print('[thred_3] e_q_list now is {}'.format(self.e_q_list))
            time.sleep(1)

    def thred_4(self):
        while True:
            time.sleep(1)
            l = self.e_q_list[:]
            print('[thred_4] e_q_list now is {}'.format(self.e_q_list))
            if l:
                print('[thred_4] now is execute {}'.format(l[0]))
                self.e_q_list.remove(l[0])
                print("[thred_4] remove {} from a_q_list".format(l[0]))
            print('[thred_4] e_q_list now is {}'.format(self.e_q_list))
            time.sleep(2)

    def start_e(self):
        self.executor.start()
        # self.executor.join()

if __name__ == '__main__':

    print("Main process id is: {mpid}".format(mpid=os.getpid()), time.asctime())
    pipe = Pipe()
    # -----------------------------------------
    c = Configuration()
    c.start_c()
    print('c_pid is :', c.config.pid, 'start at :', time.asctime())
    # -----------------------------------------
    a = Assemblr(pipe[0])
    a.start_p()
    print('a_pid is :', a.assembler.pid, 'start at :', time.asctime())
    # -----------------------------------------
    e = Execute(pipe[1])
    e.start_e()
    print('e_pid is :', e.executor.pid, 'start at :', time.asctime())
