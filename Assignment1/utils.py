from scipy import stats
from os.path import join
import os

# global parameters
GROUP = 10
runs = 10
item_num = 10

capacity = 400 + (4 * GROUP)
penalty = 60 + (GROUP / 10)
risk = {"EN": 0, "CVaR": 0.95}
confidence_interval = 0.95
accuracy = 2

output_folder = join(os.getcwd(), "output")


def profit(revenue, size_excluded):
    return revenue - (penalty * size_excluded)


def bernoulli(prob, item_size):
    return stats.bernoulli(prob).rvs(item_size)
