from questions import part5
from scipy import stats
import numpy as np
from math import sqrt


def run_sample_average_approximation(instance, properties, output_folder):
    saa_runs = properties["saa_runs"]
    data_runs = []
    for run in range(saa_runs):
        run_dict = {}
        print("Running sample average approximation. Run {}".format(run))
        print("====================================")
        items = instance.items
        item_indx = list(range(len(items)))
        saa_bernoulli_runs = properties["saa_bernoulli_runs"]
        total_items = []
        for i in range(saa_bernoulli_runs):
            new_items = []
            for item in items:
                bernoulli_res = stats.bernoulli(item.pi).rvs(1)
                item.size = item.dh if bernoulli_res[0] == 1 else item.dl
                new_items.append(item.size)
            total_items.append(new_items)
        revenues = [item.r for item in items]
        probabilities = [1 / saa_bernoulli_runs] * saa_bernoulli_runs
        capacity = properties["capacity"]
        penalty = properties["penalty"]
        cvar_risk = properties["risks"]["cvar"][0]
        ev_risk = properties["risks"]["ev"]
        beta = properties["beta"]

        print("Executing EV model for instance")
        ev_model = part5.create_model_for_problem_instance(total_items, revenues, probabilities, item_indx, i=0,
                                                           capacity=capacity,
                                                           penalty=penalty, risk=ev_risk, output_folder=output_folder)
        ev_profits = calc_ev_profits(ev_model, probabilities, total_items, revenues, item_indx, penalty)
        ev_profits_mean = np.mean(ev_profits)
        ev_variance = sum(
            (ev_profits[k] - ev_profits_mean) ** 2 for k in range(saa_bernoulli_runs)) / saa_bernoulli_runs * (
                              saa_bernoulli_runs - 1)
        print("EV variance of scenario profits for run {} is {}".format(run, ev_variance))
        ev_upper_bound = ev_profits_mean + 1.64 * sqrt(ev_variance)
        run_dict["ev_upper_bound"] = ev_upper_bound
        run_dict["ev_model"] = ev_model
        run_dict["ev_profits"] = ev_profits
        run_dict["ev_total_profit"] = ev_model.getObjective().getValue()

        print("Executing CVaR model for instance{} and CVaR risk {}".format(0, cvar_risk))
        cvar_model = part5.create_model_for_problem_instance(total_items, revenues, probabilities, item_indx, i=0,
                                                             capacity=capacity,
                                                             penalty=penalty,
                                                             risk=cvar_risk, output_folder=output_folder, beta=beta)
        cvar_profits = calc_cvar_profits(cvar_model, probabilities, total_items, revenues, item_indx, penalty, beta,
                                         cvar_risk)
        run_dict["cvar_model"] = cvar_model
        run_dict["cvar_profits"] = cvar_profits
        run_dict["cvar_total_profit"] = cvar_model.getObjective().getValue()

        cvar_profit_mean = np.mean(cvar_profits)
        print("CVaR profit mean is {}".format(cvar_profit_mean))
        cvar_variance = sum(
            (cvar_profits[k] - cvar_profit_mean) ** 2 for k in range(saa_bernoulli_runs)) / saa_bernoulli_runs * (
                                saa_bernoulli_runs - 1)
        print("CVaR variance of scenario profits for run {} is {}".format(run, cvar_variance))
        cvar_upper_bound = cvar_profit_mean + (1.64 * sqrt(cvar_variance))
        run_dict["cvar_upper_bound"] = cvar_upper_bound
        data_runs.append(run_dict)

    ev_total_profits = []
    cvar_total_profits = []
    for run, data in enumerate(data_runs):
        ev_total_profits.append(data["ev_total_profit"])
        cvar_total_profits.append(data["cvar_total_profit"])
    ev_total_profit_mean = np.mean(ev_total_profits)
    cvar_total_profit_mean = np.mean(cvar_total_profits)
    ev_total_variance = sum(
        (ev_total_profits[i] - ev_total_profit_mean) ** 2 for i in range(len(ev_total_profits))) / saa_runs * (
                                saa_runs - 1)
    print("EV model runs variance is {}".format(ev_total_variance))
    cvar_total_variance = sum(
        (cvar_total_profits[i] - cvar_total_profit_mean) ** 2 for i in range(len(cvar_total_profits))) / saa_runs * (
                                  saa_runs - 1)
    print("CVaR model runs variance is {}".format(cvar_total_variance))
    ev_lower_bound = ev_total_profit_mean - (1.84 * sqrt(ev_total_variance))
    print("EV model lower bound is {}".format(ev_lower_bound))
    cvar_lower_bound = cvar_total_profit_mean - (1.84 * sqrt(cvar_total_variance))
    print("CVaR model lower bound is {}".format(cvar_lower_bound))

    for run, data in enumerate(data_runs):
        ev_upper_bound = data["ev_upper_bound"]
        print("EV model upper bound for run {} is {}".format(run, ev_upper_bound))
        cvar_upper_bound = data["cvar_upper_bound"]
        print("CVaR model upper bound for run {} is {}".format(run, cvar_upper_bound))
        ev_gap = ev_upper_bound - ev_lower_bound
        print("EV model gap for run {} is {}".format(run, ev_gap))
        cvar_gap = cvar_upper_bound - cvar_lower_bound
        print("CVaR model gap for run {} is {}".format(run, cvar_gap))


def calc_ev_profits(model, probabilities, total_items, revenues, item_indx, penalty):
    profits = []
    for i, scenario in enumerate(total_items):
        total_revenues = part5.get_total_revenues(scenario, revenues)
        probability = probabilities[i]
        decision_vars = []
        tu = None
        for v in model.getVars():
            if "penalty_decision" in v.varName:
                tu = v.x
            elif "decision_var" in v.varName:
                decision_vars.append(v.x)
        scenario_profit = probability * (sum(total_revenues[j] * decision_vars[j] for j in item_indx) - tu * penalty)
        profits.append(scenario_profit)
    return profits


def calc_cvar_profits(model, probabilities, total_items, revenues, item_indx, penalty, beta, risk):
    profits = []
    for i, scenario in enumerate(total_items):
        total_revenues = part5.get_total_revenues(scenario, revenues)
        probability = probabilities[i]
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
        scenario_profit = (1 - beta) * probability * (
                sum(total_revenues[j] * decision_vars[j] for j in item_indx) - tu * penalty) + beta * (
                                  h - ((1 / (1 - risk)) * probabilities[i] * sw))
        profits.append(scenario_profit)
    return profits
