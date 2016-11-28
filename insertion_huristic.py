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
        sol = insert_order(sol, chosen_data, i)
        chosen_orders.remove(chosen_order)
    return sol


def insert_order(sol, order_data, i):
    for data in order_data[1]:
        vehicle = data[1]
        slot = data[2]
        day = data[0] - 1
        new_sol = copy.deepcopy(sol)

        new_route = new_sol[day][vehicle][:slot+1]
        new_route.append(Stop(i, new_sol[day][vehicle][slot].arrival_time+g.t[new_sol[day][vehicle][slot].order_number,i]+
                              g.s[new_sol[day][vehicle][slot].order_number], new_sol[day][vehicle][slot].load+g.w[i]))

        for order in range(slot+1,len(new_sol[day][vehicle])-1):
            # add all orders after j to the new route
            new_route.append(Stop(sol[day][vehicle][order].order_number, new_route[order-1].arrival_time + \
            g.t[new_route[order-1].order_number, new_sol[day][vehicle][order].order_number] + g.s[new_route[order-1].order_number],
                                  new_route[order-1].load + g.w[new_sol[day][vehicle][order].order_number]))

        new_route.append(Stop(g.N2, new_route[-1].arrival_time + g.t[new_route[-1].order_number, 0] + g.s[new_route[-1].order_number],0))
        new_sol[day][vehicle] = new_route


    return new_sol


def minimum_insertion_cost(i, sol):
    # run over all possible schedules
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
                sol[day - 1].append([Stop(0, 0, 0), Stop(N2, 0, 0)])
            for vehicle in sol[day - 1]:
                # save vehicle index
                vehicle_number = sol[day - 1].index(vehicle)
                # check if capacity constraint is broken
                if vehicle[-2].load + g.w[i] > g.C:
                    continue
                # initialize the cost per rout for vehicle for each day in a specific schedule
                minimal_route_cost = numpy.inf
                # run over all orders per vehicle
                for j in range(0,len(vehicle)-1):
                    # if we are at the middle of the route

                    if vehicle[j+1].order_number != g.N2:
                        dist_added = g.d[vehicle[j].order_number, i] + g.d[i, vehicle[j+1].order_number]\
                                     - g.d[vehicle[j].order_number, vehicle[j+1].order_number]

                        time_added = g.t[vehicle[j].order_number, i] + g.t[i, vehicle[j + 1].order_number] \
                                     - g.t[vehicle[j].order_number, vehicle[j + 1].order_number]
                    # check if we are at the landfill
                    else:
                        dist_added = g.d[vehicle[j].order_number, i] + g.d[i, 0] - g.d[vehicle[j].order_number, 0]
                        time_added = g.t[vehicle[j].order_number, i] + g.t[i, 0] - g.t[vehicle[j].order_number, 0]

                    if vehicle[-1].arrival_time +  time_added > g.shift_length:
                        continue

                    if time_added+vehicle[-1].arrival_time>3000:
                        print time_added+vehicle[-1].arrival_time
                    delta_route_cost = time_added*0.2 + dist_added*0.3


                    if delta_route_cost < minimal_route_cost:
                        minimal_location = j
                        minimal_route_cost = delta_route_cost


                if minimal_route_cost < minimal_vehicle_cost:
                    minimal_vehicle = vehicle_number
                    minimal_vehicle_cost = minimal_route_cost

            routes_for_days.append((day, minimal_vehicle, minimal_location))
            all_days_costs += minimal_vehicle_cost
            if all_days_costs < min_sched_cost:
                min_sched = (all_days_costs, routes_for_days)


        return min_sched


