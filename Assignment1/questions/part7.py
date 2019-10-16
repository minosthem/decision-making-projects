from math import sqrt

from scipy import stats

from questions import part5


def run_sample_average_approximation(instance, properties, output_folder, bonus=False):
    """
    Executes SAA algorithms for part7 and bonus question. For the latter, only EV model
    is tested. Uniform distribution is used in order to get item sizes. For the bonus question
    we get two sizes and use their mean as item size.
    :param instance: the first problem instance
    :param properties: dictionary containing properties from yaml file
    :param output_folder: the output folder to store results
    :param bonus: boolean var determining if we run the bonus question
    """
    saa_runs = properties["saa_runs"]
    data_runs = []
    for run in range(saa_runs):
        run_dict = {}
        print("Running sample average approximation. Run {}".format(run))
        print("============================================")
        items = instance.items
        item_indx = list(range(len(items)))
        saa_bernoulli_runs = properties["saa_bernoulli_runs"]
        # total_items contain 200 lists (the scenarios) with 10 items each
        total_items = []
        for i in range(saa_bernoulli_runs):
            new_items = []
            for item in items:
                # generate item sizes using uniform distribution
                unif = stats.uniform(0, 1).rvs(1)
                if not bonus:
                    item.size = item.dh if unif[0] < item.pi else item.dl
                else:
                    size1 = item.dh if unif[0] < item.pi else item.dl
                    size2 = item.dh if (1 - unif[0]) < item.pi else item.dl
                    mean_size = (size1 + size2) / 2
                    item.size = mean_size
                new_items.append(item.size)
            total_items.append(new_items)
        revenues = [item.r for item in items]
        probabilities = [1 / saa_bernoulli_runs] * saa_bernoulli_runs
        capacity = properties["capacity"]
        penalty = properties["penalty"]
        cvar_risk = properties["risks"]["cvar"][0]
        ev_risk = properties["risks"]["ev"]
        beta = properties["beta"]

        # run EV model
        print("Executing EV model for instance")
        ev_model = part5.create_model_for_problem_instance(total_items, revenues, probabilities, item_indx, i=0,
                                                           capacity=capacity,
                                                           penalty=penalty, risk=ev_risk, output_folder=output_folder)
        ev_profits = calc_ev_profits(ev_model, total_items, revenues, item_indx, penalty)
        print("EVPROFS", ev_profits)
        ev_variance, ev_profits_mean = sample_variance(ev_profits, saa_bernoulli_runs)
        print("EV variance of scenario profits for run {} is {}".format(run, ev_variance))
        ev_upper_bound = ev_profits_mean + 1.64 * sqrt(ev_variance)
        run_dict["ev_upper_bound"] = ev_upper_bound
        run_dict["ev_model"] = ev_model
        run_dict["ev_profits"] = ev_profits
        run_dict["ev_total_profit"] = ev_model.getObjective().getValue()

        # run CVaR model for part 7
        if not bonus:
            print("Executing CVaR model for instance{} and CVaR risk {}".format(0, cvar_risk))
            cvar_model = part5.create_model_for_problem_instance(total_items, revenues, probabilities, item_indx, i=0,
                                                                 capacity=capacity,
                                                                 penalty=penalty,
                                                                 risk=cvar_risk, output_folder=output_folder, beta=beta)
            cvar_profits = calc_cvar_profits(cvar_model, total_items, revenues, item_indx, penalty, beta,
                                             cvar_risk)
            print("CVARPROFS", cvar_profits)
            run_dict["cvar_model"] = cvar_model
            run_dict["cvar_profits"] = cvar_profits
            run_dict["cvar_total_profit"] = cvar_model.getObjective().getValue()
            cvar_variance, cvar_profit_mean = sample_variance(cvar_profits, saa_bernoulli_runs)
            print("CVaR variance of scenario profits for run {} is {}".format(run, cvar_variance))
            cvar_upper_bound = cvar_profit_mean + (1.64 * sqrt(cvar_variance))
            run_dict["cvar_upper_bound"] = cvar_upper_bound
        data_runs.append(run_dict)
    get_ev_model_bounds_and_gap(data_runs, saa_runs)
    if not bonus:
        get_cvar_model_bounds_and_gap(data_runs, saa_runs)


def get_cvar_model_bounds_and_gap(data_runs, saa_runs):
    """
    Calculates the lower bound, upper bounds and gap for the CVaR model.
    This function is only used for part 7
    :param data_runs: the list with the dictionary data for each run
    :param saa_runs: the number of runs for the SAA algorithm (default  runs)
    """
    cvar_total_profits = []
    for run, data in enumerate(data_runs):
        cvar_total_profits.append(data["cvar_total_profit"])
    cvar_total_variance, cvar_total_profit_mean = sample_variance(cvar_total_profits, saa_runs)
    print("CVaR model runs variance is {}".format(cvar_total_variance))
    cvar_lower_bound = cvar_total_profit_mean - (1.84 * sqrt(cvar_total_variance))
    print("CVaR model lower bound is {}".format(cvar_lower_bound))
    for run, data in enumerate(data_runs):
        cvar_upper_bound = data["cvar_upper_bound"]
        print("CVaR model upper bound for run {} is {}".format(run, cvar_upper_bound))
        cvar_gap = cvar_upper_bound - cvar_lower_bound
        print("CVaR model gap for run {} is {}".format(run, cvar_gap))


def get_ev_model_bounds_and_gap(data_runs, saa_runs):
    """
        Calculates the lower bound, upper bounds and gap for the EV model.
        :param data_runs: the list with the dictionary data for each run
        :param saa_runs: the number of runs for the SAA algorithm (default  runs)
        """
    ev_total_profits = []
    for run, data in enumerate(data_runs):
        ev_total_profits.append(data["ev_total_profit"])
    ev_total_variance, ev_total_profit_mean = sample_variance(ev_total_profits, saa_runs)
    print("EV model runs variance is {}".format(ev_total_variance))
    ev_lower_bound = ev_total_profit_mean - (1.84 * sqrt(ev_total_variance))
    print("EV model lower bound is {}".format(ev_lower_bound))
    for run, data in enumerate(data_runs):
        ev_upper_bound = data["ev_upper_bound"]
        print("EV model upper bound for run {} is {}".format(run, ev_upper_bound))
        ev_gap = ev_upper_bound - ev_lower_bound
        print("EV model gap for run {} is {}".format(run, ev_gap))


def calc_ev_profits(model, total_items, revenues, item_indx, penalty):
    """
    Based on the EV model's objective function and the variable values, we calculate
    the profit of each scenario in EV model
    :param model: the created model
    :param total_items: the list of the scenarios (sizes)
    :param revenues: the list of the revenue of each item
    :param item_indx: a list with numbers 0-9
    :param penalty: the penalty to be assigned when capacity is exceeded
    :return: a list with the profit of each scenario
    """
    profits = []
    for i, scenario in enumerate(total_items):
        total_revenues = part5.get_total_revenues(scenario, revenues)
        decision_vars = []
        tu = None
        for v in model.getVars():
            if "penalty_decision{}".format(i) in v.varName:
                tu = v.x
            elif "decision_var{}".format(i) in v.varName:
                decision_vars.append(v.x)
        scenario_profit = sum(total_revenues[j] * decision_vars[j] for j in item_indx) - tu * penalty
        profits.append(scenario_profit)
    return profits


def calc_cvar_profits(model, total_items, revenues, item_indx, penalty, beta, risk):
    """
        Based on the CVaR model's objective function and the variable values, we calculate
        the profit of each scenario in CVaR model
        :param model: the created model
        :param total_items: the list of the scenarios (sizes)
        :param revenues: the list of the revenue of each item
        :param item_indx: a list with numbers 0-9
        :param penalty: the penalty to be assigned when capacity is exceeded
        :param beta: the beta param from properties
        :param risk: the model's risk
        :return: a list with the profit of each scenario
        """
    profits = []
    for i, scenario in enumerate(total_items):
        total_revenues = part5.get_total_revenues(scenario, revenues)
        decision_vars = []
        tu = None
        h = None
        sw = None
        for v in model.getVars():
            if "penalty_decision{}".format(i) in v.varName:
                tu = v.x
            elif "decision_var{}".format(i) in v.varName:
                decision_vars.append(v.x)
            elif "eta" in v.varName:
                h = v.x
            elif "sw{}".format(i) in v.varName:
                sw = v.x
        scenario_profit = (1 - beta) * (
                    sum(total_revenues[j] * decision_vars[j] for j in item_indx) - tu * penalty) + beta * (
                                      h - ((1 / (1 - risk)) * sw))
        profits.append(scenario_profit)
    return profits


def sample_variance(values, runs):
    mean_val = sum(values) / len(values)
    return sum(v - mean_val for v in values) ** 2 / (runs * (runs - 1)), mean_val
