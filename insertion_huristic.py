import numpy
import get_data as g
from get_data import *
import removal_huristic
import copy

# weights for objective function: time_added * time_weight + dist_added * dist_weight
time_weight = 1
dist_weight = 0

# a solution is a list builed of sub-lists

# each day is represented by a list of all vehicles routes in that day
# each vehicle is represented by a list with the route for one day - all orders to service
# each order is represented by a tuple (order number, arrival time, load)

# for example: solution = [[day1:[vehicle1 route],[vehicle2 route]], [day2:[vehicle1 route],[vehicle2 route]]]

# len(sol) = number of days in the planing horizon

# sol = [[[Stop(0,0,0), Stop(1,777.0,6.48), Stop(6,1564.0,0)]], [[Stop(0,0,0), Stop(2,776.0,6.48), Stop(6,1562.0,0)]],
#      [[Stop(0,0,0), Stop(3,772.0,6.48), Stop(6,1554.0,0)]],[[Stop(0,0,0), Stop(4,764.0,12.96), Stop(5,792.0,19.44),
#                                                              Stop(6,1576.0,0)]]]


# basic greedy func gets a destracted solution and a list of orders, picks their insertion order and returns a full solution

def basic_greedy(sol, chosen_orders):
    while len(chosen_orders)>0:
        minimal_cost_for_order = numpy.inf

        # calculates objective for each order and finds best order to insert
        for i in chosen_orders:
            order_data = minimum_insertion_cost(i, sol)
            if order_data[0] < minimal_cost_for_order:
                chosen_order = i
                minimal_cost_for_order = order_data[0]
                chosen_data = order_data

        #insert the chosen order
        sol = insert_order(sol, chosen_data, chosen_order)
        chosen_orders.remove(chosen_order)

        # remove empty vehicles from solution
        for i in range(len(sol)):
            if len(sol[i][-1]) == 2:
                sol[i] = sol[i][:-1]
    return sol



# insert order func gets a solution, order data and order number, and inserts the order to the solution
# order data: [objective value, [(day in schedule, vehicle, slot in route)]

def insert_order(sol, order_data, i):
    # extract insert values
    for data in order_data[1]:
        day = data[0] - 1
        vehicle = data[1]
        slot = data[2]
        old_time = sol[day][vehicle][-1].arrival_time
        new_route = sol[day][vehicle][:slot+1]
        # insert order i in the chosen slot in the route
        new_route.append(Stop(i, sol[day][vehicle][slot].arrival_time+g.t[sol[day][vehicle][slot].order_number,i]+
                              g.s[sol[day][vehicle][slot].order_number], sol[day][vehicle][slot].load+g.w[i]))


        for order in range(slot+1,len(sol[day][vehicle])-1):
            # add all orders after j to the new route
            order_number = sol[day][vehicle][order].order_number
            new_time = new_route[-1].arrival_time + g.t[new_route[-1].order_number, sol[day][vehicle][order].order_number] + g.s[new_route[-1].order_number]
            new_load = new_route[-1].load + g.w[sol[day][vehicle][order].order_number]
            new_route.append(Stop(order_number, new_time, new_load))

        new_route.append(Stop(g.N2, new_route[-1].arrival_time + g.t[new_route[-1].order_number, 0] + g.s[new_route[-1].order_number],0))

        sol[day][vehicle] = new_route

    return sol



# minimum insertion cost func gets order number and solution, and returns min objective value and best place to insert the order
# the func returns min_sched for order i
# min_sched: [objective value, [(day in schedule, vehicle, slot in route)]

def minimum_insertion_cost(i, sol):
    # run over all possible schedules
    global dist_added
    possible_schedule = g.Pr[g.r[i]]
    min_sched_cost = numpy.inf
    for sched in possible_schedule:
        # initialize the cost per day for each schedules
        all_days_costs = 0
        # run over all days in sched
        routes_for_days = []
        for day in sched:
            # initialize the cost per vehicle for each day in a specific schedule
            minimal_vehicle_cost = numpy.inf
            flag = False
            for vehicle in sol[day - 1]:
                if len(vehicle)==2:
                    flag = True
                    break
            if flag == False:
                sol[day - 1].append([Stop(0, 0, 0), Stop(g.N2, 0, 0)])
            for vehicle in sol[day - 1]:
                # save vehicle index
                vehicle_number = sol[day - 1].index(vehicle)
                # check if capacity constraint is broken
                if vehicle[-2].load + g.w[i] > g.C:
                    continue
                # run over all orders per vehicle to find best insertion slot
                for j in range(0,len(vehicle)-1):
                    # if we are at the middle of the route
                    if vehicle[j+1].order_number != g.N2:
                        dist_added = g.d[vehicle[j].order_number, i] + g.d[i, vehicle[j+1].order_number]\
                                     - g.d[vehicle[j].order_number, vehicle[j+1].order_number]

                        time_added = g.s[i] + g.t[vehicle[j].order_number, i] + g.t[i, vehicle[j + 1].order_number] \
                                     - g.t[vehicle[j].order_number, vehicle[j + 1].order_number]

                    # if we are at the landfill
                    else:
                        dist_added = g.d[vehicle[j].order_number, i] + g.d[i, 0] - g.d[vehicle[j].order_number, 0]
                        time_added = g.s[i] + g.t[vehicle[j].order_number, i] + g.t[i, 0] - g.t[vehicle[j].order_number, 0]

                    # check if shift length constraint is broken
                    if vehicle[-1].arrival_time + time_added > g.shift_length:
                        continue

                    # calculates delta of objective for this slot
                    delta_route_cost = time_added * time_weight + dist_added * dist_weight

                    # saves only best insertion slot
                    if delta_route_cost < minimal_vehicle_cost:
                        minimal_location = j
                        minimal_vehicle_cost = delta_route_cost
                        minimal_vehicle = vehicle_number

            # calculates cost for all days in schedule
            routes_for_days.append((day, minimal_vehicle, minimal_location))
            all_days_costs += minimal_vehicle_cost

    # saves only best schedule
    if all_days_costs < min_sched_cost:
        min_sched = (all_days_costs, routes_for_days)

    return min_sched


