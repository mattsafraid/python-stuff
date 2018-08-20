#! python3
#  scrap-polishcastles.py - Reads castles information from polishcastles.eu


from re import sub
from bs4 import BeautifulSoup
from time import sleep
from sqlite3 import connect
from requests import get 
from requests.exceptions import RequestException, ReadTimeout, ConnectTimeout, Timeout

seconds = 10
retries = 3
url_castles = 'http://www.polishcastles.eu/alphabetically.php'
db_castles  = 'polishcastles.db3'

create_table_castles = """CREATE TABLE IF NOT EXISTS LANDING_CASTLE (
  ID                INTEGER PRIMARY KEY
, NAME              TEXT
, LINK              TEXT
, BUILDING          TEXT
, PRESERVATION      TEXT
, PRESERVATION_ICON TEXT
, ADMISSION         TEXT
, ADMISSION_ICON    TEXT
, PARKING           TEXT
, PARKING_ICON      TEXT
, SEARCHING         TEXT
, SEARCHING_ICON    TEXT
, ACCESS            TEXT
, ACCESS_ICON       TEXT
, RATING            TEXT
, RATING_ICON       TEXT
, PRESERVATION_DESC TEXT
, ADMISSION_DESC    TEXT
, PARKING_DESC      TEXT
, SEARCHING_DESC    TEXT
, ACCESS_DESC       TEXT
, RATING_DESC       TEXT
, LAT_COMPASS       TEXT
, LAT_DEG           TEXT
, LAT_MIN           TEXT
, LAT_SEC           TEXT
, LATITUDE          TEXT
, LONG_COMPASS      TEXT
, LONG_DEG          TEXT
, LONG_MIN          TEXT
, LONG_SEC          TEXT
, LONGITUDE         TEXT
)"""

insertSql = """INSERT INTO LANDING_CASTLE VALUES (
?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""


def log_error(e):
    """Inspiration from
    https://realpython.com/python-web-scraping-practical-introduction/"""
    
    """TODO: Implement error handling / logging"""
    print(e)


def get_content(url):
    """Gets the content from an URL."""
    tryagain = retries
    while tryagain > 0:
        try:
            res = get(url, timeout=seconds)
            res.raise_for_status()
            return res.content
        except (ConnectTimeout, ReadTimeout, Timeout) as t:
            log_error( 
                'Timeout type {0} to {1}: {2}'.format(type(t), url, str(t)))
            tryagain -= 1
            sleep(1)
        except RequestException as e:
            log_error( 
                'Error during requests to {0} : {1}, type {2}'.format(
                    url, str(e), type(e)))
            return None


def get_soup_from_url(url):
    """Retrieves a BeautifulSoup object given an URL"""
    html = get_content(url)
    soup = BeautifulSoup(html, 'html.parser')
    return soup


if __name__ == "__main__":
    '''Create the landing table'''
    conn3 = connect(db_castles)
    c3    = conn3.cursor()
    c3.execute(create_table_castles)
    
    '''Fetch the webpage with the links'''
    soup = get_soup_from_url(url_castles)
    
    '''Fetch each castle and scrap it'''
    for counter, link in enumerate( soup.select('.lista') ):
        print(':: Processing castle {}...'.format(link.getText()))
        castle = list()
        castle.append( counter+1 )
        castle.append( link.getText() )
        castle.append( link.get('href') )
        castle.append( link.get('title').split(' - ')[-1].split(',')[0] )
        
        # Request child page, 'Info' tab
        castleSoup = get_soup_from_url( castle[2] )
        
        for info in castleSoup.select('.opis2'):
            castle.append( info.contents[0].get('alt') )
            castle.append( info.contents[0].get('src') )

        for desc in castleSoup.select('.opis3'):
            castle.append( desc.getText() )

        # Request child page, 'GPS' tab
        castleSoup = get_soup_from_url( str(castle[2]) + '/2' )

        try:
            gps = castleSoup.select('#counter')[0]
            castle.extend( sub('[^\d\w\s\.]', '', gps.text).split() )
        except:
            castle.extend( [None] * 10 )

        try:
            c3.execute(insertSql, tuple(castle))
            conn3.commit()
        except Exception as e:
            conn3.rollback()
            log_error( 'Error persisting to database : {0}, Data {1}'.format(
                    str(e), castle) )

    conn3.close()
