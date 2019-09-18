# Assignment 1

## Part 1: SKP - Problem instances generation

For this part, we have created two classes to model the requirements of the assignment. The first class is called ProblemInstance to represent the generated instance and has only one field, i.e. a list with the generated items of this specific problem instance. Moreover, the second class is the Item class. The fields in this class are: the two possible sizes (i.e. dl and dh), the final size (based on the calculated probability), the probability pi and the ri. All the classes can be found in Assignment1/models package.

The file main.py is used to call all the necessary methods from the other python files. The code for this question can be found in Assignment1/questions/part1.py. The method generate_problem_instances is used to create 10 problem instances with 10 items each. For each item, dli, dhi, pi and ri are calculated and save in the respective fields of the Item object. All problem instances are save into a list which is then returned to the main program. For poisson and triangular distributions, numpy library is used (numpy.random.poisson and numpy.random.triangular) in order to generate random numbers for the items' sizes.


## Part 2: Heuristic Algorithm

This heuristic algorithm tries to find which items will be assigned to the knapsack regarding their value and size and with respect to the capacity constraint. I have created a function to solve this problem. First, an array with the items generated in the previous part is created