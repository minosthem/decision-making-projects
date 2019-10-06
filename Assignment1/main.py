from questions import part1, part2And3, part5, part7
import yaml
import os
from os.path import exists, join
import sys

properties_folder = join(os.getcwd(), "properties")
example_properties_file = join(properties_folder, "example_properties.yaml")
properties_file = join(properties_folder, "properties.yaml")


def load_properties():
    """
    Load yaml file containint program's properties
    :return: the properties dictionary and the output folder path
    """
    file = properties_file if exists(properties_file) else example_properties_file
    with open(file, 'r') as f:
        properties = yaml.safe_load(f)
    return properties, create_output_folder(properties)


def create_output_folder(properties):
    """
    Based on the provided output folder name, create the directory
    if it does not exist and return the full path
    :param properties: the dictionary with the input properties
    :return: the output folder path
    """
    output_folder_name = properties["output_folder_name"] if properties["output_folder_name"] else "output"
    output_folder = join(os.getcwd(), output_folder_name)
    if not exists(output_folder):
        os.mkdir(output_folder)
    return output_folder


def print_problem_instances(problem_instances):
    for problem_instance in problem_instances:
        print(problem_instance)


def main():
    """
    The main function used to call all necessary functions
    from questions package
    """
    print("Loading properties file")
    properties, output_folder = load_properties()
    orig_stdout = sys.stdout
    f = open(join(output_folder, "logs{}{}{}.txt".format(len(properties["risks"]["cvar"]), properties["penalty"],
                                                         properties["capacity"])), 'w')
    sys.stdout = f
    print("Starting executing assignment parts")
    step = properties["step"]
    # part 1
    instances = part1.generate_problem_instances(properties=properties)
    print(instances)
    # part 2 & 3
    if 2 or 3 in step:
        part2And3.run_knapsack_for_problem_instance(instance=instances[0], properties=properties)
    # part 5
    if 5 in step:
        part5.run_gurobi(problem_instances=instances, properties=properties, output_folder=output_folder)
    # part 7 SAA
    if 7 in step:
        part7.run_sample_average_approximation(instance=instances[0], properties=properties,
                                               output_folder=output_folder)
        print("Running Sample Average Approximation - bonus question")
        print("=====================================================")
        # bonus
        part7.run_sample_average_approximation(instance=instances[0], properties=properties,
                                               output_folder=output_folder, bonus=True)
    sys.stdout = orig_stdout
    f.close()


if __name__ == '__main__':
    main()
