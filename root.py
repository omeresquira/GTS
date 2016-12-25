from insertion_huristic import *
from removal_huristic import *
import get_data as g
import copy
import datetime
import time

random.seed(0)
# sol - a solution to destract
# q - number of orders to remove from the solution
# k - a number in R+, degree of randomness, less randomness when k is larger k
k = 10
q = 20
n = 1000  # number of iterations
time_weight = 1
dist_weight = 0


# find_best_sol func runs removal_heuristic and basic_greedy n times to find best solution
def find_best_sol(q, k, n):
    all_orders = list(g.N1)
    # creates empty solution
    initial_sol = [[[Stop(0, 0, 0), Stop(g.N2, 0, 0)]] for k in range(int(g.T))]
    # insert all orders to create an initial solution
    find_initial_sol(all_orders, initial_sol)
    #checks if the solution is valid
    test_sol(initial_sol)
    initial_cost = calc_target_objective(initial_sol)
    best_sol =[initial_sol, initial_cost]
    temp_sol = copy.deepcopy(initial_sol)
    for i in range(n):
        # chosen_orders = worst_removal_heuristic(temp_sol, q, k)
        chosen_orders = shaw_removal_heuristic(temp_sol, q, k)
        regret_heuristic_insertion(temp_sol, chosen_orders)
        # basic_greedy_insertion(temp_sol, chosen_orders)
        test_sol(temp_sol)
        objective = calc_target_objective(temp_sol)
        # saves best solution if one was found
        # print objective
        if objective < best_sol[1]:
            best_sol[0] = copy.deepcopy(temp_sol)
            best_sol[1] = objective
            print i,best_sol[1], best_sol[0]

    return best_sol


def find_initial_sol(orders, sol):
    orders_copy = copy.deepcopy(orders)
    while len(orders_copy)>0:
        for i in orders_copy:
            order_data = minimum_insertion_cost(i, sol)
            insert_order(sol, order_data, i)
            orders_copy.remove(i)
    # print "init", sol


def test_sol(sol):
    # create list of all orders
    orders_sol = []
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
                pass
            for order in range(1,len(sol[day][vehicle])-1):
                orders_sol.append(sol[day][vehicle][order].order_number)

    orders_sol = set(orders_sol)
    if orders_sol.issuperset(g.N1):
        pass
    else:
        missing_orders = (g.N1).difference(orders_sol)
        print "orders", missing_orders, "are not in the solution"


def display_sol(sol):

    instance = g.instanceFileName
    date = time.strftime("%d-%m-%Y")
    hour = time.strftime("%I_%M_%S")

    with open('./results/{}_{}_{}.txt'.format(instance[:-5], date, hour), 'w+') as txt_file:
        txt_file.write("total objective: {}  \n\n".format(calc_target_objective(sol)))
        txt_file.write("parameters: k={}, q={}, n={}  \n\n".format(k, q, n))
        for day_num in range(len(sol)):
            txt_file.write("day {} : \n".format(day_num+1))

            #delete empty vehicles
            for vehicle in range(len(sol[day_num])-1, -1, -1):
                if len(sol[day_num][vehicle]) == 2:
                    sol[day_num].pop(vehicle)

            total_service_time = 0
            total_travel_time = 0
            for vehicle_num in range(len(sol[day_num])):
                vehicle_service_time = 0
                txt_file.write("  vehicle {} route: depot -->".format(vehicle_num+1))
                for order in sol[day_num][vehicle_num][1:-1]:
                    vehicle_service_time += s[order.order_number]
                    txt_file.write("{} -->".format(order.order_number, order.arrival_time))
                txt_file.write("landfill \n")
                txt_file.write("  route total service time: {} , route total travel time: {} \n\n".format(vehicle_service_time, sol[day_num][vehicle_num][-1].arrival_time - vehicle_service_time))
                total_service_time += vehicle_service_time
                total_travel_time += (sol[day_num][vehicle_num][-1].arrival_time - vehicle_service_time)
            txt_file.write("  total service time for day {} : {} , total travel time for day {} : {} \n\n".format(day_num+1, total_service_time, day_num+1, total_travel_time ))


def calc_target_objective(sol):
    total_time = 0
    total_dist = 0
    for day in range(len(sol)):
        # print "number of vehicles in day", day, ":",  len(sol[day])
        for vehicle in sol[day]:
            total_time += vehicle[-1].arrival_time
            for order in range(len(vehicle)-1):
                total_dist+= g.d[vehicle[order].order_number, vehicle[order+1].order_number]
    return time_weight * total_time + dist_weight * total_dist

best_solution = find_best_sol(q, k, n)
display_sol(best_solution[0])

