# -*- coding: utf-8 -*-
"""
Author: Justin Deterding

Description:

"""

from deceased import Deceased


def test_find_ints_in_word():
    
    assert Deceased.find_ints_in_word('1') == [1]
    assert Deceased.find_ints_in_word('-1') == [1]
    assert Deceased.find_ints_in_word('01/02/1993') == [1, 2, 1993]
    
    
def test_is_a_day():
    
    assert Deceased.is_a_day('10') == 10
    assert Deceased.is_a_day('-01') == 1
    assert Deceased.is_a_day('32') == 0
    assert Deceased.is_a_day('5/11/1993') == 0
    assert Deceased.is_a_day('0') == 0 
    
    
def test_is_a_year():
    
    assert Deceased.is_a_year('1993') == 1993
    assert Deceased.is_a_year('32') == 0
    assert Deceased.is_a_year('5/11/1993') == 0
    assert Deceased.is_a_year('0') == 0
