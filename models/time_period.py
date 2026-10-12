import os
import pandas as pd
import sys

from pprint import pprint

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.base import Base

from sqlalchemy import Column, String, Date
from sqlalchemy.orm import relationship

class TimePeriod(Base):
    __tablename__ = 'time_periods'

    api_id = Column(String(length=10), primary_key=True)
    name = Column(String(length=100))
    start_date = Column(Date)
    end_date = Column(Date)
    query_chunk = 50

    cpi_values = relationship('CpiValue', back_populates='time_period')
    wpi_values = relationship('WpiValue', back_populates='time_period')

    def __init__(self, api_id, name, start_date, end_date):
        self.api_id = api_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return f"<TimePeriod[{self.api_id}] -> {self.name}, ({self.start_date}) - {self.end_date}]>"

    @classmethod

    def display_table_data(cls, engine):
        print('========== TIME_PERIODS ==========')
        counter = 0
        query = 'SELECT * FROM time_periods'
        for chunk in pd.read_sql_query(query, con=engine, chunksize=cls.query_chunk):
            print(f"-- from {counter}... for TIME_PERIODS")
            pprint(chunk)
            counter += cls.query_chunk
        print('========== TIME_PERIODS ==========')
