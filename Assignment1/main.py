from questions import part1, part2And3
import utils


if __name__ == '__main__':
    # part 1
    instances, weight_tuples = part1.generate_problem_instances()
    # part 2 & 3
    part2And3.run_knapsack_for_problem_instance(instances[0], utils.capacity)
