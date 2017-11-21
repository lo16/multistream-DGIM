import sys, re

#our input must be two non-negative numbers separated by a comma, 
def check_input_validity(range):
	bounds = range.split(',')
	print (bounds)
	if len(bounds) != 2:
		return False

	num_format = re.compile("^[0-9]*\.?[0-9]+$")
	for num in bounds:
		isnumber = re.match(num_format, num.strip())
		if not isnumber:
			return False
	return True

def print_mean(mean):
	print ("The mean of your query range is estimated to be %f", mean)
#TODO: CONNECT TO SERVER.PY

while True:
	x_range_provided = False
	while (not x_range_provided):
		print ('Enter x range:')
		x_range = raw_input().strip()
		x_range_provided = check_input_validity(x_range)

	y_range_provided = False
	while (not y_range_provided):
		print ('Enter y range:')
		y_range = raw_input().strip()
		y_range_provided = check_input_validity(y_range)

	[x_min, x_max] = sorted([float(x) for x in x_range])
	[y_min, y_max] = sorted([float(y) for y in y_range])

	print (x_min, x_max), (y_min, y_max)
	#TODO: SEND X, Y TO SERVER.PY

	#TODO: RECEIVE ANSWER FROM SERVER.PY
