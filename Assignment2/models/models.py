from datetime import datetime


class Customer:
    arrival_time = 0
    service_time = 0
    end_patience_time = 0
    system_arrival_time = 0
    prob_to_stay = 0
    location = ""
    state = ""
    priority = ""

    def __init__(self, arrival_time=datetime.now(), service_time=datetime.now(), end_patience_time=datetime.now(),
                 state="Needy", priority="Low", prob=0.5):
        self.arrival_time = arrival_time
        self.service_time = service_time
        self.system_arrival_time = arrival_time
        self.end_patience_time = end_patience_time
        self.state = state
        self.priority = priority
        self.prob_to_stay = prob

    def move_to(self, location, time, new_service_time):
        self.location = location
        self.arrival_time = time
        self.service_time = new_service_time

    def leave_system(self):
        self.location = -1
        self.service_time = -1


class Event:
    arrival = 0
    departure = 1
    abandonment = 2
    type = ""
    time = 0
    customer = Customer()

    def __init__(self, typ, time, cust):
        self.type = typ
        self.time = time
        self.customer = cust

    def __lt__(self, other):
        return self.time < other.time

    def __str__(self):
        s = ('Arrival', 'Departure', 'Abandonment')
        return s[self.type] + " of customer {}".format(self.customer) + "at time {}".format(self.time)


class Server:
    capacity = 0

    def __init__(self, capacity):
        self.capacity = capacity


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
