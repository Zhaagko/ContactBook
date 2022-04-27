import sqlite3
import string
import os
from prettytable import PrettyTable


class DataBase:

    def __init__(self, database_file="storage.db", table_name="CONTACTS"):
        # set the path to database with users
        self.database_filename = database_file
        # set name for database table
        self.table_name = table_name
        # connect to database
        self.database = sqlite3.connect(self.database_filename)
        # create cursor
        self.database_cursor = self.database.cursor()
        # table column scheme
        self.column_scheme = ["id integer primary key",
                              "f_name text",
                              "l_name text",
                              "phone text",
                              "email text"]
        # separated column scheme
        self.column_scheme_sep = tuple([i.split(" ")[0] for i in self.column_scheme[1:len(self.column_scheme)]])
        # is new table
        self.is_new_table = False
        # create table if not find it
        self.__create_table()

    # create a new contact entry in table
    def create_new_contact(self, f_name, l_name, phone, email):
        row = [f_name, l_name, phone, email]
        row = [f"'{str(i)}'" for i in row]

        request = f'''insert into {self.table_name} ({",".join(self.column_scheme_sep)}) values ({",".join(row)})'''
        
        # try to make INSERT request to table and return one string if succeed
        try:
            # write a request
            request = f'''insert into {self.table_name} ({",".join(self.column_scheme_sep)}) values ({",".join(row)})'''
            # send request to table
            self.database_cursor.execute(request)
            # commit changes
            self.database.commit()
            return "Success."
        # raise an exception if bad request
        except sqlite3.OperationalError:
            return "Bad request."

    # delete contacts from database
    def delete_contact(self, values):
        # delete all contacts from database
        if '*all*' in values:
            request = f"delete from {self.table_name}"
        else:
            request = f"delete from {self.table_name} where (f_name = '{values[1]}') and (l_name = '{values[2]}') and (phone = '{values[3]}') and (email = '{values[4]}')" 
       
        try:
            self.database_cursor.execute(request)
            self.database.commit()
            return "Success"
        except sqlite3.OperationalError:
            return "Bad request."
                
    # find contact which contain some of find values
    def find_contact(self, values):
        if '*all*' in values:
          request = f"select * from {self.table_name} order by f_name"
        else:
            # change values type from 'tuple' to 'list' with 'str' typed elements
            find_values = ",".join([f"'{str(i)}'" for i in values])
            # write a request
            request = f'''select * from {self.table_name} where f_name in ({find_values}) 
            or l_name in ({find_values}) or phone in ({find_values}) 
            or email in ({find_values}) order by f_name'''
        try:
            # send request to table
            self.database_cursor.execute(request)
            # get result from SELECT request
            result = self.database_cursor.fetchall()
            return result
        except sqlite3.OperationalError:
            return "Bad request"

    # create new table in database if it was not created
    def __create_table(self):
        try:
            request = f'''select * from {self.table_name}'''
            self.database_cursor.execute(request)
        except sqlite3.OperationalError:
            request = f'''create table {self.table_name} ({",".join(self.column_scheme)})'''
            self.database_cursor.execute(request)
            # commit changes
            self.database.commit()

            self.is_new_table = True
    
    # close database
    def close_database(self):
        self.database.close()


class StrOperations:

    @staticmethod
    def levenshtein_distance(word_a, word_b):
        len_a, len_b = len(word_a), len(word_b)
        if len_a > len_b:
            word_a, word_b = word_b, word_a
            len_a, len_b = len_b, len_a

        current_row = range(len_a + 1)

        for i in range(1, len_b + 1):
            prev_row, current_row = current_row, [i] + [0] * len_a
            for j in range(1, len_a + 1):
                add, delete, change = prev_row[j] + 1, current_row[j - 1] + 1, prev_row[j - 1]
                if word_a[j - 1] != word_b[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)

        return current_row[len_a]

    @staticmethod
    def fuzzy_comparison(word, compare_list):
        diff_border = 3
        max_similarity = 10 ** 6
        word_with_max_similarity = ""

        for compare in compare_list:
            distance = StrOperations.levenshtein_distance(word, compare)

            if distance < max_similarity:
                max_similarity = distance
                word_with_max_similarity = compare

        return word_with_max_similarity if (max_similarity < diff_border) else ""

    @staticmethod
    def is_chars_in_line(chars, line):
        for ch in chars:
            if ch in line:
                return True
        return False

    @staticmethod
    def count_of_chars_in_line(chars, line):
        count = 0
        for i in chars:
            for j in line:
                if i == j:
                    count += 1
        return count


class Executor:

    def __init__(self):
        # create DataBase object to work with it
        self.database = DataBase()
        # dictionary of commands and functions for its
        self.dict_of_commands = {"create": self.create_new_contact, 
                                "exit": self.__exit, 
                                "viewall": self.view_all, 
                                "deleteall": self.delete_all,
                                "find": self.find_contact,
                                "delete": self.delete_contact}

        if self.database.is_new_table:
            self.print_info()
        
        # a program work while this value True
        self.__program_work = True
        # start work with database
        self.start_work()

    # function that used to start main cycle for program that take some user's input and do something
    def start_work(self):
        command_line = ""
        # main cycle of a program
        while self.__program_work:
            # input a line with command
            command_line = input("Write a command: ").split()
            # first word in line recognize like a 'command' for program to do something
            # it used like a key for 'command_dictionary'
            command = command_line[0]
            # other words is attributes for some command
            attributes = [command_line[i] for i in range(1, len(command_line))]
            #clear previous printing
            if os.name == "nt":
                os.system('cls')
            else:
                os.system('clear')
            # here we try to run some function that placed on key 'command' in dictionary 'self.dict_of_command'
            try:
                # with key in 'command' we address to dictionary 'self.dict_of_command'
                self.dict_of_commands[command.lower()](attributes)
            # if raise an error - print message 'Unknown command....'
            except KeyError:
                # If error was raised it could mean that: user input wrong command,
                # or user just make an error in word of command.
                # With function 'fuzzy_comparison' we try to help user to find necessary word for a command
                potential_key = StrOperations.fuzzy_comparison(command.lower(), list(self.dict_of_commands.keys()))
                # if potential key was found we print message with prompt
                if potential_key != "":
                    print(f"Unknown command: '{command}'. Maybe you meant '{potential_key}'?")
                else:
                    print(f"Unknown command: '{command}'.")

            print("")
        # close database when end the programm
        self.database.close_database()

    # set new value to variable to end the program
    def __exit(self, *args):
        self.__program_work = False

    # create new contact in database
    def create_new_contact(self, values):
        if len(values) < 3:
            print(values)
            print("More data needed.")

        else:
            if len(values) > 4:
                print("Extra information will be cut!", end="\n")
            contact_attributes = " ".join(values[0:2])

            values.append("---")

            self.database.create_new_contact(f_name=values[0],
                                                     l_name=values[1],
                                                     phone=values[2],
                                                     email=values[3])
            print(f"Contact '{contact_attributes}' was created!")

    def view_all(self, *args):
        result = self.database.find_contact("*all*")
        if len(result) == 0:
            print("There are no one contact! Create some contacts to see they!")
        else:
            self.__table_printing(result)
    
    def delete_all(self, *args):
        clear_database = input("Do you want to delete ALL contacts from database? Write 'Yes' or 'No': ").lower()
        if clear_database == "yes":
            self.database.delete_contact("*all*")
            print("Contacts has been deleted successfully!")
            
    def find_contact(self, values):
        result = self.database.find_contact(values)
        if result != "Bad request":
            self.__table_printing(result)
            return result
        else:
            print(result)

    def delete_contact(self, values):
        result = self.find_contact(values)

        id_to_delete = int(input("Input ID of contact that you will delete: ")) - 1

        delete = result[id_to_delete]
        self.database.delete_contact(delete)

        print(f"Contact {result[id_to_delete][1]} {result[id_to_delete][2]} has been deleted successfuly.")
    
    def __table_printing(self, rows):
        table = PrettyTable()
        table.field_names = ["id"] + list(self.database.column_scheme_sep)
        
        for id, row in enumerate(list(rows)):
            table.add_row([id+1] + list(row[1:len(row)]))
        
        print(table)

    def print_info(self, *args):
        None


if __name__ == "__main__":
    new_executor = Executor()
