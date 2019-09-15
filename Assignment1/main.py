from questions import part2And3, part1
import utils


if __name__ == '__main__':
    # main()
    # part 1
    instances = part1.generate_problem_instances()
    # part 2 & 3
    part2And3.run_knapsack_for_problem_instance(instances[0], utils.capacity)
