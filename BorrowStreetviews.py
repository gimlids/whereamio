#!/usr/bin/env python

import sys
import urllib2
import json
import pprint
import time, calendar
from datetime import timedelta
import math

def distance_on_spherical_earth(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 6378100


top    = float(sys.argv[1])
left   = float(sys.argv[2])
bottom = float(sys.argv[3])
right  = float(sys.argv[4])

degree_width  = (right - left)
degree_height = (top - bottom)

center_x = left + (right - left) / 2.0
center_y = bottom + (top - bottom) / 2.0

meter_width  = distance_on_spherical_earth(center_y, left, center_y, right)
meter_height = distance_on_spherical_earth(bottom, center_x, top, center_x)

print (meter_width, meter_height)

columns = int(sys.argv[5])
rows = int(columns * meter_height / meter_width)

name = sys.argv[6]

def now():
   unix_time = calendar.timegm(time.gmtime())
   return unix_time

unix_time = now()

zoom = 2

print 'Session is: ' + name + ' ' + str(unix_time)

#print rows
#exit()

print str(columns) + ' x ' + str(rows)
print str(degree_width) + " x " + str(degree_height)


def saveMetadataAndDownloadTiles(panoJSON, column, row):
   pano = json.loads(panoJSON)
   if len(pano) > 0:
      #pp = pprint.PrettyPrinter(indent=4)
      #pp.pprint(pano)

      longitude = pano[u'Location'][u'lng']
      latitude  = pano[u'Location'][u'lat']
      localFile = open('data/panojson/'+name+'_'+str(unix_time)+'_'+str(latitude)+'_'+str(longitude)+'_'+str(row)+'_'+str(column)+'.json', 'w')
      localFile.write(panoJSON)
      localFile.close()

      panoid = pano[u'Location'][u'panoId']
      for pano_x in range(0, 4): # this range depends on zoom level TODO
         tile_url = "http://cbk0.google.com/cbk?output=tile&panoid="+panoid+"&zoom="+str(zoom)+"&x="+str(pano_x)+"&y=0"
         #print "Borrowing image at " + tile_url
         tile_response = urllib2.urlopen(tile_url)
         tile_file = open('data/panotile/'+panoid+'_z'+str(zoom)+'_'+str(pano_x)+'_0.jpeg', 'w')
         tile_file.write(tile_response.read())
         tile_file.close()
   

for x in range(0, columns):
   for y in range(0, rows):
      latitude  = left   + degree_width  * x / columns
      longitude = bottom + degree_height * y / rows
      metadata_url = "http://cbk0.google.com/cbk?output=json&ll="+str(longitude)+","+str(latitude)
      #print "Borrowing " + metadata_url
      u = urllib2.urlopen(metadata_url)
      panoJSON = u.read()
      saveMetadataAndDownloadTiles(panoJSON, x, y)
      
      elapsed = now() - unix_time
      progress = float(x * rows + y) / float(rows * columns)
      if progress > 0:
         remaining = elapsed * (1 - progress) / progress
      else:
         remaining = 0
      hours, remainder = divmod(remaining, 3600)
      minutes, seconds = divmod(remainder, 60)

      sys.stdout.write('|')
      for p in range(0, int(progress * 50)):
         sys.stdout.write('=')
      for p in range(int(progress * 50), 50):
         sys.stdout.write(' ')
      sys.stdout.write('| ' + str(int(progress*100)) + ' % Remaining: ' + str(int(hours)) + 'h ' + str(int(minutes)) + 'm ' + str(int(seconds)) + 's               \r')
      sys.stdout.flush()

sys.stdout.write('\n')
sys.stdout.flush()
      
