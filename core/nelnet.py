# python3!

from time import time, sleep
from PyQt5.QtCore import pyqtSlot, QVariant

try:
    from nmmp.logger import NLogger
except ImportError:
    # This part is ONLY required to run when the module is NOT installed
    import os
    import sys
    cmd_subfolder = os.path.abspath(
        os.path.join( os.path.dirname( __file__ ), ".." ) )
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    from nmmp.logger import NLogger

from nmmp.classinterfaces import NClassesInterface
from nmmp.net.netlayer import NNetworkLayer
from nmmp.mac.datalinklayer import NDataLinkLayer
from nmmp.hal.executor import NHALExecutor


# -----------------------------------------------------------------------------


class NClient(NClassesInterface):
    """docstring for NClient"""

    def __init__(self, name, ip, mac32, parent=None):
        """  """
        super(NClient, self).__init__(parent)
        self._name = name
        self._ip = ip
        self._mac32 = mac32

    def __str__(self):
        """ """
        return '"%s (%s)"' % (self._name, self.__class__.__name__)

    @property
    def name(self):
        return self._name

    @property
    def ip(self):
        return self._ip

    @property
    def mac32(self):
        return self._mac32

    @pyqtSlot( QVariant, bytearray )
    def _recive_slot(self, frame_id, data):
        """ """
        pass

    @pyqtSlot( QVariant, str )
    def _timeout_slot(self, frame_id, msg):
        """ """
        pass

    @pyqtSlot( QVariant, str )
    def _error_slot(self, frame_id, msg):
        """ """
        pass


# -----------------------------------------------------------------------------


class NELnetHALExecutor(NHALExecutor):
    """docstring for NELnetHALExecutor"""

    def start(self, **kwargs):
        self.ex_start_op(**kwargs)
        self.join()


# -----------------------------------------------------------------------------


class NELnetServer(NClassesInterface):
    """docstring for NELnetServer"""

    def __init__(self, executor, **kwargs):
        """ Constructor """
        super(NELnetServer, self).__init__()

        self._hal_executor = executor

        # ---
        self._name = kwargs.get('name', 'NELnet Server instance')
        self._ip = kwargs.get('ip', 0x0000)
        self._mac = kwargs.get('mac', 0x00000000)

        qconntype = kwargs.get('qconntype', 'DirectConnection')

        # construct NELnet network layer
        self._netlayer = NNetworkLayer( self._ip )
        # construct NELnet datalink layer
        self._datalinklayer = NDataLinkLayer( self._mac )

        # --- connect signals/slots
        NClassesInterface.connect(
            [ self, self._netlayer, self._datalinklayer, self._hal_executor ],
            qconntype
        )

    def __str__(self):
        """ """
        return '"%s (%s)"' % (self._name, self.__class__.__name__)

    @property
    def name(self):
        return self._name

    @property
    def ip(self):
        return self._ip

    @property
    def mac(self):
        return self._mac

    @property
    def hal_executor(self):
        return self._hal_executor

    # --- self operation methods

    @NLogger.wrap('DEBUG')
    def start(self, **kwargs):
        """  """
        # emit start operate signal
        self.operation_putlow_signal.emit(
            'net_start',
            kwargs
        )

    @NLogger.wrap('DEBUG')
    def send(self, reciver_mac, reciver_ip, data):
        """ """
        self.operation_putlow_signal.emit(
            'net_send',
            {
                'reciver_mac': reciver_mac,
                'reciver_ip': reciver_ip,
                'data': data
            }
        )

    @NLogger.wrap('DEBUG')
    def recive(self, timeout_ms):
        """ """
        self.operation_putlow_signal.emit(
            'net_recive', { 'timeout_ms': timeout_ms }
        )

    # --- NClassesInterface operation methods

    @NLogger.wrap('DEBUG')
    def net_read_op(self, **kwargs):
        """ """
        pass

    @NLogger.wrap('WARN')
    def net_read_timeout_op(self, **kwargs):
        """ """
        pass

    @NLogger.wrap('ERROR')
    def net_error_op(self, **kwargs):
        """ """
        pass


# -----------------------------------------------------------------------------

import threading
import queue

class NuDHCP_Server(NELnetServer):
    """docstring for NuDHCP_Server"""

    def __init__(self, executor, **kwargs):
        """ Constructor """
        super(NuDHCP_Server, self).__init__(executor, **kwargs)

        self._taskqueue = queue.Queue()
        #
        t = threading.Thread(target=self._worker)
        t.daemon = True
        t.start()

    # ---

    def _worker(self):
        """  """
        sleep(0.1)

    # ---

    def _datagramm_serialize(client, datagramm_type):
        pass

        # # /* DPV  [ PROTOCOL VERSION ] */
        # client->txfer[0] = client->datagramm.protocol_version.bytes[0];
        # client->txfer[1] = client->datagramm.protocol_version.bytes[1];
        # # /* DRT  [ REQUEST TYPE ] */
        # client->datagramm.type = type;
        # client->txfer[2] = type;
        # # /* SID  [ TRANSACTION ID ] */
        # memcpy( &client->txfer[3], client->datagramm.session_id.bytes, 4 );
        # # /* SMAC  [ SERVER MAC ] */
        # memcpy( &client->txfer[7], client->datagramm.server_mac.bytes, 4 );
        # # /* CMAC  [ CLIENT MAC ] */
        # memcpy( &client->txfer[11], client->datagramm.client_mac.bytes, 4 );
        # # /* OPT  [ OPTIONS ] */
        # memcpy( &client->txfer[15], client->datagramm.options, 16 );
        # # /* CRC calculs */
        # client->txfer[31] = nmmp_crc_buffer( client->txfer, 31 );

        # return True


    def _datagramm_deserialize(client, data):
        pass

        # # /* CRC verify */
        # if ( nmmp_crc_buffer( data, 31 ) != data[31] ) {
        #     return NMMP_ERROR;
        # }

        # # /* DPV  [ PROTOCOL VERSION ] */
        # client->datagramm.protocol_version.bytes[0] = data[0];
        # client->datagramm.protocol_version.bytes[1] = data[1];

        # # /* Protocol version verify */
        # if ( client->datagramm.protocol_version.word != __UDHCP_PROTOCOL_VERSION__ ) {
        #     return NMMP_ERROR;
        # }

        # # /* DRT  [ REQUEST TYPE ] */
        # client->datagramm.type = data[2];
        # # /* SID  [ TRANSACTION ID ] */
        # memcpy( client->datagramm.session_id.bytes, &data[3], 4 );
        # # /* SMAC  [ SERVER MAC ] */
        # memcpy( client->datagramm.server_mac.bytes, &data[7], 4 );
        # # /* CMAC  [ CLIENT MAC ] */
        # memcpy( client->datagramm.client_mac.bytes, &data[11], 4 );
        # # /* OPT  [ OPTIONS ] */
        # memcpy( client->datagramm.options, &data[15], 16 );

        # # /* */
        # memcpy( client->rxfer, data, 32 );
        # # /* */
        # return NMMP_OK;


    # --- NClassesInterface operation methods

    @NLogger.wrap('DEBUG')
    def net_read_op(self, **kwargs):
        """ """
        sender_ip = kwargs.get('sender_ip', 0xEA60)
        sender_mac = kwargs.get('sender_mac', 0xFFFFFFFF)
        data = kwargs.get('data', bytearray)

        if sender_ip == 0xEA60 and sender_mac == 0xFFFFFFFF:
            #
            nelnet.send( 0xFFFFFFFF, 0xEA60, bytearray( [0x00] + [int(0x00) for g in range(4)] ) )

    @NLogger.wrap('WARN')
    def net_read_timeout_op(self, **kwargs):
        """ """
        pass

    @NLogger.wrap('ERROR')
    def net_error_op(self, **kwargs):
        """ """
        pass


# -----------------------------------------------------------------------------


def _nelnet_test():
    """ """
    from time import time, sleep
    from nmmp.hal.vcom_usart import NQSerial

    loglevel = 'DEBUG'
    # create 'main' logger
    mainlogger = NLogger.init('__main__', loglevel)

    mainlogger.info( 'Create NELNet server instance object' )

    hal_executor = NELnetHALExecutor()

    nelnet = NuDHCP_Server(
        hal_executor,
        name='Droid NELnet Server',
        ip=0xEA60,
        mac32=0xFFFFFFFF,
        qconntype='DirectConnection'
        # qconntype='QueuedConnection'
    )

    # --- create loggers
    nelnet.logger = NLogger.init('NELnet uDHCP Server', loglevel)
    # nelnet._netlayer.logger = NLogger.init('Network', loglevel)
    # nelnet._datalinklayer.logger = NLogger.init('Datalink', loglevel)

    # hal_executor.logger = NLogger.init('TransactionManager', loglevel)

    mainlogger.info( 'Start NQSerial HAL interface' )

    # --- start server with respect HAL
    hal_executor.start(
        hal = NQSerial,
        name = 'CP210x',
        baud = 921600
    )



    # for x in range(1,10):
    #     nelnet.send( 0x00000010, 0x01, bytearray( [0x00] + [int(0x00) for g in range(4)] ) )
    #     hal_executor.join()

    # # --- test mac/ip and packet
    # remote_mac = 0x00000010
    # remote_ip = 0x01
    # packet = bytearray( [0x00] + [int(0x00) for g in range(4)] )
    # #
    # packets_cnt = 100

    # # ---
    # mainlogger.info('Put to MAC/IP - 0x%08X - 0x%X' % (remote_mac, remote_ip))
    # mainlogger.info('Transaction count - %s' % packets_cnt)
    # mainlogger.info('Test data packed - %s' % [ hex(b) for b in packet ])

    # # ---
    # ts = time()
    # mainlogger.info('START sending on %.2g sec ...' % ts)

    # for x in range(0, packets_cnt):
    #     nelnet.send( remote_mac, remote_ip, packet )

    # mainlogger.info('Wait while processing all packets...')

    # nelnet.tr_manager.join()

    # # ---
    # ts = time()-ts
    # one_packet = ts*1000/packets_cnt
    # mainlogger.info( 'One transaction average time %.4g msec' % one_packet )
    # mainlogger.info( 'Average transaction/sec - %d' % (1000/one_packet) )
    # mainlogger.info( 'DONE - work time is %.4g sec - %s' % (ts, '# --- '*20))


if __name__ == '__main__':
    _nelnet_test()
