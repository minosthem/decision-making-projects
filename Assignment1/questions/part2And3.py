import numpy as np
from models.Item import Item
from models.MonteCarloSim import MonteCarloSim
from scipy import stats


def run_knapsack_for_problem_instance(instance, properties):
    """
    Gets a specific problem instance and the default container capacity.
    Creates a list of tuples for each item of each problem instance, containing the value of the item,
    its size and its position in the list and runs the knapsack problem.
    Then, monte carlo simulation is executed, based on Bernoulli distribution that defines if an item
    will be in the knapsack or not. Finally, the profit from the monte carlo simulation is
    calculated.
    :param instance: a specific problem instance
    :param properties: properties read from yaml file
    """
    print("Executing Knapsack problem")
    items = reform_items(instance.items)
    best_value = knapsack_dp(items, properties["capacity"], return_all=True)
    selected_items, total_revenue = get_knapsack_result(best_value, instance.items)
    print("Running monte carlo simulation for a small number of runs")
    sn_small_run = run_small_monte_carlo(properties=properties, selected_items=selected_items)
    if properties["run_full_runs_monte_carlo"]:
        run_full_monte_carlo(properties=properties, selected_items=selected_items, sn_small_run=sn_small_run)

# ================================== Knapsack Algorithm ================================================= #


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
                table[i, w] = (vi * wi) + table[i - 1, w - wi]
                keep[i, w] = 1
            else:
                table[i, w] = table[i - 1, w]

    picks = []
    remaining_capacity = capacity

    for i in range(n_items, 0, -1):
        if keep[i, remaining_capacity] == 1:
            picks.append(i)
            remaining_capacity -= weights[i - 1]

    picks.sort()
    picks = [x - 1 for x in picks]  # change to 0-index

    if return_all:
        max_val = table[n_items, capacity]
        return picks, max_val
    return picks


def get_knapsack_result(best_value, items):
    item_indices = best_value[0]
    total_revenue = best_value[1]
    print("Knapsack result")
    print("=========================================")
    print("Selected items ", item_indices)
    print("Total revenue: {}".format(total_revenue))
    print("=========================================")
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

# =================================== Monte Carlo Simulation ================================================= #


def run_small_monte_carlo(properties, selected_items):
    monte_carlo_runs = properties["small_run_monte_carlo"]
    profits = monte_carlo(monte_carlo_runs, selected_items, properties["capacity"], properties["penalty"])
    m = np.mean(profits)
    print("Profit mean is {}".format(m))

    # Construct a confidence interval
    sn_small_run = np.std(profits)
    half_width_small_run = 1.96 * sn_small_run / np.sqrt(int(monte_carlo_runs))
    ci = (m - half_width_small_run, m + half_width_small_run)
    print("Confidence interval is {}".format(ci))
    return sn_small_run


def run_full_monte_carlo(properties, selected_items, sn_small_run):
    monte_carlo_runs = (1 / (10 ** -properties["accuracy"])) ** 2
    print("Running monte carlo simulation for runs {}".format(int(monte_carlo_runs)))
    profits = monte_carlo(monte_carlo_runs, selected_items, properties["capacity"], properties["penalty"])
    m = np.mean(profits)
    print("Profit mean is {}".format(m))

    # Construct a confidence interval
    sn = np.std(profits)
    half_width = 1.96 * sn / np.sqrt(int(monte_carlo_runs))
    ci = (m - half_width, m + half_width)
    print("Confidence interval is {}".format(ci))


def monte_carlo(runs, selected_items, capacity, penalty):
    # monte carlo
    monte_carlo_runs = []
    profits = []
    for i in range(int(runs)):
        monte_carlo_sim = MonteCarloSim(i)
        new_items = []
        for j, old_item in enumerate(selected_items):
            item = Item(j)
            item.copy_item(old_item)
            unif = stats.uniform(0, 1).rvs(1)
            item.size = item.dh if unif[0] < item.pi else item.dl
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
        run_profit = total_revenue - (penalty * total_size_excluded)
        monte_carlo_sim.items = new_items
        monte_carlo_sim.profit = run_profit
        monte_carlo_runs.append(monte_carlo_sim)
        profits.append(run_profit)
    print_monte_carlo_result(monte_carlo_runs)
    return profits


def print_monte_carlo_result(monte_carlo_runs):
    print("Run\t\t\t\t\tItems\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tProfit")
    print("===================================================================================================")
    for monte_carlo_sim in monte_carlo_runs:
        printed = str(monte_carlo_sim.run) + "\t\t"
        for item in monte_carlo_sim.items:
            printed += "Item {}: {},".format(str(item.position), str(item.size))
        printed += "\t\t"
        printed += str(monte_carlo_sim.profit)
        printed += "\n"
        printed += "================================================================" \
                   "===================================\n"
        print(printed)
