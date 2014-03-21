import sys
import time
import subprocess

import socketserver
from queue import Queue
from threading import Thread

IDLE=0
RECORDING=1
PLAYING=2

class Sender:
  def __init__(self, queue):
    self.queue=queue

  def run(self):
    while True:
      command=self.queue.get()
      self.handle(command)        

  def handle(self, command):
    print('Sending '+command)

class Encoder:
  sender=None
  queue=None
  senderQueue=Queue()
  thread=None

  def __init__(self, queue):
    self.queue=queue
    self.sender=Sender(self.senderQueue)
    self.thread=Thread(target=self.sender.run)
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
  encoder=None
  encoderQueue=Queue()
  thread=None

  def __init__(self, queue):
    self.queue=queue
    self.encoder=Encoder(self.encoderQueue)
    self.thread=Thread(target=self.encoder.run)
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
    self.process=subprocess.Popen(['c:\\Users\\Brandon\\PartyLine\\rec.exe', filename])
    print(self)
    print(self.process)
    self.state=RECORDING

#  def play(self, filename):
#    print('Playing...')
#    if 
#      process.terminate()
#      recording=False
#      playing=False
#    process=subprocess.Popen(['c:\\Users\\Brandon\\PartyLine\\play.exe', filename])
#    playing=True

  def stopcommand(self):
    print('Stopping')
    print(self)
    print(self.process)
    if self.process:
      self.process.terminate()
      self.process=None
      self.state=RECORDING
      self.encoderQueue.put('test')

  def handle_command(self, command):
    if command==b'r':
      self.record('test.wav')
#    elif command==b'p':
#      self.play('test.wav')
    elif command==b's':
      self.stopcommand()
    elif command==b'q':
      sys.exit(1)
    else:
      print('Unknown command '+str(command))

class UDPHandler(socketserver.BaseRequestHandler):
  queue=Queue()
  handler=None
  thread=None

  def handle(self):
    if not self.handler:
      self.handler=ProcessHandler(self.queue)
      self.thread=Thread(target=self.handler.run)
      self.thread.start()
    command = self.request[0].strip()
    self.queue.put(command)

server = socketserver.UDPServer(('0.0.0.0', 7050), UDPHandler)
server.serve_forever()
