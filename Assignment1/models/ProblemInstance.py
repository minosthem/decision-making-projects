class ProblemInstance:
    """
    ProblemInstance class represents a generated instance. It has only one field, i.e. items,
    where the 10 generated items are stored
    """
    items = []

    def __init__(self, item_list=None):
        if item_list is None:
            item_list = []
        self.items = item_list

    def __str__(self):
        representation = ''
        if self.items:
            representation = "ProblemInstance{"
            for item in self.items:
                representation += item.__str__()
            representation += "},\n"
        return representation

    def __repr__(self):
        return self.__str__()
