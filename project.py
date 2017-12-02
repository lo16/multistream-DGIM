#!/opt/python-3.4/linux/bin/python3

import sys
import re
import random
from socket import *
import threading
import time
from flrtreelib.flrtree import LRTree

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

#buckets will have points as keys and buckets as values
buckets = {}
buckets_lock = threading.Lock()

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
      if potential_key not in buckets.keys(): 
        #add to dictionary of points
        buckets_lock.acquire()
        try:
          #points[(self.x_coord, self.y_coord)] = (self.host, self.port)
          #the dict now stores buckets for DGIM
          buckets[(self.x_coord, self.y_coord)] = []
        finally:
          buckets_lock.release()
        break

  def run(self):
    '''
    #THIS SECTION IS FOR THE DISTRIBUTED VERSION IF WE GET TO THAT POINT
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
    '''

    #use RNG to generate integers and add them to buckets
    random.seed()
    for i in range(self.num):
      self.rand_int = random.randint(0, 10)
      #TODO: ADD TIME
      add_to_bucket((self.x_coord, self.y_coord), self.rand_int)

#TODO: IMPLEMENT
def add_to_bucket((x, y), n):
  pass

#our input must be two non-negative numbers separated by a comma, 
def check_bounds_input_validity(range):
  bounds = range.split(',')
  #print (bounds)
  if len(bounds) != 2:
    return False

  num_format = re.compile("^[0-9]*\.?[0-9]+$")
  for num in bounds:
    isnumber = re.match(num_format, num.strip())
    if not isnumber:
      return False
  return True
  
#single number version of check_bounds_input_validity
def check_input_validity(timeframe):
  num_format = re.compile("^[0-9]*\.?[0-9]+$")
  return re.match(num_format, timeframe.strip())

if __name__ == '__main__':
  num_points = 10
  e = threading.Event()
  for i in xrange(num_points):
    try:
      t = streamThread()
      t.start()
      #TODO: SYNCHRONIZE THREADS TO START AT THE SAME TIME?
    except Exception as ex:
      print ("Unable to start thread")
      print ex
  time.sleep(2)
  e.set()
  assert(len(buckets) == num_points)

  #initalize LRT here, once all points have been created
  points_tree = LRTree(buckets.keys())

  #client loop
  while True:
    x_range_provided = False
    while (not x_range_provided):
      print ('Enter x range:')
      x_range = raw_input().strip()
      x_range_provided = check_bounds_input_validity(x_range)

    y_range_provided = False
    while (not y_range_provided):
      print ('Enter y range:')
      y_range = raw_input().strip()
      y_range_provided = check_bounds_input_validity(y_range)

    [x_min, x_max] = sorted([float(x) for x in x_range])
    [y_min, y_max] = sorted([float(y) for y in y_range])

    timeframe_provided = False
    while (not timeframe_provided):
      print ('Enter timeframe (in seconds):')
      timeframe = raw_input().strip()
      timeframe_provided = check_input_validity(timeframe)

    print (x_min, x_max), (y_min, y_max)
    
    #query LRT for points to estimate
    points_in_range = points_tree.query((x_min, y_min), (x_max, y_max))

    #TODO: CALL FUNCTION TO ESTIMATE MEANS 
    mean = None

    print ("The mean of your query range is estimated to be %f", mean)
