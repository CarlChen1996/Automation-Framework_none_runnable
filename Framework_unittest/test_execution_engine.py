from Framework_Kernel import execution_engine
from Framework_Kernel.task import Task
from multiprocessing import Pipe
from unittest.mock import patch
import unittest


'''
setUp: Instantiated pipe and send task, instantiated Execution Engine
test_1_add_task_to_execution: when add task to queue in Execution Engine, insert_task can be called
test_2_add_task_to_execution: add task to execution queue after pipe receive task
test_3_send_signal: Execution Engine can send signal after pipe receive task
'''


class ExecutionEngineTest(unittest.TestCase):
    def setUp(self):
        self.pipe = Pipe()
        deploy_list = []
        self.execution = execution_engine.ExecutionEngine(deploy_list, self.pipe[0])
        self.task = Task(name='task_1')
        self.pipe[1].send(self.task)

    @patch('Framework_Kernel.queue_task.Queue.insert_task')
    def test_1_add_task_to_execution(self, insert_task):
        self.execution.insert_task_to_queue()
        insert_task.assert_called_once()

    def test_2_add_task_to_execution(self):
        self.assertEqual(self.execution.execution_queue.get_task_list(), [])
        self.execution.insert_task_to_queue()
        self.assertEqual(self.execution.execution_queue.get_task_list()[0].get_name(), 'task_1')

    def test_3_send_signal(self):
        self.execution.insert_task_to_queue()
        self.assertEqual(self.pipe[1].recv(), 'task_1')


if __name__ == '__main__':
    unittest.main()
