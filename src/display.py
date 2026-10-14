import os
import sys

import matplotlib.pyplot as plt
import pandas as pd

from sqlalchemy import select
from sqlalchemy.orm import Session

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
        print('[E] CPI Inflation vs Wage Growth (Year on Year)')
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
        case 'E':
            graph_cpi_yoy()
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

def graph_cpi_yoy():
    engine = get_engine()
    tp_and_year_before = TimePeriod.quarter_and_previous_year(engine)
    cpi_values = {}
    wpi_values = {}

    with Session(engine) as session:
        cpis = session.scalars(select(CpiValue).where(CpiValue.category_api_id == '10001')).all()
        for cpi in cpis:
            cpi_values[cpi.time_period_api_id] = cpi.value
        wpis = session.scalars(select(WpiValue)).all()
        for wpi in wpis:
            wpi_values[wpi.time_period_api_id] = wpi.value

    data = []
    for quarter, previous_quarter in tp_and_year_before.items():
        current_cpi = cpi_values[quarter]
        previous_cpi = cpi_values[previous_quarter]
        current_wpi = wpi_values[quarter]
        previous_wpi = wpi_values[previous_quarter]

        if current_cpi and previous_cpi and current_wpi and previous_wpi:
            cpi_yoy = ((current_cpi / previous_cpi) - 1) * 100
            wpi_yoy = ((current_wpi / previous_wpi) - 1) * 100
            data.append({'quarter': quarter, 'cpi_yoy': cpi_yoy, 'wpi_yoy': wpi_yoy})

    df = pd.DataFrame(data)
    plt.figure(figsize=(12, 6))

    plt.plot(
        df['quarter'],
        df['cpi_yoy'],
        label='CPI Inflation',
        linewidth=2
    )

    plt.plot(
        df['quarter'],
        df['wpi_yoy'],
        label='Wage Growth',
        linewidth=2
    )
    plt.axhline(0, linewidth=0.8)

    plt.title('Australian CPI Inflation vs Wage Growth')
    plt.xlabel('Quarter')
    plt.ylabel('Annual change (%)')

    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=90, fontsize=7)

    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)

    input('Press Enter to continue...')

    plt.close()
