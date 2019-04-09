#!/usr/bin/env python
#
# Creator: carlosadean@linea.gov.br
# 
# Name: count_objects_into_fits
# Version: 1.0 2019-03-01
# Short description: script to counts lines(objects) into fits files
#
# Dependencies: pyfits 3.4+0
#
# How to use: 
# 1 - setup eups and load pyfits 3.4+0
# 2 - access the dir where .fits live
# 3 - run the script as 'python count_objects_into_fits.py' and wait the result
#
# the output of the script looks like this:
# 
# # file: 100
# # objects: 1100000

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
