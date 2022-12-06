#!/bin/bash
set -e
date
#unzip -d KS_SLO_SHP_G-2021-03-20_TLORISI_d96 KS_SLO_SHP_G-2021-03-20 *_TLORISI_*

#ogr2ogr -s_srs "EPSG:3794" -t_srs "EPSG:4326" KS_SLO_SHP_G-2021-03-20_TLORISI_EPSG4326 KS_SLO_SHP_G-2021-03-20_TLORISI_d96 -nln KS_SLO_SHP_G-2021-03-20_TLORISI_EPSG4326 -progress

# install to crontab as eg:
#55 5 * * SAT cd /osm/wms/gurs ; ./KS-to-wms.sh > crontablog.txt 2>&1

ogr2ogr -s_srs "EPSG:3794" -t_srs "EPSG:4326" \
	VDV_EPSG4326 \
	/tmp/openaddresses-si/VDV/VDV.shp \
	-nln VDV_EPSG4326 -progress


