

class Queue:
    def __init__(self):
        self._task_list = []

    def insert_task(self, index=-1, task=''):
        self._task_list.insert(index, task)

    def remove_task(self, task):
        self._task_list.remove(task)

    def set_order(self, index, task):
        pass

    def clear(self):
        self._task_list = []

    def get_task_list(self):
        return self._task_list