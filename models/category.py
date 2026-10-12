import os
import pandas as pd
import sys

from pprint import pprint

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.base import Base

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = 'categories'

    api_id = Column(String(length=10), primary_key=True)
    name = Column(String(length=100))
    sequence = Column(Integer)
    parent_api_id = Column(String(length=10))
    query_chunk = 50

    cpi_values = relationship('CpiValue', back_populates='category')

    def __init__(self, api_id, name, sequence, parent_api_id):
        self.api_id = api_id
        self.name = name
        self.sequence = sequence
        self.parent_api_id = parent_api_id

    def __repr__(self):
        return f"<Category[{self.api_id}] -> {self.name}, ({self.sequence}) => {self.parent_api_id}]>"

    @classmethod

    def display_table_data(cls, engine):
        print('========== CATEGORIES ==========')
        counter = 0
        query = 'SELECT * FROM categories ORDER BY sequence'
        for chunk in pd.read_sql_query(query, con=engine, chunksize=cls.query_chunk):
            print(f"-- from {counter}... for CATEGORIES")
            pprint(chunk)
            counter += cls.query_chunk
        print('========== CATEGORIES ==========')
