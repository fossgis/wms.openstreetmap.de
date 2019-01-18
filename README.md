# The Mapserver configuration at wms.openstreetmap.de

The layers can be browsed at: https://wms.openstreetmap.de

The WMS service can be accessed via WMS client (QGIS, JOSM...) at: `https://wms.openstreetmap.de/wms`

Tiles are available via: `https://wms.openstreetmap.de/tms/<layername>/<z>/<x>/<y>.png`

Copyright Watermarks are always added to the requested layers. Requests for
more thane one layer are denied.


### Implementation:

The Mapserver is implemented as a python wsgi-script inside the Apache
server.  It is using methods from umn mapserver (python mapscript). 
Configuration is done by a map-file which is read by the wsgi-scripts.

In addition to the script itself tiles are cached using Apache
`mod_disk_cache`.


### Configuration:

Layers are created into per-topic `.map` files and included into [osmwms.map](osmwms.map). 
These are (more or less) an ordinary mapfiles with the [usual mapfile syntax](https://mapserver.org/mapfile/),
but with some some additional metadata fields in layers:

* "copyright"     - This is used for layer specific copyright messages rendered as watermark.
* "-wms-disabled" - If true, WMS is disabled for this layer.
* "-terms-of-use" - Additional terms-of-use text that is displayed on the overview index page.

