import gurobipy as gb
from itertools import product


def run_gurobipy(problem_instances):
    for i, problem_instance in enumerate(problem_instances):
        model = gb.Model()

        senarios = get_all_combinations()
        senarios, probabilities = select_size_items(senarios, problem_instance.items)


def get_all_combinations():
    return list(product(['dl', 'dh'], repeat=10))


def select_size_items(senarios, items):
    new_senarios = []
    probabilities = []
    for senario in senarios:
        new_senario = []
        senario_prob = 1
        for i, item in enumerate(items):
            new_senario.append(item.dl if senario[i] == 'dl' else item.dl)
            prob = item.pi if senario[i] == 'dh' else (1 - item.pi)
            senario_prob *= prob
        new_senarios.append(new_senario)
        probabilities.append(senario_prob)
    return new_senarios, probabilities
