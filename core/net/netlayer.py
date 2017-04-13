# python3!

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
from nmmp.constants import link_headers_len


# -----------------------------------------------------------------------------


class NNetworkLayer(NClassesInterface):
    """docstring for NNetworkLayer"""
    def __init__(self, ip=0x00):
        """ create object """
        super(NNetworkLayer, self).__init__()
        #
        self.header_len = link_headers_len['network']
        self._ip = ip

    @property
    def ip(self):
        return self._ip

    def _packed_serialize(self, reciver_ip, sender_ip, data):
        """ """
        out = bytearray(self.header_len)
        #
        out[0] = (reciver_ip) & 0xFF
        out[1] = (reciver_ip >> 8) & 0xFF
        #
        out[2] = (sender_ip) & 0xFF
        out[3] = (sender_ip >> 8) & 0xFF
        #
        out.extend( bytearray(data) )
        return out

    def _packet_deserialize(self, packet):
        """  """
        #
        reciver_ip = packet[1] << 8
        reciver_ip |= packet[0]
        #
        sender_ip = packet[2]
        sender_ip |= packet[3] << 8
        #
        return (reciver_ip, sender_ip, packet[self.header_len:])

    @NLogger.wrap('DEBUG')
    def net_start_op(self, **kwargs):
        """ """
        self.operation_putlow_signal.emit(
            'dl_start',
            kwargs
        )

    @NLogger.wrap('DEBUG')
    def net_send_op(self, **kwargs):
        """ Send packet to device """
        # format packet
        reciver_mac = kwargs.get('reciver_mac', 0x00)
        reciver_ip = kwargs.get('reciver_ip', 0x00)
        data = kwargs.get('data', bytearray())
        #
        net_packet = self._packed_serialize( reciver_ip, self._ip, data )
        # forming frame id
        frame_id = ( reciver_mac, reciver_ip )

        # send operation emit
        self.operation_putlow_signal.emit(
            'dl_send',
            {
                'frame_id': frame_id,
                'reciver_mac': reciver_mac,
                'data': net_packet
            }
        )

        # self._send_signal.emit( frame_id, reciver_mac, net_packet )

    @NLogger.wrap('DEBUG')
    def net_recive_op(self, **kwargs):
        """ """
        self.operation_putlow_signal.emit(
            'dl_recive', kwargs
        )

    @NLogger.wrap('DEBUG')
    def dl_read_op(self, **kwargs):
        """ """
        data = kwargs.get('data', None)

        if data is not None:
            #
            reciver_ip, sender_ip, cutdata = self._packet_deserialize(data)
            #
            if reciver_ip != self._ip:
                # return 'False' is not necessary, only for logging.
                return False
            #
            kwargs['data'] = cutdata
            kwargs['sender_ip'] = sender_ip

            del(kwargs['frame_id'])

            # net read operation emit
            self.operation_puthigh_signal.emit(
                'net_read',
                kwargs
            )

    @NLogger.wrap('WARN')
    def dl_read_timeout_op(self, **kwargs):
        """ """
        # timeout operation emit
        self.operation_puthigh_signal.emit(
            'net_read_timeout',
            kwargs
        )

    @NLogger.wrap('ERROR')
    def dl_error_op(self, **kwargs):
        """ """
        self.operation_puthigh_signal.emit(
            'net_error',
            kwargs
        )
