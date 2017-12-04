from Node import Node
sample_list = [38, 29, 75, 32, 87, 92, 91, 47, 74, 54, 57, 4, 82, 21, 73,
               90, 23, 15, 14, 46, 64, 87, 98, 23, 33, 34, 19, 42, 27, 98,
               73, 23, 61, 95, 3, 89, 25, 88, 29, 25, 32, 48, 92, 15, 70, 45, 60, 48, 83, 14]
class DGIM:
    def __init__(self, k):
        self.dgim_list = None
        self.k = k
        
    def add(self, timestamp, value):
        if value == 0:
            return
        self.dgim_list = Node(timestamp, value, self.dgim_list)
        temp = self.dgim_list

        curr_size = 0
        curr_count = 0
        while temp != None:
            if curr_size == temp.size:
                curr_count += 1
                if curr_count == self.k and temp.next != None:
                    if temp.next.size == curr_size:
                        if temp.next.sum + temp.sum <= 2**(curr_size + 1):
                            temp.size += 1
                            temp.sum = temp.sum + temp.next.sum
                            temp.timestamp = temp.next.timestamp
                            temp.next = temp.next.next
                        else:
                            temp = temp.next
                            temp.size += 1
                    curr_size = temp.size
                    curr_count = 1
            temp = temp.next


    def query(self, query_timestamp):
        current_timestamp = self.dgim_list.timestamp
        target_timestamp = current_timestamp - query_timestamp
        print("target_timestamp:", target_timestamp)

        num_elements = 0
        total_sum = 0

        prev_timestamp = current_timestamp + 1
        temp = self.dgim_list
        while (temp != None and temp.timestamp > target_timestamp):
            total_sum += temp.sum
            num_elements += prev_timestamp - temp.timestamp
            prev_timestamp = temp.timestamp
            temp = temp.next

        avg = total_sum / num_elements

        return avg

    def __repr__(self):
        to_return = ""
        temp = self.dgim_list
        while temp != None:
            to_return += "Bucket(timestamp={}, sum={}, size={})\n".format(temp.timestamp, temp.sum, temp.size)
            temp = temp.next
        return to_return

dgim = DGIM(2)
if __name__ == "__main__":
    for i in range(len(sample_list)):
        dgim.add(i, sample_list[i])  
        print(dgim)
    print(dgim)
    last_x = 47
    print("length:", len(sample_list[len(sample_list)-last_x:]))
    print("Actual Average:", sum(sample_list[len(sample_list)-last_x:])/last_x)
    print("Estimated Average:", dgim.query(last_x))
