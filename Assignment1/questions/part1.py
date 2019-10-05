import numpy as np

from models.Item import Item
from models.ProblemInstance import ProblemInstance


def generate_problem_instances(properties):
    """
    Method to generate the requested problem instances with 10 items each.
    For each item, dli, dhi, pi and ri are calculated and saved in the respective fields of the Item object.
    In order to decide the item size, we combine dl, dh and their probabilities
    All problem instances are save into a list which is then returned to the main program.
    For poisson and triangular distributions, numpy library is used (numpy.random.poisson and numpy.random.triangular)
    in order to generate random numbers for the items' sizes.
    :return: a list with all the generated problem instances
    """
    problem_instances = []
    print("Generating problem instances with items")
    for i in range(properties["problem_instances"]):
        instance = ProblemInstance()
        for j in range(properties["item_nums_per_instance"]):
            item = Item(j)
            # calculate pi
            item.pi = 0.5 + (0.05 * j) - 0.001
            # calculate d_lj
            gj = np.random.poisson(lam=(j / 2), size=properties["item_nums_per_instance"])[j]
            item.dl = int(max(gj, 10))
            # calculate d_hj
            item.dh = int(generate_triangular_random_numbers(properties, j)[j])
            # define item size based on dl, dh and their probabilities
            item.size = int((item.pi * item.dh) + ((1 - item.pi) * item.dl))
            # calculate r
            item.r = 51 - j
            instance.items.append(item)
        problem_instances.append(instance)
    return problem_instances


def generate_triangular_random_numbers(properties, item_iteration):
    """
    Method that generates random numbers using triangular distribution.
    Left, mode and right parameters are calculated and provided in numpy.random.triangular
    to generate an array with the relevant random numbers
    :param item_iteration: the iterator's index (position of the item)
    :param properties properties from yaml file
    :return: nd array with the random numbers
    """
    left = 90 + properties["group"] - item_iteration
    mode = 100 + properties["group"] - item_iteration
    right = 110 + properties["group"] - item_iteration
    return np.random.triangular(left=left, mode=mode, right=right, size=properties["item_nums_per_instance"])
