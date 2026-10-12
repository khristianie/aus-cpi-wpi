import os
import sys
from sqlalchemy import create_engine

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

import constants

_engine = None

def get_engine(echo = False):
    global _engine

    if _engine is None:
        _engine = create_engine(
            f"mysql+mysqlconnector://{constants.DB_USERNAME}:{constants.DB_PASSWORD}@{constants.DB_HOST}:{constants.DB_PORT}/{constants.DB_NAME}",
            echo=echo
        )

    return _engine
