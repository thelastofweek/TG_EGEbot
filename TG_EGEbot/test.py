class Test:
    def __init__(self, subject, user_id):
        self.subject = subject
        self.user_id = user_id
        self.tasks = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.actual_task = 0
    
    def next_task(self):
        if len(self.tasks) - 1 > self.actual_task:
            self.actual_task += 1
            return True
        return False
    
    def previous_task(self):
        if 0 < self.actual_task:
            self.actual_task -= 1
            return True
        return False
    
    def get_task(self):
        return 'task'
    
    def finish_test(self):
        # останавливаем таймер, записываем все данные в бд, сохраняем, выводим результат экза
        pass


# test = Test('inf', '398895918')
# test.get_task()
