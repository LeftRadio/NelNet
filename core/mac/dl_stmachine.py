
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

from nmmp.crc8 import ncrc8_buf
from nmmp.constants import datalink_start_frame_byte as dl_sf_byte


class DL_RX_StateMachine(object):
    """docstring for NMMP_DL_RX_StateMachine"""

    rx_default = 0
    rx_mac = 1
    rx_crc = 2,
    rx_len = 3,
    rx_len_inv = 4,
    rx_data = 5,
    rx_complite = 6,
    rx_error = False

    def __init__(self):
        """ """
        #
        self._reciver_mac = 0x00000000
        self._sender_mac = 0x00000000
        # self reset to default
        self.reset()

    @NLogger.wrap('DEBUG')
    def reset(self):
        self._read_macbuf = bytearray()
        self._read_maccnt = 0
        self._read_crc = 0
        self._read_len = 0
        self._read_data = bytearray()
        self._read_cnt = 0
        self._state = DL_RX_StateMachine.rx_default
        return True

    @NLogger.wrap('DEBUG')
    def _byte_next(self, state, byte):
        """ serial datalink input state machine """

        # Start frame byte, datalink_start_frame_byte expected
        if state == DL_RX_StateMachine.rx_default and byte == dl_sf_byte:
            # return next state
            return DL_RX_StateMachine.rx_mac

        # MAC ADDRESS byte, range 0x00000000 - 0xFFFFFFF0 expected
        if state == DL_RX_StateMachine.rx_mac:
            # collect
            self._read_macbuf.append( byte )
            self._read_maccnt += 1
            # complite, verify recived mac address
            if self._read_maccnt > 7:
                reciver_mac = int.from_bytes( self._read_macbuf[:3],
                                              byteorder='little' )
                sender_mac = int.from_bytes( self._read_macbuf[4:],
                                             byteorder='little' )
                #
                self._reciver_mac = reciver_mac
                self._sender_mac = sender_mac
                return DL_RX_StateMachine.rx_crc

            else:
                return DL_RX_StateMachine.rx_mac

        # CRC byte
        if state == DL_RX_StateMachine.rx_crc:
            # store CRC byte
            self._read_crc = byte
            # return next state
            return DL_RX_StateMachine.rx_len

        # RX data lenght
        if state == DL_RX_StateMachine.rx_len:
            self._read_len = byte
            # return next state
            return DL_RX_StateMachine.rx_len_inv

        # invert RX data lenght
        if state == DL_RX_StateMachine.rx_len_inv:
            if self._read_len == ~byte & 0xFF:
                return DL_RX_StateMachine.rx_data

        if state == DL_RX_StateMachine.rx_data:
            # collecting data
            self._read_data.append(byte)
            self._read_cnt += 1

            # if collecting all data bytes is complite */
            if self._read_cnt >= self._read_len:
                # verify CRC and return next state if OK
                if self._read_crc == ncrc8_buf( self._read_data ):
                    return DL_RX_StateMachine.rx_complite
            else:

                return DL_RX_StateMachine.rx_data

        # some errors happened, reset state maschine
        self.reset()
        # return error state
        return DL_RX_StateMachine.rx_error

    @NLogger.wrap('DEBUG')
    def update(self, bytes):
        """ """
        frames = []

        # put all bytes to nmmp datalink recive state machine
        for b in bytes:

            self._state = self._byte_next( self._state, b )

            # if valid frame recived
            if self._state == DL_RX_StateMachine.rx_complite:
                # store recived frame
                frames.append(
                    (self._reciver_mac, self._sender_mac, self._read_data)
                )
                # reset state
                self.reset()

        return frames


# --- self test
if __name__ == '__main__':

    from time import sleep

    #
    rx_statemachine = DL_RX_StateMachine()
    #
    rx_statemachine.logger = NLogger.init( 'DL_RX_StateMachine', 'INFO' )

    # ---
    dl_frame = [ 0x5B ]

    data = [ 0x00, 0xBB, 0xEE ]

    # reciver mac addr
    dl_frame.extend( [ 0x15, 0x00, 0x00, 0x00 ] )
    # sender mac addr
    dl_frame.extend( [ 0xA0, 0x00, 0x00, 0x00 ] )
    # crc
    dl_frame.append( ncrc8_buf( data ) )
    # lenght
    dl_frame.append( 0x03 )
    # invert lenght
    dl_frame.append( (~0x03) & 0xFF )
    # data
    dl_frame.extend( data )

    # ---
    frames_count = 7
    #
    in_raw_data = []
    #
    for x in range(0, frames_count):
        in_raw_data.extend(dl_frame)
    #
    complite_frames = rx_statemachine.update(
        0x00000015,
        bytearray(in_raw_data) )
    #
    rx_statemachine.logger.info(
        'Success decoded [ %s ] frames' % len(complite_frames) )

    sleep(0.5)

    # ---
    complite_frames = []
    splitlen = 4
    #
    for x in range(0, len(in_raw_data), splitlen):
        complite_frames.extend(
            rx_statemachine.update(
                0x00000015, bytearray( in_raw_data[ x:x+splitlen ] )
            )
        )
    #
    rx_statemachine.logger.info(
        'Success decoded [ %s ] splited frames' % len(complite_frames) )
