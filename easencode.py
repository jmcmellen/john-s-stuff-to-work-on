#!/usr/bin/python
#===============================================================
#  easencode.py - A utility to make EAS audio files
#  February 25, 2011
#
#===============================================================
#
#===============================================================
#License (see the MIT License)
#
#Copyright (c) 2011 John McMellen
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation
#files (the "Software"), to deal in the Software without
#restriction, including without limitation the rights to use,
#copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the
#Software is furnished to do so, subject to the following
#conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.
#
#=================================================================

from eastestgen import *
from optparse import OptionParser
import sys, os
import re

program_version = "1.0"

parser = OptionParser(usage="usage: %prog [options] output.wav")
parser.add_option("-v", "--ver", dest="show_version",
	action="store_true", default=False,
	help="show program version")
parser.add_option("-o", "--org", dest="originator", 
	help="set the message originator:")
parser.add_option("-e", "--event", dest="event",
	help="set the event type")
parser.add_option("-f", "--fips", dest="fips",
	help="set the destination fips codes")
parser.add_option("-d", "--dur", dest="evt_dur",
	help="set the event duration")
parser.add_option("-t", "--start", dest="evt_ts",
	help="override the start timestamp, default is NOW")
parser.add_option("-c", "--call", dest="callsign",
	help="set the originator call letters or id")

(options, args) = parser.parse_args()

def main():
    if options.show_version:
	print "EASEncode Version {0}/Core version {1}".format(program_version,
		eastestgen_core_version)
	if len(args) != 1:
	    sys.exit()
    if len(args) != 1:
	parser.error("Output file not specified. " 
		"Try {0} -h for detailed help."
		.format(os.path.basename(sys.argv[0])))
    outputfile = args[0]
    try:
	if re.match(r'.*\.wav$', outputfile, re.I) is not None:
	    pass
	else:
	    raise Exception("Unrecognized filename extension on file: "
		    "{0}\nOnly WAV files are supported".format(outputfile))
	for option, value in options.__dict__.iteritems():
	    if value is not None:
		print option, value
	if options.originator is not None:
	    originator = options.originator
	else:
	    print "Setting Originator to default value EAS"

    except Exception as inst:
	print inst

if __name__ == "__main__":
    main()

