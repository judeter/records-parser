# -*- coding: utf-8 -*-
"""
Author: Justin Deterding

Description:

"""
import os

from recordsparser.deathrecord import DeathRecord


def test_parse_page_to_words():
    
    record = DeathRecord.parse_page_to_words("word11 word12 word13 \n \
                                              \n \
                                              word21 word22 word23 ")
    
    assert record == [['word11', 'word12', 'word13'],
                      ['word21', 'word22', 'word23']]


    record = DeathRecord.parse_page_to_words("word11 word12 word13 \n \
                                              \n \n \
                                              word21 word22 word23 ")
    
    assert record == [['word11', 'word12', 'word13'],
                      ['word21', 'word22', 'word23']]


def test_get_page_number():
    
    assert 9 == DeathRecord.get_page_number([['foo', 'bar', 'baz'],
                                             ['Print', 'this', 'item:', 'Page', '9']])
    
def test_has_get_find_deceased():
    
    test_str = "Lots 5 & 6: \n \
                STULLKEN family stone with small stones that read:\n \
                STULLKEN, Catharine F.W. 14 Jan 1838 - 3 Nov 1874 double stone\n"
    
    names = [('STULLKEN', 'Catharine')]
    
    lines = DeathRecord.parse_page_to_words(test_str)
    
    deceased_indices = DeathRecord.find_deceased_lines(lines)
    
    assert deceased_indices == [2]
    
    for index, name in zip(deceased_indices, names):
        assert name == DeathRecord.get_deceased_from_line(lines[index])
        
def test_has_get_find_lots():
    
    test_str = "Lots 5 & 6: \n \
                STULLKEN family stone with small stones that read:\n \
                STULLKEN, Catharine F.W. 14 Jan 1838 - 3 Nov 1874 double stone\n \
                Lot 3B:\n"
    
    lots = [('5', '6'), ('3B',)]
    
    lines = DeathRecord.parse_page_to_words(test_str)
    
    lot_indices = DeathRecord.find_lot_lines(lines)
    
    assert lot_indices == [0, 3]
    
    for index, lot in zip(lot_indices, lots):
        assert lot == DeathRecord.get_lot_from_line(lines[index])
        
def test_parse_page():

    record = DeathRecord('records_directory')
    record.write_to_csv('parsed_data.csv')
    assert 'parsed_data.csv' in os.listdir(path='.')

    
if __name__ == '__main__':
    
    test_parse_page()

    
