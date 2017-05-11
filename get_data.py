import xlrd
import numpy as np
np.set_printoptions(threshold='nan')


class Data:
    def __init__(self, n_orders):
        self.n_orders = n_orders
        self.s = []
        self.r = []
        self.w = []
        self.C = 0
        self.W = 0
        self.shift_length = 3000
        self.unique_r = []
        self.T = 0
        self.Pr = {}
        self.N1 = []
        self.orders_to_num = []
        self.N2 = []
        self.num_to_orders = []
        self.N = []
        self.d = 0
        self.t = []

        self.instanceFileName = 'instances/{}_test_Instance.xlsx'.format(self.n_orders)
        self.xl_data = xlrd.open_workbook(self.instanceFileName)
        self.orders_sheet = self.xl_data.sheet_by_name('Orders')
        self.Vehicle_sheet = self.xl_data.sheet_by_name('Vehicle')
        self.distance_sheet = self.xl_data.sheet_by_name('Distance Matrix')
        # list of all orders as appear in excel (UNICODE)
        self.orders_name = self.orders_sheet.col_values(0)[1:]

        # get the data
        self.run()

    def run(self):
        # service time per order
        self.s = [0] + self.orders_sheet.col_values(1)[1:]

        # rhythm per prder
        self.r = self.orders_sheet.col_values(3)[1:]

        # weight per order
        self.w = [0] + self.orders_sheet.col_values(2)[1:]

        # max capacity
        self.C = self.Vehicle_sheet.cell(0, 1)

        # max driving time
        self.W = self.Vehicle_sheet.cell(1, 1)

        # get unique rhythms
        self.unique_r = set(self.r)
        self.unique_r = list(self.r)

        # get T planing horizon as lcm
        self.T = lcm(int(self.unique_r[0]), int(self.unique_r[1]))
        for i in range(2, len(self.unique_r)):
            self.T = lcm(self.T, int(self.unique_r[i]))

        # Pr dictionary with all possible schedules for each rhythm
        self.Pr = {}
        for ry in self.unique_r:
            all_schedules = []
            for i in range(1,int(ry)+1):
                sched = []
                while i <= self.T:
                    sched.append(int(i))
                    i += ry
                all_schedules.append(sched)
            self.Pr[ry] = all_schedules

        # add zero to rhythms
        self.r = [0] + self.r

        # Run functions
        self.create_orders_dict()
        self.set_d()
        self.set_t()

        # turn into sets
        self.N1 = set(self.N1)
        self.N = set(self.N)
        # orders_to_num - dict that maps a name to an order number
        # num_to_orders - dict that maps number to order name
        # N1 - list of orders numbers
        # N2 - list of landfils

    def create_orders_dict(self):
        self.orders_to_num = {u'Vehicle Location': 0}
        self.num_to_orders = {0: u'Vehicle Location'}
        i = 1
        for order in self.orders_name:
            self.num_to_orders[i] = order
            self.orders_to_num[order] = i
            self.N1.append(i)
            i += 1
        self.N2 = 0
        self.N = [0] + self.N1

    def set_d(self):
        origins = self.distance_sheet.col_values(1)[1:]
        destinations = self.distance_sheet.col_values(2)[1:]
        distance = self.distance_sheet.col_values(3)[1:]
        self.d = np.zeros((len(self.N), len(self.N)))
        num_of_dist = len(origins)
        for i in range(0, num_of_dist):
            self.d[self.N[self.orders_to_num[origins[i]]], self.N[self.orders_to_num[destinations[i]]]] = distance[i]

    def set_t(self):
        origins = self.distance_sheet.col_values(1)[1:]
        destinations = self.distance_sheet.col_values(2)[1:]
        duration = self.distance_sheet.col_values(4)[1:]
        self.t = np.zeros((len(self.N), len(self.N)))
        num_of_dur = len(origins)
        for i in range(0, num_of_dur):
            self.t[self.N[self.orders_to_num[origins[i]]], self.N[self.orders_to_num[destinations[i]]]] = duration[i]



class Stop(object):
    def __init__(self, order_number, arrival_time, load):
        self.order_number = order_number
        self.arrival_time = arrival_time
        self.load = load

    def __str__(self):
        return self.order_number

    def __repr__(self):
        return str(self.order_number)

    def __hash__(self):
        hash((self.order_number, self.arrival_time, self.load))

        #


        # print 'N1:', N1
        # print 'N2:', N2
        # print 'N:', N
        # print 'orders_to_num:', orders_to_num
        # print 'order_names:', orders_name
        # print 'T:', T
        # print 's:', s
        # print 'w:', w
        # print 'r:', [int(i) for i in r]
        # print 't:', t
        # print 'd:', d
        # print 'Pr:', Pr


def gcd(a, b):
    if a < b:
        a, b = b, a
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    return (a * b) / gcd(a, b)
