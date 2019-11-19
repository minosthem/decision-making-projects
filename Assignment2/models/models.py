import random

import numpy as np

from utils import now

random.seed(1337)


def get_new_customers(properties, num_customers_created):
    # poisson
    ll, lh = properties["poisson_lambda_low_priority"], properties["poisson_lambda_high_priority"]
    mu, delta = properties["mu"], properties["delta"]
    nl, nh = np.random.poisson(ll), np.random.poisson(lh)
    customers = {"low": [], "high": []}
    priorities = ["low"] * nl + ["high"] * nh
    # at the first iteration, make sure at least one customer is created
    for _, pr in zip(range(nl + nh), priorities):
        cust = Customer(arrival_index=num_customers_created, prob_stay=properties["prob_stay"], mu=mu, delta=delta, priority=pr)
        customers[pr].append(cust)
        num_customers_created += 1
    return customers["low"], customers["high"], num_customers_created


class Customer:
    arrival_time = 0
    prob_stay = 0
    priority = ""
    content_time_needed = 0
    started_being_content = 0
    server = None
    service_time_needed = 0

    waited_outside = False
    waited_inside = False

    def tick(self, dt):
        self.time_counter += dt

    def __init__(self, arrival_index, prob_stay, mu, delta, priority="low"):
        self.time_counter = 0
        self.arrival_index = arrival_index
        self.became_needy_timestamp = None
        self.started_being_served_time = None

        self.priority = priority
        self.prob_stay = prob_stay
        self.mu, self.delta = mu, delta

        # durations:
        # time waiting to enter
        self.wait_time_to_enter = None
        # times waiting to be served
        self.wait_times_to_be_served = []
        # times during which you are served
        self.served_times = []
        # times during which you are content
        self.content_times = []

    def get_arrival_index(self):
        return self.arrival_index

    def get_waiting_times(self):
        return self.wait_time_to_enter, sum(self.wait_times_to_be_served), sum(self.served_times), sum(
            self.content_times)

    def decide_to_leave(self):
        if random.random() < self.prob_stay:
            # stay
            return False
        else:
            # leave
            return True

    def get_time_counter(self):
        return self.time_counter

    def reset_time_counter(self):
        self.time_counter = 0

    def compute_service_time_needed(self, num_servers, num_customers_served):
        if num_customers_served <= num_servers - 1:
            return num_customers_served * self.mu
        return num_servers * self.mu

    def become_served(self, server, num_servers, num_customers_served):
        self.server = server
        server.customer = self
        server.occupied = True
        # time waited to be served
        self.wait_times_to_be_served.append(self.get_time_counter())
        self.reset_time_counter()
        # compute the time the customer needs
        self.service_time_needed = self.compute_service_time_needed(num_servers, num_customers_served)

    def is_done_being_served(self):
        return self.time_counter >= self.service_time_needed

    def is_done_being_content(self):
        return self.time_counter >= self.content_time_needed

    def completed_being_served(self):
        self.served_times.append(self.service_time_needed)

    def become_content(self, num_customers_content):
        # calculate content duration
        self.content_time_needed = self.delta * num_customers_content
        self.reset_time_counter()

    def completed_being_content(self):
        self.content_times.append(self.content_time_needed)
        self.reset_time_counter()

    def complete_waiting_outside(self):
        self.wait_time_to_enter = self.get_time_counter()
        self.reset_time_counter()


class Server:
    occupied = False
    customer = None

    def __init__(self):
        self.occupied = False

    def is_occupied(self):
        return self.occupied

    def release(self):
        self.occupied, self.customer = False, None
