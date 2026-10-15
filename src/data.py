import os
import sys

import pandas as pd

from sqlalchemy import select
from sqlalchemy.orm import Session

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.cpi_value import CpiValue
from models.time_period import TimePeriod
from models.wpi_value import WpiValue
from src.db import get_engine

def get_data():
    engine = get_engine()
    tp_and_year_before = TimePeriod.quarter_and_previous_year(engine)
    cpi_values = {}
    wpi_values = {}
    data = []

    with Session(engine) as session:
        cpis = session.scalars(select(CpiValue).where(CpiValue.category_api_id == '10001')).all()
        for cpi in cpis:
            cpi_values[cpi.time_period_api_id] = cpi.value
        wpis = session.scalars(select(WpiValue)).all()
        for wpi in wpis:
            wpi_values[wpi.time_period_api_id] = wpi.value

    for quarter, previous_quarter in tp_and_year_before.items():
        current_cpi = cpi_values[quarter]
        previous_cpi = cpi_values[previous_quarter]
        current_wpi = wpi_values[quarter]
        previous_wpi = wpi_values[previous_quarter]

        if current_cpi and previous_cpi and current_wpi and previous_wpi:
            cpi_yoy = ((current_cpi / previous_cpi) - 1) * 100
            wpi_yoy = ((current_wpi / previous_wpi) - 1) * 100
            data.append({'quarter': quarter, 'cpi_yoy': cpi_yoy, 'wpi_yoy': wpi_yoy})

    return data
