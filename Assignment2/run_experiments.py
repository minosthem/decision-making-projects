import yaml
import postprocess
import experiment
from os.path import join, exists
import os
import logging

properties_folder = join(os.getcwd(), "properties")
example_properties_file = join(properties_folder, "example_properties.yaml")
properties_file = join(properties_folder, "properties.yaml")


def load_properties():
    """
    Load yaml file containing program's properties
    :return: the properties dictionary and the output folder path
    """
    ffile = properties_file if exists(properties_file) else example_properties_file
    with open(ffile, 'r') as f:
        properties = yaml.safe_load(f)
    if "max_total_admitted" not in properties:
        properties["max_total_admitted"] = None
    return properties


def create_output_dir(properties):
    output_dir = properties["output_dir"] if properties["output_dir"] else "output"
    if not exists(output_dir):
        os.mkdir(output_dir)


def start_execution(n_values, lambda_h, lambda_l, deltas, probability_stay):
    # set the non-changing parameters here
    properties = load_properties()
    create_output_dir(properties=properties)

    # .... and the rest
    for N in n_values:
        for lh in lambda_h:
            for ll in lambda_l:
                for delta in deltas:
                    logging.info("Running experiment with params N {} lh {} ll {}".format(N, lh, ll))
                    run_id = "run_N{}_lh{}_ll{}".format(N, lh, ll)
                    # set the changing parameters here
                    properties["delta"] = delta
                    properties["poisson_lambda_high_priority"] = lh
                    properties["poisson_lambda_low_priority"] = ll
                    properties["run_id"] = run_id
                    # ....
                    # output file check
                    outfile = os.path.join(properties["output_dir"], "{}_stats.csv".format(run_id))
                    if os.path.exists(outfile):
                        print("Run {} already completed, skipping.".format(run_id))
                        continue

                    # write configuration
                    with open(properties_file, "w") as f:
                        yaml.dump(properties, f)
                    # run the experiment
                    # either import the run.py as a library
                    # or run it with sys.cmd or subprocess.run
                    experiment.run_experiment(properties=properties)
                    # get output file names (customer, loops)
                    file_c = join(properties["output_dir"], "{}_customers.csv".format(properties["run_id"]))
                    file_l = join(properties["output_dir"], "{}_loops.csv".format(properties["run_id"]))
                    # after experiment is done, run the postprocess.py on the resulting files to get desired statistics
                    postprocess.run(file_c, file_l, properties["output_dir"], run_id, properties["num_burnin"])


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger().debug("TEST")
    n = [5, 10, 20]
    lhs = [0.4, 0.6]
    lls = [0.4, 0.6]
    d = [0.2, 0.3, 0.5]
    prob_stay = [0.2, 0.3, 0.5]
    start_execution(n, lhs, lls, d, prob_stay)
