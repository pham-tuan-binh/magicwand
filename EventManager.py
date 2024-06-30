from typing import List
from collections import deque
import time
import numpy as np

# Event class
# id 1: touch down
# id 2: touch up

class Event:
    def __init__(self, id: int, name: str, time: int, coordPair):
        self.id = id
        self.name = name
        self.time = time
        self.coordPair = coordPair

    def __str__(self):
        return f"Event: {self.name} at {self.time}"

class EventManager:
    def __init__(self, name: str, coordPair: List[int]):
        self.name = name
        self.coordPair = coordPair
        self.eventQueue = deque()
        self.threshold = 0.1

    def setSingleTapCallback(self, callback):
        self.singleTapCallback = callback

    def update(self, landmarks):
        self.point1 = landmarks[self.coordPair[0]]
        self.point2 = landmarks[self.coordPair[1]]

        # Calculate distance between two points in x y z 
        distance = ((self.point1.x - self.point2.x)**2 + (self.point1.y - self.point2.y)**2 + (self.point1.z - self.point2.z)**2)**0.5

        # Get the current time
        current_time = time.time_ns() // 1_000_000

        # Remove last elem of queue if len > 6
        if len(self.eventQueue) > 6:
            self.eventQueue.popleft()

        # If the event queue is empty or the last event is touch up and the distance is less than threshold, add a touch down event
        if (len(self.eventQueue) == 0 or self.eventQueue[-1].id == 2) and distance < self.threshold:
            self.eventQueue.append(Event(1, "touch down", current_time, [self.point1, self.point2]))
            #print("Touch down for " + self.name)
            return
        
        # If the last event is touch down and the distance is greater than threshold, add a touch up event
        if (len(self.eventQueue) > 0 and self.eventQueue[-1].id == 1) and distance > self.threshold:
            self.eventQueue.append(Event(2, "touch up", current_time, [self.point1, self.point2]))
            #print("Touch up for " + self.name)
            return
        
        # Detect single tap and clear queue
        if len(self.eventQueue) > 1 and self.eventQueue[-1].id == 2 and self.eventQueue[-1].time - self.eventQueue[-2].time < 400:
            self.singleTapCallback()
            self.eventQueue.clear()

        return

    @property
    def isDragging(self):
        if len(self.eventQueue) > 0 and self.eventQueue[-1].id == 1 and time.time_ns() // 1_000_000 - self.eventQueue[-1].time > 500:
            return True
        
        return False
    
    @property
    def dragVector(self):
        if self.isDragging:
            origin = self.eventQueue[-1].coordPair[0]

            # calculate vector between thumb and index tip
            current = self.point1

            # Convert origin and current to pixel coordinates
            return (current.x - origin.x, current.y - origin.y)
        

        return None, None

    @property
    def dragOrigin(self):
        if self.isDragging:
            origin = self.eventQueue[-1].coordPair[0]
            return np.array([origin.x, origin.y])

        return None, None
    
    @property
    def dragCurrent(self):
        if self.isDragging:
            current = self.point1
            return np.array([current.x, current.y])

        return None, None

    