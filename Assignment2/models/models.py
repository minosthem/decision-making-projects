from datetime import datetime
import numpy as np
import random


class Customer:
    arrival_time = 0
    service_time = 0
    end_patience_time = 0
    system_arrival_time = 0
    prob_to_stay = 0
    location = ""
    state = ""
    priority = ""

    def __init__(self, arrival_time=datetime.now(), state="Needy", priority=None, prob_stay=0.5, exp_params=(0.5,0.6)):
        self.arrival_time = arrival_time
        self.started_being_served_time = None

        self.prob_stay = prob_stay
        self.priority = priority
        self.mu, self.delta = exp_params

        # durations:
        # times waiting to be served
        self.wait_times_to_be_served = []
        # times during which you are served
        self.served_times = []
        # times during which you are content
        self.content_times = []

    def decide_to_leave(self):
        if random.random() < self.prob_stay:
            # stay
            return False
        else:
            # leave
            return True

    def become_served(self, server):
        self.server = server
        server.customer = self
        server.occupied = True
        # time waited to be served
        self.wait_times_to_be_served.append(datetime.now() - self.arrival_time)
        # compute the time the customer needs
        self.service_time_needed = np.random.exponential(self.mu)
        self.started_being_served_time = datetime.now()

    def is_done_being_served(self):
        return (datetime.now() - self.started_being_served_time) >= self.service_time_needed

    def is_done_being_content(self):
        return (datetime.now() - self.started_being_content) >= self.content_time_needed

    def completed_being_served(self):
        self.served_times.append(self.service_time_needed)

    def become_content(self):
        # calculate content duration
        self.content_time_needed = np.random.exponential(self.delta)
        self.started_being_content = datetime.now()

    def completed_being_content(self):
        self.content_times.append(self.content_time_needed)
        self.arrival_time = datetime.now()

    def move_to(self, location, time, new_service_time):
        self.location = location
        self.arrival_time = time
        self.service_time = new_service_time

    def leave_system(self):
        self.location = -1
        self.service_time = -1


class Server:
    occupied = False
    customer = None

    def __init__(self):
        self.occupied = False
    def is_occupied(self):
        return self.occupied
    def release(self):
        self.occupied, self.customer = False, None


class Queue:
    param = ""
    service_time = 0

    def __init__(self, param):
        self.param = param
        if param == "m":
            # TODO calculate service time
            pass
        elif param == "d":
            # TODO calculate service time
            pass
