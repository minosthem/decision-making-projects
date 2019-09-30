from questions import part1, part2And3, part5
import utils


def main():
    # part 1
    instances = part1.generate_problem_instances()
    # part 2 & 3
    part2And3.run_knapsack_for_problem_instance(instances[0], utils.capacity)
    # part 4 & 5
    part5.run_gurobi(instances)


if __name__ == '__main__':
    # TODO remove all line and uncomment main()
    # main()
    instances = part1.generate_problem_instances()
    part5.run_gurobi(instances)
