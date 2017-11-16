#!/opt/python-3.4/linux/bin/python3

import sys
import random
from socket import *
import thread

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

def create_point():  
  num, min, max = (100000, 5000, 10000)
  if len(sys.argv) == 2 and sys.argv[1] == "-h":
    help()
  elif len(sys.argv) == 4:
    num = int(sys.argv[1])
    min = int(sys.argv[2])
    max = int(sys.argv[3])
    if num <= 0 or min <= 0:
      help()
    if min > max:
      help()
  else:
    help()

  s = socket(AF_INET, SOCK_STREAM)
  s.bind(('', 0))
  #get socket data
  host, port = s.getsockname()

  #initialize to random coordinates
  x_min = 0
  y_min = 0
  x_max = 10000
  y_max = 10000
  x_coord = random.uniform(x_min, x_max)
  y_coord = random.uniform(y_min, y_max)

  #add to dictionary of points
  points[(x_coord, y_coord)] = (host, port)

  print("connect to port number %s" % port)
  s.listen(10)
  while True:
    client, addr = s.accept()
    print("Got a connection from %s" % str(addr))
    random.seed(32767)
    for i in range(num):
      j = random.randint(0,1)
      print j,
      x = str(j)
      x = x + "\n"
      client.send(x.encode('ascii'))
      for k in range(random.randint(min,max)):
        j = j + k
    client.close()

if __name__ == '__main__':
  num_points = 10
  for i in xrange(num_points):
    try:
      thread.start_new_thread(create_point)
    except:
      print ("Unable to start thread")
  print len(points)