import sys
import time
import subprocess
import signal

import socket
from queue import Queue
from threading import Thread

IDLE=0
RECORDING=1
PLAYING=2

class Sender:
  queue=None
  thread=None

  def __init__(self, queue):
    self.queue=queue
    self.thread=Thread(target=self.run)
    self.thread.start()

  def run(self):
    while True:
      command=self.queue.get()
      self.handle(command)        

  def handle(self, command):
    print('Sending '+command)

class Encoder:
  queue=None
  senderQueue=Queue()
  sender=None
  thread=None

  def __init__(self, queue):
    self.queue=queue
    self.sender=Sender(self.senderQueue)
    self.thread=Thread(target=self.run)
    self.thread.start()

  def run(self):
    while True:
      command=self.queue.get()
      self.handle(command)        

  def handle(self, command):
    subprocess.call(['c:\\Users\\Brandon\\PartyLine\\opusenc.exe', command+'.wav', command+'.opus'])
    self.senderQueue.put(command)

class ProcessHandler:
  recording=False
  playing=False
  process=None
  state=IDLE
  queue=None
  gui=None
  encoder=None
  encoderQueue=Queue()
  thread=None
  playthread=None

  def __init__(self, queue, gui):
    self.queue=queue
    self.gui=gui
    self.encoder=Encoder(self.encoderQueue)
    self.thread=Thread(target=self.run)
    self.thread.start()

  def run(self):
    while True:
      command=self.queue.get()
      self.handle_command(command)      

  def record(self, filename):
    print('Recording...')
    if self.state==RECORDING:
      self.stopcommand()
    elif self.state==PLAYING:
      if self.process:
        self.process.terminate()
    self.process=subprocess.Popen(['c:\\Users\\Brandon\\PartyLine\\rec.exe', filename], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    print('New process: '+str(self.process))
    self.state=RECORDING

  def play(self, filename):
    print('Playing...')
    if self.state==RECORDING:
      self.stopcommand()
    elif self.state==PLAYING:
      return
    self.state=PLAYING
    self.process=subprocess.Popen(['c:\\Users\\Brandon\\PartyLine\\play.exe', filename])
    self.playthread=Thread(target=self.waitForPlay)
    self.playthread.start()

  def waitForPlay(self):
    if self.process:
      self.process.wait()
      self.process=None
      if self.state==PLAYING:
        self.state=IDLE
        self.gui.broadcast(b's')

  def stopcommand(self):
    print('Stopping')
    print(self.process)
    if self.process:
      self.process.send_signal(signal.CTRL_C_EVENT)
      if not self.process.poll():
        print('Escalating 1')
        time.sleep(1)
        self.process.terminate()
        if not self.process.poll():
          print('Escalating 2')
          time.sleep(1)
          self.process.kill()
          while not self.process.poll():
            print('Escalated 3')
            time.sleep(1)
            self.process.kill()            
      print('Killed')
      self.state=IDLE
      self.process=None
      self.encoderQueue.put('test')
    else:
      print('No process to stop')

  def handle_command(self, command):
    if command==b'r':
      self.record('test.wav')
    elif command==b'p':
      self.play('test.wav')
    elif command==b's':
      self.stopcommand()
    elif command==b'q':
      sys.exit(1)
    elif command==b'h':
      print('Hello!')
    else:
      print('Unknown command '+str(command))

class UDPServer:
  sock=None
  queue=Queue()
  backQueue=Queue()
  handler=None
  thread=None
  clients=set([])

  def __init__(self):
    self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.bind(('0.0.0.0', 7050))
    self.handler=ProcessHandler(self.queue, self)
    self.thread=Thread(target=self.run)
    self.thread.start()

  def run(self):
    while True:
      data, addr=self.sock.recvfrom(1440)
      self.clients.add(addr)
      print(str(self.clients))
      self.handle(data)

  def handle(self, data):
    print(data)
    command = data[12:13]
    print('command: '+str(command))
    self.queue.put(command)

  def broadcast(self, data):
    print('Broadcasting '+str(data))
    self.sock.sendto(self.format(data), ('127.0.0.1', 7049))

  def format(self, data):
    return b'\xde\xc0\xad\xde\x0c\x00\x00\x00\x01\x00\x00\x00'+data

class BackendServer:
  sock=None
  gui=None
  thread=None

  def __init__(self, gui):
    self.gui=gui
    self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.bind(('0.0.0.0', 7051))
    self.thread=Thread(target=self.run)
    self.thread.start()

  def run(self):
    while True:
      data, addr=self.sock.recvfrom(1440)
      self.handle(data)

  def handle(self, data):
    command = data[0:1]
    print('Backend '+str(command))
    if command==b'p':
      print('Broadcasting')
      print(self.gui)
      self.gui.broadcast(command)

gui=UDPServer()
backend=BackendServer(gui)
