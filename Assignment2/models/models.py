class Customer:
    prob_to_stay = 0
    state = ""
    priority = ""

    def __init__(self, state, priority, prob):
        self.state = state
        self.priority = priority
        self.prob_to_stay = prob


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
