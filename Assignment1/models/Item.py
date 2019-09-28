class Item:
    """
    Class to represent a generated item. The fields describing the class are:
    the dl and dh (i.e. the possible size values), the probability associated with each possible size value (i.e. pi),
    the final selected size based on the pi field (i.e. the size field) and finally the r field
    """
    size = 0
    selected_size = "dl"
    dl = 0
    dh = 0
    position = 0
    pi = 0
    r = 0
    decision_variable = 0

    def __init__(self, position=-1):
        """
        Item constructor. In order to instanciate an Item object you need to provide its position in the iterations.
        This number will be used as an ID to this item for the Knapsack Problem.
        :param position: the iterator's index
        """
        if position == -1:
            raise Exception("Provide a valid i in")
        else:
            self.position = position

    def copy_item(self, item):
        self.pi = item.pi
        self.r = item.r
        self.position = item.position
        self.dl = item.dl
        self.dh = item.dh
