#!/opt/python-3.4/linux/bin/python3

import sys
import random
from socket import *
import threading
import time

def help():
  s = '''
  server.py - server program for integer stream

  USAGE:
    server.py -h
    server.py <#int> <min> <max>

  OPTIONS:
    -h   get this help page
    <#int> number of bits (default is 1000000)
    <min> minimum delay (default is 5000)
    <max> maximum delay (default is 10000)

  EXAMPLE:
    server.py -h
    server.py 10 1000 2000

  CONTACT:
    Ming-Hwa Wang, Ph.D. 408/805-4175  m1wan@scu.edu
  '''
  print(s)
  raise SystemExit(1)

points = {}
points_lock = threading.Lock()

class streamThread(threading.Thread):
  def __init__(self):  
    threading.Thread.__init__(self)
    self.num, self.min, self.max = (100000, 5000, 10000)

    self.s = socket(AF_INET, SOCK_STREAM)
    self.s.bind(('', 0))
    #get socket data
    self.host, self.port = self.s.getsockname()

    #initialize to random coordinates
    x_min = 0
    y_min = 0
    x_max = 10000
    y_max = 10000

    while True:
      self.x_coord = random.uniform(x_min, x_max)
      self.y_coord = random.uniform(y_min, y_max)
      potential_key = (self.x_coord, self.y_coord)
      if potential_key not in points.keys(): 
        #add to dictionary of points
        points_lock.acquire()
        try:
          points[(self.x_coord, self.y_coord)] = (self.host, self.port)
        finally:
          points_lock.release()
        break

  def run(self):
    print("connect to port number %s\n" % self.port)
    
    #wait for all points to be added to the dictionary
    e.wait()
    
    #start listening
    self.s.listen(10)
    while True:
      client, addr = self.s.accept()
      print("Got a connection from %s" % str(addr))
      random.seed(32767)
      for i in range(self.num):
        j = random.randint(0,1)
        print j,
        x = str(j)
        x = x + "\n"
        client.send(x.encode('ascii'))
        for k in range(random.randint(self.min,self.max)):
          j = j + k
      client.close()


if __name__ == '__main__':
  num_points = 10
  e = threading.Event()
  for i in xrange(num_points):
    try:
      t = streamThread()
      t.start()
    except Exception as ex:
      print ("Unable to start thread")
      print ex
  time.sleep(2)
  e.set()
  print 'number of streams:', len(points)