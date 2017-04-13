# python3!

from ctypes import cdll, byref, c_ubyte, c_int

_crc_cext = cdll.LoadLibrary('./crc8_c_lib/crc8.dll')


# calc crc for single byte and old(init) crc value
def ncrc8_byte(byte, crc):
    j = 0
    while j < 8:
        crc_msb = crc & 0x80
        crc = (crc << 1) & 0xFF

        if (byte & 0x80):
            crc |= 0x01
        else:
            crc &= 0xfe

        if crc_msb:
            crc ^= 0x85

        byte = (byte << 1) & 0xFF

        j = j + 1

    return (crc & 0xFF)


# calc crc for input buf data
def ncrc8_buf_py(buf):
    crc = 0
    for j in buf:
        crc = ncrc8_byte(j, crc)
    return crc


# calc crc for input buf data
def ncrc8_buf_c_win(cubyte_buff, clen):
    """ """
    return _crc_cext.crc8_buffer( byref(cubyte_buff), clen )


# calc crc for input buf data
def ncrc8_buf(buf):
    """  """
    crbuf = (c_ubyte * (len(buf)))(*buf)
    blck_len = c_int(len(buf))

    crc = _crc_cext.crc8_buffer( byref(crbuf), blck_len)

    del(crbuf)

    return int(crc)


#
if __name__ == '__main__':
    """ test """

    from logger import NLogger
    from time import time

    # logger
    mainlogger = NLogger.init( '__main__', 'DEBUG' )

    # test buffer
    rbuf = bytearray( [ 0x5b, 0x00, 0x00, 0x2, 0x86, 0x93 ] )
    # test buffer pre-calc control crc
    control_crc = 0x8f

    # ---
    ts = time()
    mainlogger.info('START native python on %.8g sec ...' % ts)

    for x in range(1000):
        calc_crc = ncrc8_buf_py( rbuf )

    # ---
    ts = time()-ts
    mainlogger.info( 'DONE native python - work time is %s msec - %s' % (ts*(10**3), '# --- '*20))
    mainlogger.info( 'verify crc: %s' % (control_crc == calc_crc) )

    # ------------------------------------------------------------------------------

    # ---
    ts = time()
    mainlogger.info('START C dll on %.8g sec ...' % ts)

    crbuf = (c_ubyte * (len(rbuf) + 1))(*rbuf)
    blck_len = c_int(len(rbuf))
    calc_crc = c_ubyte(0)

    x = 0
    while x < 1000:
        calc_crc = _crc_cext.crc8_buffer( byref(crbuf), blck_len )
        x += 1

    del(crbuf)

    # ---
    ts = time()-ts
    mainlogger.info( 'DONE C dll - work time is %.8g msec - %s' % (ts*(10**3), '# --- '*20))
    mainlogger.info( 'dll calc crc val: 0x%02X' % int(calc_crc) )
    mainlogger.info( 'verify crc: %s' % ( control_crc == int(calc_crc) ) )
