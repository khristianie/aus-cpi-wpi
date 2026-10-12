import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.category import Category
from models.cpi_value import CpiValue
from models.time_period import TimePeriod
from models.wpi_value import WpiValue

from src.db import get_engine

def show_menu():
    display_menu = True
    while display_menu:
        print('########## Australia CPI - WPI ##########')
        print('[A] Display CPI Categories')
        print('[B] Display Time Periods')
        print('[C] Display stored CPI values')
        print('[D] Display stored WPI values')
        print('[Q] Quit')
        print('#########################################')
        user_input = input('Please choose an option... or [Q]uit ').strip().upper()
        display_menu = choose_option(user_input)

def choose_option(user_input):
    ret = True
    match user_input:
        case 'A':
            display_cpi_categories()
        case 'B':
            display_time_periods()
        case 'C':
            display_stored_cpi_values()
        case 'D':
            display_stored_wpi_values()
        case 'Q':
            goodbye()
            ret = False

    return ret

def goodbye():
    print('... Thanks, see you again!')

def display_cpi_categories():
    Category.display_table_data(get_engine(), False)

def display_time_periods():
    TimePeriod.display_table_data(get_engine(), False)

def display_stored_cpi_values():
    CpiValue.display_table_data(get_engine(), False)

def display_stored_wpi_values():
    WpiValue.display_table_data(get_engine(), False)
