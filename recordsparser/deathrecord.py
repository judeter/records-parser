# -*- coding: utf-8 -*-
"""
Author: Justin Deterding

Description:


# TODO: Change deathrecord.py -> record.py
"""
import logging
from io import StringIO
import pytesseract as pt
import cv2
from pdf2image import convert_from_path
import os
import sys

from .deceased import Deceased


class DeathRecord(object):

    def __init__(self, page_file_name):
        self.lots = []
        self.deceased = []
        self.page_number = None
        self.page_str = ''
        logging.basicConfig(filename=page_file_name[:-3]+'log', level=logging.INFO)
        if '.' in page_file_name:
            self.parse_pdf_to_csv(page_file_name)
        else:
            self.parse_directory_to_csvs(page_file_name)

    def write_to_csv(self, file_name):
        with open(file_name, mode='w') as file:
            file.write(Deceased.get_csv_header())
            for person in self.deceased:
                file.write(person.to_csv_line())

    def parse_page(self, page_text_file: str) -> None:

        with open(page_text_file, mode='r') as file:
            self.page_str = "".join(file.readlines())

        lines = self.parse_page_to_words(self.page_str)

        self.page_number = DeathRecord.get_page_number(lines)

        lot_iter = iter(DeathRecord.find_lot_lines(lines))
        dec_iter = iter(DeathRecord.find_deceased_lines(lines))

        # Main loop
        try:
            next_lot_indx = next(lot_iter)
            next_dec_indx = next(dec_iter)
            if next_lot_indx > next_dec_indx:
                curr_lot: str = 'NA'
            else:
                curr_lot = DeathRecord.get_lot_from_line(lines[next_lot_indx])
                next_lot_indx = next(lot_iter)
        except StopIteration:
            # What to fo if lot_iter or dec_iter have nothing
            pass

        last_lot = False
        while True:
            # passed into a new lot and need to update current lot
            if next_lot_indx < next_dec_indx:
                curr_lot = DeathRecord.get_lot_from_line(lines[next_lot_indx])
                try:
                    next_lot_indx = next(lot_iter)
                except StopIteration:
                    pass

            curr_dec_indx = next_dec_indx
            try:
                next_dec_indx = next(dec_iter)
            except StopIteration:
                next_dec_indx = -1

            record_line = []
            for line in lines[curr_dec_indx:next_dec_indx]:
                record_line += line

            self.deceased.append(Deceased(record_line, self.page_number, curr_lot))

            if next_dec_indx == -1:
                break

    @staticmethod
    def get_page_number(page_list: list) -> int:
        """
        Searched for the phrase,
            Print this item: Page #
        and extracts the page number from the phrase.
        
        Parameters
        ----------
        page_list : list
            The parsed page string from parse_page_to_words.

        Raises
        ------
        Warning
            Warns if the page number cannot be found.

        Returns
        -------
        int
            Returns the found page number or -1 if the page cannot be found.

        """

        for line in page_list:
            if line[0:3] == ['Print', 'this', 'item:']:
                return int(line[-1])
        # raise Warning('Unable to determine page number. Returning page as -1')
        return -1

    # has, get, and find deceased key word functions --------------------------

    @staticmethod
    def has_deceased_in_line(line: list) -> bool:
        """
        Determines is the line containes the start of the record of a deceased 
        person. Based on the following pattern
            LASTNAME, Firstname 
            -> Last name is all capital letters.
            -> Last name ends with ','.
            -> First name starts with capital letter.
        Parameters
        ----------
        line : list
            A list of words in a line.

        Returns
        -------
        bool
            True if the pattern is matched, false otherwise.

        """
        if len(line) == 1:
            return False

        last_name = line[0]
        first_name = line[1]
        if (last_name.isupper() and last_name[-1] == ','
                and first_name[0].isupper()):
            return True
        return False

    @staticmethod
    def get_deceased_from_line(line: list) -> (str, str):
        """
        Parses the (LASTNAME, Firstname) from a line containing a deceased.
        Line is checked agains the pattern for deceased names using 
        has_dceased_in_line.
        Parameters
        ----------
        line : list
            A list of words parsed from a line in the death record.

        Raises
        ------
        RuntimeError
            The given line does not contain a deceased individual.

        Returns
        -------
        (str, str)
            (LASTNAME, Firstname) of deceased from the line.

        """
        if DeathRecord.has_deceased_in_line(line):
            last_name = line[0]
            first_name = line[1]
            return last_name[:-1], first_name
        raise RuntimeError('Given line did not have deceased.')

    @staticmethod
    def find_deceased_lines(lines: list) -> list:
        """
        Findes the indicies of lines where decesed names are found.

        Parameters
        ----------
        lines : list
            A list of lines or words from the parse_page_to_words mehod.

        Returns
        -------
        list
            A list of the indicies containing decesed.

        """

        indices = []
        for index, line in enumerate(lines):
            if DeathRecord.has_deceased_in_line(line):
                indices.append(index)

        return indices

    # has, get, and find lot key word functions -------------------------------

    @staticmethod
    def has_lot_in_line(line: list) -> bool:
        """
        Checks if the line contains lot information by checking that the first
        words is, 'Lot' or 'Lots'.

        Parameters
        ----------
        line : list
            A list of words parsed from a line in the death record.

        Returns
        -------
        bool
            True is the pattern is meet otherwise false.

        """
        if line[0] in ['Lots', 'Lot']:
            return True
        return False

    @staticmethod
    def get_lot_from_line(line: list) -> str:
        """
        Parses the lot from the line assuming its the last word in the line
        and removes the ':'

        Parameters
        ----------
        line : list
            Line containing the lot.

        Returns
        -------
        str
            The parsed lot from the line.

        """

        assert DeathRecord.has_lot_in_line(line)
        return tuple([word.replace(':', '') for word in line
                      if word[0].isnumeric()])

    @staticmethod
    def find_lot_lines(lines: list) -> list:
        """
        Searches for lines tha match the pattern in has_lot_in_line.

        Parameters
        ----------
        lines : list
            The list from the parse_pages_to_words method.

        Returns
        -------
        list
            A list of indices of the lines containing lot information.

        """

        indices = []
        for index, line in enumerate(lines):
            if DeathRecord.has_lot_in_line(line):
                indices.append(index)

        return indices

    @staticmethod
    def parse_page_to_words(page_string: str) -> list:
        """
        From a string of a death record page, the string is parsed into a list
        of list with each inner list being list of words in a line and the
        outer list being all of the list in a page.

        Parameters
        ----------
        page : str
            A string of the death record.

        Returns
        -------
        list
            A nested list.
            [[word_11, word_12,...], # line 1
             [word_21, word_22,...], # line 2
             ...,
             [word_n1, word_n2,...]] # line n

        """

        stream = StringIO(page_string)
        page_list = [line.strip().split(' ') for line in stream
                     if line.strip() != '']

        return page_list

    @staticmethod
    def convert_pdf_to_image(pdf_file: str) -> str:

        img = convert_from_path(pdf_file, dpi=500)[0]

        image_file = pdf_file.split('.')[0] + '.jpg'
        img.save(image_file, 'JPEG')

        return image_file

    @staticmethod
    def convert_image_to_text(image_file: str) -> str:
        img_cv = cv2.imread(image_file)
        # By default OpenCV stores images in BGR format and since pytesseract
        # assumes RGB format, we need to convert from BGR to RGB format/mode:
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        pg_string = pt.image_to_string(img_rgb)
        text_file = image_file.split('.')[0] + '.txt'

        with open(text_file, mode='w') as file:
            file.write(pg_string)

        return text_file

    @staticmethod
    def parse_texts_to_csv(text_file: str) -> str:

        page = DeathRecord(text_file)
        page.write_to_csv(text_file[:-3]+'csv')

        return page

    @staticmethod
    def parse_pdf_to_csv(pdf_file: str) -> str:
        image_file = DeathRecord.convert_pdf_to_image(pdf_file)
        text_file = DeathRecord.convert_image_to_text(image_file)
        csv_file = DeathRecord.parse_texts_to_csv(text_file)
        return csv_file

    @staticmethod
    def parse_directory_to_csvs(dir_name: str) -> list:

        csv_files = []
        for path, sub_dirs, files in os.walk(dir_name):
            for file in files:
                if file.endswith('pdf') and file.split(' ')[0]== 'page':
                    csv_file = DeathRecord.parse_pdf_to_csv(path + '\\' + file)
                    csv_files.append(csv_file)
        return csv_files

# TODO: change converts to convert a single file
# TODO: Add parse directory
# TODO: Add parse file

if __name__ == '__main__':

    DeathRecord(sys.argv[1])
