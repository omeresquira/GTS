import numpy
import random
import xlrd
import get_data as g
import removal_huristic
import copy


# a solution includes 2 parts: sol, schedule
# sol:
# len(sol) = number of days in the planing horizon
# each index contains a list with all the routs for one day, each route contains tuples
# (i, Sid (starting_time), # Fid (load after leaving the customer) in the order of the visit
# schedule:
# schedule is a dict for each order, the value is the schedule chosen in sol

sol = [[[(0,0,0), (1,777.0,6.48), (6,1564.0,0)],[(0,0,0),(6,0,0)]], [[(0,0,0), (2,776.0,6.48), (6,1562.0,0)],[(0,0,0),(6,0,0)]],
     [[(0,0,0), (3,772.0,6.48), (6,1554.0,0)],[(0,0,0),(6,0,0)]],[[(0,0,0), (4,764.0,12.96), (5,792.0,19.44), (6,1576.0,0)],[(0,0,0),(6,0,0)]]]
schedule = {1:0, 2:1, 3:2, 4:3, 5:3}

random.seed(0)

k = 5
q = 2

removed_sol, removed_schedule, chosen_orders = removal_huristic.shaw_removal_huristic(sol, schedule, q, k)


def Basic_gready(sol, schedule, chosen_orders):
    while len(chosen_orders)>0:
        minimal_cost_for_order = numpy.inf
        for i in chosen_orders:
            order_data = minimum_insertion_cost(i, sol)
            if order_data[0] < minimal_cost_for_order:
                chosen_order = i
                chosen_data = order_data
        new_sol = insert_order(sol, chosen_data)
        sol = new_sol
        remove.chosen_orders(chosen_order)
        return sol

def minimum_insertion_cost(i, solution):
    # take all possible schedules for order i
    possible_schedule = g.Pr[g.r[i]]
    min_sched_cost = numpy.inf
    for sched in possible_schedule:
        # initialize the cost per day for each schedules
        all_days_costs = 0
        routes_for_days = []
        for day in sched:
            # initialize the cost per vehicle for each day in a specific schedule
            minimal_vehicle_cost = numpy.inf
            for vehicle in sol[day-1]:
                # save vehicle index
                vehicle_number = sol[day-1].index(vehicle)
                # check if capacity constraint is broken
                if vehicle[-2][2] + g.w[i] > g.C:
                    continue
                orig_total_time = vehicle[-1][1]
                minimal_route_cost = numpy.inf

                # initiate cost for each optional slots between the depot and landfill
                for j in range(len(vehicle)-1):
                    new_route = copy.deepcopy(vehicle[:j+1])
                    new_route.append((i, vehicle[j][1]+g.t[vehicle[j][0],i]+g.s[j], vehicle[j][2]+g.w[i]))

                    for order in range(j+1,len(vehicle)-1):
                        # add all orders after j to the new route
                        new_route.append((vehicle[order][0], new_route[order-1][-2] + \
                        g.t[new_route[order-1][0], vehicle[order][0]] + g.s[new_route[order-1][0]], new_route[order-1][-1] \
                        + g.w[vehicle[order][0]]))
                    new_route.append((6, new_route[-1][1] + g.t[new_route[-1][0], 0]))
                    #check shift length constraint
                    if new_route[-1][1] > g.shift_length:
                        continue
                    time_saved = orig_total_time - new_route[-1][1]
                    if vehicle[j+1][0] != 6:
                        dist_saved = g.d[vehicle[j][0], i] + g.d[i, vehicle[j+1][0]] - g.d[vehicle[j][0], vehicle[j+1][0]]
                    else:
                        dist_saved = g.d[vehicle[j][0], i] + g.d[i, 0] - g.d[vehicle[j][0], 0]
                    new_route_cost = 0.2*time_saved + 0.3*dist_saved
                    if new_route_cost < minimal_route_cost:
                        minimal_route = new_route
                        minimal_route_cost = new_route_cost

                #for each day find the best vehicle
                if minimal_route_cost < minimal_vehicle_cost:
                    minimal_vehicle = vehicle_number
                    minimal_vehicle_cost = minimal_route_cost
                    minimal_vehicle_route = minimal_route

            routes_for_days.append((day, minimal_vehicle, minimal_vehicle_cost, minimal_vehicle_route))
            all_days_costs = all_days_costs + minimal_vehicle_cost
        if all_days_costs < min_sched_cost:
            min_sched = [all_days_costs, sched, routes_for_days]

    return min_sched

def insert_order(sol, order_data):
    for route in order_data[2]:
        day = route[0]
        vehicle = route[1]
        sol[day][vehicle] = route[3]
    return sol



order_data = minimum_insertion_cost(1, sol)
print insert_order(sol, order_data)
#Basic_gready(removed_sol, removed_schedule, chosen_orders)
