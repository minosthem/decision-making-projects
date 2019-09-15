# global parameters
GROUP = 10
runs = 10
item_num = 10

capacity = 400 + (4 * GROUP)
penalty = 60 + (GROUP / 10)
risk = {"EN": 0, "CVaR": 0.95}
confidence_interval = 0.95
accuracy = 2
monte_carlo_runs = ((1.96 * (1 / 2)) / (10 ** -accuracy)) ** 2


def profit(revenue, items_not_included):
    return revenue - (penalty * items_not_included)
