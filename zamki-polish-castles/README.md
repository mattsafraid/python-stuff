## Zamki: Polish castles

These scripts are used to scrap information from [polishcastles.eu](http://www.polishcastles.eu) 
and create a KML file, which can be later imported into Google MyMaps.

The steps are as follows:

1. Run `python3 scrap-polishcastles.py` in order to scrap the website and persist data into **polishcastles.db3**;
2. Run `sqlite3 zamki.db3 -init stage-polishcastles.sql` to stage data and create **zamki.db3**;
3. Run `create-kml-polishcastles.py` to read from **zamki.db3** and create **POLISHCASTLES.kml**.

The KML file contains one folder for each type of building. 
The buildings in each folder are ordered by preservation state and rating, meaning the best preserved, 
most rated building is the first in the line.

These options may be tweaked changing the script source. 

This project is fixed to one website but can be adapted to scrap data from other places, 
or to create KML files from other datasets containing coordinates.

TO DO: Add an extra step to retrieve the geo-political information from each coordinate, 
such as City name, country, Wikipedia link, and so on.
