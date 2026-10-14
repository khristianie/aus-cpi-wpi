import constants
import itertools
import requests
from pprint import pprint

from sqlalchemy.orm import Session

from models.base import Base
from models.category import Category
from models.time_period import TimePeriod
from models.cpi_value import CpiValue
from models.wpi_value import WpiValue

from src.db import get_engine

engine = get_engine(True)
Base.metadata.create_all(engine)

def retrieve_json_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.text == 'NoRecordsFound':
            pass
        else:
            print(f"Error fetching data calling {url}: {response.status_code}")
            return {}

    except requests.exceptions.RequestException as e:
        print(f"An error occurred calling {url}: {e}")
        return {}

def parse_indexes(data):
    indexes = []
    for val in data['values']:
        indexes.append(
            {
                'name': val['name'],
                'sequence': val['order'],
                'api_id': val['id'],
                'parent_api_id': val.get('parent')
            }
        )
    return indexes

def parse_time_period(data):
    time_period = []
    for val in data['values']:
        time_period.append(
            {
                'api_id': val['id'],
                'name': val['name'],
                'start_date': val['start'],
                'end_date': val['end']
            }
        )
    return time_period

def parse_dimensions(data, detail):
    # we only use a few of the data in the array
    # array of deets, check when id is
    # MEASURE
    # INDEX - index of categories
    # TSEST
    # REGION
    # FREQ
    # TIME_PERIOD - time period of data
    dimensions = {}
    for d in data:
        match d['id']:
            case 'INDEX':
                if detail == 'INDEX':
                    dimensions['indexes'] = parse_indexes(d)
            case 'TIME_PERIOD':
                if detail == 'TIME_PERIOD':
                    dimensions['time_periods'] = parse_time_period(d)
    return dimensions

def parse_structures(data, detail):
    return parse_dimensions(data['dimensions']['observation'], detail) | {
        'name': data['name']
    }

def store_wpi_values_to_db(data, structure):
    row_nums = len(structure['time_periods'])

    with Session(engine) as session:
        row_num = 0
        while row_num < row_nums:
            key = f"0:0:0:0:0:0:0:{row_num}"
            val = None
            try:
                val = float(data['observations'][key][0])
                time_period_api_id = structure['time_periods'][row_num]['api_id']
                existing_record = session.query(WpiValue).filter_by(time_period_api_id=time_period_api_id).first()
                if existing_record:
                    existing_record.value = val
                else:
                    wpi_value = WpiValue(time_period_api_id, val)
                    session.add(wpi_value)
                    session.flush()
            except:
                pass
            finally:
                session.commit()
                row_num += 1

    return True

def store_cpi_values_to_db(data, structure):
    col_nums = len(structure['time_periods'])
    index_nums = len(structure['indexes'])

    with Session(engine) as session:
        index = 0
        while index < index_nums:
            col = 0
            while col < col_nums:
                key = f"0:{index}:0:0:0:{col}"
                val = None
                try:
                    val = float(data['observations'][key][0])
                    category_api_id = structure['indexes'][index]['api_id']
                    time_period_api_id = structure['time_periods'][col]['api_id']
                    existing_record = session.query(CpiValue).filter_by(category_api_id=category_api_id, time_period_api_id=time_period_api_id).first()
                    if existing_record:
                        existing_record.value = val
                    else:
                        cpi_value = CpiValue(category_api_id, time_period_api_id, val)
                        session.add(cpi_value)
                        session.flush()
                except:
                    # key not found
                    pass
                finally:
                    session.commit()
                    col += 1
            index += 1

    return True

def store_indexes_to_db(structure):
    categories = structure['indexes']
    with Session(engine) as session:
        for cat in categories:
            api_id = cat['api_id']
            existing_record = session.query(Category).filter_by(api_id=api_id).first()
            if existing_record:
                existing_record.name = cat['name']
                existing_record.sequence = cat['sequence']
                existing_record.parent_api_id = cat['parent_api_id']
            else:
                new_cat = Category(cat['api_id'], cat['name'], cat['sequence'], cat['parent_api_id'])
                session.add(new_cat)
                session.flush()

            print(f"===> storing Category: api_id {api_id}, name {cat['name']}")
            session.commit()

def store_time_periods_to_db(structure):
    time_periods = structure['time_periods']
    with Session(engine) as session:
        for tp in time_periods:
            api_id = tp['api_id']
            existing_record = session.query(TimePeriod).filter_by(api_id=api_id).first()
            if existing_record:
                existing_record.api_id = tp['api_id']
                existing_record.name = tp['name']
                existing_record.start_date = tp['start_date']
                existing_record.end_date = tp['end_date']
            else:
                new_tp = TimePeriod(tp['api_id'], tp['name'], tp['start_date'], tp['end_date'])
                session.add(new_tp)
                session.flush()

            print(f"===> storing TimePeriod: api_id {api_id}, name {tp['name']}, start_date {tp['start_date']}, end_date {tp['end_date']}")
            session.commit()

def cpi_url(categories_string):
    return (constants.BASE_URL +
        categories_string +
        constants.URL_PARAMS +
        f"&startPeriod={constants.START_YEAR}-{constants.START_QUARTER}&endPeriod={constants.END_YEAR}-{constants.END_QUARTER}")

def all_groups_cpi_url():
    return (constants.ALL_GROUPS_URL +
        constants.URL_PARAMS +
        f"&startPeriod={constants.START_YEAR}-{constants.START_QUARTER}&endPeriod={constants.END_YEAR}-{constants.END_QUARTER}")

response = retrieve_json_from_url(constants.CPI_STRUCTURE_URL)
if response:
    all_indexes_structure = parse_structures(response['data']['structures'][0], 'INDEX')
    store_indexes_to_db(all_indexes_structure)

    # iterate through the indexes, in chunks of indexes call cpi url to retrieve data
    # since retrieving data all in one go results in truncated results
    # first call will need to update structure for time_period, since it was not in the first nodata structure call
    resp = retrieve_json_from_url(all_groups_cpi_url())
    if resp:
        if not all_indexes_structure.get('time_period'):
            all_indexes_structure |= parse_structures(resp['data']['structures'][0], 'TIME_PERIOD')
            store_time_periods_to_db(all_indexes_structure)
        store_cpi_values_to_db(resp['data']['dataSets'][0], all_indexes_structure | parse_structures(resp['data']['structures'][0], 'INDEX'))
    for chunk in itertools.batched(all_indexes_structure['indexes'], 5):
        result = "+".join(c['api_id'] for c in chunk)
        resp = retrieve_json_from_url(cpi_url(f".{result}...Q"))
        if resp:
            store_cpi_values_to_db(resp['data']['dataSets'][0], all_indexes_structure | parse_structures(resp['data']['structures'][0], 'INDEX'))

    # now we get the wpi values
    wpi_url = constants.WPI_URL + f"&startPeriod={constants.START_YEAR}-{constants.START_QUARTER}&endPeriod={constants.END_YEAR}-{constants.END_QUARTER}"
    resp = retrieve_json_from_url(wpi_url)
    if resp:
        store_wpi_values_to_db(resp['data']['dataSets'][0], parse_structures(resp['data']['structures'][0], 'TIME_PERIOD'))
