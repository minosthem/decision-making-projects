from itertools import product
from os.path import join

import gurobipy as gb


def run_gurobi(problem_instances, properties, output_folder):
    """
    Method used by main.py, generates models for each problem instance.
    Uses properties dictionary to get the capacity and penalty params.
    :param problem_instances: the generated problem instances
    :param properties: dictionary with the properties from yaml file
    :param output_folder: the folder to save the models
    :return:
    """
    capacity = properties["capacity"]
    penalty = properties["penalty"]
    cvar_risks = properties["risks"]["cvar"]
    ev_risk = properties["risks"]["ev"]
    beta = properties["beta"]

    print("Running gurobi for each problem instance")
    for i, problem_instance in enumerate(problem_instances):
        item_indx = list(range(len(problem_instance.items)))
        scenarios, revenues, probabilities = get_model_data(problem_instance.items)
        print("Executing EV model for instance{}".format(i))
        create_model_for_problem_instance(scenarios, revenues, probabilities, item_indx, i=i, capacity=capacity,
                                          penalty=penalty, risk=ev_risk, output_folder=output_folder)
        for c, cvar_risk in enumerate(cvar_risks):
            print("Executing CVaR model for instance{} and CVaR risk {}".format(i, cvar_risk))
            create_model_for_problem_instance(scenarios, revenues, probabilities, item_indx, i=i, capacity=capacity,
                                              penalty=penalty,
                                              risk=cvar_risk, output_folder=output_folder, beta=beta)


def create_model_for_problem_instance(scenarios, revenues, probabilities, item_indx, i, capacity, penalty, risk,
                                      output_folder, beta=None):
    """
    Method executed for each problem instance. Generates the scenarios for size combinations (dl, dh)
    for all the items. Creates a model for this instance and iterates the possible scenarios
    :param scenarios: item scenarios
    :param revenues: list with the revenues of the items
    :param probabilities: scenarios' probabilities
    :param item_indx: list enumerating the number of items
    :param i: problem instance position in the list
    :param capacity: property from yaml file
    :param penalty: property from yaml file
    :param risk: model risk
    :param output_folder: the folder to store the model
    :param beta: beta param
    :return:
    """
    print("Creating model for problem instance {}".format(i))
    model = gb.Model('MILP')
    obj = gb.LinExpr()

    print("Executing scenarios")
    h = model.addVar(vtype=gb.GRB.CONTINUOUS, name="eta", lb=0)
    for j, scenario in enumerate(scenarios):
        execute_scenario(model=model, obj=obj, scenario=scenario, j=j, h=h, item_indx=item_indx,
                         capacity=capacity, penalty=penalty, risk=risk, beta=beta, probabilities=probabilities,
                         revenues=revenues)
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
    check_model_status(model, i, risk, probabilities, output_folder)
    return model


def execute_scenario(model, obj, scenario, j, h, item_indx, capacity, penalty, risk, beta, probabilities, revenues):
    """
    Method executed for each scenario. Calculates for each item its revenue i.e. size[i] * revenue[i]
    and stores them in a list. Updates the objective function with the current scenario and adds the
    relevant constraint
    :param model: the model of this problem instance
    :param obj: the objective function to be updated
    :param scenario: the current scenario, i.e. list of the sizes of the items
    :param j: the scenario's position in the list
    :param h: eta variable
    :param item_indx: the number of items
    :param capacity: property in the yaml file
    :param penalty: property in the yaml file
    :param risk: model risk
    :param beta: beta parm
    :param probabilities: the calculated probabilities of all the scenarios
    :param revenues: the revenue of each item stored in a list
    :return:
    """
    total_revenues = get_total_revenues(scenario, revenues)
    # create model variables for scenario j
    decision_vars = model.addVars(item_indx, vtype=gb.GRB.BINARY, name="decision_var{}".format(j), lb=0)
    tu = model.addVar(vtype=gb.GRB.CONTINUOUS, name="penalty_decision{}".format(j), lb=0)
    if risk == 0:
        # calculate the objective function of the current scenario and decision var vector
        obj += probabilities[j] * (sum(total_revenues[k] * decision_vars[k] for k in item_indx) - (tu * penalty))
        # add constraints
        model.addConstr((tu >= sum(scenario[k] * decision_vars[k] for k in item_indx) - capacity),
                        name="items_capacity{}".format(j))
        model.addConstr(lhs=tu, sense=gb.GRB.GREATER_EQUAL, rhs=0, name="tu_positive{}".format(j))
    else:

        sw = model.addVar(vtype=gb.GRB.CONTINUOUS, name="sw{}".format(j), lb=0)
        obj += (1 - beta) * (probabilities[j] * (sum(total_revenues[k] * decision_vars[k]
                                                     for k in item_indx) - (tu * penalty))) + beta * (
                       h - (1 / (1 - risk) * sum(probability * sw for probability in probabilities)))
        # add constraints
        model.addConstr((tu >= sum(scenario[k] * decision_vars[k] for k in item_indx) - capacity),
                        name="items_capacity{}".format(j))
        model.addConstr(lhs=tu, sense=gb.GRB.GREATER_EQUAL, rhs=0, name="tu_positive{}".format(j))
        model.addConstr(lhs=sw, sense=gb.GRB.GREATER_EQUAL, rhs=0, name="sw_positive{}".format(j))
        model.addConstr((sw >= h - sum(total_revenues[k] * decision_vars[k] - (tu * penalty) for k in item_indx)),
                        name="eta_constr{}".format(j))


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
    """
    Creates a list where in each position stores the result of size*revenue
    for each item
    :param sizes: the list of sizes of all items
    :param revenues: the list of the revenue of each item
    :return: list of the total revenue per item
    """
    total_revenues = []
    for i, size in enumerate(sizes):
        total_revenues.append(size * revenues[i])
    return total_revenues


def check_model_status(model, problem_instance, risk, probabilities, output_folder):
    """
    Checks the result of the model
    :param model: the generated model
    :param problem_instance: the respective problem instance
    :param risk: the model's risk
    :param probabilities: scenarios' probabilities
    :param output_folder: folder to store the model
    :return:
    """
    status = model.status
    if status == gb.GRB.Status.OPTIMAL:
        optimal_model(model=model, problem_instance=problem_instance, risk=risk, probabilities=probabilities,
                      output_folder=output_folder)
    elif status == gb.GRB.Status.INFEASIBLE:
        infeasible_model(model=model, problem_instance=problem_instance, risk=risk, output_folder=output_folder)
    elif status == gb.GRB.Status.INF_OR_UNBD:
        inf_or_unb_model(model=model, problem_instance=problem_instance, risk=risk, probabilities=probabilities,
                         output_folder=output_folder)
    elif status == gb.GRB.Status.UNBOUNDED:
        unbounded_model(model=model, problem_instance=problem_instance, risk=risk, probabilities=probabilities,
                        output_folder=output_folder)


def optimal_model(model, problem_instance, risk, probabilities, output_folder):
    """
     Print results for optimal model - Solution found!
    :param model: model for a specific problem instance
    :param problem_instance: problem instance's position
    :param risk: the model's risk
    :param probabilities: scenarios' probabilities
    :param output_folder: the folder to store the model
    """
    model_type = "EV" if risk == 0 else "CVaR"
    print("Showing variables and objective function values for problem instance {}".format(problem_instance))
    for v in model.getVars():
        print('%s %g' % (v.varName, v.x))
    obj = model.getObjective()
    print('Profit: %g' % obj.getValue())
    # mps extension for writing the model itself
    model.write(join(output_folder, "model{}{}.mps".format(model_type, problem_instance)))
    # sol extension to write current solution
    model.write(join(output_folder, "model{}{}.sol".format(model_type, problem_instance)))
    if model_type == "CVaR":
        sum_sw_p = 0
        for p, probability in enumerate(probabilities):
            for v in model.getVars():
                if "sw{}".format(p) in v.varName:
                    sum_sw_p += probability * v.x
        for v in model.getVars():
            if "eta" in v.varName:
                exp_sw = v.x - ((1 / (1 - risk)) * sum_sw_p)
                print("Expected sw is {}".format(exp_sw))


def infeasible_model(model, problem_instance, risk, output_folder):
    """
    Compute IIS if model is infeasible. Print the constraints and
    store the model in a file
    :param model: problem instance model
    :param problem_instance: the position in the list of problem instances
    :param risk: the model's risk
    :param output_folder: the folder to store the model
    """
    model_type = "EV" if risk == 0 else "CVaR"
    print('Optimization was stopped with status %d' % gb.GRB.Status.INFEASIBLE)
    # do IIS
    model.computeIIS()
    model.write(join(output_folder, "model_iis{}{}.ilp".format(model_type, problem_instance)))
    for c in model.getConstrs():
        if c.IISConstr:
            print('%s' % c.constrName)


def inf_or_unb_model(model, problem_instance, risk, probabilities, output_folder):
    """
    Model is either infeasible or unbounded. Set DualReductions parameter
    to zero in order to get a more precise response and re-optimize. Finally,
    calls again the check_model_status function
    :param model: problem instance model
    :param problem_instance: the position of the problem instance
    :param risk: the model's risk
    :param probabilities: scenarios' probabilities
    :param output_folder: the folder to store the model
    """
    model.setParam("DualReductions", 0)
    model.optimize()
    check_model_status(model, problem_instance, risk, probabilities, output_folder)


def unbounded_model(model, problem_instance, risk, probabilities, output_folder):
    """
    Model is unbounded. Set objective function to zero and re-optimize.
    Check the status of the model again to see if it is feasible
    :param model: problem instance model
    :param problem_instance: position of instance in the list
    :param risk: the model's risk
    :param probabilities: scenarios' probabilities
    :param output_folder: folder to store the model
    """
    model.setObjective(0, gb.GRB.MAXIMIZE)
    model.optimize()
    check_model_status(model, problem_instance, risk, probabilities, output_folder)
