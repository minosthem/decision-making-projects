from itertools import product
from os.path import join
import gurobipy as gb
import utils


def run_gurobi(problem_instances):
    print("Running gurobi for each problem instance")
    for i, problem_instance in enumerate(problem_instances):
        item_indx = list(range(len(problem_instance.items)))
        scenarios, revenues, decision_combs, probabilities = get_model_data(problem_instance.items)

        print("Creating model for problem instance {}".format(i))
        model = gb.Model('MILP')
        obj = gb.LinExpr()

        for j, scenario in enumerate(scenarios):
            for z, decision_var in enumerate(decision_combs):
                # create model variable for scenario j and decision var vector z
                sizes = model.addVars(item_indx, vtype=gb.GRB.CONTINUOUS, name="sizes{}{}".format(j, z), lb=0)
                # calculate the total selected size based on the decision variables
                total_size_selected = total_selected_size(scenario, decision_var)
                # calculate the penalty based on the capacity and selected weights
                final_penalty = utils.penalty * (total_size_selected - utils.capacity)
                # calculate the objective function of the current scenario and decision var vector
                obj += probabilities[j] * (sum((scenario[k] * revenues[k] * decision_var[k]) * sizes[k]
                                               for k in item_indx) - final_penalty if final_penalty > 0 else sum(
                    (scenario[k] * revenues[k] * decision_var[k]) * sizes[k] for k in item_indx))
                rhs = total_size_selected - utils.capacity
                # TODO unbounded model??
                model.addConstr(lhs=gb.quicksum(sizes[k] for k in item_indx if decision_var[k] == 1),
                                sense=gb.GRB.LESS_EQUAL, rhs=utils.capacity, name="noPenalty{}{}".format(j, z))
                model.addConstr(lhs=gb.quicksum(sizes[k] for k in item_indx) - utils.capacity,
                                sense=gb.GRB.GREATER_EQUAL, rhs=rhs, name="scenario{}{}".format(j, z))
                model.addConstr(lhs=gb.quicksum(sizes[k] for k in item_indx) - utils.capacity,
                                sense=gb.GRB.GREATER_EQUAL, rhs=0, name="scenarioPositive{}{}".format(j, z))
        # set the objective function to the model
        print("Setting total objective function to model {}".format(i))
        model.setObjective(obj, gb.GRB.MAXIMIZE)
        print("Updating model {}".format(i))
        # update the model
        model.update()
        model.feasRelaxS(relaxobjtype=0, minrelax=True, vrelax=False, crelax=True)
        print("Optimizing model {}".format(i))
        # optimize the model
        model.optimize()
        check_model_status(model, i)


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


def check_model_status(model, problem_instance):
    status = model.status
    if status == gb.GRB.Status.OPTIMAL:
        print("Showing variables and objective function values for problem instance {}".format(problem_instance))
        for v in model.getVars():
            print('%s %g' % (v.varName, v.x))
        obj = model.getObjective()
        print('Profit: %g' % -obj.getValue())
        # mps extension for writing the model itself
        model.write(join(utils.output_folder, "model{}.mps".format(problem_instance)))
        # sol extension to write current solution
        model.write(join(utils.output_folder, "model{}.sol".format(problem_instance)))
    elif status == gb.GRB.Status.INFEASIBLE:
        print('Optimization was stopped with status %d' % status)
        # do IIS
        model.computeIIS()
        model.write(join(utils.output_folder, "model_iis{}.ilp".format(problem_instance)))
        for c in model.getConstrs():
            if c.IISConstr:
                print('%s' % c.constrName)
    elif status == gb.GRB.Status.INF_OR_UNBD:
        model.setParam("DualReductions", 0)
        model.optimize()
        check_model_status(model, problem_instance)
    elif status == gb.GRB.Status.UNBOUNDED:
        model.setObjective(0, gb.GRB.MAXIMIZE)
        model.optimize()
        check_model_status(model, problem_instance)
