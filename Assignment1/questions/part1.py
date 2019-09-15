import numpy as np
from models.ProblemInstance import ProblemInstance
from models.Item import Item
import utils


def generate_problem_instances():
    """
    Method to generate the requested problem instances with 10 items each.
    For each item, dli, dhi, pi and ri are calculated and saved in the respective fields of the Item object.
    All problem instances are save into a list which is then returned to the main program.
    For poisson and triangular distributions, numpy library is used (numpy.random.poisson and numpy.random.triangular)
    in order to generate random numbers for the items' sizes.
    :return: a list with all the generated problem instances
    """
    problem_instances = []

    for i in range(utils.runs):
        instance = ProblemInstance()
        for j in range(utils.item_num):
            item = Item(j)
            # calculate d_lj
            gj = np.random.poisson(lam=(j / 2), size=utils.item_num)[j]
            item.dl = int(max(gj, 10))
            # calculate d_hj
            item.dh = int(generate_triangular_random_numbers(j)[j])
            # calculate pi
            item.pi = 0.5 + (0.05 * j) - 0.001
            if item.pi <= 0.5:
                item.size = item.dl
            else:
                item.size = item.dh
            # calculate r
            item.r = 51 - j
            instance.items.append(item)
        problem_instances.append(instance)
    return problem_instances


# def generate_poisson_random_numbers(j):
#     random_numbers = []
#     i = 0
#     lamda = j / 2
#     poisson = np.random.poisson(lam=(j / 2))
#     u = np.random.uniform(size=runs)
#     p = math.exp(-lamda)
#     F = p
#     for count in range(runs):
#         if u < F:
#             x = i
#             random_numbers.append(x)
#         else:
#             p = (lamda / (i + 1)) * p
#             F = F + p
#             i += 1
#     return random_numbers


def generate_triangular_random_numbers(j):
    """
    Method that generates random numbers using triangular distribution.
    Left, mode and right parameters are calculated and provided in numpy.random.triangular
    to generate an array with the relevant random numbers
    :param j: the iterator's index (position of the item)
    :return: nd array with the random numbers
    """
    left = 90 + utils.GROUP - j
    mode = 100 + utils.GROUP - j
    right = 110 + utils.GROUP - j
    return np.random.triangular(left=left, mode=mode, right=right, size=utils.item_num)
