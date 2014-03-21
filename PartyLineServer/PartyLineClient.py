import socket

HOST, PORT = "localhost", 7050

def communicate(sock):
  command=input('input command> ')
  while command=='r' or command=='p' or command=='s' or command=='q':
    sock.sendto(bytes(command, 'UTF-8'), (HOST,PORT))
    command=input('input command> ')    

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
communicate(sock)
