


class Task:
    def __init__(self, name, need_build=True):
        self._script_list = []
        self._exe_list = []
        self._uut_list = []
        self._id = 0
        self._name = name
        self._status = ''
        self._state = ''
        self._need_build = need_build

    def insert_script(self, script):
        # set scripts
        self._script_list.append(script)

    def get_script(self, name):
        # get scripts
        for script in self._script_list:
            if script.name == name:
                return script

    def get_script_list(self):
        # get scripts
        return self._script_list

    def insert_exe_list(self, file):
        self._exe_list.append(file)

    def get_exe(self, name):
        pass

    def get_exe_list(self):
        return self._exe_list

    def insert_uut_list(self, uut):
        self._uut_list.append(uut)

    def get_uut(self, name):
        pass

    def get_uut_list(self):
        return self._uut_list

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def get_status(self):
        return self._status

    def get_state(self):
        return self._state

