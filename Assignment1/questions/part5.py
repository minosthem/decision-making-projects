from itertools import product
from gurobipy import GRB, Model, LinExpr
import utils


def run_gurobi(problem_instances):
    print("Running gurobi for each problem instance")
    for i, problem_instance in enumerate(problem_instances):
        item_indx = list(range(len(problem_instance.items)))
        scenarios, revenues, decision_combs, probabilities = get_model_data(problem_instance.items)

        print("Creating model for problem instance {}".format(i))
        model = Model('MILP')
        obj = LinExpr()

        for j, scenario in enumerate(scenarios):
            for z, decision_var in enumerate(decision_combs):
                # create model variable for scenario j and decision var vector z
                sizes = model.addVars(item_indx, vtype=GRB.CONTINUOUS, name="sizes{}{}".format(j, z), lb=0)
                # calculate the total selected size based on the decision variables
                total_size_selected = total_selected_size(scenario, decision_var)
                # calculate the penalty based on the capacity and selected weights
                final_penalty = utils.penalty * (total_size_selected - utils.capacity)
                # calculate the objective function of the current scenario and decision var vector
                scenario_obj = probabilities[j] * (sum(sizes[k] * scenario[k] * revenues[k] * decision_var[k]
                                                       for k in item_indx) - final_penalty)
                rhs = total_size_selected - utils.capacity
                model.addConstr(lhs=sum(sizes) - utils.capacity, sense=GRB.GREATER_EQUAL, rhs=rhs,
                                name="scenario{}{}".format(j, z))
                model.addConstr(lhs=sum(sizes) - utils.capacity, sense=GRB.GREATER_EQUAL, rhs=0,
                                name="scenarioPositive{}{}".format(j, z))
                # add the objective function to the model's total objective function
                obj.add(scenario_obj)
        # set the objective function to the model
        print("Setting total objective function to model {}".format(i))
        model.setObjective(obj, GRB.MAXIMIZE)
        print("Updating model {}".format(i))
        # update the model
        model.update()
        print("Optimizing model {}".format(i))
        # optimize the model
        model.optimize()

        # TODO check why x attribute cannot be accessed
        print("Showing variables and objective function values for problem instance {}".format(i))
        for v in model.getVars():
            print('%s %g' % (v.varName, v.x))
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
    scenarios = list(product(['dl', 'dh'], repeat=len(items)))
    decision_combs = list(product([0, 1], repeat=len(items)))
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
        if decision_var == 1.0 or decision_var == 1:
            total_size += sizes[i]
    return total_size
