import gurobipy as gb
from itertools import product
import utils


def run_gurobipy(problem_instances):
    for i, problem_instance in enumerate(problem_instances):
        model = gb.Model('MILP')
        senarios = get_all_combinations()
        senarios, probabilities = select_size_items(senarios, problem_instance.items)
        decision_comb = get_decision_combinations()
        revenues = get_item_revenues_vector(problem_instance.items)
        obj = gb.LinExpr()
        for j, senario in enumerate(senarios):
            sizes = model.addVars(10, vtype=gb.GRB.CONTINUOUS, name="sizes", lb=0)
            decision_vars = model.addVars(10, vtype=gb.GRB.BINARY, name="decision_var")
            for k, item in enumerate(senario):
                s = sizes[k] * item * revenues[k]
               # d = decision_vars[k] * decision_comb[j][k]
                obj += (s)
            if obj.getValue() < utils.capacity:
                obj -= (utils.penalty * (obj - utils.capacity))


def get_all_combinations():
    return list(product(['dl', 'dh'], repeat=10))


def get_decision_combinations():
    return list(product([0, 1], repeat=10))


def select_size_items(senarios, items):
    new_senarios = []
    probabilities = []
    for senario in senarios:
        new_senario = {}
        senario_prob = 1
        for i, item in enumerate(items):
            new_senario[i] = item.dl if senario[i] == 'dl' else item.dh
            prob = item.pi if senario[i] == 'dh' else (1 - item.pi)
            senario_prob *= prob
        new_senarios.append(new_senario)
        probabilities.append(senario_prob)
    return new_senarios, probabilities


def get_item_revenues_vector(items):
    return [item.r for item in items]


def total_selected_size(sizes, decision_vars):
    total_size = 0
    for i, decision_var in enumerate(decision_vars):
        if decision_var == 1.0:
            total_size += sizes[i]