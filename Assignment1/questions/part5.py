from itertools import product

import gurobipy as gb

import utils


def run_gurobipy(problem_instances):
    print("Running gurobi for each problem instance")
    for i, problem_instance in enumerate(problem_instances):
        print("Creating model for problem instance {}".format(i))
        model = gb.Model('MILP')
        item_indx = list(range(len(problem_instance.items)))
        scenarios, revenues, decision_combs, probabilities = get_model_data(problem_instance.items)
        obj = gb.LinExpr()
        for j, scenario in enumerate(scenarios):
            senario_obj = gb.LinExpr()
            sizes = model.addVars(item_indx, vtype=gb.GRB.CONTINUOUS, name="sizes{}".format(j), lb=0)
            total_size = total_selected_size(scenario, decision_combs[j])
            tu = total_size - utils.capacity
            for k in item_indx:
                senario_obj += sizes[k] * (scenario[k] * revenues[k] * decision_combs[j][k])
            if total_size > utils.capacity:
                senario_obj -= utils.penalty * (total_size - utils.capacity)
            senario_obj *= probabilities[j]
            model.addConstr(lhs=tu, sense=gb.GRB.GREATER_EQUAL, rhs=total_size, name="scenario{}".format(j))
            model.addConstr(lhs=tu, sense=gb.GRB.GREATER_EQUAL, rhs=0, name="scenarioPositive{}".format(j))
            obj.add(senario_obj)
        model.setObjective(obj, gb.GRB.MAXIMIZE)
        model.update()
        model.optimize()

        print("Showing variables and objective function values for problem instance {}".format(i))
        for v in model.getVars():
            print('%s %g' % (v.varName, v.X))
        obj = model.getObjective()
        print('Profit: %g' % -obj.getValue())


def get_model_data(items):
    """
    Based on the combinations for dl and dh, all sizes are created
    in the list new_scenarios. The function generates the combinations
    for sizes, decision variables, the possibility of each scenario
    and a list of the revenue of each item of the problem instance
    :param items: the problem instance items
    :return: four lists with the scenarios (i.e. sizes), the revenues, the
    decision variables and the probabilities
    """
    new_scenarios = []
    senarios = get_all_combinations()
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
        new_scenarios.append(new_senario)
        new_decision_combs.append(decision_vars)
        probabilities.append(senario_prob)
    return new_scenarios, revenues, new_decision_combs, probabilities


def get_all_combinations():
    """
    Uses product function from itertools to create all combinations of dl and dh
    for the ten items of each problem instance
    :return: the combinations
    """
    return list(product(['dl', 'dh'], repeat=10))


def get_decision_combinations():
    """
    Uses product function from itertools to generate all
    possible combinations of values 0 and 1 for the 10 items
    of each problem instance
    :return: the list of the combinations
    """
    return list(product([0, 1], repeat=10))


def get_item_revenues_vector(items):
    """
    Creates a list with the revenue of each item
    :param items: the problem instance items
    :return: list with the respective revenues
    """
    return [item.r for item in items]


def total_selected_size(sizes, decision_vars):
    """
    Calculates the total selected size based on the
    decision variables and the item sizes
    :param sizes: the sizes of the items
    :param decision_vars: list with binary values (0,1)
    :return: the total size of the items with decision variable 1
    """
    total_size = 0
    for i, decision_var in enumerate(decision_vars):
        if decision_var == 1.0:
            total_size += sizes[i]
    return total_size
