# python3!

from PyQt5.QtCore import QObject, QIODevice, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtCore import QCoreApplication, QMutexLocker, QMutex, QThread, QWaitCondition, QVariant
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow

try:
    from nmmp.logger import NLogger
except ImportError:
    # This part is only required to run
    # when the module itself is not installed.
    import os, sys
    cmd_subfolder = os.path.abspath(
        os.path.join( os.path.dirname( __file__ ), "../.." ) )
    if cmd_subfolder not in sys.path:
        sys.path.append(cmd_subfolder)
    from nmmp.logger import NLogger

from nmmp.hal.interface import NHalInterfaceBase


# Interfase class ------------------------------------------------------------

class NQSerial(QSerialPort, NHalInterfaceBase):
    """docstring for QSerialInterface"""

    read_async_signal = pyqtSignal( bytearray )

    def __init__(self, **kwargs):
        """constructor"""
        super(NQSerial, self).__init__()
        super(NHalInterfaceBase, self).__init__()

        # create Qt application for correct working QTimer
        self.app = QCoreApplication([])

        self.read_async_signal = self.readyRead

        # self.logger = NLogger.init('NQSerial', 'DEBUG')

        # create def serial device
        self.config(**kwargs)

    @NLogger.wrap('DEBUG')
    def device(self, name):
        """ Reimplement NHalInterfaceBase.device() method. """
        ports = QSerialPortInfo.availablePorts()
        ports = list( filter(lambda x: str(name) in x.description(), ports) )
        if len(ports):
            return ports[0].portName()
        return None

    @NLogger.wrap('DEBUG')
    def config(self, info=None, **kwargs):
        """ Reimplement NHalInterfaceBase.config() method.
            Configurate baudrate and timeouts for work with USART. """

        # get port name for provided device name
        dev_name = kwargs.get('name', self.portName())
        port_name = self.device( dev_name )
        if port_name is None:
            raise RuntimeError('Device "%s" not found!' % dev_name)

        # set port configuration
        if isinstance(info, QSerialPortInfo):
            info.setPortName(port_name)
            self.setPort(info)
        else:
            self.setPortName( port_name )
            self.setBaudRate( kwargs.get('baud', 115200) )
            self.setDataBits( kwargs.get('databit', 8) )
            self.setParity( kwargs.get('parity', self.parity()) )
            self.setStopBits( kwargs.get('stopbit', self.stopBits() ) )
            self.setFlowControl( kwargs.get('flow', self.flowControl()) )

        return True

    @NLogger.wrap('DEBUG')
    def open(self):
        """ Reimplement NHalInterfaceBase.open() method. """
        if not self.isOpen():
            return super().open(QIODevice.ReadWrite)
        return True

    @NLogger.wrap('DEBUG')
    def flush_bufers(self):
        """ Reimplement NHalInterfaceBase.flush_bufers() method. """
        super().readAll().data()

    @NLogger.wrap('DEBUG')
    def write(self, data, timeout):
        """ Reimplement NHalInterfaceBase.write() method. """
        self.writeData(data)
        return self.waitForBytesWritten(timeout)

    @NLogger.wrap('DEBUG')
    def read(self, timeout):
        """ Reimplement NHalInterfaceBase.read() method. """
        # read input data
        if self.waitForReadyRead(timeout):
            # read input data
            raw = self.readAll().data()
            while self.bytesAvailable():
                raw.extend( self.readAll().data() )
            return raw


# Self test -------------------------------------------------------------------


def _vcom_test():
    # from time import sleep
    from nmmp.classinterfaces import NClassesInterface
    from nmmp.hal.executor import NHALExecutor

    class DataLinkTest(NClassesInterface):
        """docstring for DataLinkTest"""
        def __init__(self, **kwargs):
            super(DataLinkTest, self).__init__()

            # --- construct NELnet transaction manager
            self.tmanager = NHALExecutor()

            # --- connect to NHALExecutor
            conntype = kwargs.get('connect', 'DirectConnection')
            NClassesInterface.connect( [self, self.tmanager], conntype )

            # --- create loggers
            loglevel = kwargs.get('loglevel', None)
            if loglevel:
                self.logger = NLogger.init('DataLinkTest', loglevel)
                self.tmanager.logger = NLogger.init('NHALExecutor', loglevel)

            self.join = self.tmanager.join

        @NLogger.wrap('DEBUG')
        def start(self, **kwargs):
            #
            self.operation_putlow_signal.emit('tr_start', kwargs)

        @NLogger.wrap('DEBUG')
        def send(self, data, frame_id, timeout_ms):
            msgd = {
                'frame': data,
                'frame_id': frame_id,
                'timeout_ms': timeout_ms
            }
            self.operation_putlow_signal.emit('transaction', msgd)

        # NHalInterfaceBase ---------------------------------------------------

        @NLogger.wrap('DEBUG')
        def tr_read_op(self, **kwargs):
            return False

        @NLogger.wrap('ERROR')
        def tr_read_timeout_op(self, **kwargs):
            return False

        @NLogger.wrap('DEBUG')
        def tr_error_op(self, **kwargs):
            return False

    # create DataLinkTest instance object
    datalink = DataLinkTest( connect='DirectConnection', loglevel='DEBUG' )

    # start with NQSerial HAL interface
    datalink.start( hal=NQSerial, name='CP210x', baud=921600 )

    # --- test send sequences
    transaction_cnt = 10

    print('-'*10 + ' initiate [ %s ] transactions in loop' % transaction_cnt)

    data = bytearray( [0x00] + [int(0x00) for g in range(4)] )
    frame_id = 0x13013013
    timeout_ms = 10

    for x in range(0, transaction_cnt):
        datalink.send( data, frame_id, timeout_ms )

    # ---
    # sleeptime = transaction_cnt * timeout_ms / 2000
    # print('SLEEP ON %s SEC  %s' % (sleeptime, '--- - '*20))
    # sleep(sleeptime)
    # print('WAKEUP!  %s' % ('--- + '*20))
    datalink.join()
    print('EXIT  %s' % ('# --- '*20))


if __name__ == '__main__':

    from multiprocessing import Process
    Process(target=_vcom_test).start()

    for x in range(100):
        print('# --- '*20)
