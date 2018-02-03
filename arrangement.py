from random import shuffle
from table import Table
from copy import deepcopy
import csv

EMPTY_SEAT = 'Z'


# todo make number_tables, table_size static and or constant?
class Arrangement:
    def __init__(self, number_tables, table_size, guest_list):
        self.tables = []  # list of tables
        self.table_seat_tuples = []
        self.number_tables = number_tables
        self.table_size = table_size
        self.guest_list = deepcopy(guest_list)  # make a copy of guest_list but don't change caller's list
        self.init_tuples()
        self.shuffle_tuples()
 #       self.create_tables()
 #       self.print_tables()    # take this out later
 #       self.seat_guests()  # should NOT BE CALLED I CONSTRUCTOR, ONLY INITIAL POPULATION, NOT FUTURE GENS
 #       self.print_tables()  # take this out later
        self.fitness = None

    # defines tuples for ever spot at every table (table #, seat #)
    def init_tuples(self):  # todo check if this is getting the correct tuples for 12 guests, 3 tables
        for i in range(self.number_tables):
            for j in range(self.table_size):
                self.table_seat_tuples.append((i, j))

    def print_tuples(self):
        print(self.table_seat_tuples)

    def shuffle_tuples(self):
        shuffle(self.table_seat_tuples)

    def create_tables(self):
        for i in range(self.number_tables):
            self.tables.append(Table(self.table_size, i))

    # to facilitate crossover Arrangements will pass representation of tables as a single list to population
    def export_master_list(self):  # todo breakpoint here check it's working
        master_list = []
        for table in self.tables:
            for guest in table.guests:
                guest_copy = deepcopy(guest)
                master_list.append(guest_copy)
        return master_list

    # todo am i even using this?
    # reverse of above function. After
    def import_master(self, master_list):
        new_tables_list = deepcopy(master_list)
        self.tables = [new_tables_list[x: x + self.table_size] for x in range(0, len(new_tables_list), self.table_size)]
        print("working?")  # todo erase

    def print_tables(self):
        for index, t in enumerate(self.tables):
            print(index)
            t.print_table()

    def seat_guests(self):  # todo find out why arrangements guests have the wrong table number and position number
                            # todo when testing test_diversity in population
        """Only used during population initialization"""
        for guest in self.guest_list:
            if len(guest.preferences) > 1:
                table_number, seat_index = self.table_seat_tuples.pop(0)
                guest.assign_table(table_number)
                guest.assign_position(seat_index)
                self.tables[table_number].seat_guest(guest, seat_index)

    def get_fitness(self):
        total_penalty = 0
        # ol --> outer loop, il --> inner loop
        for ol_table in self.tables:
            for ol_person in ol_table.guests:
                if not(ol_person is EMPTY_SEAT):
                    for il_table in self.tables:
                        for il_person in il_table.guests:
                            if not(ol_person is il_person) and not (il_person is EMPTY_SEAT):
                                il_person_index = il_person.index
                                # todo make sure this works with names coming in the csv file and not just numbers
                                pref = Arrangement.get_preference(ol_person, il_person_index)
                                total_penalty += self.get_penalty(ol_person, il_person, pref)
        self.fitness = total_penalty/2  # /2 because we've counted every relation between guests twice



    # todo make sure this works with names coming in the csv file and not just numbers
    @staticmethod
    def get_preference(outer_guest, preference_index):
        pref = outer_guest.preferences[preference_index]
        return pref

    def get_penalty(self, outer_guest, inner_guest, pref):
        penalty = 0
        if pref == '1':
            if self.check_next_to(outer_guest, inner_guest):
                penalty += 15
            elif self.check_same_table(outer_guest, inner_guest):
                penalty += 10
        elif pref == '2':
            if self.check_next_to(outer_guest, inner_guest):
                penalty += 15
        elif pref == '3':
            pass
        elif pref == '4':
            if not self.check_same_table(outer_guest, inner_guest):
                penalty += 10
        elif pref == '5':
            if self.check_same_table(outer_guest, inner_guest) and not self.check_next_to(outer_guest, inner_guest):
                penalty += 15
            elif not self.check_same_table(outer_guest, inner_guest):
                penalty += 20
        else:
            pass  # pref should be empty, guest has no pref in reference to herself
        return penalty

    def list_for_csv(self):
        person_list = []
        for table in self.tables:
            for person in table.guests:
                person_list.append(person)
        return person_list

    def output_csv(self):
        list_to_csv = self.list_for_csv()
        with open('solution.csv', 'w', newline='') as myfile:
            wr = csv.writer(myfile, )  # ,
            # fitness = "Fitness: {}".format(self.fitness)
            # wr.writerow(["name", "table", "seat", fitness])
            wr.writerow(["name", "table", "seat"])
            for person in list_to_csv:
                if person is not EMPTY_SEAT:
                    row = [person.name, person.table_number, person.position_number]
                    wr.writerow(row)

    @staticmethod
    def check_same_table(person1, person2):
        return person1.table_number == person2.table_number

    def check_next_to(self, person1, person2):
        # fringe cases
        if self.check_same_table(person1, person2):
            if person1.position_number == self.table_size - 1:
                return (person2.position_number == self.table_size - 2) \
                       or (person2.position_number == 0)

            elif person1.position_number == 0:
                return (person2.position_number == self.table_size - 1) \
                       or (person2.position_number == 1)

            elif person2.position_number == self.table_size - 1:
                return (person1.position_number == self.table_size - 2) \
                       or (person1.position_number == 0)
            elif person2.position_number == 0:
                return (person1.position_number == self.table_size - 1) \
                       or (person1.position_number == 1)
            else:
                return (person1.position_number == person2.position_number + 1) \
                       or (person1.position_number == person2.position_number - 1)
        else:
            return False

    def guest_from_index(self, index): # todo step through this and make sure it's working
        "Given a guests self.index find them and return their table # and position #"
        for table in self.tables:
            for guest in table.guests:
                if guest == EMPTY_SEAT:
                    continue
                if guest.index == index:
                    return guest.table_number, guest.position_number
        print("Guest not found: check guest_from_index() in Arrangement")

    def check_seat_right(self, index_p1, index_p2):  # todo step through this and make sure it's working
        """Given the index of person 1 this function returns true if the index of
            peron2 is found to the right of person1"""
        for table in self.tables:
            for i, guest in enumerate(table.guests):
                if guest == EMPTY_SEAT:
                    continue
                if guest.index == index_p1:
                    if i == self.table_size - 1:
                        return index_p2 == table.guests[0].index
                    else:
                        return index_p2 == table.guests[i + 1].index

    def check_seat_left(self, index_p1, index_p2):  # todo step through this and make sure it's working
        """Given the index of person 1 this function returns true if the index of
            peron2 is found to the right of person1"""
        for table in self.tables:
            for i, guest in enumerate(table.guests):
                if guest == EMPTY_SEAT:
                    continue
                if guest.index == index_p1:
                    if i == 0:
                        return index_p2 == table.guests[self.table_size - 1].index
                    else:
                        return index_p2 == table.guests[i + 1].index

    def get_empty_seats(self, table_number):
        total = 0
        for guest in self.tables[table_number].guests:
            if guest == EMPTY_SEAT:
                total += 1
        return total










