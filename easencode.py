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
import argparse #from optparse import OptionParser
import sys, os
import re
import time, wave

program_version = "1.1"

parser = argparse.ArgumentParser(description="A script to generate EAS messages")
parser.add_argument("-v", "--ver", "--version", action='version', 
	version="EASEncode Version {0}/Core version {1}".format(program_version,
		eastestgen_core_version) )
parser.add_argument("-o", "--org", dest="originator", 
	help="set the message originator", default='EAS')
parser.add_argument("-e", "--event", dest="event",
	help="set the event type", required=True)
parser.add_argument("-f", "--fips", dest="fips", nargs='+',
	help="set the destination fips codes", required=True)
parser.add_argument("-d", "--dur", dest="duration",
	help="set the event duration", required=True)
parser.add_argument("-t", "--start", dest="timestamp", default="now",
	help="override the start timestamp, default is NOW")
parser.add_argument("-c", "--call", dest="callsign",
	help="set the originator call letters or id", required=True)
parser.add_argument("-a", "--audio-in", dest="audioin", type=file,
	help="insert audio file between EAS header and eom; max length"
	" is 2 minutes")
parser.add_argument('outputfile', metavar='OUTPUT.WAV', type=str)

args = parser.parse_args()

events = ('ean', 'eat', 'nic', 'npt', 'rmt', 'rwt', 'toa', 'tor', 'sva', 'svr',
	  'svs', 'sps', 'ffa', 'ffw', 'ffs', 'fla', 'flw', 'fls', 'wsa', 'wsw',
	  'bzw', 'hwa', 'hww', 'hua', 'huw', 'hls', 'tsa', 'tsw', 'evi', 'cem',
	  'dmo', 'adr')
originators = ('ean', 'pep', 'wxr', 'civ', 'eas')
arg_patterns = {'event':r'|'.join(events), 'fips':r'^(\d{6})(\s+\d{6})*$', 
	        'timestamp':r'.*', 'originator':r'|'.join(originators), 
		'duration':r'\d{4}', 'callsign':r'.*', 'audioin':r'.+\.wav', 
		'outputfile':r'.+\.wav' }
timeslanguage = {'now':''}
numCh = 2
peakLevel = -10
sampWidth = 16
sampRate = 44100

def main():

    try:
	for option, value in args.__dict__.iteritems():
	    if value is not None:
		if option is 'fips':
		    value = " ".join(value)
		print option, value
		if not re.match(arg_patterns[option], str(value), re.I):
		    parser.error("Invalid {0} '{1}'".format(option, value ))
	
	for ts_pattern in timeslanguage:
	    if re.match(ts_pattern, args.timestamp, re.I):
		ts_val = time.strftime('%j%H%M', time.gmtime())
		#print ts_val
	    else:
		ts_val = time.strftime('%j%H%M', time.gmtime())
	if len(args.fips) > 32:
	    print "WARNING: only 32 FIPS codes allowed. Truncating..."
	if len(args.callsign) > 8:
	    print "WARNING: callsign max width is 8 characters. Truncating..."
	data = generateEASpcmData(args.originator, args.event, args.fips, 
		args.duration, ts_val, args.callsign, sampRate, sampWidth, 
		peakLevel, numCh)
	file = wave.open(args.outputfile, 'wb')
	file.setparams( (numCh, sampWidth/8 , sampRate, sampRate, 'NONE', '') )
	file.writeframes(data)
	file.close()

    except Exception as inst:
	print inst

if __name__ == "__main__":
    main()

