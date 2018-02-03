import arrangement


class Table:

    def __init__(self, size, table_number):
        self.table_number = table_number
        self.size = size
        self.guests = []
        for i in range(size):
            self.guests.append(arrangement.EMPTY_SEAT)  # a z will indicate an empty chair

    def seat_guest(self, person, position_number):
        self.guests[position_number] = person

    def print_table(self):
        #print(self.guests)
        temp_table = []
        for g in self.guests:
            if not g == arrangement.EMPTY_SEAT:
                temp_table.append(g.index)  # make a new list w/ each persons index from csv file
            else:
                temp_table.append(g)  # g == 'z' here
        print(temp_table)








