# -*- coding: utf-8 -*-
"""
Author: Justin Deterding

Description:

"""
import logging

class Deceased(object):
    
    def __init__(self, record_line, page_number, lot):
        self.last_name = None
        self.first_name = None
        self.birth_year = None
        self.death_year = None
        self.birth_month = None
        self.death_month = None
        self.page_number = page_number
        self.lot = lot
        self.record_information = " ".join(record_line)
        self.parse_record_line(record_line)
        
    def __str__(self):
        msg = '{:15s}, {:15s}\n'.format(self.last_name, self.first_name)
        msg += '\tPage Number:{}, \tLot(s):{}\n'.format(self.page_number,
                                                     self.lot)
        msg += '\tBirth Data:{} / {}\n'.format(self.birth_month, 
                                               self.birth_year)
        msg += '\tDeath Data:{} / {}\n'.format(self.death_month, 
                                               self.death_year)
        return msg
    
    def to_csv_line(self):
        """ 
        Return a string of camma seperated values for the deceased.
        """
        csv_line = "{},".format(self.last_name)
        csv_line += "{},".format(self.first_name)
        csv_line += "{},".format(self.birth_year)
        csv_line += "{},".format(self.birth_month)
        csv_line += "{},".format(self.death_year)
        csv_line += "{},".format(self.death_month)
        csv_line += "{},".format(self.page_number)
        csv_line += "{}\n".format("&".join(self.lot))
        return csv_line

    @staticmethod
    def get_csv_header():
        csv_line = "{},".format('Last Name')
        csv_line += "{},".format('First Name')
        csv_line += "{},".format('Birth year')
        csv_line += "{},".format('Birth_month')
        csv_line += "{},".format('Death_year')
        csv_line += "{},".format('Death month')
        csv_line += "{},".format('Page number')
        csv_line += "{}\n".format('Lot')
        return csv_line
        
    def parse_record_line(self, line):
        # Death data could be in day/month/year format
        # Also could only have a death data.
        self.last_name = line[0][:-1]
        if line[1][0].isupper():
            self.first_name = line[1]
        self.set_birth_and_death_dates(line)

    @staticmethod
    def is_a_month(word):
        # TODO: docs
        # TODO: unit test
        if word.lower() in ['jan','jan.', 'january']:
            return 1
        elif word.lower() in ['feb', 'feb.', 'februrary']:
            return 2
        elif word.lower() in ['mar', 'mar.', 'march']:
            return 3
        elif word.lower() in ['apr', 'apr.', 'april']:
            return 4
        elif word.lower() in ['may']:
            return 5
        elif word.lower() in ['jun', 'jun.', 'june']:
            return 6
        elif word.lower() in ['jul', 'jul.', 'july']:
            return 7
        elif word.lower() in ['aug', 'aug.', 'august']:
            return 8
        elif word.lower() in ['sept', 'sept.', 'september']:
            return 9
        elif word.lower() in ['oct', 'oct.', 'october']:
            return 10
        elif word.lower() in ['nov', 'nov.', 'november']:
            return 11
        elif word.lower() in ['dec', 'dec.', 'december']:
            return 12
        else:
            return False
    
    @staticmethod
    def is_a_year(word: str) -> int:
        """
        Uses the find_ints_in_word function to find ints in word. If a single
        int it found it is examed to determine if it is a year. If it is then 
        the year is returned otherwise zero is returned.

        Parameters
        ----------
        word : str
            A string to attempt to find a year in.

        Returns
        -------
        int
            The year if one is found otherwise 0

        """
        year = Deceased.find_ints_in_word(word)
        if len(year) == 1 and year[0] > 1500 and year[0] < 2020:
            return year[0]
        return 0
    
    @staticmethod
    def is_a_day(word: str) -> int:
        """
        Uses the find_ints_in_word function to find ints in word. If a single
        int it found it is examed to determine if it is a day. If it is then 
        the day is returned otherwise zero is returned.

        Parameters
        ----------
        word : str
            A string to attempt to find a day in.

        Returns
        -------
        int
            The year if one is found otherwise 0

        """
        day = Deceased.find_ints_in_word(word)
        if len(day) == 1 and day[0] > 0 and day[0] < 32:
            return day[0]
        return 0
        
    @staticmethod
    def find_ints_in_word(word: str) -> list:
        """
        This function determines if there are integers in a word.
        It is a helper function for other functions used for determining dates.

        Parameters
        ----------
        word : str
            A word that could possibly contain a integer.

        Returns
        -------
        list
            A list of the discovered integers in the word.

        """

        numbers = []
        i = 0
        current_number = ''
        while i < len(word):
            # Found the start of a number or more of a number
            if word[i] in '0123456789':
                current_number += word[i]
            # Current character not a number, check if number just ended
            elif len(current_number) > 0:
                numbers.append(int(current_number))
                current_number = ''
            i += 1
        # if ended on gathering a number
        if len(current_number) > 0:
            numbers.append(int(current_number))
            
        return numbers

    def find_dates_in_a_line(self, line):
        
        dates = []
        words = iter(line)
        while True:
            try:
                word = next(words)
                
                if self.is_a_day(word):
                    day = self.is_a_day(word)
                    month = self.is_a_month(next(words))
                    year = self.is_a_year(next(words))
                    dates.append((day, month, year))
                
                if self.is_a_month(word):
                    day = None
                    month = self.is_a_month(word)
                    year = self.is_a_year(next(words))
                    dates.append((day, month, year))
                
                if self.is_a_year(word):
                    day = None
                    month = None
                    year = self.is_a_year(word)
                    dates.append((day, month, year))
                
                if self.is_dd_mm_yyyy(word):
                    day, month, year = self.is_dd_mm_yyyy(word)
                    dates.append((day, month, year))
                    
            except StopIteration:
                break
        return dates

    def is_dd_mm_yyyy(self, word):
        
        if word.find('/') == 2:
            day_month_year = self.find_ints_in_word(word)
            
            if len(day_month_year) == 3:
                day, month, year = day_month_year            
                return day, month, year
        
        return False
    
    def set_birth_and_death_dates(self, line):
        
        dates = self.find_dates_in_a_line(line)
        
        base_msg_str = '-----------------------------------------------\n'
        base_msg_str += '{}\n'
        base_msg_str += '-----------------------------------------------\n'
       
        if len(dates) > 2:
            birth_date = dates[0]
            death_date = dates[1]

            msg_str = 'More than two years were found in the record...\n'
            msg_str += base_msg_str
            msg_str += 'Below are birth and death dates returned:\n'
            msg_str += 'birth date: {} \n '
            msg_str += 'death date: {} \n'
            msg_str = msg_str.format(' '.join(line), birth_date, death_date)
            logging.info(msg_str)
            
            self.birth_year = birth_date[2]
            self.birth_month = birth_date[1]
            self.death_year = death_date[2]
            self.death_year = death_date[1]
        
        elif len(dates) == 2:
            birth_date = dates[0]
            death_date = dates[1]
            
            self.birth_year = birth_date[2]
            self.birth_month = birth_date[1]
            self.death_year = death_date[2]
            self.death_month = death_date[1]
        
        elif len(dates) == 1:
            
            death_date = dates[0]
            
            msg_str = 'Only one date was found in the record...\n'
            msg_str += base_msg_str
            msg_str += 'Below is the death date reurned:\n'
            msg_str += 'death date: {} \n'
            msg_str = msg_str.format(' '.join(line), death_date)
            logging.info(msg_str)
            
            self.death_year = death_date[2]
            self.death_month = death_date[1]
        
        else:
            msg_str = 'No dates were found in the record...\n'
            msg_str += base_msg_str
            msg_str = msg_str.format(' '.join(line))
            logging.info(msg_str)
