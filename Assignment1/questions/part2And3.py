import numpy as np
from models.Item import Item
import utils


def run_knapsack_for_problem_instance(instance, capacity):
    """
    Gets a specific problem instance and the default container capacity.
    Creates a list of tuples for each item of each problem instance, containing the value of the item,
    its size and its position in the list and runs the knapsack problem.
    Then, monte carlo simulation is executed, based on Bernoulli distribution that defines if an item
    will be in the knapsack or not. Finally, the profit from the monte carlo simulation is
    calculated.
    :param instance: a specific problem instance
    :param capacity: the container's capacity
    """
    items = reform_items(instance.items)
    best_value = knapsack_dp(items, capacity, return_all=True)
    selected_items, total_revenue = get_knapsack_result(best_value, instance.items)
    profits = monte_carlo(selected_items, capacity)
    m = np.mean(profits)
    print(m)

    # Construct a confidence interval
    Sn = np.std(profits)
    halfWidth = 1.96 * Sn / np.sqrt(int(utils.monte_carlo_runs))
    ci = (m - halfWidth, m + halfWidth)
    print(ci)


def reform_items(items):
    """
    Creates list of tuples with the values, sizes and indices of the items provided
    :param items: list of Item objects
    :return: list of tuples
    """
    new_items = []
    for j in range(len(items)):
        new_items.append((items[j].r, items[j].size, items[j].position))
    return new_items


def monte_carlo(selected_items, capacity):
    # monte carlo
    profits = []
    for i in range(int(utils.monte_carlo_runs)):
        new_items = []
        for j, old_item in enumerate(selected_items):
            item = Item(j)
            item.copy_item(old_item)
            bernoulli_res = utils.bernoulli(item.pi, 1)
            item.size = item.dh if bernoulli_res[0] == 1 else item.dl
            new_items.append(item)
        sum_sizes = 0
        total_revenue = 0
        count_oversize = 0
        total_size_excluded = 0
        for j, item in enumerate(new_items):
            if sum_sizes + item.size <= capacity:
                sum_sizes += item.size
                total_revenue += item.r * item.size
            else:
                count_oversize += 1
                total_size_excluded += item.size
        profit = utils.profit(total_revenue, total_size_excluded)
        profits.append(profit)
    return profits


def knapsack_dp(items, capacity, return_all=False):
    """
    Knapsack problem using Dynamic Programming
    :param items: list of tuples i.e. (value, size, index), where index is the index in the initial list
    :param capacity: the capacity of the knapsack
    :param return_all: boolean variable to return the max value and the items or only the items
    :return: based on return_all value return the items and the max value
    """
    values = [x[0] for x in items]
    weights = [x[1] for x in items]
    n_items = len(items)
    check_inputs(values, weights, n_items, capacity)

    table = np.zeros((n_items + 1, capacity + 1), dtype=np.float32)
    keep = np.zeros((n_items + 1, capacity + 1), dtype=np.float32)

    for i in range(1, n_items + 1):
        for w in range(0, capacity + 1):
            wi = weights[i - 1]  # weight of current item
            vi = values[i - 1]  # value of current item
            if (wi <= w) and (vi + table[i - 1, w - wi] > table[i - 1, w]):
                table[i, w] = (vi* wi) + table[i - 1, w - wi]
                keep[i, w] = 1
            else:
                table[i, w] = table[i - 1, w]

    picks = []
    K = capacity

    for i in range(n_items, 0, -1):
        if keep[i, K] == 1:
            picks.append(i)
            K -= weights[i - 1]

    picks.sort()
    picks = [x - 1 for x in picks]  # change to 0-index

    if return_all:
        max_val = table[n_items, capacity]
        return picks, max_val
    return picks


def get_knapsack_result(best_value, items):
    item_indices = best_value[0]
    total_revenue = best_value[1]
    for i, item in enumerate(items):
        if i in item_indices:
            item.decision_variable = 1
        else:
            item.decision_variable = 0
    selected_items = [x for x in items if x.decision_variable == 1]
    return selected_items, total_revenue


def check_inputs(values, weights, n_items, capacity):
    # check variable type
    assert (isinstance(values, list))
    assert (isinstance(weights, list))
    assert (isinstance(n_items, int))
    assert (isinstance(capacity, int))
    # check value type
    assert (all(isinstance(val, int) or isinstance(val, float) for val in values))
    assert (all(isinstance(val, int) for val in weights))
    # check validity of value
    assert (all(val >= 0 for val in weights))
    assert (n_items > 0)
    assert (capacity > 0)
