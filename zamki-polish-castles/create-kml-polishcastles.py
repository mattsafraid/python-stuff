#! python3
# create-kml-polishcastles - Generates KML file based on database 

from xml.etree.ElementTree import Element, SubElement, ElementTree
from sqlite3 import connect

db_zamki = 'zamki.db3'
sql_building = 'SELECT DISTINCT BUILDING FROM POLISHCASTLES ORDER BY 1;'
sql_info = """
SELECT C.NAME, P.PRESERVATION
     , C.LONGITUDE, C.LATITUDE
     , RATING_ID, ACCESS_ID
     , C.RATING_DESC, PRESERVATION_DESC, ACCESS_DESC, C.LINK
FROM   POLISHCASTLES C
JOIN   POLISHCASTLES_PRESERVATION P ON C.PRESERVATION_ID = P.ID
WHERE  C.LONGITUDE IS NOT NULL
AND    C.BUILDING = ? 
ORDER BY C.PRESERVATION_ID DESC, C.RATING_ID DESC, C.ACCESS_ID;"""

icons = {
    'heart': u"\u2665",
    'star' : u"\u2605"
}

def placemark_name(lst):
    """Formats the placemark name to include its state if incomplete."""
    if lst[1] == 'Complete':
        return lst[0]
    else:
        return ': '.join(lst)


def cdata(lst):
    """Formats the comments for each monument. First two items are ratings"""
    l = list()
    l.append( (lst[0]-1) * icons['star'] + ' ' + lst[2] )
    l.append( lst[3] )
    l.append( lst[1] * icons['heart'] + ' ' + lst[4] )
    l.extend( lst[5:] )
    return '<br>'.join( l )


def kmlcoord(lst):
    """Formats the coordinates according to KML file requirements."""
    if len(lst) == 2:
        lst += ('0',)
    return ','.join(str(i) for i in lst)


'''
Main
'''
conn3 = connect(db_zamki)
c3    = conn3.cursor()

"""Creates the fixed part of KML document: Root & Document tag"""
root = Element('kml')
root.set('xmlns', 'http://www.opengis.net/kml/2.2')
tree = ElementTree(root)

Document = SubElement(root, 'Document')
SubElement(Document, 'name').text = 'Polish Castles'
SubElement(Document, 'description').text = """
Location of polishcastles.eu monuments on the map. 
They are divided by building type and ordered by preservation status.
Enjoy!"""

"""Folder tags: Each tag is a different building type."""
c3.execute(sql_building)
buildings = c3.fetchall()

for building in buildings:
    Folder = SubElement(Document, 'Folder')
    SubElement(Folder, 'name').text = building[0]
    
    """Add the placemarks to the resultset."""
    for castle in c3.execute(sql_info, building):
        print( ':: Processing: {0} - {1}'.format(building[0], castle[0]) )
        Placemark = SubElement(Folder, 'Placemark')
        Point = SubElement(Placemark, 'Point')
        SubElement(Placemark, 'name').text = placemark_name( castle[:2] )
        SubElement(Placemark, 'description').text = cdata( castle[4:] )
        SubElement(Point, 'coordinates').text = kmlcoord( castle[2:4] )

conn3.close()

tree.write( 'POLISHCASTLES.kml' )