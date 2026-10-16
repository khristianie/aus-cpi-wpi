DEFAULTS = '1....Q'
ALL_GROUPS_URL = 'https://data.api.abs.gov.au/rest/data/ABS,CPI/1.10001.10.50.Q'
BASE_URL = 'https://data.api.abs.gov.au/rest/data/ABS,CPI_Q,1.0.0/'
URL_PARAMS = '?dimensionAtObservation=AllDimensions&format=jsondata'
NODATA_URL_PARAMS = URL_PARAMS + '&detail=nodata'
CPI_STRUCTURE_URL = BASE_URL + DEFAULTS + NODATA_URL_PARAMS
START_YEAR = 1999
START_QUARTER = 'Q1'
END_YEAR = 2026
END_QUARTER = 'Q2'

WPI_URL = 'https://data.api.abs.gov.au/rest/data/ABS,WPI,1.2.0/1.THRPEB.7.TOT.10.AUS.Q' + URL_PARAMS

VISUALISATION_FOLDER = 'output_graphs'

DB_USERNAME = 'root'
DB_PASSWORD = 'password'
DB_HOST = 'localhost'
DB_PORT = 3306
DB_NAME = 'aus_cpi_wpi'
