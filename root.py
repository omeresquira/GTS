import random
from insertion_huristic import *
import get_data as g
import numpy

random.seed(0)
# sol - a solution to destract
# q - number of orders to remove from the solution
# k - a number in R+, degree of randomness, less randomness when k is larger k
k = 5
q = 5
n = 20


# find_best_sol func runs removal_huristic and basic_greedy n times to find best solution
def find_best_sol(q, k, n):
    all_orders = list(g.N1)
    # creates empty solution
    empty_sol = [[[Stop(0, 0, 0), Stop(g.N2, 0, 0)]] for k in range(int(g.T))]
    # insert all orders to create an initial solution
    sol = find_initial_sol(all_orders, empty_sol)
    #checks if the solution is valid
    test_sol(sol)
    best_sol =[sol, calc_target_objective(sol)]
    temp_sol = copy.deepcopy(sol)
    result = {"target function":[best_sol[1]]}
    for i in range(n):
        removed_sol, chosen_orders = removal_huristic.shaw_removal_huristic(temp_sol, q, k)
        temp_sol = basic_greedy(removed_sol, chosen_orders)
        test_sol(temp_sol)
        objective = calc_target_objective(temp_sol)
        # saves best solution if one was found
        if objective < best_sol[1]:
            best_sol[0] = temp_sol
            best_sol[1] = objective
            print best_sol
            print best_sol[1]
        result["target function"].append(objective)
##    # deletes empty vehicles
##    for day in range(len(sol)):
##        for vehicle in range(len(sol[day]) - 1, -1, -1):
##            if len(sol[day][vehicle]) == 2:
##                sol[day].pop(vehicle)

    return result, best_sol

def find_initial_sol(orders, sol):
    orders_copy = copy.deepcopy(orders)
    while len(orders_copy)>0:
        for i in orders_copy:
            order_data = minimum_insertion_cost(i, sol)
            sol = insert_order(sol, order_data, i)
            orders_copy.remove(i)
    print "init", sol
    return sol


def test_sol(sol):

    # check each order is visited??
    # check target function

    for day in range(len(sol)):
        for vehicle in range(len(sol[day])):
            # check capacity for each vehicle
            if sol[day][vehicle][-2].load > g.C:
                print "over load on vehicle ", vehicle
            # check shift length for each vehicle
            if sol[day][vehicle][-1].arrival_time > g.shift_length:
                print "shift is to long for vehicle ", vehicle, sol[day][vehicle][-1].arrival_time
            # check for each vehicle that starts at depo and ends at landfill
            if sol[day][vehicle][-1].order_number != g.N2:
                print "vehicle",vehicle, "route does not end at landfill "
            else:
                continue
    return


best_solution = find_best_sol(q, k, n)
print display_sol(best_solution[1][0])

