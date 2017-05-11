import random
import copy
from get_data import *

# a solution is a list builed of sub-lists

# each day is represented by a list of all vehicles routes in that day
# each vehicle is represented by a list with the route for one day - all orders to service
# each order is represented by a tuple (order number, arrival time, load)

# for example: solution = [[day1:[vehicle1 route],[vehicle2 route]], [day2:[vehicle1 route],[vehicle2 route]]]

# len(sol) = number of days in the planing horizon

# sol = [[[Stop(0,0,0), Stop(1,777.0,6.48), Stop(6,1564.0,0)]], [[Stop(0,0,0), Stop(2,776.0,6.48), Stop(6,1562.0,0)]],
#      [[Stop(0,0,0), Stop(3,772.0,6.48), Stop(6,1554.0,0)]],[[Stop(0,0,0), Stop(4,764.0,12.96), Stop(5,792.0,19.44),
#                                                              Stop(6,1576.0,0)]]]


# weights for similarity function:

rythem_weight = 0.2
service_time_weight = 0.4
time_weight = 1
dist_weight = 0


# function that checks similarity of two orders based on service time and rhythm
def calc_target_objective(sol, g):
    total_time = 0
    total_dist = 0
    for day in range(len(sol)):
        # print "number of vehicles in day", day, ":",  len(sol[day])
        for vehicle in sol[day]:
            total_time += vehicle[-1].arrival_time
            for order in range(len(vehicle)-1):
                total_dist += g.d[vehicle[order].order_number, vehicle[order+1].order_number]
    return 0.2 * total_time + 0.3 * total_dist


def similarity_func(i, j, g):
    return rythem_weight * abs(g.r[i] - g.r[j]) + service_time_weight * abs(g.s[i] - g.s[j])


def shaw_removal_heuristic(sol, q, k, g):

    # sol - a solution to destract
    # q - number of orders to remove from the solution
    # k - a number in R+, degree of randomness, less randomness when k is larger k

    # choose a random order from all orders numbers
    chosen_order = random.randint(1,len(g.N1))
    unchosen_orders = copy.deepcopy(g.N1)

    # initialize a list with all orders to remove
    chosen_orders = [chosen_order]
    unchosen_orders.remove(chosen_order)

    while len(chosen_orders) < q:
        # for a chosen order calculate the similarity with all unchosen orders
        similarity_list = []
        for order in unchosen_orders:
            similarity_list.append((similarity_func(order, chosen_order, g), order))
        # sort the similarity list from small to large
        similarity_list = sorted(similarity_list)
        p = random.uniform(0, 1)
        # choose the next order to remove
        remove_index = int(len(similarity_list)*p**k)
        chosen_order = similarity_list[remove_index][1]
        chosen_orders.append(chosen_order)
        unchosen_orders.remove(chosen_order)

    return remove_orders(sol, chosen_orders, g)


def worst_removal_heuristic(sol, q, k, g):
    # copy a list of all orders
    unchosen_orders = copy.deepcopy(g.N1)
    chosen_orders = []
    initial_objective = calc_target_objective(sol, g)

    while len(chosen_orders) < q:
        # list of all orders and cost
        # the cost is defined by the difference between the cost of sol with the order and without it

        orders_cost_list = []

        # calc each order cost
        for order in unchosen_orders:
            cost = calc_worst_cost(sol, order, g)
            orders_cost_list.append((cost, order))

        # sort cost list
        orders_cost_list = sorted(orders_cost_list, reverse=True)

        p = random.uniform(0, 1)
        remove_index = int(len(orders_cost_list) * p ** k)
        chosen_order = orders_cost_list[remove_index][1]
        chosen_orders.append(chosen_order)
        remove_orders(sol, [chosen_order], g)
        unchosen_orders.remove(chosen_order)

    return chosen_orders


def calc_worst_cost(sol, order, g):
    cost = 0
    for day in range(len(sol)):
        for vehicle in range(len(sol[day])):
            for order in range(len(sol[day][vehicle])):
                if sol[day][vehicle][order].order_number == order:
                    dist_saved = g.d[sol[day][vehicle][order-1].order_number, order] + g.d[order, sol[day][vehicle][order+1].order_number]\
                                 - g.d[sol[day][vehicle][order-1].order_number, sol[day][vehicle][order+1].order_number]
                    time_saved = g.t[sol[day][vehicle][order-1].order_number, order] + g.t[order, sol[day][vehicle][order+1].order_number]\
                                 - g.t[sol[day][vehicle][order-1].order_number, sol[day][vehicle][order+1].order_number] + g.s[order]
                    cost += dist_weight * dist_saved + time_weight * time_saved
    return cost


def remove_orders(sol, chosen_orders, g):
    # remove the chosen orders from sol
    for day in range(len(sol)):
        vehicle_to_remove = []
        for vehicle in range(len(sol[day])):

            removed = False
            for i in range(len(sol[day][vehicle]) - 1, -1, -1):
                if sol[day][vehicle][i].order_number in chosen_orders:
                    sol[day][vehicle].remove(sol[day][vehicle][i])
                    if len(sol[day][vehicle]) == 2:
                        vehicle_to_remove.append(vehicle)
                    removed = True

            if removed:
                for i in range(1, len(sol[day][vehicle])):
                    order_num = sol[day][vehicle][i].order_number

                    if order_num in g.N1:
                        new_F = sol[day][vehicle][i-1].load + g.w[order_num]
                        new_S = sol[day][vehicle][i - 1].arrival_time + g.t[sol[day][vehicle][i - 1].order_number, order_num] + \
                                g.s[sol[day][vehicle][i - 1].order_number]
                    else:
                        new_F = 0
                        new_S = sol[day][vehicle][i - 1].arrival_time + g.t[sol[day][vehicle][i - 1].order_number, 0] + \
                                g.s[sol[day][vehicle][i - 1].order_number]
                    sol[day][vehicle][i] = Stop(order_num, new_S , new_F)

        if len(vehicle_to_remove) > 0:
            for v in range(len(sol[day])-1,-1,-1):
                if v in vehicle_to_remove:
                    sol[day].pop(v)

    return chosen_orders