#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# generate index page for wms.openstreetmap.de dynamically
#
# from information provided by templates and mapfile information
#
# this way for adding new layers the mapfile is the only place we need to
# make changes. No redundant information anymore :)
#
# this is not a very elegant script (intermixes content and code)
# but serves its purpose
#
# (c) 2010 Sven geggus <sven-osm@geggus.net>
#
# GNU GPL Version 3 or later
# http://www.gnu.org/copyleft/gpl.html

header_template='/osm/wms/templates/index_header.html'
footer_template='/osm/wms/templates/index_footer.html'
# zoomlevel for potlatch URL
zoom=17

mapfile='/osm/wms/osmwms.map'

import re,cgi,mapscript,os,pyproj

# this will generate an extent in WGS84 projection
# regardless of the actual layer projection
def gen4326Extent(ms_extent,ms_srs):
  ms_srs=ms_srs.lower()
  if ms_srs == "espg:4326":
    return ms_extent
  else:
    x0,y0,x1,y1=eval('['+ms_extent.replace(' ',',')+']')
    proj4326 = pyproj.Proj(init='epsg:4326')
    projlayer = pyproj.Proj({'init':ms_srs})
    lon0,lat0 = pyproj.transform(projlayer,proj4326,x0,y0)
    lon1,lat1 = pyproj.transform(projlayer,proj4326,x1,y1)
    return "%f %f %f %f" % (lon0,lat0,lon1,lat1)

def application(env, start_response):
  wmsurl="://wms.openstreetmap.de/wms"
  tmsurl="://wms.openstreetmap.de/tms"
  mapurl="://wms.openstreetmap.de/slippymap"

  status = '200 OK'
  
  port = env.get('SERVER_PORT', '80')
  if (port == '443'):
    wmsurl='https'+wmsurl
    tmsurl='https'+tmsurl
    mapurl='https'+mapurl
  else:
    wmsurl='http'+wmsurl
    tmsurl='http'+tmsurl
    mapurl='http'+mapurl

  map = mapscript.mapObj(mapfile)
  templ = open(header_template,'r')
  index_html = templ.read()
  templ.close()
  
  for i in range(0,map.numlayers):
   layer = map.getLayer(i)
   
   zoom = layer.metadata.get('zoomlevels')
   if zoom is None:
    zoom = 19
   zoom = int(zoom)+1
   if layer.name != 'copyright':
    extent = gen4326Extent(layer.metadata.get('wms_extent'),layer.metadata.get('wms_srs'))
    index_html += "<hr />\n"
    index_html += '<table border="0" width="100%">\n'
    index_html += '<tr><td width="30%%"><b>Name:</b></td><td id="%s"><b>%s</b></td></tr>' % (layer.name,layer.name)
    wiki = layer.metadata.get('wiki')
    if wiki is not None:
     index_html += '<tr><td width="30%%"><b>Wiki:</b></td><td><a href="%s">%s</a></td></tr>' % (wiki,wiki)
    index_html += '<tr><td width="30%%"><b>Source:</b></td><td>%s</td></tr>' % layer.metadata.get('copyright')
    if layer.metadata.get('-terms-of-use'):
     index_html += '<tr><td width="30%%"><b>Terms of Use:</b></td><td>%s</td></tr>' % layer.metadata.get('-terms-of-use')
    index_html += '<tr><td width="30%%"><b>Content:</b></td><td>%s</td></tr>' % layer.metadata.get('wms_title')
    index_html += '<tr><td width="30%%"><b>Bounding Box:</b></td><td>%s</td></tr>' % extent
    index_html += '<tr><td width="30%%"><b>TMS URL for JOSM Imagery:</b></td><td><b>tms:%s/%s (zoom %d)</b> ' % (tmsurl,layer.name,zoom)
    # https://josm.openstreetmap.de/wiki/Help/RemoteControlCommands#imagery
    index_html += '<a href="http://localhost:8111/imagery?title=%s&type=tms&max_zoom=%s&url=%s/%s/{zoom}/{x}/{y}.png">Add via Remote control</a> ' \
    % (layer.name,zoom,tmsurl,layer.name)
    index_html += '</td></tr>'
    if not layer.metadata.get('-wms-disabled'):
     index_html += '<tr><td width="30%%"><b>WMS URL (for JOSM/Merkaartor):</b></td><td>%s?layers=%s&</td></tr>' % (wmsurl,layer.name)
    index_html += '<tr><td width="30%%"><b>Interactive map:</b></td><td><a href="%s/%s">%s/%s</a></td></tr>' % (mapurl,layer.name,mapurl,layer.name)
    latlon=extent.split()
    lon1=float(latlon[0])
    lat1=float(latlon[1])
    lon2=float(latlon[2])
    lat2=float(latlon[3])
    lat=lat1+(lat2-lat1)/2
    lon=lon1+(lon2-lon1)/2
    index_html += '<tr><td width="30%%"><b>Online Editor URL:</b></td><td>'
    # https://github.com/openstreetmap/iD/blob/master/API.md
    # background=custom:https://{switch:a,b,c}.tile.openstreetmap.org/{zoom}/{x}/{y}.png
    index_html += '<a href="https://www.openstreetmap.org/edit#background=custom:%s/%s/{zoom}/{x}/{y}.png">iD</a> ' \
    % (tmsurl,layer.name)
    index_html += '(<a href="https://www.openstreetmap.org/edit#background=custom:%s/%s/{zoom}/{x}/{y}.png&map=%s/%f/%f">center</a>), ' \
    % (tmsurl,layer.name,zoom,lat,lon)
    index_html += '<a href="https://www.openstreetmap.org/edit?lat=%f&lon=%f&zoom=%s&tileurl=%s/%s/!/!/!.png">Potlatch %s</a> ' \
    % (lat,lon,zoom,tmsurl,layer.name,layer.name)
    index_html += '</td></tr>'
    index_html += '</table>\n'
  
  templ = open(footer_template,'r')
  index_html += templ.read()
  templ.close()

  response_headers = [('Content-type', 'text/html'),
                      ('Content-Length', str(len(index_html)))]
                       
  start_response(status, response_headers)
  return [index_html]



