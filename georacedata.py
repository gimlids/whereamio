#!/usr/bin/env python
import os
import sys
import csv

from PIL import Image, ImageDraw, ImageColor

import dgeo

# file format info
LATITUDE_COLUMN = 72
LONGITUDE_COLUMN = 73
#race_codes = { 'SE_T054_001' : 'Total population',
race_codes = { 'SE_T054_002' : { 'label': 'White alone', 'color' : '#60b260' },
               'SE_T054_003' : { 'label': 'Black or African American alone', 'color' : '#55bef2' },
               'SE_T054_004' : { 'label': 'American Indian and Alaska Native alone', 'color' : '#f4b925' },
               'SE_T054_005' : { 'label': 'Asian alone', 'color' : '#ea4934' },
               'SE_T054_006' : { 'label': 'Native Hawaiian and Other Pacific Islander alone', 'color' : '#f4b925' },
               'SE_T054_007' : { 'label': 'Some Other Race alone', 'color' : '#f4b925' },
               'SE_T054_008' : { 'label': 'Two or More Races', 'color' : '#f4b925' } }

class GeoRaceData:
   races = {}
   samples = []
   header = []

   min_lat = None
   max_lat = None
   min_lng = None
   max_lng = None

   def __init__(self, socialexplorer_dot_com_csv_path):

      csv_file = file(socialexplorer_dot_com_csv_path, "r")
      race_csv = csv.reader(csv_file, delimiter=',', quotechar='"')
      self.header = None

      for line in race_csv:
	 if self.header == None:
	    self.header = line
	    for race_code in race_codes:
	       new_race = {}
	       new_race['code'] = race_code
	       new_race['title'] = race_codes[race_code]
	       new_race['csv_column'] = self.header.index(race_code)
	       self.races[race_code] = new_race
	 else:
	    latitude =  float(line[LATITUDE_COLUMN])
	    longitude = float(line[LONGITUDE_COLUMN])
            if self.min_lat == None:
	       self.min_lat = latitude
	       self.max_lat = latitude
	       self.min_lng = longitude
	       self.max_lng = longitude
            else:
	       self.min_lat = min(self.min_lat, latitude)
	       self.max_lat = max(self.max_lat, latitude)
	       self.min_lng = min(self.min_lng, longitude)
	       self.max_lng = max(self.max_lng, longitude)
	    sample = {}
	    sample['latlng'] = (latitude, longitude)
	    dominant_race_code = None
	    dominant_race_count = 0
	    for race_code in self.races:
	       race = self.races[race_code]
	       sample[race_code] = int(line[race['csv_column']])
	       if dominant_race_count < sample[race_code] or dominant_race_code == None:
		  dominant_race_count = sample[race_code]
		  dominant_race_code = race_code
	    sample['dominant_race_code'] = dominant_race_code
	    self.samples.append(sample)

   def degree_width(self):
      return self.max_lng - self.min_lng;

   def degree_height(self):
      return self.max_lat - self.min_lat;

   def latlng_to_fractional(self, latlng, bounds=None):
      (left, right, top, bottom) = (None, None, None, None)
      if bounds != None:
         left = bounds[0]
         right = bounds[1]
         top = bounds[2]
         bottom = bounds[3]
      else:
         left = self.min_lng
         right = self.max_lng
         top = self.max_lat
         bottom = self.min_lat
      degree_width  = right - left
      degree_height = top - bottom
      return ( (latlng[1] - left)   / degree_width,
               (latlng[0] - bottom) / degree_height )
   
   def get_image(self, width, bounds):
      aspect = dgeo.ok_projection_aspect(bounds[0], bounds[1], bounds[2], bounds[3])
      height = int(float(width) / aspect)
      image = Image.new('RGBA', (width, height))
      draw = ImageDraw.Draw(image)

      for sample in self.samples:
         fractional_location = self.latlng_to_fractional(sample['latlng'], bounds)
         x = fractional_location[0] * width
         y = height - fractional_location[1] * height

         ellipse_radius = 0.006 * width
         ellipse_left = x - ellipse_radius
         ellipse_right = x + ellipse_radius
         ellipse_top = y + ellipse_radius
         ellipse_bottom = y - ellipse_radius

         if ellipse_right < 0:
            continue

         color = race_codes[sample['dominant_race_code']]['color']

         #TODO show pop magnitude somehow? actually blocks might be uniform-ish population counts...
         draw.ellipse((ellipse_left, ellipse_bottom, ellipse_right, ellipse_top), fill=color, outline=color) # damn PIL uses different order, nead TODO better

      return image
      
# if this script is run by itself (not included from another python file)
if __name__ == "__main__":
   if len(sys.argv) < 2:
      print "Usage: " + sys.argv[0] + " geo_race_csv_from_http://www.socialexplorer.com/"
      sys.exit(0)

   sys.stderr.write("Parsing CSV...")
   geo_race_data = GeoRaceData(sys.argv[1])
   sys.stderr.write(" Done.\n")

   image = geo_race_data.get_image()
   image.save("plot.jpg")
   print "Saved plot.jpg"
