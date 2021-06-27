#!/bin/bash

set -e

wget https://github.com/rok/dolines/releases/download/v1.0/dolines-v1.0.zip

unzip -d doline_statistics dolines-v1.0.zip doline_statistics.*


#ogr2ogr -s_srs "EPSG:3794" -t_srs "EPSG:4326" KS_SLO_SHP_G-2021-03-20_TLORISI_EPSG4326 KS_SLO_SHP_G-2021-03-20_TLORISI_d96 -nln KS_SLO_SHP_G-2021-03-20_TLORISI_EPSG4326 -progress


