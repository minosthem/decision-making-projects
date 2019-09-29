from itertools import product

import gurobipy as gb

import utils


def run_gurobipy(problem_instances):
    for i, problem_instance in enumerate(problem_instances):
        model = gb.Model('MILP')
        item_indx = list(range(10))
        senarios = get_all_combinations()
        new_senarios, revenues, new_decision_combs, probabilities = get_model_data(senarios, problem_instance.items)
        obj = gb.LinExpr()
        for j, senario in enumerate(new_senarios):
            senario_obj = gb.LinExpr()
            sizes = model.addVars(item_indx, vtype=gb.GRB.CONTINUOUS, name="sizes{}".format(j), lb=0)

            total_size = total_selected_size(senario, new_decision_combs[j])
            tu = total_size - utils.capacity
            for k in item_indx:
                senario_obj += sizes[k] * (senario[k] * revenues[k] * new_decision_combs[j][k])
            if total_size > utils.capacity:
                senario_obj -= utils.penalty * (total_size - utils.capacity)
            senario_obj *= probabilities[j]
            model.addConstr(lhs=tu, sense=gb.GRB.GREATER_EQUAL, rhs=total_size, name="scenario{}".format(j))
            model.addConstr(lhs=tu, sense=gb.GRB.GREATER_EQUAL, rhs=0, name="scenarioPositive{}".format(j))
            obj.add(senario_obj)
        model.setObjective(obj, gb.GRB.MAXIMIZE)
        model.update()
        model.optimize()

        for v in model.getVars():
            print('%s %g' % (v.varName, v.X))
        obj = model.getObjective()
        print('Profit: %g' % -obj.getValue())


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
