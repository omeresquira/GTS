import xlrd
import numpy as np


xl_data = xlrd.open_workbook('10_Test_Instance.xlsx')
orders_sheet = xl_data.sheet_by_name('Orders')
Vehicle_sheet = xl_data.sheet_by_name('Vehicle')
distance_sheet = xl_data.sheet_by_name('Distance Matrix')

# list of all orders as appear in excel (UNICODE)
orders_name = orders_sheet.col_values(0)[1:]

# service time per order
s = [0] + orders_sheet.col_values(1)[1:]

# rhythm per prder
r = orders_sheet.col_values(3)[1:]

# weight per order
w = [0] + orders_sheet.col_values(2)[1:]

# max capacity
C = Vehicle_sheet.cell(0, 1)

# max driving time
W = Vehicle_sheet.cell(1, 1)

# shift length
shift_length = 14400

def gcd(a, b):
    if a < b:
        a, b = b, a
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    return (a * b)/gcd(a, b)

# get unique rhythms
unique_r = set(r)
unique_r = list(r)

# get T planing horizon as lcm
T = lcm(int(unique_r[0]), int(unique_r[1]))
for i in range(2, len(unique_r)):
    T = lcm(T, int(unique_r[i]))

# Pr dictionary with all possible schedules for each rhythm
Pr = {}
for ry in unique_r:
    all_schedules = []
    for i in range(1,int(ry)+1):
        sched = []
        while i <= T:
            sched.append(int(i))
            i += ry
        all_schedules.append(sched)
    Pr[ry] = all_schedules

# add zero to rhythms
r = [0] + r

# orders_to_num - dict that maps a name to an order number
# num_to_orders - dict that maps number to order name
# N1 - list of orders number
# N2 - list of landfils

def create_orders_dict():
    global N1
    global orders_to_num
    global N2
    global num_to_orders
    global N
    orders_to_num = {u'Vehicle Location': 0}
    num_to_orders = {0: u'Vehicle Location'}
    N1 = []
    i = 1
    for order in orders_name:
        num_to_orders[i] = order
        orders_to_num[order] = i
        N1.append(i)
        i +=1
    N2 = [N1[-1]+1]
    N = [0] + N1
    return N1, N2,N, num_to_orders, orders_to_num


def get_d():
    global d
    origins = distance_sheet.col_values(1)[1:]
    destinations = distance_sheet.col_values(2)[1:]
    distance = distance_sheet.col_values(3)[1:]
    d = np.zeros((len(N), len(N)))
    num_of_dist = len(origins)
    for i in range(0, num_of_dist):
        d[N[orders_to_num[origins[i]]], N[orders_to_num[destinations[i]]]] = distance[i]
    return d

def get_t():
    global t
    origins = distance_sheet.col_values(1)[1:]
    destinations = distance_sheet.col_values(2)[1:]
    duration = distance_sheet.col_values(4)[1:]
    t = np.zeros((len(N), len(N)))
    num_of_dur = len(origins)
    for i in range(0, num_of_dur):
        t[N[orders_to_num[origins[i]]], N[orders_to_num[destinations[i]]]] = duration[i]
    return t

def print_sol(sol):
    total_time = 0
    total_dist = 0
    # print "planing_horizon:", len(sol)
    for day in range(len(sol)):

        # print "number of vehicles in day", day, ":",  len(sol[day])
        for vehicle in sol[day]:
            total_time += vehicle[-1].arrival_time
            total_dist += vehicle[-2].load
            # print "total time:", vehicle[-1].arrival_time, "load:", vehicle[-2].load, "route:", vehicle[1:-1]
    return 0.2*total_time + 0.3*total_dist


class Stop(object):
    def __init__(self, order_number, arrival_time, load):
        self.order_number = order_number
        self.arrival_time = arrival_time
        self.load = load

    def __str__(self):
        return self.order_number

    def __repr__(self):
        return str(self.order_number)


create_orders_dict()
get_d()
get_t()

# turn into sets
N1 = set(N1)
N2 = set(N2)
N = set(N)


# print 'N1:', N1
# print 'N2:', N2
# print 'N:', N
# print 'orders_to_num:', orders_to_num
# print 'order_names:', orders_name
# print 'T:', T
# print 's:', s
# print 'w:', w
# print 'r:', r
# print 't:', t
# print 'd:', d
# print 'Pr:', Pr

