import numpy
import get_data as g
from get_data import *
import removal_huristic
import copy

# a solution includes 2 parts: sol, schedule
# sol:
# len(sol) = number of days in the planing horizon
# each index contains a list with all the routs for one day, each route contains tuples
# (i, Sid (starting_time), # Fid (load after leaving the customer) in the order of the visit
# schedule:
# schedule is a dict for each order, the value is the schedule chosen in sol


# orig_sol = [[[Stop(0,0,0), Stop(1,777.0,6.48), Stop(6,1564.0,0)]], [[Stop(0,0,0), Stop(2,776.0,6.48), Stop(6,1562.0,0)]],
#      [[Stop(0,0,0), Stop(3,772.0,6.48), Stop(6,1554.0,0)]],[[Stop(0,0,0), Stop(4,764.0,12.96), Stop(5,792.0,19.44),
#                                                              Stop(6,1576.0,0)]]]
# schedule = {1:0, 2:1, 3:2, 4:3, 5:3}

#n = number of times runing



def basic_greedy(sol, chosen_orders):
    while len(chosen_orders)>0:
        minimal_cost_for_order = numpy.inf
        for i in chosen_orders:
            order_data = minimum_insertion_cost(i, sol)
            if order_data[0] < minimal_cost_for_order:
                chosen_order = i
                chosen_data = order_data
        sol = insert_order(sol, chosen_data)
        chosen_orders.remove(chosen_order)
    return sol


def insert_order(sol, order_data):
    for route in order_data[2]:
        day = route[0]
        vehicle = route[1]
        if len(sol[day-1])< vehicle + 1:
            sol[day-1].append(route[2])
        else:
            sol[day-1][vehicle] = route[2]
    return sol

def minimum_insertion_cost(i, sol):
    solution = copy.deepcopy(sol)
    # take all possible schedules for order i
    possible_schedule = g.Pr[g.r[i]]
    min_sched_cost = numpy.inf
    for sched in possible_schedule:
        # initialize the cost per day for each schedules
        all_days_costs = 0
        routes_for_days = []
        for day in sched:
            # initialize the cost per vehicle for each day in a specific schedule
            solution[day-1].append([Stop(0,0,0), Stop(6,0,0)])
            minimal_vehicle_cost = numpy.inf
            for vehicle in solution[day-1]:
                # save vehicle index
                vehicle_number = solution[day-1].index(vehicle)
                # check if capacity constraint is broken
                if vehicle[-2].load + g.w[i] > g.C:
                    continue
                orig_total_time = vehicle[-1].arrival_time
                minimal_route_cost = numpy.inf

                # initiate cost for each optional slots between the depot and landfill
                for j in range(len(vehicle)-1):
                    new_route = copy.deepcopy(vehicle[:j+1])
                    new_route.append(Stop(i, vehicle[j].arrival_time+g.t[vehicle[j].order_number,i]+g.s[vehicle[j].order_number], vehicle[j].load+g.w[i]))

                    for order in range(j+1,len(vehicle)-1):
                        # add all orders after j to the new route
                        new_route.append(Stop(vehicle[order].order_number, new_route[order-1].arrival_time + \
                        g.t[new_route[order-1].order_number, vehicle[order].order_number] + g.s[new_route[order-1].order_number],
                                              new_route[order-1].load + g.w[vehicle[order].order_number]))

                    new_route.append(Stop(6, new_route[-1].arrival_time + g.t[new_route[-1].order_number, 0] + g.s[new_route[-1].order_number],0))
                    #check shift length constraint
                    if new_route[-1].arrival_time > g.shift_length:
                        continue
                    time_added = new_route[-1].arrival_time - orig_total_time
                    if vehicle[j+1].order_number != 6:
                        dist_added = g.d[vehicle[j].order_number, i] + g.d[i, vehicle[j+1].order_number]\
                                     - g.d[vehicle[j].order_number, vehicle[j+1].order_number]
                    else:
                        dist_added = g.d[vehicle[j].order_number, i] + g.d[i, 0] - g.d[vehicle[j].order_number, 0]
                    new_route_cost = 0.2*time_added + 0.3*dist_added
                    if new_route_cost < minimal_route_cost:
                        minimal_route = new_route
                        minimal_route_cost = new_route_cost

                #for each day find the best vehicle
                if minimal_route_cost < minimal_vehicle_cost:
                    minimal_vehicle = vehicle_number
                    minimal_vehicle_cost = minimal_route_cost
                    minimal_vehicle_route = minimal_route

            routes_for_days.append((day, minimal_vehicle, minimal_vehicle_route))
            all_days_costs = all_days_costs + minimal_vehicle_cost
        if all_days_costs < min_sched_cost:
            min_sched = [all_days_costs, sched, routes_for_days]
    return min_sched



