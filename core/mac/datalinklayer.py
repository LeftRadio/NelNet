# python3!

import threading
import queue

try:
    from nmmp.logger import NLogger
except ImportError:
    # This part is only required to run
    # when the module itself is not installed.
    import os
    import sys
    cmd_subfolder = os.path.abspath(
        os.path.join( os.path.dirname( __file__ ), "../.." ) )
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    from nmmp.logger import NLogger

from nmmp.classinterfaces import NClassesInterface
from nmmp.mac.dl_stmachine import DL_RX_StateMachine
from nmmp.crc8 import ncrc8_buf
from nmmp.constants import datalink_start_frame_byte as dl_sf_byte
from nmmp.constants import link_headers_len


# -----------------------------------------------------------------------------


class NMicroDHCP(object):
    """docstring for NMicroDHCP"""
    def __init__(self):
        super(NMicroDHCP, self).__init__()

        self._queue = queue.Queue()
        self.join = self._queue.join
        #
        t = threading.Thread(target=self._worker)
        t.daemon = True
        t.start()

    def _worker(self):
        """ """
        while True:
            # get
            item, data = self._queue.get()
            #
            with threading.Lock():

                if item == 'new client start':
                    pass

            self._queue.task_done()

    def start_new_client(self, packet):
        """ """
        self._queue.put( ('new client start', packet) )


class NDataLinkLayer(NClassesInterface):
    """docstring for NDataLinkLayer"""

    def __init__(self, mac32=0x00000000):
        """ create object """
        super(NDataLinkLayer, self).__init__()
        # self mac address
        self._mac32 = mac32
        #
        self._remote_clients = [0x00000010]
        # create recive state machine
        self._rx_statemachine = DL_RX_StateMachine()
        #
        self._mdhcp = NMicroDHCP()

    def _frame_packet_c(self, reciver_mac, sender_mac, data):
        # --- get lenghts
        data_len = len(data)
        cindata = ( c_ubyte * data_len )(*data)
        out = ( c_ubyte * (DATALINK_HEADER_LEN + data_len) )()
        addr_out = addressof(out)

        # --- create and fill bytes buffer
        # out = bytearray( DATALINK_HEADER_LEN + data_len )

        # start frame byte
        out[0] = c_ubyte(dl_sf_byte)

        # copy mac address
        rmac = reciver_mac.to_bytes( 4, byteorder='little' )
        memmove( addr_out + 1, rmac, 4 )
        smac = sender_mac.to_bytes( 4, byteorder='little' )
        memmove( addr_out + 5, smac, 4 )

        # calc CRC byte
        out[9] = ncrc8_buf_c_win( cindata, c_int(data_len) )

        # two data lenght bytes, normal and invert
        out[10] = c_ubyte(data_len)
        out[11] = c_ubyte((~data_len) & 0xFF)

        # copy data
        memmove( addr_out + DATALINK_HEADER_LEN, cindata, data_len )

        # return result frame buffer
        return bytearray(out)

    def _frame_packet(self, reciver_mac, sender_mac, data):
        """ Create nmmp datalink layer frame packet """
        # --- get lenghts
        data_len = len(data)
        # datalink header len
        dl_header_len = link_headers_len['datalink']

        # --- create and fill bytes buffer
        out = bytearray( dl_header_len + data_len )
        # start frame byte
        out[0] = dl_sf_byte
        # copy mac address
        out[1:4] = reciver_mac.to_bytes( 4, byteorder='little' )
        # copy mac address
        out[5:8] = sender_mac.to_bytes( 4, byteorder='little' )
        # calc CRC byte
        out[9] = ncrc8_buf(data)
        # two data lenght bytes, normal and invert
        out[10] = data_len
        out[11] = (~data_len) & 0xFF
        # copy data
        out[dl_header_len:] = data

        # return result frame buffer
        return out

    @NLogger.wrap('DEBUG')
    def dl_start_op(self, **kwargs):
        """ """
        self.operation_putlow_signal.emit(
            'ex_start',
            kwargs
        )

    @NLogger.wrap('DEBUG')
    def dl_send_op(self, **kwargs):
        """ Send packet to device """

        reciver_mac = kwargs.pop('reciver_mac', None)

        # --- format datalink frame
        data = kwargs.pop('data', bytearray())
        kwargs['frame'] = self._frame_packet( reciver_mac, self._mac32, data )
        kwargs['timeout_ms'] = 50
        # send operation emit
        self.operation_putlow_signal.emit('ex_transaction', kwargs)

    @NLogger.wrap('DEBUG')
    def dl_recive_op(self, **kwargs):
        """ """
        self.operation_putlow_signal.emit(
            'ex_recive', kwargs
        )

    @NLogger.wrap('DEBUG')
    def ex_read_op(self, **kwargs):
        """ """
        data = kwargs.get('data', None)
        if data is not None:
            # put data to frame compare maschine
            packets = self._rx_statemachine.update( data )
            #
            for reciver_mac, sender_mac, packet in packets:

                # ! broadcast packet
                if reciver_mac == 0xFFFFFFFF:
                    # if new device try connect to us
                    if sender_mac & 0xFF000000:

                        if self._mdhcp.started is False:
                            # microDHCP service start
                            self._mdhcp.start_new_client(packet)

                        else:
                            # wait while end of config
                            self._mdhcp._continue()

                        #
                        if self._mdhcp.complite is True:
                            #
                            self._register_new_mac()
                            self._mdhcp.stop()

                        #
                        print('broadcast packet end')
                        return

                # emit recive complite layer signal
                kwargs['data'] = packet
                kwargs['sender_mac'] = sender_mac
                # timeout operation emit
                self.operation_puthigh_signal.emit(
                    'dl_read',
                    kwargs
                )

    @NLogger.wrap('WARN')
    def ex_read_timeout_op(self, **kwargs):
        """ """
        # timeout operation emit
        self.operation_puthigh_signal.emit(
            'dl_read_timeout',
            kwargs
        )

    @NLogger.wrap('ERROR')
    def ex_error_op(self, **kwargs):
        """ """
        self.operation_puthigh_signal.emit(
            'dl_error',
            kwargs
        )
