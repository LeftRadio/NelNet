

// calc crc for single byte and old(init) crc value
__declspec(dllexport) unsigned char crc8_byte( unsigned char byte, unsigned char crc )
{
    int i = 0;
    unsigned char crc_msb;

    do {

        crc_msb = crc & 0x80;
        crc = (crc << 1) & 0xFF;

        if (byte & 0x80) crc |= 0x01;
        else crc &= 0xfe;

        if (crc_msb) crc ^= 0x85;

        byte = (byte << 1) & 0xFF;

        i++;

    } while(i < 8);

    return crc;
}


__declspec(dllexport) unsigned char crc8_buffer( unsigned char* in, int len )
{
    int i = 0;
    unsigned char crc = 0;

    do {

        crc = crc8_byte(in[i], crc);

    } while(++i < len);

    return crc;
}