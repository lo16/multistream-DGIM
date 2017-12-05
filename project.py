#!/opt/python-3.4/linux/bin/python3

import sys
import re
import random
from socket import *
import threading
import time
import math
from flrtree import LRTree
from DGIM import DGIM
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


#buckets will have points as keys and buckets as values
buckets = {}
buckets_lock = threading.Lock()

X_MIN, X_MAX = (0, 100)
Y_MIN, Y_MAX = (0, 100)

e = threading.Event()

class streamThread(threading.Thread):
  def __init__(self):  
    threading.Thread.__init__(self)
    self.num, self.min, self.max = (100000, 5000, 10000)

    self.s = socket(AF_INET, SOCK_STREAM)
    self.s.bind(('', 0))
    #get socket data
    self.host, self.port = self.s.getsockname()

    #initialize to random coordinates

    while True:
      self.x_coord = random.uniform(X_MIN, X_MAX)
      self.y_coord = random.uniform(Y_MIN, Y_MAX)
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
    #wait for all threads to be created before streaming
    e.wait()
    for i in range(self.num):
      #n = random.randint(int(self.x_coord), int(self.x_coord)+int(self.y_coord)*2)
      n = random.normalvariate(self.x_coord + self.y_coord, math.sqrt((X_MAX - X_MIN + Y_MAX - Y_MIN)/2))

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
        bucket_average = buckets[point].getAverage(timestamp)
        print("Bucket Average: ", bucket_average)
        total_average += (bucket_average / len(points_list)) 

    return total_average


def setup_streams(num_points):
  for i in range(num_points):
    try:
      t = streamThread()
      t.start()
      #TODO: SYNCHRONIZE THREADS TO START AT THE SAME TIME?
    except Exception as ex:
      print ("Unable to start thread")
      print(ex)
  time.sleep(2)  
  assert(len(buckets) == num_points)
  e.set()
  e.clear()

def get_query_bounds():
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

    x_range = sorted([float(x) for x in x_range])
    y_range = sorted([float(y) for y in y_range])

    return x_range, y_range


def get_timeframe():
    timeframe_provided = False
    while (not timeframe_provided):
      print ('Enter timeframe (in seconds):')
      timeframe = input().strip()
      timeframe_provided = check_input_validity(timeframe)
    
    return int(timeframe)


def naive_query(bound_min, bound_max, point_list):
    x_bound_min, y_bound_min = bound_min
    x_bound_max, y_bound_max = bound_max
    return filter(lambda point: (x_bound_min < point[0] < x_bound_max and y_bound_min < point[1] < y_bound_max),point_list)




def random_query():
    pass    


def show_stream_locations(point_list):
    plt.scatter([point[0] for point in point_list],
                [point[1] for point in point_list])
    plt.show()

def show_query(point_list, points_in_query, x_range, y_range):
    width = x_range[1] - x_range[0]
    height = y_range[1] - y_range[0]
    fig = plt.figure()
    ax = fig.add_subplot(111, aspect="equal")
    ax.scatter([point[0] for point in point_list],
               [point[1] for point in point_list], color='blue')
    ax.scatter([point[0] for point in points_in_query],
               [point[1] for point in points_in_query], color='red')
    ax.add_patch(Rectangle((x_range[0], y_range[0]), width, height, fill=False))

    plt.show()



def main():
  num_points = 100
  setup_streams(num_points)

  #initalize LRT here, once all points have been created
  points_list = list(buckets.keys())

  show_stream_locations(points_list)

  points_tree = LRTree(points_list)

  #client loop
  while True:
    x_range, y_range = get_query_bounds()
    x_bound_min, x_bound_max = x_range[0], x_range[1]
    y_bound_min, y_bound_max = y_range[0], y_range[1]

    timeframe = get_timeframe()


    print("x-range: ({}, {})   y-range: ({}, {})  timeframe: {}".format(x_bound_min, x_bound_max, y_bound_min, y_bound_max, timeframe))
    
    #query LRT for points to estimate
    points_in_range_indicies = points_tree.query((x_bound_min, y_bound_min), (x_bound_max, y_bound_max))

    points_in_range = [points_list[i] for i in points_in_range_indicies]

    show_query(points_list, points_in_range, x_range, y_range)

    mean = get_combined_average(points_in_range, int(timeframe))

    print ("The mean of your query range is estimated to be {}".format(mean))
    
if __name__ == '__main__':
    main()
