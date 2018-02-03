

class Person:

    # constructor must be passed a row from the csv file
    def __init__(self, person_index, name, csv_row):
        self.index = person_index  # todo with the addition of name, index may now be unnecessary
        self.name = name
        self.preferences = csv_row[:]
        self.table_number = None
        self.position_number = None

    def change_index(self, index):
        self.index = index

    def print_preferences(self):
        print(self.index, self.preferences)

    def assign_table(self, table_number):
        self.table_number = table_number

    # position within the table
    def assign_position(self, position_number):
        self.position_number = position_number


# todo am i even using these two functions??
    def check_on_right(self, person2):
        """check if person2 is on the right at the same table of person1 """
        if self.table_number == person2.table_number:
            if self.position_number == self.table_size - 1:
                return person2.position_number == 0
            else:
                return person2.position_number == self.position_number + 1
        else:
            return False

    def check_on_left(self, person2):
        """check if person2 is on the left at the same table of person1 """
        if self.table_number == person2.table_number:
            if self.position_number == 0:
                return person2.position_number == self.table_size + 1
            else:
                return person2.position_number == self.position_number - 1
        else:
            return False



