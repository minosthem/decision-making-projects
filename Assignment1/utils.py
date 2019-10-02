from scipy import stats
from os.path import join, exists
import os
import yaml

properties_folder = join(os.getcwd(), "properties")
example_properties_file = join(properties_folder, "example_properties.yaml")
properties_file = join(properties_folder, "properties.yaml")


def load_properties():
    if exists(properties_file):
        with open(properties_file, 'r') as f:
            return yaml.safe_load(f)
    else:
        with open(example_properties_file, 'r') as f:
            return yaml.safe_load(f)


def profit(penalty, revenue, size_excluded):
    return revenue - (penalty * size_excluded)


def bernoulli(prob, item_size):
    return stats.bernoulli(prob).rvs(item_size)
