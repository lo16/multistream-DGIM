class Node:
    def __init__(self, timestamp, value, nextNode):
        self.timestamp = timestamp
        self.sum = value
        self.size = 0
        self.next = nextNode
