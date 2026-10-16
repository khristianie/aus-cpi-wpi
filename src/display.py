import os
import sys
import platform
import subprocess

import matplotlib.pyplot as plt
import pandas as pd

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

import constants

from models.category import Category
from models.cpi_value import CpiValue
from models.time_period import TimePeriod
from models.wpi_value import WpiValue

from src.db import get_engine
from src.data import get_data

def show_menu():
    display_menu = True
    while display_menu:
        print('########## Australia CPI - WPI ##########')
        print('[A] CPI Inflation vs Wage Growth (Year on Year)')
        print('[B] Wage Growth vs Inflation Gap')
        print('[C] Display CPI Categories')
        print('[D] Display Time Periods')
        print('[E] Display stored CPI values')
        print('[F] Display stored WPI values')
        print('[Q] Quit')
        print('#########################################')
        user_input = input('Please choose an option... or [Q]uit ').strip().upper()
        display_menu = choose_option(user_input)

def choose_option(user_input):
    ret = True
    match user_input:
        case 'A':
            graph_cpi_wpi_yoy()
        case 'B':
            graph_wage_growth()
        case 'C':
            display_cpi_categories()
        case 'D':
            display_time_periods()
        case 'E':
            display_stored_cpi_values()
        case 'F':
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

def graph_cpi_wpi_yoy():
    df = pd.DataFrame(get_data())
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

    file_path = full_path_filename('CPI_Inflation_vs_Wage_Growth')
    plt.savefig(file_path)
    open_graph(file_path)
    print(f"\nOutput saved: {file_path}")
    input('Press Enter to continue...')

def time_now_string():
    return datetime.now().strftime("%Y%m%d%H%M%S.%f")[:-3]

def full_path_filename(prefix):
    os.makedirs(constants.VISUALISATION_FOLDER, exist_ok=True)
    return f"{constants.VISUALISATION_FOLDER}/{prefix}_{time_now_string()}.png"

def open_graph(file_path):
    system = platform.system()

    match system:
        case 'Darwin':
            subprocess.run(["open", file_path])
        case 'Windows':
            os.startfile(file_path)
        case 'Linux':
            subprocess.run(["xdg-open", file_path])
        case _:
            print(f"\nOutput saved: {file_path}")

def graph_wage_growth():
    df = pd.DataFrame(get_data())
    plt.figure(figsize=(12, 6))

    plt.bar(
        df['quarter'],
        df['wpi_yoy'] - df['cpi_yoy']
    )

    plt.axhline(0, linewidth=1)

    plt.title('Wage Growth vs Inflation Gap')
    plt.xlabel('Quarter')
    plt.ylabel('WPI YoY - CPI YoY (%)')
    plt.xticks(rotation=90, fontsize=7)
    plt.yticks(fontsize=7)
    plt.tight_layout()

    file_path = full_path_filename('Wage_Growth_vs_Inflation_Gap')
    plt.savefig(file_path)
    open_graph(file_path)
    print(f"\nOutput saved: {file_path}")
    input('Press Enter to continue...')
