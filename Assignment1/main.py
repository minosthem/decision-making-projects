from questions import part1, part2And3, part5, part7
import yaml
import os
from os.path import exists, join

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


def main():
    """
    The main function used to call all necessary functions
    from questions package
    """
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
