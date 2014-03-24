/// InitNetwork()

global.server = network_create_server(network_socket_udp, 7049, 1);
global.client = network_create_socket(network_socket_udp);
//network_connect_raw(global.client, “127.0.0.1”, 7050);

global.sendBuffer=buffer_create(1440, buffer_fixed, 1);
