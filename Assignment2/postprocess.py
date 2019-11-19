import pandas
import os
def run(file_customers, file_loops, run_folder, run_id, burnin):
    cust = pandas.read_csv(file_customers)
    # apply burnin
    cust = cust[cust["arrival_index"].isin(list(range(burnin)))]

    results = []
    for prior in "high low".split():
        dprior = cust[cust.priority == prior]
        if len(dprior) == 0:
            pdout, pdin, pnd = 0, 0, 0
            continue
        # prob. of delay out
        pdout = len(dprior[dprior.delay_out == True]) / len(dprior)
        # prob. of delay in
        pdin = len(dprior[dprior.delay_in == True]) / len(dprior)
        # prob. no delay
        pnd = len(dprior[dprior.delay_in == False][dprior.delay_out == False]) / len(dprior)
        keys = [x + "_" + prior for x in "prob_nodelay prob_delayin prob_delayout".split()]
        results.extend(list(zip(keys, [pnd, pdin, pdout])))

    loops = pandas.read_csv(file_loops)

    # apply burnin to at least the number of customers have arrived
    loops = loops[loops["number_arrived"] >= burnin]

    for k, v in loops.mean().to_dict().items():
        if k.startswith("number_"):
            continue
        results.append(("mean_" + k, v))

    stats_file = os.path.join(run_folder, "{}_stats.csv".format(run_id))
    print("Writing run results to {}".format(stats_file))