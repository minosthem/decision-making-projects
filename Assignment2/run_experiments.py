import yaml
N_values = [5, 10, 20]
lambda_h = [0.4, 0.6]
lambda_l = [0.4, 0.6]

config = {} # set the non-changing parameters here

# .... and the rest
for N in N_values:
    for lh in lambda_h values:
        for ll in lambda_l values:

            run_id = "run_N{}_lh{}_ll{}".format(N, lh, ll)
            # set the changing parameters here
            config["exp_params"] = [lh, ll]
            config["run_id"] = run_id
            # ....
            # write configuration
            with open("properties.yml", "w") as f:
                yaml.dump(config, f)
            # run the experiment
            # either import the run.py as a library
            # or run it with sys.cmd or subprocess.run

            # get output file names (customer, loops)
            file_c, file_l = "", "" #....
            # after experiment is done, run the postprocess.py on the resulting files to get desired statistics 
            postprocess.run(file_c, file_l)
            
