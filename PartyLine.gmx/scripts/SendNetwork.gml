/// SendNetwork(data)
var data, buff;
data=argument0;

buff=global.sendBuffer;
buffer_seek(buff, buffer_seek_start, 0);
buffer_write(buff, buffer_u8, data);

network_send_udp(global.client, "127.0.0.1", 7050, buff, buffer_tell(buff));
