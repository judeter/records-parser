# -*- coding: utf-8 -*-
"""
Author: Justin Deterding

Description:

"""
import logging
from io import StringIO
from pdf2image import convert_from_path
import pytesseract as pt
import cv2
import os


from deceased import Deceased


class DeathRecord(object):

    def __init__(self, page_file_name):
        self.lots = []
        self.deceased = []
        self.page_number = None
        self.page_str = ''
        logging.basicConfig(filename=page_file_name[:-3]+'log', level=logging.INFO)
        self.parse_page(page_file_name)

    def write_to_csv(self, file_name):
        with open(file_name, mode='w') as file:
            file.write(Deceased.get_csv_header())
            for person in self.deceased:
                file.write(person.to_csv_line())

    def parse_page(self, page_text_file: str) -> None:

        with open(page_text_file, mode='r') as file:
            self.page_str = "".join(file.readlines())

        lines = parse_page_to_words(self.page_str)

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

        """
        for line in stream:
            words = line.strip().split(' ')
            
            if 'Lot' in words or 'Lots' in words:
                current_lot = DeathRecord.parse_lot_from_line(words)
                self.lots.append(current_lot)
            
            if DeathRecord.has_deceased_in_line(words):
                deceased_line = words
                current_pos = stream.tell()
                words = stream.readline().strip().split(' ')
                while not DeathRecord.has_deceased_in_line(words) and words[0] != '' \
                      and ('Lot' in words or 'Lots' in words):
                    deceased_line += words
                    current_pos = stream.tell()
                    words = stream.readline().strip().split(' ')
                stream.seek(current_pos)
                self.deceased.append(Deceased(deceased_line, current_lot))
        """

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


def convert_pdfs_to_imgs(pdfs: list):
    img_names = []
    for pdf in pdfs:
        print('Converting {} to image ...'.format(pdf))
        img = convert_from_path(pdf, dpi=500)[0]

        img_name = pdf.split('.')[0] + '.jpg'
        img.save(img_name, 'JPEG')
        img_names.append(img_name)

    return img_names


def convert_imgs_to_txts(imgs: list):
    txt_names = []
    for img in imgs:
        print('Converting {} to text'.format(img))
        img_cv = cv2.imread(img)
        # By default OpenCV stores images in BGR format and since pytesseract
        # assumes RGB format, we need to convert from BGR to RGB format/mode:
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        pg_string = pt.image_to_string(img_rgb)
        txt_name = img.split('.')[0] + '.txt'

        with open(txt_name, mode='w') as file:
            file.write(pg_string)
        txt_names.append(txt_name)

    return txt_names

def convert_txts_to_csvs(text_file_names: list):

    pages = []

    for page_name in text_file_names:
        page = DeathRecord(page_name)
        page.write_to_csv(page_name[:-3]+'csv')
        pages.append(page)

    return pages


if __name__ == '__main__':

    #pdfs = []
    #for path, dirs, files in os.walk('Woodlawn cemetery'):
    #    pdfs += [path+'\\'+file for file in files if file.endswith('pdf') and file[:4] == 'page']
    #img_names = convert_pdfs_to_imgs(pdfs)

    #txt_names = convert_imgs_to_txts(img_names)
    #txt_names = [file for file in os.listdir() if file.endswith('txt')]
    txt_names = []
    for path, dirs, files in os.walk('Woodlawn cemetery'):
        txt_names += [path+'\\'+file for file in files if file.endswith('txt') and file[:4] == 'page']

    pages = convert_txts_to_csvs(txt_names)