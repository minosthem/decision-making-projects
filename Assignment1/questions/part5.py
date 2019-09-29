from itertools import product

import gurobipy as gb

import utils


def run_gurobipy(problem_instances):
    for i, problem_instance in enumerate(problem_instances):
        model = gb.Model('MILP')
        senarios = get_all_combinations()
        new_senarios, revenues, new_decision_combs, probabilities = get_model_data(senarios, problem_instance.items)
        obj = gb.LinExpr()
        for j, senario in enumerate(senarios):
            sizes = model.addVars(10, vtype=gb.GRB.CONTINUOUS, name="sizes", lb=0)
            revs = model.addVars(10, vtype=gb.GRB.CONTINUOUS, name="revs", lb=0)
            decision_vars = model.addVars(10, vtype=gb.GRB.BINARY, name="decision_var")
            for k in range(10):
                obj += senario[k] * sizes[k]
                pass
            for k in range(10):
                obj += revenues[k] * revs[k]
            for k in range(10):
                obj += new_decision_combs[j][k] * decision_vars[k]
            total_size = total_selected_size(senario, new_decision_combs[j])
            if total_size > utils.capacity:
                obj -= (utils.penalty * (total_size - utils.capacity))


def get_all_combinations():
    return list(product(['dl', 'dh'], repeat=10))


def get_decision_combinations():
    return list(product([0, 1], repeat=10))


def get_model_data(senarios, items):
    new_senarios = []
    decision_combs = get_decision_combinations()
    new_decision_combs = []
    revenues = get_item_revenues_vector(items)
    probabilities = []
    for i, senario in enumerate(senarios):
        new_senario = {}
        dec = decision_combs[i]
        decision_vars = {}
        senario_prob = 1
        for j, item in enumerate(items):
            new_senario[j] = item.dl if senario[j] == 'dl' else item.dh
            decision_vars[j] = dec[j]
            prob = item.pi if senario[j] == 'dh' else (1 - item.pi)
            senario_prob *= prob
        new_senarios.append(new_senario)
        new_decision_combs.append(decision_vars)
        probabilities.append(senario_prob)
    return new_senarios, revenues, new_decision_combs, probabilities


def get_item_revenues_vector(items):
    return [item.r for item in items]


def total_selected_size(sizes, decision_vars):
    total_size = 0
    for i, decision_var in enumerate(decision_vars):
        if decision_var == 1.0:
            total_size += sizes[i]
    return total_size
