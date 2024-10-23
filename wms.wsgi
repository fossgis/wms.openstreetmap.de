#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Mapscript WMS server with default request parameters for josm
#
# to be used in conjunction with wsgi Interface
# 
# (c) 2009-2010 Sven Geggus <sven-osm@geggus.net>
#
# Released under the GNU GENERAL PUBLIC LICENSE
# http://www.gnu.org/copyleft/gpl.html
#
# $Id$
#

debug = 1
mapfile="/osm/wms/osmwms.map"
tcopyright="copyrighted Material: OSM use only"

josmdefaults={'SERVICE': 'WMS', 'VERSION': '1.1.1', 'FORMAT':'image/png', 'REQUEST':'GetMap'}

import os,crypt,mapscript,sys,math,string,cgi
from time import *
from urllib.parse import parse_qs

# make our WMS also usable as TMS
def TileToMeters(tx, ty, zoom):
  initialResolution = 20037508.342789244 * 2.0 / 256.0
  originShift = 20037508.342789244
  tileSize = 256.0
  zoom2 = (2.0**zoom)
  res = initialResolution / zoom2
  mx = (res*tileSize*(tx+1))-originShift
  my = (res*tileSize*(zoom2-ty))-originShift
  return mx, my

# this will give the BBox Parameter from x,y,z
def TileToBBox(x,y,z):
  x1,y1=TileToMeters(x-1,y+1,z)
  x2,y2=TileToMeters(x,y,z) 
  return x1,y1,x2,y2

# generate a valid XML ServiceException message text
# from a simple textual error message
def SException(start_response,msg,code=""):
  xml = '<ServiceExceptionReport '
  xml += 'xmlns=\"http://www.opengis.net/ogc\" '
  xml += 'xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance" '
  xml += 'xsi:schemaLocation=\"http://www.opengis.net/ogc '
  xml += 'http://schemas.opengis.net/wms/1.1.1/OGC-exception.xsd\">\n'
  if code == "":
    xml += '  <ServiceException>\n  ' + msg
  else:
    xml += '  <ServiceException code=\"' + code +'\">\n  ' + msg
  xml += '\n  </ServiceException>\n</ServiceExceptionReport>\n'
  bxml=xml.encode()
  status = '200 OK'
  response_headers = [('Content-type', 'application/vnd.ogc.se_xml'),('Content-Length', str(len(bxml)))]
  start_response(status, response_headers)
  return bxml

# "main"
def application(env, start_response):
  
  global debug
  global tcopyright

  # read apaceh environment variables
  content_type = "text/plain"
  response_headers = dict([('Content-type', content_type)])

  if (env['SERVER_PORT'] == '80'):
    proto="http"
  else:
    proto="https"
  
  url = "%s://%s%s" % \
        (proto,env['SERVER_NAME'],env['REQUEST_URI'])

  os.chdir(env['DOCUMENT_ROOT'])
  
  querystr = env['QUERY_STRING']
  try:
    uagent = env['HTTP_USER_AGENT']
  except:
    uagent = ''
  
  qupper=querystr.upper()
  
  # MAP=something in request is always an error  
  if "MAP=" in qupper:
    return SException(start_response,'Invalid argument "MAP=..." in request')
    
  # if tile=something is given we are in TMS mode
  
    
  # parse QUERY_STRING
  query = parse_qs(querystr)
  query = dict(query)
  
  msreq = mapscript.OWSRequest()

  query_layers=''
  tilemode=0
  REQUEST=''
  # ad QUERY items into mapscript request object
  for key, value in query.items():
    key=key.upper()
    if (key == "DEBUG"):
      debug = 1
    if (key == "REQUEST"):
      REQUEST = value
    if (key == "LAYERS"):
      query_layers=value
      if ("," in query_layers):
        return SException(start_response,'Multiple Layers are currently unsupported')
    if key != "TILE":
      msreq.setParameter(key,value[0])
    else:
      xyz=value[0].split(',')
      if (len(xyz) != 3):
        return SException(start_response,'Invalid argument "TILE=%s" in request, must be TILE=x,y,z' % value)
      try:
        x=int(xyz[0])
      except:
        return SException(start_response,'Invalid argument "TILE=%s" in request, must be TILE=x,y,z' % value)
      try:
        y=int(xyz[1])
      except:
        return SException(start_response,'Invalid argument "TILE=%s" in request, must be TILE=x,y,z' % value)
      try:
        z=int(xyz[2])
      except:
        return SException(start_response,'Invalid argument "TILE=%s" in request, must be TILE=x,y,z' % value)                                                                                                                                                      
      tilemode=1

  # we are in tilemode, lets add the required keys
  if (tilemode):
    msreq.setParameter("srs","EPSG:3857")
    msreq.setParameter("bbox","%f,%f,%f,%f" % TileToBBox(x,y,z))
    msreq.setParameter("width","256")
    msreq.setParameter("height","256")

  # add default QUERY items for use with JOSM
  # this will allow for easy to remember WMS Request-URLs
  if ("JOSM" in uagent) or (tilemode):
    for d in josmdefaults:
      if d not in qupper:
        msreq.setParameter(d,josmdefaults[d])

  map = mapscript.mapObj(mapfile)
  map.web.metadata.set("wms_onlineresource",url.split("?")[0])
  map.web.metadata.set("wms_allow_getmap_without_styles","true")
  try:
    layer=map.getLayerByName(query_layers[0])
    cstring=layer.metadata.get('copyright')
  except:
    cstring=tcopyright

  try:
    wms_disabled=layer.metadata.get('-wms-disabled')
  except:
    wms_disabled='false'
  
  if wms_disabled == 'true' and not tilemode:
    return SException(start_response,'No WMS available for this layer, try TMS.')
  
  clayer=map.getLayerByName("copyright")
  cclass=clayer.getClass(0)
  cclass.setText(cstring)
  if (REQUEST == "GetCapabilities"):
    map.removeLayer(clayer.index)
  
  # write a mapfile for debugging purposes
  if (debug):
    os.umask(0o022)
    map.save("/tmp/topomap.map")

  # write mapserver results to buffer
  mapscript.msIO_installStdoutToBuffer()
  try:
    res = map.OWSDispatch(msreq)
  except:
    return [SException(start_response,str(sys.exc_info()[1]))]

  # adjust content-type
  content_type = mapscript.msIO_stripStdoutBufferContentType()
  
  output=mapscript.msIO_getStdoutBufferBytes()
  
  # set Expire header to 100 days from now
  expire = strftime('%a, %d %b %Y %H:%M:%S %z',gmtime(time()+3600*24*100))
  
  response_headers = [('Content-type', content_type),
                      ('Expires', expire),
                      ('Content-Length', str(len(output)))]
  status = '200 OK'
  start_response(status, response_headers)

  # write image data to stdout
  return [output]

if __name__ == '__main__':
  import wsgiref.handlers
  wsgiref.handlers.CGIHandler().run(application)
