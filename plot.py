from lxml import objectify
import pandas as pd
from dateutil import parser
 
# helper function to handle missing data in my file
def add_trackpoint(element, subelement, namespaces, default=None):
    in_str = './/' + subelement

    
    try:
        return float(element.find(in_str, namespaces=namespaces).text)
    except AttributeError:
        return default
    except ValueError:
        return parser.parse(element.find(in_str, namespaces=namespaces).text)
 
# activity file and namespace of the schema
tcx_file = 'data/activity_4554131733.tcx'
namespaces={'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
 
# get activity tree
tree = objectify.parse(tcx_file)
root = tree.getroot()
activity = root.Activities.Activity
 
# run through all the trackpoints and store lat and lon data
trackpoints = []
for trackpoint in activity.xpath('.//ns:Trackpoint', namespaces=namespaces):
    latitude_degrees = add_trackpoint(trackpoint, 'ns:Position/ns:LatitudeDegrees', namespaces)
    longitude_degrees = add_trackpoint(trackpoint, 'ns:Position/ns:LongitudeDegrees', namespaces)
    altitude_meters = add_trackpoint(trackpoint, 'ns:AltitudeMeters', namespaces)
    time = add_trackpoint(trackpoint, 'ns:Time', namespaces)

    
     
    trackpoints.append((latitude_degrees,
                        longitude_degrees,
                        altitude_meters,
                        time
                       
                       ))
 
# store as dataframe
activity_data = pd.DataFrame(trackpoints, columns=['latitude_degrees', 'longitude_degrees', 'altitude_meters', 'time'])

activity_data = activity_data.dropna()
locations = list(zip(activity_data.latitude_degrees.values, activity_data.longitude_degrees.values))

# Create Map

from ipyleaflet import Map, Marker, AntPath

center = (34.1137553,-118.2001699)

m = Map(center=center, zoom=12)

marker = Marker(location=center, draggable=False)
m.add_layer(marker);

ant_path = AntPath(
    locations=locations,
    dash_array=[1, 10],
    delay=1000,
    color='#7590ba',
    pulse_color='#3f6fba'
)


m.add_layer(ant_path)


# Export Map into HTML

from ipywidgets.embed import embed_minimal_html, dependency_state

embed_minimal_html('export.html', views=[m], state=dependency_state([m]))