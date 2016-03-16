import time, logging, datetime

class Timer():

    def __init__(self, log_name, log_level='info'):

        self.__log = logging.getLogger(log_name)
        self.__log_level = log_level

    def start(self, msg):

        if self.__log_level == 'info':
            self.__log.info(msg)
        else:
            self.__log.debug(msg)

        self.start_time = time.perf_counter()

    def stop(self, msg='%s'):

        self.elapsed = time.perf_counter() - self.start_time
        print(self.elapsed)
        fmt = datetime.timedelta(seconds=self.elapsed)

        if self.__log_level == 'info':
            self.__log.info(msg % fmt)
        else:
            self.__log.debug(msg % fmt)

        