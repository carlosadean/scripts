#!/usr/bin/env python
#
# @carlosadean
# 
# name: count_objects_into_fits
# version: 1.0 2019-03-01
# short description: script that counts objects in fits files
#
# dependencies: pyfits 3.4+0

import pyfits
import os

files = os.listdir('.')

count = 0
fcount = 0
for file in files:
    fcount += 1
    hdulist = pyfits.open(file)
    tbdata = hdulist[1].data
    lines = int(len(tbdata))
    count += lines
    hdulist.close()
    print('# files: %s' %fcount, end='\r')

print('# files: %s' %len(files), end='\n')
print('# objects: %s' %count)
