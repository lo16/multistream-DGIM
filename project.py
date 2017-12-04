#!/opt/python-3.4/linux/bin/python3

import sys
import re
import random
from socket import *
import threading
import time
from flrtree import LRTree
from DGIM import DGIM

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
    x_max = 100
    y_max = 100

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
          k = 2
          print(self.x_coord, self.y_coord)
          buckets[(self.x_coord, self.y_coord)] = DGIM(k)
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
      n = random.randint(0, 10)

      #add timestamp and value to our bucket
      buckets[(self.x_coord, self.y_coord)].add(i, n)
      #we are setting our stream rate to one int per second
      time.sleep(1)

  

#our input must be two non-negative numbers separated by a comma, 
def get_bounds_from_input(input_range):
  bounds = input_range.split(',')
  #print (bounds)
  if len(bounds) != 2:
    return False

  num_format = re.compile("^[0-9]*\.?[0-9]+$")
  for num in bounds:
    isnumber = re.match(num_format, num.strip())
    if not isnumber:
      return None
  return bounds
  
#single number version of check_bounds_input_validity
def check_input_validity(timeframe):
  num_format = re.compile("^[0-9]*\.?[0-9]+$")
  return re.match(num_format, timeframe.strip())


def get_combined_average(points_list, timestamp):
    total_average = 0
    for point in points_list:
        bucket_average = buckets[point].query(timestamp)
        print("Bucket Average: ", bucket_average)
        total_average += (bucket_average / len(points_list)) 

    return total_average


if __name__ == '__main__':
  num_points = 10
  e = threading.Event()
  for i in range(num_points):
    try:
      t = streamThread()
      t.start()
      #TODO: SYNCHRONIZE THREADS TO START AT THE SAME TIME?
    except Exception as ex:
      print ("Unable to start thread")
      print(ex)
  time.sleep(2)
  e.set()
  assert(len(buckets) == num_points)

  #initalize LRT here, once all points have been created
  points_list = list(buckets.keys())
  points_tree = LRTree(points_list)

  #client loop
  while True:
    x_range = None
    while (not x_range):
      print ('Enter x range:')
      x_range_input = input().strip()
      x_range = get_bounds_from_input(x_range_input)

    y_range = None
    while (not y_range):
      print ('Enter y range:')
      y_range_input = input().strip()
      y_range = get_bounds_from_input(y_range_input)

    [x_min, x_max] = sorted([float(x) for x in x_range])
    [y_min, y_max] = sorted([float(y) for y in y_range])

    timeframe_provided = False
    while (not timeframe_provided):
      print ('Enter timeframe (in seconds):')
      timeframe = input().strip()
      timeframe_provided = check_input_validity(timeframe)

    print("x-range: ({}, {})   y-range: ({}, {})  timeframe: {}".format(x_min, x_max, y_min, y_max, timeframe))
    
    #query LRT for points to estimate
    points_in_range = points_tree.query((x_min, y_min), (x_max, y_max))
    print(points_in_range)

    #TODO: CALL FUNCTION TO ESTIMATE MEANS 
    mean = get_combined_average([points_list[i] for i in points_in_range], int(timeframe))

    print ("The mean of your query range is estimated to be {}".format(mean))
