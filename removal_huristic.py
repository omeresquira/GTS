import random
import copy
import get_data as g

# a solution includes 2 parts: sol, schedule
# sol:
# len(sol) = number of days in the planing horizon
# each index contains a list with all the routs for one day, each route contains tuples (i, Sid, Fid) in the order of the visit
# schedule:
# schedule is a dict for each order, the value is the schedule chosen in sol

sol = [[[(0,0,0), (1,777.0,6.48), (6,1564.0,0)]], [[(0,0,0), (2,776.0,6.48), (6,1562.0,0)]],
     [[(0,0,0), (3,772.0,6.48), (6,1554.0,0)]],[[(0,0,0), (4,764.0,12.96), (5,792.0,19.44), (6,1576.0,0)]]]
schedule = {1:0, 2:1, 3:2, 4:3, 5:3}


# function that checks similarity of two orders based on service time and rhythm
def similarity_func(i, j):
    return 0.2 * abs(g.r[i] - g.r[j]) + 0.4 * abs(g.s[i] - g.s[j])


def shaw_removal_huristic(sol, schedule , q, k):

    # sol - a solution to destract
    # q - number of schedules to remove from orders
    # k - a number in R+, degree of randomness, less randomness when k is larger k

    # choose a random order
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

    # remove the orders from sol
    for day in range(len(sol)):
        for vehicle in range(len(sol[day])):
            removed = False
            for i in sol[day][vehicle]:
                for j in chosen_orders:
                    if i[0] == j:
                        sol[day][vehicle].remove(i)
                        removed = True

            if removed == True:
                for i in range(1, len(sol[day][vehicle])):
                    order_num = sol[day][vehicle][i][0]

                    if order_num in g.N1:
                        new_F = sol[day][vehicle][i-1][2] + g.w[order_num]
                        new_S = sol[day][vehicle][i - 1][1] + g.t[sol[day][vehicle][i - 1][0], order_num] + \
                                g.s[sol[day][vehicle][i - 1][0]]
                    else:
                        new_F = 0
                        new_S = sol[day][vehicle][i - 1][1] + g.t[sol[day][vehicle][i - 1][0], 0] + \
                                g.s[sol[day][vehicle][i - 1][0]]
                    sol[day][vehicle][i] = (order_num, new_S , new_F)

            # check if the vehicle has no orders, and remove vehicle location and landfill, if so.
            # (put an empty list instead)
            remove_vehicle_flag = True
            for i in sol[day][vehicle]:
                if i[0] in g.N1:
                    remove_vehicle_flag = False
                    break
            if remove_vehicle_flag:
                sol[day][vehicle] = []

        # check no orders are visited in a day, pop the vehicles so there is an empty list for that day.
        for vehicle in range(len(sol[day])-1,-1,-1):
            if len(sol[day][vehicle]) == 0:
                sol[day].pop(vehicle)

    return sol, schedule, chosen_orders


'''  upadte times and weights (load) values '''

    # # remove the chosen orders from the dict
    # for i in chosen_orders:
    #     chosen_schedule = schedule[i]
    #     Pr[r[i]] = Pr[r[i]].remove(Pr[r[i]][chosen_schedule])
    #     schedule.pop(i)
    #
    # return sol, schedule, Pr, chosen_orders


random.seed(0)
k = 5
q = 2
shaw_removal_huristic(sol, schedule, q, k)