from questions import part1, part2And3, part5
import utils
import os
from os.path import exists, join


def main():
    properties = utils.load_properties()
    output_folder_name = properties["output_folder_name"] if properties["output_folder_name"] else "output"
    output_folder = join(os.getcwd(), output_folder_name)
    if not exists(output_folder):
        os.mkdir(output_folder)
    # part 1
    instances = part1.generate_problem_instances(properties)
    # part 2 & 3
    part2And3.run_knapsack_for_problem_instance(instances[0], properties)
    # part 4 & 5
    part5.run_gurobi(instances, properties, output_folder)


if __name__ == '__main__':
    main()
