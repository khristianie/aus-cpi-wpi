import os
import pandas as pd
import sys

from pprint import pprint

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.base import Base

from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

class CpiValue(Base):
    __tablename__ = 'cpi_values'

    value = Column(Float)
    query_chunk = 40

    category_api_id = Column(Integer, ForeignKey('categories.api_id'), primary_key=True)
    time_period_api_id = Column(Integer, ForeignKey('time_periods.api_id'), primary_key=True)

    category = relationship('Category', back_populates='cpi_values')
    time_period = relationship('TimePeriod', back_populates='cpi_values')

    def __init__(self, category_api_id, time_period_api_id, value):
        self.category_api_id = category_api_id
        self.time_period_api_id = time_period_api_id
        self.value = value

    def __repr__(self):
        return f"<CpiValue -> {self.category_api_id}, ({self.time_period_api_id}) => {self.value}]>"

    @classmethod

    def display_table_data(cls, engine, display_all = True):
        print('========== CPI_VALUES ==========')
        total = pd.read_sql_query(
            'SELECT COUNT(*) AS count FROM cpi_values',
            engine
        ).iloc[0]['count']

        counter = 0
        query = 'SELECT * FROM cpi_values'
        for chunk in pd.read_sql_query(query, con=engine, chunksize=cls.query_chunk):
            print(f"-- from {counter}... for CPI_VALUES")
            pprint(chunk)
            counter += cls.query_chunk
            if not display_all and counter < total:
                user_input = input("\nPress any key for next page, or [Q]uit: ").strip().lower()
                if user_input == 'q':
                    break
        print('========== CPI_VALUES ==========')
