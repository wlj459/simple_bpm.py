class ExecutionManager(object):

    def __init__(self, task_id):
        self.task_id = task_id
        self.__namespace = {}

    def __getitem__(self, item):
        if item in self.__namespace:
            return self.__namespace[item]

    def __execute(self):
        pass

    @property
    def succeeded(self):
        return True
