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

class WpiValue(Base):
    __tablename__ = 'wpi_values'

    value = Column(Float)
    query_chunk = 20

    time_period_api_id = Column(Integer, ForeignKey('time_periods.api_id'), primary_key=True)

    time_period = relationship('TimePeriod', back_populates='wpi_values')

    def __init__(self, time_period_api_id, value):
        self.time_period_api_id = time_period_api_id
        self.value = value

    def __repr__(self):
        return f"<WpiValue -> {self.time_period_api_id} => {self.value}]>"

    @classmethod

    def display_table_data(cls, engine):
        print('========== WPI_VALUES ==========')
        counter = 0
        query = 'SELECT * FROM wpi_values'
        for chunk in pd.read_sql_query(query, con=engine, chunksize=cls.query_chunk):
            print(f"-- from {counter}... for WPI_VALUES")
            pprint(chunk)
            counter += cls.query_chunk
        print('========== WPI_VALUES ==========')
