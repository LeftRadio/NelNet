# python3!

try:
    from nmmp.logger import NLogger
except ImportError:
    # This part is only required to run
    # when the module itself is not installed.
    import os, sys
    cmd_subfolder = os.path.abspath(
        os.path.join( os.path.dirname( __file__ ), "../.." ) )
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    from nmmp.logger import NLogger


class NHalInterfaceBase(object):
    """docstring for NHalInterfaceBase"""

    def __str__(self):
        """ """
        return self.__class__.__name__

    def create_logger(self, name, level):
        """ create logger """
        self.logger = NLogger.init(name, level)

    def destroy_logger(self):
        """ create logger """
        self.logger = None

    def vidpid(self, dev):
        """ return 'vid'/'pid' 16 bit values """
        vid = 0x10C4
        pid = 0x8693
        return ( vid, pid )

    def port(self, description):
        """ return device hal name from 'frendly' description string,
            'frendly' description usually provided from high level,
            for example 'CP210x' description may be hide 'COM3' port name """
        return ''

    def description(self, portname):
        """ return device description string """
        return 'base virtual device'

    def config(self, **kwargs):
        """ configurate device """
        pass

    def open(self):
        """ open hal port """
        return False

    def close(self):
        """ close hal port """
        return False

    def flush_bufers(self):
        """ flush tx/rx buffers """
        pass

    def write(self, data, timeout):
        """ non blocking write to device,
            timeout off if set to 0 """
        pass

    def read(self, timeout):
        """ non blocking write to device,
            timeout off if set to 0 """
        pass
