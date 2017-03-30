import time

class ClockSpawner(object):
    def __init__(self, thours, func, *args):
        self.func = func
        self.func_args = args
        self.thours = thours

    def __convert_hours_sec(self, thours):
        return (thours * 60) * 60

    def __counter(self):
        cur = 0
        tsecs = self.__convert_hours_sec(self.thours)
        while True:
            time.sleep(1)
            cur += 1
            if cur >= tsecs:
                break
            if cur >= (tsecs / 2): # TODO, prevent overflow
                tsecs -= (tsecs / 2)
                cur = 0
        return True

    def run(self):
        if self.thours <= 0:
            return
        if self.__counter():
            return self.func(*self.func_args)
        return False

if __name__ == "__main__":
    def dummy(a, b):
        print a, b
    ClockSpawner(0.00277778, dummy, "A!", "B!").run() # 10 sec
