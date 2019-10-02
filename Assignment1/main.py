from questions import part1, part2And3, part5, part7
import yaml
import os
from os.path import exists, join

properties_folder = join(os.getcwd(), "properties")
example_properties_file = join(properties_folder, "example_properties.yaml")
properties_file = join(properties_folder, "properties.yaml")


def load_properties():
    if exists(properties_file):
        with open(properties_file, 'r') as f:
            properties = yaml.safe_load(f)
    else:
        with open(example_properties_file, 'r') as f:
            properties = yaml.safe_load(f)
    output_folder_name = properties["output_folder_name"] if properties["output_folder_name"] else "output"
    output_folder = join(os.getcwd(), output_folder_name)
    if not exists(output_folder):
        os.mkdir(output_folder)
    return properties, output_folder


def main():
    print("Loading properties file")
    properties, output_folder = load_properties()
    print("Starting executing assignment parts")
    # part 1
    instances = part1.generate_problem_instances(properties=properties)
    # part 2 & 3
    part2And3.run_knapsack_for_problem_instance(instance=instances[0], properties=properties)
    # part 4 & 5
    part5.run_gurobi(problem_instances=instances, properties=properties, output_folder=output_folder)
    # part 7 SAA
    part7.run_sample_average_approximation(instance=instances[0], properties=properties)


if __name__ == '__main__':
    main()
