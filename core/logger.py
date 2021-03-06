

import time
import logging
import logging.config


class NLogger(object):
    """docstring for NLogger"""

    OK = [True]
    ERR = [False]

    loglevels = ['debug','info', 'warning', 'error']

    @staticmethod
    def init(name, level):
        """ """

        level = logging.__dict__[level]

        logger = logging.getLogger(name)
        logger.setLevel(level)
        # create file handler which logs even debug messages
        # fh = logging.FileHandler('nelnet.log')
        # fh.setLevel(level)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(level)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(
                fmt='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S',
        )
        # fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # add the handlers to the logger
        # logger.addHandler(fh)
        logger.addHandler(ch)
        #
        return logger

    @staticmethod
    def deinit(inobject):
        """ """
        if 'logger' in inobject.__dict__:
            inobject.logger = None

    def wrap(lvl='INFO'):
        """ logging decorator maker """
        def logdec(func):
            def wrapper(self, *argv, **kwargv):
                """  """

                res = func(self, *argv, **kwargv)

                if 'logger' not in self.__dict__ or self.logger is None:
                    return res

                level = lvl

                msg = ', '.join([str(a) for a in argv])
                msg += ' | ' + ', '.join(['%s=%s' % (str(a), kwargv[a]) for a in kwargv])
                msg = '"%s"  -  %s (in)  -  %s (out)' % ( func.__name__, str(msg), str(res) )

                if res in NLogger.ERR or level == 'ERROR':
                    msg = ' [ ERROR ]  %s' % msg
                    level = 'ERROR'
                else:
                    msg = ' [ OK ]  %s' % msg

                msg = msg.replace('\r\n', '')
                level = level.lower()

                if level in NLogger.loglevels:
                    putlog = getattr(self.logger, level)
                    putlog(msg)

                return res
            return wrapper
        return logdec


if __name__ == '__main__':

    class TestObj(object):
        def __init__(self):
            pass

        @NLogger.wrap('DEBUG')
        def foo(self, data):
            if data:
                return ''.join(str(data))

        @NLogger.wrap('DEBUG')
        def foo2(self, data):
            if data:
                return False
            return 'ALARM!'

    test_obj = TestObj()
    test_obj.logger = NLogger.init('test log', 'DEBUG')

    test_obj.logger.debug('debug test message')

    test_obj.foo(None)
    test_obj.foo([0x00, 0x01])

    test_obj.foo2(None)
    test_obj.foo2([0x00, 0x01])
