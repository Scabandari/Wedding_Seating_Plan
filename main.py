#!/usr/bin/env/ python3
import random as rand
import csv
import math
import copy
from person import Person
from population import Population
from arrangement import Arrangement, EMPTY_SEAT

"""
    This is a solution to Assignment 1 Evolutionary Algorithms with Dr. Kharma, Concordia University, Winter 2018.
    Given a csv file of guest preferences this program attempts to find an optimal seating arrangement using 
    Evolutionary Algorithms. The fitness of the solution is based on a penalty system for ignoring guests preferences.
    The lower the better. Diversity is a measure of how different the solutions are from each other.  
"""

NUMBER_GENERATIONS = 80
# table_size = rand.randrange(5, 11)

text_file = open('settings.txt', 'r')

table_size = int(text_file.readline())
number_guests = int(text_file.readline())
CSV_FILE = 'preferences.csv'
#
# table_size = 4
# number_guests = 7
#
# number_guests = 5
# #
# table_size = 4
# number_guests = 10

# for testing diversity
# number_guests = 12
# table_size = 4

print("The size of tables for this simulation is: ", table_size)

guest_list = []
global_names = []

# with open('preferences_7.csv') as csv_file:
# with open('preferences_10 _names.csv') as csv_file:
    # with open('preferences_5.csv') as csv_file:
    # with open('preferences_12.csv') as csv_file:
with open(CSV_FILE) as csv_file:
    readCSV = csv.reader(csv_file, delimiter=',')
    iter_csv = iter(readCSV)
    names = next(iter_csv)
    for name in names:
        global_names.append(name)
    # i = 0
    # for row in readCSV:
    #     person = Person(i, row)
    #     guest_list.insert(i, person)
    #     i = i + 1
    names.pop(0)  # gets rid of the ''

    for index, row in enumerate(iter_csv):
        if len(row) < 1:
            continue
        name = row.pop(0)
        person = Person(index, names[index], row)
        if len(person.preferences) > 0:
            guest_list.insert(index, person)

number_tables = math.ceil(number_guests / table_size)
print("The number of guests and tables for this simulation is:", len(guest_list), number_tables)

population = Population(number_tables, table_size, guest_list)
population.evolve_generations(NUMBER_GENERATIONS, False)  # True A only, False B runs with Diversity enhancement



