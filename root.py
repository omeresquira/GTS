import random
from insertion_huristic import *
import get_data as g

random.seed(0)
k = 5
q = 2
n=10

def find_best_sol(q, k, n):
    all_orders = list(g.N1)
    empty_sol = [[] for k in range(int(g.T))]
    sol = find_initial_sol(all_orders, empty_sol)
    result = {"target function":[]}
    for i in range(n):
        removed_sol, chosen_orders = removal_huristic.shaw_removal_huristic(sol, q, k)
        sol = basic_greedy(removed_sol, chosen_orders)
        test_sol(sol)
        result["target function"].append(print_sol(sol))
    return result

def find_initial_sol(orders, sol):
    orders_copy = copy.deepcopy(orders)
    while len(orders_copy)>0:
        for i in orders_copy:
            order_data = minimum_insertion_cost(i, sol)
            sol = insert_order(sol, order_data)
            orders_copy.remove(i)
    return sol

def test_sol(sol):
    # check each order is visited??

    for day in range(len(sol)):
        for vehicle in range(len(sol[day])):
            # check capacity for each vehicle
            if sol[day][vehicle][-2].load > g.C:
                print "over load on vehicle ", vehicle
            # check shift length for each vehicle
            if sol[day][vehicle][-1].arrival_time > g.shift_length:
                print "shift is to long for vehicle ", vehicle
            # check for each vehicle that starts at depo and ends at landfill
            if sol[day][vehicle][-1].order_number not in g.N2:
                print "vehicle",vehicle, "route does not end at landfill "
            if sol[day][vehicle][0].order_number != 0:
                print "vehicle",vehicle, "route does not start at depot "
            else:
                continue
    return


print find_best_sol(q, k, n)

