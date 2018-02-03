#from __future__ import division
from arrangement import Arrangement, EMPTY_SEAT
from table import Table
import random as rand
import copy
from person import Person

# WINDOW_SIZE = 4
# POPULATION_SIZE = 20
# LIMIT_MUTATIONS = 20
# # an upper limit on the number of random changes in the sorted order for parent selection
# LIMIT_CHANGES_SURVIVOR_SELECTION = 50
# MUTANT_GROUPS = 100  # a mutant group is both parents + 2 offspring from crossover, all to be mutated

# WINDOW_SIZE = 6
# POPULATION_SIZE = 60
# LIMIT_MUTATIONS = 20
# LIMIT_CHANGES_SURVIVOR_SELECTION = 50
# MUTANT_GROUPS = 100

WINDOW_SIZE = 4
POPULATION_SIZE = 20
LIMIT_MUTATIONS = 10
LIMIT_CHANGES_SURVIVOR_SELECTION = 15
MUTANT_GROUPS = 50
WITH_REPLACEMENT = True


def grouped(iterable, n):
    return zip(*[iter(iterable)]*n)


class Population:

    def __init__(self, number_tables, table_size, guest_list):
        # arrangement_list is population
        self.arrangement_list = []
        self.table_size = table_size
        self.number_tables = number_tables
        self.guest_list = copy.deepcopy(guest_list)
        for i in range(POPULATION_SIZE):
            new_gl = copy.deepcopy(self.guest_list)
            self.arrangement_list.append(Arrangement(self.number_tables, self.table_size, new_gl))
        for arr_ in self.arrangement_list:
            arr_.create_tables()
            arr_.seat_guests()
            # DON'T FORGET TO SHUFFLE ARRANGEMENT?

    def evolve_generations(self, number_generations, a_only):

        for i in range(number_generations):
            print("\tGeneration: {}".format(i))
            if a_only:
                self.evolve_one_generation_a()
            else:
                self.evolve_one_generation_b()
        self.get_best_solution()

    def evolve_one_generation_b(self):  # todo haven't changed this yet
        # for each window select parents
        range_of_arrangements = int(POPULATION_SIZE / WINDOW_SIZE)
        rand.shuffle(self.arrangement_list)
        diversity_for_avg = []
        new_arrangements = []
        for i in range(range_of_arrangements):
            window = copy.deepcopy(self.arrangement_list[:WINDOW_SIZE])  # todo deepcpy?
            del (self.arrangement_list[:WINDOW_SIZE])
            for arrangement in window:
                arrangement.get_fitness()
            window.sort(key=lambda arr: arr.fitness)  # get best 2 parents

            parent1, parent2 = window[0], window[1]  # PARENT SELECTION HERE

            # cross_over
            p1_master_list = copy.deepcopy(parent1.export_master_list())
            p2_master_list = copy.deepcopy(parent2.export_master_list())
            p1_for_child1 = copy.deepcopy(p1_master_list)
            p2_for_child1 = copy.deepcopy(p2_master_list)
            p1_for_child2 = copy.deepcopy(p1_master_list)
            p2_for_child2 = copy.deepcopy(p2_master_list)
            child_list1 = self.pmx_crossover(p1_for_child1, p2_for_child1, self.table_size)
            child_list2 = self.pmx_crossover(p1_for_child2, p2_for_child2, self.table_size)

            list_for_mutating = []  # list of lists

            for i_ in range(MUTANT_GROUPS):
                # p1_mutant = copy.deepcopy(p1_master_list)
                # p2_mutant = copy.deepcopy(p2_master_list)
                ch1_mutant = copy.deepcopy(child_list1)
                ch2_mutant = copy.deepcopy(child_list2)
                # list_for_mutating.append(p1_mutant)
                # list_for_mutating.append(p2_mutant)
                list_for_mutating.append(ch1_mutant)
                list_for_mutating.append(ch2_mutant)

            for new_mutant in list_for_mutating:
                self.mutate(new_mutant, LIMIT_MUTATIONS)

            list_of_new_mutants = []  # list of Arrangement objects
            for new_mutant in list_for_mutating:
                guest_list_copy = copy.deepcopy(self.guest_list)
                arrangement = Arrangement(self.number_tables, self.table_size, guest_list_copy)
                # break continutous list of guests back into their seperate tables
                now_seperate = [new_mutant[x: x + self.table_size] for x in range(0, len(new_mutant), self.table_size)]
                table_list = []
                for index, list_ in enumerate(now_seperate):
                    table = Table(self.table_size, index)
                    table.guests = list_
                    table_list.append(table)
                arrangement.tables = table_list
                list_of_new_mutants.append(arrangement)

            # now list_of_new_mutants [] has mutated arrangement objects ready for survivor selection
            for arrangement in list_of_new_mutants:
                arrangement.get_fitness()
            parent1_group = []
            parent2_group = []
            for arr in list_of_new_mutants:
                div_1 = self.measure_diversity(arr, parent1)
                div_2 = self.measure_diversity(arr, parent2)
                if div_1 < div_2:
                    parent1_group.append(arr)
                else:
                    parent2_group.append(arr)

            parent1_group.sort(key=lambda arr: arr.fitness)
            parent2_group.sort(key=lambda arr: arr.fitness)

            # Attempting to add some diversity here, we want SOME suboptimal solutions to pass
            # so that they may end up evolving into even better solutions
            if parent1_group:
                self.add_randomness(parent1_group, LIMIT_CHANGES_SURVIVOR_SELECTION)
            if parent2_group:
                self.add_randomness(parent2_group, LIMIT_CHANGES_SURVIVOR_SELECTION)

            # for i in range(WINDOW_SIZE - 2):
            if WITH_REPLACEMENT:
                survivors = [parent1, parent2]
            else:
                survivors = []
            p1_index = 0
            p2_index = 0
            while len(survivors) < WINDOW_SIZE:
                if i % 2 == 0:
                    if parent1_group:
                        survivors.append(parent1_group[p1_index])
                        p1_index += 1
                    else:
                        survivors.append(parent2_group[p2_index])
                        p2_index += 1

                else:
                    if parent2_group:
                        survivors.append(parent2_group[p2_index])
                        p2_index += 1
                    else:
                        survivors.append(parent1_group[p1_index])
                        p1_index += 1
                i += 1
            for survivor in survivors:
                new_arrangements.append(survivor)
            diversity = self.measure_diversity(parent1, parent2)  # todo get avg diversity among group?
            diversity_for_avg.append(diversity)
            print("Parents fitness(1, 2): {} {} Their Diversity: {}".format(parent1.fitness, parent2.fitness, diversity))

        avg_diversity = sum(diversity_for_avg)/len(diversity_for_avg)
        print("Average diversity between parents: ", avg_diversity)


        self.arrangement_list = new_arrangements
        top_three_diversity = self.top_three_diversity()
        print("Diversity for the top three in the next generation: ", top_three_diversity)
        # todo below is just for testing
        #arr1, arr2 = self.arrangement_list[0], self.arrangement_list[1]
        #self.test_diversity(arr1, arr2)
        #diversity = self.measure_diversity(arr1, arr2)
        #print("test")

    def evolve_one_generation_a(self):
        # for each window select parents
        range_of_arrangements = int(POPULATION_SIZE / WINDOW_SIZE)
        rand.shuffle(self.arrangement_list)
        new_arrangements = []
        diversity_for_avg = []
        for i in range(range_of_arrangements):
            window = copy.deepcopy(self.arrangement_list[:WINDOW_SIZE])  # todo deepcpy?
            del (self.arrangement_list[:WINDOW_SIZE])
            for arrangement in window:
                arrangement.get_fitness()
            window.sort(key=lambda arr: arr.fitness)  # get best 2 parents

            parent1, parent2 = window[0], window[1]  # PARENT SELECTION HERE

            # cross_over
            p1_master_list = copy.deepcopy(parent1.export_master_list())
            p2_master_list = copy.deepcopy(parent2.export_master_list())
            p1_for_child1 = copy.deepcopy(p1_master_list)
            p2_for_child1 = copy.deepcopy(p2_master_list)
            p1_for_child2 = copy.deepcopy(p1_master_list)
            p2_for_child2 = copy.deepcopy(p2_master_list)
            child_list1 = self.pmx_crossover(p1_for_child1, p2_for_child1, self.table_size)
            child_list2 = self.pmx_crossover(p1_for_child2, p2_for_child2, self.table_size)

            list_for_mutating = []  # list of lists

            for i_ in range(MUTANT_GROUPS):
                # p1_mutant = copy.deepcopy(p1_master_list)
                # p2_mutant = copy.deepcopy(p2_master_list)
                ch1_mutant = copy.deepcopy(child_list1)
                ch2_mutant = copy.deepcopy(child_list2)
                # list_for_mutating.append(p1_mutant)
                # list_for_mutating.append(p2_mutant)
                list_for_mutating.append(ch1_mutant)
                list_for_mutating.append(ch2_mutant)

            for new_mutant in list_for_mutating:
                self.mutate(new_mutant, LIMIT_MUTATIONS)

            list_of_new_mutants = []  # list of Arrangement objects
            for new_mutant in list_for_mutating:
                guest_list_copy = copy.deepcopy(self.guest_list)
                arrangement = Arrangement(self.number_tables, self.table_size, guest_list_copy)
                # break continutous list of guests back into their seperate tables
                now_seperate = [new_mutant[x: x + self.table_size] for x in range(0, len(new_mutant), self.table_size)]
                table_list = []
                for index, list_ in enumerate(now_seperate):
                    table = Table(self.table_size, index)
                    table.guests = list_
                    table_list.append(table)
                arrangement.tables = table_list
                list_of_new_mutants.append(arrangement)

            # now list_of_new_mutants [] has mutated arrangement objects ready for survivor selection
            for arrangement in list_of_new_mutants:
                arrangement.get_fitness()

            list_of_new_mutants.sort(key=lambda arr: arr.fitness)

            # Attempting to add some diversity here, we want SOME suboptimal solutions to pass
            # so that they may end up evolving into even better solutions
            self.add_randomness(list_of_new_mutants, LIMIT_CHANGES_SURVIVOR_SELECTION)

            if WITH_REPLACEMENT:
                for i in range(WINDOW_SIZE - 2):
                    new_arrangements.append(list_of_new_mutants[i])
                new_arrangements.append(parent1)
                new_arrangements.append(parent2)
            else:
                for i in range(WINDOW_SIZE):
                    new_arrangements.append(list_of_new_mutants[i])

            diversity = self.measure_diversity(parent1, parent2)
            diversity_for_avg.append(diversity)

            print("Parents fitness(1, 2): {} {} Their Diversity: {}".format(parent1.fitness, parent2.fitness, diversity))

        avg_diversity = sum(diversity_for_avg) / len(diversity_for_avg)
        print("Average diversity between parents: ", avg_diversity)

        self.arrangement_list = new_arrangements
        top_three_diversity = self.top_three_diversity()
        print("Diversity for the top in the next generation: ", top_three_diversity)
        # todo below is just for testing
        #arr1, arr2 = self.arrangement_list[0], self.arrangement_list[1]
        #self.test_diversity(arr1, arr2)
        #diversity = self.measure_diversity(arr1, arr2)
        #print("test")

    def pmx_crossover(self, person_list1, person_list2, table_size):
        child_list = [EMPTY_SEAT] * len(person_list1)

        p1_list_copy = copy.deepcopy(person_list1)
        p2_list_copy = copy.deepcopy(person_list2)
        # step 1 from slides
        length = len(p1_list_copy)
        segment_end = rand.randrange(2, length)
        segment_start = rand.randrange(0, segment_end)
        # segment_end = 2
        # segment_start = 7

        #segment_start = 3  # todo swap these commented lines
        #segment_end = 6
        child_list[segment_start: segment_end + 1] = p1_list_copy[segment_start: segment_end + 1]
#        print("seg start, end, list: ", segment_start, segment_end, child_list)

        # step 2 from slides
        for i in range(segment_start, segment_end + 1):
            # todo if things aren't working maybe don't need this if statement but need next line
            if not (p2_list_copy[i] == EMPTY_SEAT):
                self.go_opposite_get_index(p2_list_copy[i], i, p1_list_copy, p2_list_copy, child_list, table_size)

        # step 3 from slides
        for i in p2_list_copy:
            #        if not (i in child_list):
            if not Population.in_list(i.index, child_list):
                for index_, j in enumerate(child_list):
                    if j == EMPTY_SEAT:
                        child_list[index_] = i
                        i.position_number = index_ % table_size  # CHANGE HERE TO CHANG THEIR TABLES NUMBER AS WELL
                        i.table_number = int(index_ / table_size)
                        break
        return child_list

    def go_opposite_get_index(self, guest, i, p1, p2, child, table_size):
        """used in pmx_crossover and called recursively to place guest"""
        if not Population.in_list(guest.index, child):
            val_yours_at_i = p1[i]
            if val_yours_at_i is EMPTY_SEAT:
                child[i] = guest
            else:
                index_yours_in_mine = Population.get_index(val_yours_at_i.index, p2)
                if child[index_yours_in_mine] == EMPTY_SEAT:
                    child[index_yours_in_mine] = guest
                    # guest.position_number = index_yours_in_mine  # this needs to be changed to allow for tracking which table they're at
                    guest.position_number = index_yours_in_mine % table_size  # this needs to be changed to allow for tracking which table they're at
                    guest.table_number = int(index_yours_in_mine / table_size)
                else:
                    self.go_opposite_get_index(guest, index_yours_in_mine, p1, p2, child, table_size)

    def add_randomness(self, list_, upper_limit_of_changes):
        """this should be called on a sorted list to add an element of randomness"""
        max_changes = rand.randrange(upper_limit_of_changes)
        list_length = len(list_)
        for i in range(max_changes):
            index_1 = rand.randrange(list_length)
            index_2 = rand.randrange(list_length)
            list_[index_1], list_[index_2] = list_[index_2], list_[index_1]

    def mutate(self, guest_list_, number_mutations):
        """Mutates a list that can be used to set an Arrangement objects tables[]
            , it mutates a raw list seating arrangement like that made available in
            Arrangement.export_master_list(), exactly how many mutations should be random
            with an upper limit of number_of_changes"""

        changes = rand.randrange(number_mutations)

        for change in range(changes):
            index1 = rand.randrange(len(guest_list_))
            index2 = rand.randrange(len(guest_list_))
            guest1 = guest_list_[index1]
            guest2 = guest_list_[index2]
            g1_table_number = None
            g1_position_number = None
            g2_table_number = None
            g2_position_number = None

            if guest1 is not EMPTY_SEAT:
                g1_table_number = guest1.table_number
                g1_position_number = guest1.position_number
            else:
                g1_table_number = int(index1/self.table_size)
                g1_position_number = index1 % self.table_size

            if guest2 is not EMPTY_SEAT:
                g2_table_number = guest2.table_number
                g2_position_number = guest2.position_number
            else:
                g2_table_number = int(index2 / self.table_size)
                g2_position_number = index2 % self.table_size

            if guest1 is not EMPTY_SEAT:
                guest1.table_number = g2_table_number
                guest1.position_number = g2_position_number

            if guest2 is not EMPTY_SEAT:
                guest2.table_number = g1_table_number
                guest2.position_number = g1_position_number

            guest_list_[index1], guest_list_[index2] = guest_list_[index2], guest_list_[index1]

    def get_best_solution(self):
        """This function also outputs the solution to csv file, maybe change this later"""
        for arrangement in self.arrangement_list:
            arrangement.get_fitness()
        self.arrangement_list.sort(key=lambda arr: arr.fitness)
        best = self.arrangement_list[0]

        best.output_csv()

    def top_three_diversity(self):
        for arrangement in self.arrangement_list:
            arrangement.get_fitness()
        self.arrangement_list.sort(key=lambda arr: arr.fitness)
        one = self.arrangement_list[0]
        two = self.arrangement_list[1]
        three = self.arrangement_list[2]

        total = self.measure_diversity(one, two)
        total += self.measure_diversity(one, three)
        total += self.measure_diversity(two, three)
        return total


    # todo get rid of this if not using
    # def test_diversity(self):
    #     gl = copy.deepcopy(self.guest_list)
    #     gl2 = copy.deepcopy(self.guest_list)
    #     arr1 = Arrangement(3, 4, gl)
    #     arr2 = Arrangement(3, 4, gl2)
    #
    #     tables_A = []
    #     for i in range(3):
    #         table = Table(4, i)
    #         tables_A.append(table)
    #
    #     tables_B = []
    #     for i in range(3):
    #         table = Table(4, i)
    #         tables_B.append(table)
    #
    #     p1_A = Person(1, "P1", 0)
    #     p1_A.table_number = 0
    #     p1_A.position_number = 1
    #     tables_A[0].guests[1] = p1_A
    #
    #     p2_A = Person(2, "P2", 0)
    #     p2_A.table_number = 0
    #     p2_A.position_number = 2
    #     tables_A[0].guests[2] = p2_A
    #
    #     p3_A = Person(3, "P3", 0)
    #     p3_A.table_number = 0
    #     p3_A.position_number = 3
    #     tables_A[0].guests[3] = p3_A
    #
    #     p4_A = Person(4, "P4", 0)
    #     p4_A.table_number = 0
    #     p4_A.position_number = 0
    #     tables_A[0].guests[0] = p4_A
    #
    #     p5_A = Person(5, "P5", 0)
    #     p5_A.table_number = 1
    #     p5_A.position_number = 1
    #     tables_A[1].guests[1] = p5_A
    #
    #     p6_A = Person(6, "P6", 0)
    #     p6_A.table_number = 1
    #     p6_A.position_number = 2
    #     tables_A[1].guests[2] = p6_A
    #
    #     p7_A = Person(7, "P7", 0)
    #     p7_A.table_number = 1
    #     p7_A.position_number = 3
    #     tables_A[1].guests[3] = p7_A
    #
    #     p8_A = Person(8, "P8", 0)
    #     p8_A.table_number = 1
    #     p8_A.position_number = 0
    #     tables_A[1].guests[0] = p8_A
    #
    #     p9_A = Person(9, "P9", 0)
    #     p9_A.table_number = 2
    #     p9_A.position_number = 1
    #     tables_A[2].guests[1] = p9_A
    #
    #     p10_A = Person(10, "P10", 0)
    #     p10_A.table_number = 2
    #     p10_A.position_number = 2
    #     tables_A[2].guests[2] = p10_A
    #
    #     p11_A = Person(11, "P11", 0)
    #     p11_A.table_number = 1
    #     p11_A.position_number = 3
    #     tables_A[2].guests[3] = p11_A
    #
    #     p12_A = Person(12, "P12", 0)
    #     p12_A.table_number = 2
    #     p12_A.position_number = 0
    #     tables_A[2].guests[0] = p12_A
    #
    #     p1_B = Person(1, "P1", 0)
    #     p1_B.table_number = 1
    #     p1_B.position_number = 3
    #     tables_B[1].guests[1] = p1_B
    #
    #     p2_B = Person(2, "P2", 0)
    #     p2_B.table_number = 0
    #     p2_B.position_number = 2
    #     tables_B[2].guests[0] = p2_B
    #
    #     p3_B = Person(3, "P3", 0)
    #     p3_B.table_number = 0
    #     p3_B.position_number = 3
    #     tables_B[0].guests[3] = p3_B
    #
    #     p4_B = Person(4, "P4", 0)
    #     p4_B.table_number = 0
    #     p4_B.position_number = 0
    #     tables_B[0].guests[0] = p4_B
    #
    #     p5_B = Person(5, "P5", 0)
    #     p5_B.table_number = 1
    #     p5_B.position_number = 1
    #     tables_B[1].guests[1] = p5_B
    #
    #     p6_B = Person(6, "P6", 0)
    #     p6_B.table_number = 2
    #     p6_B.position_number = 3
    #     tables_B[2].guests[3] = p6_B
    #
    #     p7_B = Person(7, "P7", 0)
    #     p7_B.table_number = 0
    #     p7_B.position_number = 1
    #     tables_B[0].guests[1] = p7_B
    #
    #     p8_B = Person(8, "P8", 0)
    #     p8_B.table_number = 1
    #     p8_B.position_number = 0
    #     tables_B[1].guests[0] = p8_B
    #
    #     p9_B = Person(9, "P9", 0)
    #     p9_B.table_number = 2
    #     p9_B.position_number = 1
    #     tables_B[2].guests[1] = p9_B
    #
    #     p10_B = Person(10, "P10", 0)
    #     p10_B.table_number = 2
    #     p10_B.position_number = 2
    #     tables_B[2].guests[2] = p10_B
    #
    #     p11_B = Person(11, "P11", 0)
    #     p11_B.table_number = 1
    #     p11_B.position_number = 2
    #     tables_B[1].guests[2] = p11_B
    #
    #     p12_B = Person(12, "P12", 0)
    #     p12_B.table_number = 2
    #     p12_B.position_number = 0
    #     tables_B[2].guests[0] = p12_B
    #
    #     arr1.tables = tables_A
    #     arr2.tables = tables_B
    #
    #     diversity = self.measure_diversity(arr1, arr2)
    #     print("Arr1 and Arr2 diversity: ", diversity)

    def test_diversity(self, arr1, arr2):
        """This only works for table sizes and number of guests as in the
            given example so number guests 12, table size 4, choose correct csv file"""
        arr1 = copy.deepcopy(arr1)
        arr2 = copy.deepcopy(arr2)
        number_of_guests = self.table_size * self.number_tables
        for i in range(number_of_guests):
            P = i + 1
            table_number = int(i / self.table_size)
            position_number = i % self.table_size
            guest = arr1.tables[table_number].guests[position_number]
            if guest is EMPTY_SEAT:
                row = [1]
                new_guest = Person(P, P, row)
                new_guest.table_number = table_number
                new_guest.position_number = position_number
                arr1.tables[table_number].guests[position_number] = new_guest
            else:
                guest.change_index(P)
            # arr1.tables[table_number].guests[position_number].index = P

        indexs = [4, 7, 2, 3, 8, 5, 11, 1, 12, 9, 10, 6]
        for i, p in enumerate(indexs):
            table_number = int(i / self.table_size)
            position_number = i % self.table_size
            guest = arr2.tables[table_number].guests[position_number]
            if guest is EMPTY_SEAT:
                row = [1]
                new_guest = Person(p, p, row)
                new_guest.table_number = table_number
                new_guest.position_number = position_number
                arr2.tables[table_number].guests[position_number] = new_guest
            else:
                guest.change_index(p)

        diversity = self.measure_diversity(arr1, arr2)
        print("working")

    def measure_diversity(self, arr1, arr2):  # todo step through this and make sure it's working
        diversity = 0
        seating_matched = False
        position_matched = 0  # 0 means nextToR and 1 means nextToL
        for table in arr1.tables:
            for i, person in enumerate(table.guests):  # todo step through to see where diverty per person fails?
                if person is EMPTY_SEAT:
                    continue
                A_nexto_R = self.nextToR(person.index, arr1)
                A_nexto_L = self.nextToL(person.index, arr1)
                B_nexto_R = self.nextToR(person.index, arr2)
                B_nexto_L = self.nextToL(person.index, arr2)
                if not(A_nexto_R == B_nexto_R) and not(A_nexto_R == B_nexto_L):
                    diversity += 1
                else:
                    seating_matched = True
                    if A_nexto_R == B_nexto_R:
                        position_matched = 0
                    else:
                        position_matched = 1
                if not seating_matched:
                    if not(A_nexto_L == B_nexto_R) and not(A_nexto_L == B_nexto_L):
                        diversity += 1
                else:
                    if not position_matched and not (A_nexto_L == B_nexto_L):
                        diversity += 1
                    elif position_matched and not (A_nexto_L == B_nexto_R):
                        diversity += 1

                temp = 0

                # for every other person at the table, check if they share a table in arr2
                for other_person in table.guests:
                    if person is not other_person and other_person is not EMPTY_SEAT:
                        if self.check_share_table(person.index, other_person.index, arr2):
                            temp += 1

                for i in range(self.get_common_emtpy_seats(person, arr1, arr2)):
                    temp += 1

                diversity += self.table_size - 1 - temp

        return diversity

    def nextToR(self, person_number, arrangement): #todo step through this make sure working
        """Given a person's identifier index number and an arrangement
            return the person's identifier seated to the right"""
        for table in arrangement.tables:
            for guest in table.guests:
                if guest.index == person_number:
                    if guest.position_number == 0:
                        if table.guests[0] == EMPTY_SEAT:
                            return EMPTY_SEAT
                        return table.guests[self.table_size - 1].index
                    else:
                        if table.guests[guest.position_number - 1] == EMPTY_SEAT:
                            return EMPTY_SEAT
                        return table.guests[guest.position_number - 1].index

    def nextToL(self, person_number, arrangement): #todo step through this make sure working
        """Given a person's identifier index number and an arrangement
            return the person's identifier seated to the right"""
        for table in arrangement.tables:
            for guest in table.guests:
                if guest.index == person_number:
                    if guest.position_number == self.table_size - 1:
                        if table.guests[0] == EMPTY_SEAT:
                            return EMPTY_SEAT
                        return table.guests[0].index
                    else:
                        if table.guests[guest.position_number + 1] == EMPTY_SEAT:
                            return EMPTY_SEAT
                        return table.guests[guest.position_number + 1].index

    def check_share_table(self, id_1, id_2, arrangement):  #todo step through this make sure working
        """Check if person.index = 1d_1 && id_2 share a table in arrangement"""
        first_table, first_position = arrangement.guest_from_index(id_1)
        second_table, second_position = arrangement.guest_from_index(id_2)
        return first_table == second_table

    def get_common_emtpy_seats(self, person, arr1, arr2):
        empty_1 = arr1.get_empty_seats(person.table_number)
        empty_2 = arr2.get_empty_seats(person.table_number)
        if empty_1 >= empty_2:
            return empty_1
        else:
            return empty_2

    @staticmethod
    def in_list(index_search, person_list):
        for index, i in enumerate(person_list):
             # if self.__eq__(i):
            if index_search == i.index:
                 return True
        return False

    @staticmethod
    def get_index(index_search, person_list):
        for index, i in enumerate(person_list):
            if index_search == i.index:
                return index
    #
    # def check_left_left(self, person, table, arr2):
    #     """take the person find their identity and the identity
    #         of the peron on their left in arr1 then check if the same person is
    #         seated to the left of peron in arr2"""
    #     middle_person_identity = person.index
    #     left_person_index1, right_person_index1 = self.leftright_index(i, table.guests)
    #     table_arr2, position_arr2 = arr2.guest_from_index(middle_person_identity)
    #     if position_arr2 == 0:
    #         left_index_arr2 = arr2.tables[table_arr2].guests[self.table_size - 1]
    #     else:
    #         left_index_arr2 = arr2.tables[table_arr2].guests[position_arr2 - 1]
    #     return left_index_arr2 == left_person_index1
    #
    #
    # def check_left_left(self, person, table, arr2):  # todo need this?
    #     """take the person find their identity and the identity
    #         of the peron on their left in arr1 then check if the same person is
    #         seated to the left of peron in arr2"""
    #     middle_person_identity = person.index
    #     left_person_index1, right_person_index1 = self.leftright_index(i, table.guests)
    #     table_arr2, position_arr2 = arr2.guest_from_index(middle_person_identity)
    #     if position_arr2 == 0:
    #         left_index_arr2 = arr2.tables[table_arr2].guests[self.table_size - 1]
    #     else:
    #         left_index_arr2 = arr2.tables[table_arr2].guests[position_arr2 - 1]
    #     return left_index_arr2 == left_person_index1
    #
    # def leftright_index(self, middle_position, arrangement):  # todo need this?
    #     """given the position in the table get the index of the persons to the left and right"""
    #     if middle_position == 0:
    #         left_person_index = table.guests[self.table_size - 1].index
    #         right_person_index = table.guests[middle_position + 1].index
    #     elif middle_position == self.table_size - 1:
    #         left_person_index = table.guests[middle_position - 1].index
    #         right_person_index = table.guests[0].index
    #     else:
    #         left_person_index = middle_position - 1
    #         right_person_index = middle_position + 1
    #
    #     return left_person_index, right_person_index
    #




