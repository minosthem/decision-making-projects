from questions import part5
from scipy import stats


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
        probabilities = [1 / 200] * saa_bernoulli_runs
        capacity = properties["capacity"]
        penalty = properties["penalty"]
        cvar_risks = properties["risks"]["cvar"]
        ev_risk = properties["risks"]["ev"]
        beta = properties["beta"]

        print("Executing EV model for instance")
        ev_model = part5.create_model_for_problem_instance(total_items, revenues, probabilities, item_indx, i=0,
                                                           capacity=capacity,
                                                           penalty=penalty, risk=ev_risk, output_folder=output_folder)
        ev_profits = calc_ev_profits(ev_model, probabilities, total_items, revenues, item_indx, penalty)
        run_dict["ev_model"] = ev_model
        run_dict["ev_profits"] = ev_profits
        run_dict["ev_total_profit"] = ev_model.getObjective().getValue()
        cvar_models = []
        all_cvar_profits = []
        cvar_total_profits = []
        for c, cvar_risk in enumerate(cvar_risks):
            print("Executing CVaR model for instance{} and CVaR risk {}".format(0, cvar_risk))
            model = part5.create_model_for_problem_instance(total_items, revenues, probabilities, item_indx, i=0,
                                                            capacity=capacity,
                                                            penalty=penalty,
                                                            risk=cvar_risk, output_folder=output_folder, beta=beta)
            cvar_models.append(model)
            cvar_profits = calc_cvar_profits(model, probabilities, total_items, revenues, item_indx, penalty, beta,
                                             cvar_risk)
            all_cvar_profits.append(cvar_profits)
            cvar_total_profits.append(model.getObjective().getValue())
        run_dict["cvar_models"] = cvar_models
        run_dict["all_cvar_profits"] = all_cvar_profits
        run_dict["cvar_total_profits"] = cvar_total_profits
        data_runs.append(run_dict)


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
            if "penalty_decision" in v.varName:
                tu = v.x
            elif "decision_var" in v.varName:
                decision_vars.append(v.x)
            elif "eta" in v.varName:
                h = v.x
            elif "sw" in v.varName:
                sw = v.x
        scenario_profit = (1 - beta) * probability * (
                sum(total_revenues[j] * decision_vars[j] for j in item_indx) - tu * penalty) + beta * (
                                  h - ((1 / (1 - risk)) * sum(probability * sw for probability in probabilities)))
        profits.append(scenario_profit)
    return profits
