from itertools import product
from gurobipy import GRB, Model, LinExpr
import utils
import numpy as np


def run_gurobi(problem_instances):
    print("Running gurobi for each problem instance")
    for i, problem_instance in enumerate(problem_instances):
        item_indx = list(range(len(problem_instance.items)))
        scenarios, revenues, decision_combs, probabilities = get_model_data(problem_instance.items)

        print("Creating model for problem instance {}".format(i))
        model = Model('MILP')
        obj = LinExpr()

        for j, scenario in enumerate(scenarios):
            sizes = model.addVars(item_indx, vtype=GRB.CONTINUOUS, name="sizes{}".format(j), lb=0)
            decision_var = model.addVars(item_indx, vtype=GRB.BINARY, name="decisionvar{}".format(j), lb=0)
            total_size_selected = total_selected_size(scenario, decision_combs[j])
            # TODO check decision variables - how to provide them to the obj
            scenario_obj = probabilities[j] * (sum(sizes[k] * revenues[k] * decision_combs[j][k] for k in item_indx) - (
                    utils.penalty * (total_size_selected - utils.capacity)))
            model.addConstr(
                ((sum(sizes[k]) - utils.capacity) >= (sum(sizes[k] * decision_var[k]) - utils.capacity) for k
                 in range(len(item_indx))), name="scenario{}".format(j))
            model.addConstr(((sum(sizes[k]) - utils.capacity) >= 0 for k in
                             range(len(item_indx))), name="scenarioPositive{}".format(j))
            # model.addConstr(lhs=tu, sense=GRB.GREATER_EQUAL, rhs=total_size_selected, name="scenario{}".format(j))
            # model.addConstr(lhs=tu, sense=GRB.GREATER_EQUAL, rhs=0, name="scenarioPositive{}".format(j))
            obj.add(scenario_obj)
        model.setObjective(obj, GRB.MAXIMIZE)
        model.update()
        model.optimize()

        # TODO check why x attribute cannot be accessed
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
    scenarios = list(product(['dl', 'dh'], repeat=10))
    decision_combs = list(product([0, 1], repeat=10))
    new_decision_combs = []
    revenues = [item.r for item in items]
    probabilities = []
    for i, scenario in enumerate(scenarios):
        new_scenario = {}
        dec = decision_combs[i]
        decision_vars = {}
        scenario_prob = 1
        for j, item in enumerate(items):
            new_scenario[j] = item.dl if scenario[j] == 'dl' else item.dh
            decision_vars[j] = dec[j]
            prob = item.pi if scenario[j] == 'dh' else (1 - item.pi)
            scenario_prob *= prob
        new_scenarios.append(new_scenario)
        new_decision_combs.append(decision_vars)
        probabilities.append(scenario_prob)
    return new_scenarios, revenues, new_decision_combs, probabilities


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
