import random
import copy
import get_data as g

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

# function that checks similarity of two orders based on service time and rhythm
def calc_target_objective(sol):
    total_time = 0
    total_dist = 0
    for day in range(len(sol)):
        # print "number of vehicles in day", day, ":",  len(sol[day])
        for vehicle in sol[day]:
            total_time += vehicle[-1].arrival_time
            for order in range(len(vehicle)-1):
                total_dist+= g.d[vehicle[order].order_number, vehicle[order+1].order_number]
    return 0.2 * total_time + 0.3 * total_dist


def similarity_func(i, j):
    return rythem_weight * abs(g.r[i] - g.r[j]) + service_time_weight * abs(g.s[i] - g.s[j])


def shaw_removal_huristic(sol, q, k):

    # sol - a solution to destract
    # q - number of orders to remove from the solution
    # k - a number in R+, degree of randomness, less randomness when k is larger k

    # choose a random order from all orders numbers
    chosen_order = random.randint(1,len(g.N1))
    unchosen_orders = copy.deepcopy(g.N1)

    # initialize a list with all orders to remove
    chosen_orders = [chosen_order]
    unchosen_orders.remove(chosen_order)

    while len(chosen_orders) < q :
        # for a chosen order calculate the similarity with all unchosen orders
        similarity_list = []
        for order in unchosen_orders:
            similarity_list.append((similarity_func(order,chosen_order),order))
        # sort the similarity list from small to large
        similarity_list = sorted(similarity_list)
        p = random.uniform(0, 1)
        # choose the next order to remove
        remove_index = int(len(similarity_list)*p**k)
        chosen_order = similarity_list[remove_index][1]
        chosen_orders.append(chosen_order)
        unchosen_orders.remove(chosen_order)

    return remove_orders(sol, chosen_orders)


def worst_removel(sol, q, k):
    # copy a list of all orders
    unchosen_orders = copy.deepcopy(g.N1)
    chosen_orders = []
    initial_objective = calc_target_objective(sol)

    while len(chosen_orders) < q:
        # list of all orders and cost
        # the cost is defined by the difference between the cost of sol with the order and without it
        orders_cost_list = []
        # calc each order cost
        for order in unchosen_orders:
            temp_sol = copy.deepcopy(sol)
            removed_sol = remove_orders(temp_sol, [order]+chosen_orders)[0]
            cost = initial_objective - calc_target_objective(removed_sol)
            orders_cost_list.append((cost, order))
        # sort cost list
        orders_cost_list = sorted(orders_cost_list, reverse=True)

        p = random.uniform(0, 1)
        remove_index = int(len(orders_cost_list) * p ** k)
        chosen_order = orders_cost_list[remove_index][1]
        chosen_orders.append(chosen_order)
        orders_cost_list.remove(orders_cost_list[remove_index])
        unchosen_orders.remove(chosen_order)

    # remove the chosen orders
    return remove_orders(sol, chosen_orders)

# def calc_worst_cost(sol, orders):
#     cost = 0
#     for day in range(len(sol)):
#         for vehicle in range(len(sol[day])):
#             for order in range(len(sol[day][vehicle])):
#                 if sol[day][vehicle][order].order_number in orders:
#                     last_order = order -1
#                     while sol[day][vehicle][last_order].order_number in orders:
#                         cost +=
#                         last_order -= 1
#
#
#
#     total_time = 0
#     total_dist = 0
#     for day in range(len(sol)):
#         for vehicle in range(len(sol[day])):
#             total_vehicle_time = 0
#             total_vehicle_dist = 0
#             for order in range(1,len(sol[day][vehicle])):
#                 last_order_num = sol[day][vehicle][order-1].order_number
#                 order_num = sol[day][vehicle][order].order_number
#                 if sol[day][vehicle][order].order_number in orders:
#                     continue
#                 elif order in g.N1:
#                     if last_order_num in orders:
#                         total_vehicle_time += g.t[sol[day][vehicle][order - 2].order_number, order_num] + \
#                                               g.s[sol[day][vehicle][order - 2].order_number]
#                         total_vehicle_dist += g.d[sol[day][vehicle][order - 2].order_number, order_num]
#                     else:
#                         total_vehicle_time += g.t[sol[day][vehicle][order - 1].order_number, order_num] + \
#                                               g.s[sol[day][vehicle][order - 1].order_number]
#                         total_vehicle_dist += g.d[sol[day][vehicle][order - 1].order_number, order_num]
#                 else:
#                     if last_order_num == i:
#                         total_vehicle_time += g.t[sol[day][vehicle][order - 2].order_number, 0] + \
#                                 g.s[sol[day][vehicle][order - 2].order_number]
#                         total_vehicle_dist += g.d[sol[day][vehicle][order - 2].order_number, 0]
#
#                     else:
#                         total_vehicle_time += g.t[sol[day][vehicle][order - 1].order_number, 0] + \
#                                               g.s[sol[day][vehicle][order - 1].order_number]
#                         total_vehicle_dist += g.d[sol[day][vehicle][order - 1].order_number, 0]
#             total_time += total_vehicle_time
#             total_dist += total_vehicle_dist
#
#     return 0.2 * total_time + 0.3 * total_dist


def remove_orders(sol, chosen_orders):
    # remove the chosen orders from sol
    for day in range(len(sol)):
        vehicle_to_remove = []
        for vehicle in range(len(sol[day])):

            removed = False
            for i in range(len(sol[day][vehicle])-1,-1,-1):
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
                    sol[day][vehicle][i] = g.Stop(order_num, new_S , new_F)

        if len(vehicle_to_remove) > 0:
            for v in range(len(sol[day])-1,-1,-1):
                if v in vehicle_to_remove:
                    sol[day].pop(v)

    return sol, chosen_orders