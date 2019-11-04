import random

import numpy as np

from utils import now

random.seed(1337)


def get_new_customers(properties):
    # poisson
    custs = []
    ll, lh = properties["poisson_lambda_low_priority"], properties["poisson_lambda_high_priority"]
    nl, nh = np.random.poisson(ll), np.random.poisson(lh)
    priorities = ["low"] * nl + ["high"] * nh
    for _, pr in zip(range(nl + nh), priorities):
        custs.append(Customer(prob_stay=properties["prob_stay"], exp_params=properties["exp_params"], priority=pr))
    return custs[:nl], custs[nl:]


class Customer:
    arrival_time = 0
    prob_stay = 0
    location = ""
    priority = ""
    content_time_needed = 0
    started_being_content = 0
    server = None
    service_time_needed = 0

    def __init__(self, arrival_time=now(), prob_stay=0.5, exp_params=(0.5, 0.6), priority="low"):
        self.arrival_time = arrival_time
        self.started_being_served_time = None

        self.priority = priority
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

    def get_waiting_times(self):
        return {"waited": sum(self.wait_times_to_be_served), "served": sum(self.served_times),
                "content": sum(self.content_times)}

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
        self.wait_times_to_be_served.append(now() - self.arrival_time)
        # compute the time the customer needs
        self.service_time_needed = np.random.exponential(self.mu)
        self.started_being_served_time = now()

    def is_done_being_served(self):
        return (now() - self.started_being_served_time) >= self.service_time_needed

    def is_done_being_content(self):
        return (now() - self.started_being_content) >= self.content_time_needed

    def completed_being_served(self):
        self.served_times.append(self.service_time_needed)

    def become_content(self):
        # calculate content duration
        self.content_time_needed = np.random.exponential(self.delta)
        self.started_being_content = now()

    def completed_being_content(self):
        self.content_times.append(self.content_time_needed)
        self.arrival_time = now()


class Server:
    occupied = False
    customer = None

    def __init__(self):
        self.occupied = False

    def is_occupied(self):
        return self.occupied

    def release(self):
        self.occupied, self.customer = False, None
