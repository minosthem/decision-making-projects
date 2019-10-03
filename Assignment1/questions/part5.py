from itertools import product
from os.path import join

import gurobipy as gb


def run_gurobi(problem_instances, properties, output_folder):
    capacity = properties["capacity"]
    penalty = properties["penalty"]

    print("Running gurobi for each problem instance")
    for i, problem_instance in enumerate(problem_instances):
        create_model_for_problem_instance(problem_instance=problem_instance, i=i, capacity=capacity, penalty=penalty,
                                          output_folder=output_folder)


def create_model_for_problem_instance(problem_instance, i, capacity, penalty, output_folder):
    item_indx = list(range(len(problem_instance.items)))
    scenarios, revenues, probabilities = get_model_data(problem_instance.items)

    print("Creating model for problem instance {}".format(i))
    model = gb.Model('MILP')
    obj = gb.LinExpr()

    print("Executing scenarios")
    for j, scenario in enumerate(scenarios):
        execute_scenario(model=model, obj=obj, scenario=scenario, j=j, item_indx=item_indx, capacity=capacity,
                         penalty=penalty, probabilities=probabilities, revenues=revenues)
    # set the objective function to the model
    print("Setting total objective function to model {}".format(i))
    model.setObjective(obj, gb.GRB.MAXIMIZE)
    print("Updating model {}".format(i))
    # update the model
    model.update()
    print("Optimizing model {}".format(i))
    # optimize the model
    model.optimize()
    print("Getting model results")
    check_model_status(model, i, output_folder)


def execute_scenario(model, obj, scenario, j, item_indx, capacity, penalty, probabilities, revenues):
    total_revenues = get_total_revenues(scenario, revenues)
    # create model variables for scenario j
    decision_vars = model.addVars(item_indx, vtype=gb.GRB.BINARY, name="decision_var{}".format(j), lb=0)
    # calculate the objective function of the current scenario and decision var vector
    obj += probabilities[j] * (sum(total_revenues[k] * decision_vars[k] for k in item_indx) - (
            penalty * (sum(scenario[k] * decision_vars[k] for k in item_indx) - capacity)))

    # add constraints
    model.addConstr(lhs=(sum(scenario[k] * decision_vars[k] for k in item_indx) - capacity),
                    sense=gb.GRB.GREATER_EQUAL, rhs=0, name="constraint{}".format(j))


def get_model_data(items):
    """
    Based on the combinations for dl and dh, all sizes are created
    in the list new_scenarios. The function generates the combinations
    for sizes, the possibility of each scenario and a list of the revenue
    of each item of the problem instance
    :param items: the problem instance items
    :return: four lists with the size combinations, the revenues and the probabilities
    """
    new_scenarios = []
    scenarios = list(product(['dl', 'dh'], repeat=len(items)))
    revenues = [item.r for item in items]
    probabilities = []
    for i, scenario in enumerate(scenarios):
        new_scenario = []
        scenario_prob = 1
        for j, item in enumerate(items):
            new_scenario.append(item.dl if scenario[j] == 'dl' else item.dh)
            prob = item.pi if scenario[j] == 'dh' else (1 - item.pi)
            scenario_prob *= prob
        new_scenarios.append(new_scenario)
        probabilities.append(scenario_prob)
    return new_scenarios, revenues, probabilities


def get_total_revenues(sizes, revenues):
    total_revenues = []
    for i, size in enumerate(sizes):
        total_revenues.append(size * revenues[i])
    return total_revenues


def check_model_status(model, problem_instance, output_folder):
    status = model.status
    if status == gb.GRB.Status.OPTIMAL:
        print("Showing variables and objective function values for problem instance {}".format(problem_instance))
        for v in model.getVars():
            print('%s %g' % (v.varName, v.x))
        obj = model.getObjective()
        print('Profit: %g' % -obj.getValue())
        # mps extension for writing the model itself
        model.write(join(output_folder, "model{}.mps".format(problem_instance)))
        # sol extension to write current solution
        model.write(join(output_folder, "model{}.sol".format(problem_instance)))
    elif status == gb.GRB.Status.INFEASIBLE:
        print('Optimization was stopped with status %d' % status)
        # do IIS
        model.computeIIS()
        model.write(join(output_folder, "model_iis{}.ilp".format(problem_instance)))
        for c in model.getConstrs():
            if c.IISConstr:
                print('%s' % c.constrName)
    elif status == gb.GRB.Status.INF_OR_UNBD:
        model.setParam("DualReductions", 0)
        model.optimize()
        check_model_status(model, problem_instance, output_folder)
    elif status == gb.GRB.Status.UNBOUNDED:
        model.setObjective(0, gb.GRB.MAXIMIZE)
        model.optimize()
        check_model_status(model, problem_instance, output_folder)
