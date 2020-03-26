## Import necessary packages
import requests
import pandas as pd
from pandas import json_normalize
import json
import folium
from folium.plugins import Fullscreen
from folium.features import CustomIcon
from folium.plugins import FloatImage

## Apply your Google Geocoding API key here (ours is saved locally)
google_key = pd.read_csv('S:/Shared Data/Palmer Capital Partners/Digital Transformation/Datasets/credentials.csv',
                 index_col='Application').loc['Google Maps'][0]


## Import the file with locations and details
df = pd.read_csv('women_history_london.csv')

## Iterate through the table to retrieve coordinates from the Google Geocoding API
locations = pd.DataFrame()
for x in range(len(df)):
    address = df.iloc[x]['address']
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?address={}".format(address)+ "&key={}".format(google_key)
    geo = requests.get(geocode_url)
    geo = geo.json()
    location = json_normalize(geo['results'][0])
    data = location[['geometry.location.lat','geometry.location.lng']]
    locations = locations.append(data)

## Reformat the locations that you retrieved from the Google API
locations = locations.reset_index(drop=True)
df['lat'] = locations['geometry.location.lat'] # create new column in dataframe with latitudes
df['lng'] = locations['geometry.location.lng'] # create new column in dataframe with longitudes

## Create the maps
history_map = folium.Map((51.510637,-0.115),
                        tiles='cartodbpositron',
                        attr='CartoDB',
                        zoom_start=13.5)

## Add the locations to a map
places = folium.FeatureGroup(name='Places', show=True)
for x in range(len(df)):
    
    site = df.iloc[x]['site']
    description = df.iloc[x]['description']
    website = df.iloc[x]['website']

    html_code = """ 
            <p style = "font-family:Calibri;font-size:18px">
            <a href={WEBSITE} target="_blank"><b>{SITE}</b><a> <br>
            {DESCRIPTION}</p>
            """
    html = html_code.format(SITE=site, DESCRIPTION=description, WEBSITE=website)
    iframe = folium.IFrame(html=html, width=300, height='100%')
    
    point = folium.Marker(location=[df.iloc[x]['lat'], df.iloc[x]['lng']],
                        icon=folium.Icon(color=df.iloc[x]['icon'], icon='monument', prefix='fa'), 
                          popup=folium.Popup(iframe, parse_html=True),
                          tooltip=folium.Tooltip(site))
    point.add_to(places)
    

history_map.add_child(places)

## Save the file to the desired filepath and filename
filepath = 'S:/Shared Data/Palmer Capital Partners/Digital Transformation/Maps/'
filename = 'Womens_History_London.html'
history_map.save(filepath + filename)