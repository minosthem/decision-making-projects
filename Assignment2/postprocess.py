import pandas
import os
import math


def run(file_customers, file_loops, run_folder, run_id, burnin, max_total_admitted):
    cust = pandas.read_csv(file_customers)
    # apply burnin
    cust = cust[cust["arrival_index"] >= burnin]

    results = []
    for prior in "high low".split():
        dprior = cust[cust.priority == prior]
        if len(dprior) == 0:
            pdout, pdin, pnd, waits_mean, conf_int = 0, 0, 0, 0, (0, 0)
        else:
            # prob. of delay out
            pdout = len(dprior[dprior.delay_out == True]) / len(dprior)
            # prob. of delay in
            pdin = len(dprior[dprior.delay_in == True]) / len(dprior)
            # prob. no delay
            pnd = len(dprior[dprior.delay_in == False][dprior.delay_out == False]) / len(dprior)

            waits = dprior.waited_in + dprior.waited_out

            waits_mean = waits.mean()
            waits_var = waits.var()

            offset = 1.96 * math.sqrt(waits_var / 1000)
            conf_int = waits_mean - offset, waits_mean + offset

        keys = [x + "_" + prior for x in "prob_nodelay prob_delayin prob_delayout mean_waiting_time conf_int".split()]
        results.extend(list(zip(keys, [pnd, pdin, pdout, waits_mean, conf_int])))

    loops = pandas.read_csv(file_loops)

    # apply burnin to at least the number of customers have arrived
    loops = loops[loops["number_arrived"] >= burnin]

    for k, v in loops.mean().to_dict().items():
        if k.startswith("number_"):
            continue
        results.append(("mean_" + k, v))

    results = {k: [v] for (k, v) in results}
    results = pandas.DataFrame(results)
    results["max_total_admitted"] = max_total_admitted
    stats_file = os.path.join(run_folder, "{}_stats.csv".format(run_id))
    print("Writing run results to {}".format(stats_file))
    results.to_csv(stats_file, index=None)
