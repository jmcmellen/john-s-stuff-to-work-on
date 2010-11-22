import math, struct, random, array

def makeDTMF(sequence, duration, pause, peakLevel, sampRate, sampWidth, numCh):
    dtmf_values = {
        '1':(1209, 697), '2':(1336, 697), '3':(1477, 697), 'A':(1633, 697),
	'4':(1209, 770), '5':(1336, 770), '6':(1477, 770), 'B':(1633, 770),
	'7':(1209, 852), '8':(1336, 852), '9':(1477, 852), 'C':(1633, 852),
	'*':(1209, 941), '0':(1336, 941), '#':(1477, 941), 'D':(1633, 941) }
    data_out = ''
    phase = 0 * math.pi
    level = math.pow(10, (float(peakLevel - 6) / 20)) * 32767

    for a in sequence:
	#print a, peakLevel - 6
	if a == ' ':
	    data_out += generateSimplePCMToneData(1000, 1000, sampRate, pause, 
		    sampWidth, -110, numCh)
	else:
	    freq1, freq2 = dtmf_values[a]
	    #print freq1, freq2
	    for i in range(0, int(math.floor(sampRate * duration))):
		for ch in range(numCh):
		    sample =  int(math.ceil( level * math.sin(
	                   (freq1 * 2 * math.pi * i)/ sampRate + phase) )) 
		    sample += int(math.ceil( level * math.sin(
			   (freq2 * 2 * math.pi * i)/ sampRate + phase) ))
		    #print sample
		    data_out += struct.pack('<h', sample)
	    
    return data_out

def applyLinearFade(startVal, endVal, numCh, sampWidth, data):
    endLvl = math.pow(10, (float(endVal) / 20))
    startLvl = math.pow(10, (float(startVal) / 20))
    samples = array.array('h', data)
    out_data = ''
    slope = (endLvl - startLvl) / (len(samples))
    print endLvl, startLvl
    x = 0

    for sample in samples:
        factor = slope * x + startLvl
        #print factor
        out_data += struct.pack('<h', int(math.floor(sample * factor)))
        x += 1

    return out_data

def changeLevelPCMdata(sampRate, sampWidth, amount, numCh, data):
    "Apply amount of dB change to samples"
    
    factor = math.pow(10, (float(amount) / 20))
    #print factor
    samples = array.array('h', data)
    out_data = ''

    for sample in samples:
	#print sample
	#sample, = struct.unpack('<h', byte1 + byte2)
	#data[i] = struct.pack('<h', int(math.floor(sample * factor)))
        #print sample
	out_data += struct.pack('<h', int(math.floor(sample * factor)))

    return out_data

def generateSimplePCMToneData(startfreq, endfreq, sampRate, duration, sampWidth, peakLevel, numCh):
    """Generate a string of binary data formatted as a PCM sample stream. Freq is in Hz,
    sampRate is in Samples per second, duration is in seconds, sampWidth is in bits, 
    peakLevel is in dBFS, and numCh is either 1 or 2."""

    phase = 0 * math.pi
    level = math.pow(10, (float(peakLevel) / 20)) * 32767 #Should depend on sampWidth
    pcm_data = ''
    freq = startfreq
    #print duration * sampRate

    for i in range(0, int(math.floor(sampRate * duration))):
        for ch in range(numCh):
	    sample =  int(( level * math.sin(
	                   (freq * 2 * math.pi * i)/ sampRate + phase) ))
	    #print sample
	    pcm_data += struct.pack('<h', sample)

    return pcm_data

def generateAFSKpcmData(markF, spaceF, bitrate, sampRate, sampWidth, peakLevel, numCh,
	                stringData):
    "Generate a string of binary data of AFSK audio"

    pcm_data = ''
    bitstream = ''
    bitduration = 1.0 / bitrate
    print stringData
    for byte in stringData:
	bytebits = "{0:08b}".format( ord(byte))
	bitstream += bytebits[::-1]
	#bitstream += bytebits
    print bitstream
    one_bit = generateSimplePCMToneData(markF, markF, sampRate, bitduration, sampWidth,
		           peakLevel, numCh)
    zero_bit = generateSimplePCMToneData(spaceF, spaceF, sampRate, bitduration, sampWidth,
			   peakLevel, numCh)
    for bit in bitstream:
	if bit == '1':
	    pcm_data += one_bit
	else:
	    pcm_data += zero_bit

    return pcm_data

def generateEASpcmData(org, event, fips, eventDuration, timestamp, stationId, sampRate, sampWidth, 
	                peakLevel, numCh):
    "Put together info to generate an EAS message"

    markF = 2083.3
    spaceF = 1562.5
    bitrate = 521
    pcm_data = ''

    preamble = '\xab' * 16
    message = 'ZCZC-{0}-{1}-{2}+{3}-{4}-{5: <8}-'.format(org, event, fips, eventDuration,
	    timestamp, stationId[0:8])
    endOfMessage = 'NNNN'
    header = generateAFSKpcmData(markF, spaceF, bitrate, sampRate, sampWidth, peakLevel,
	                 numCh, preamble + message.upper())
    eom = generateAFSKpcmData(markF, spaceF, bitrate, sampRate, sampWidth, peakLevel,
	                 numCh, preamble + endOfMessage)
    silence = generateSimplePCMToneData(10000, 10000, sampRate, 1, sampWidth, -94, numCh)
    
    pcm_data = silence + silence

    for i in range(3):
	pcm_data = pcm_data + header + silence
    for i in range(3):
	pcm_data = pcm_data + eom + silence

    return pcm_data

if __name__ == "__main__":
    import wave, time

    freq = 1209
    sampRate = 48000
    duration = 10
    sampWidth = 16
    peakLevel = -20
    numCh = 2
    now = time.gmtime()
    timestamp = time.strftime('%j%H%M', now) 
    #dtmf_seq = ' 1 2 3 4 5 6 7 8 9 A B C D * # '
    dtmf_seq = '      1   4 1 7   8 3 6   6 2 5 5      '
    #dtmf_seq = '1234'
    #dtmf_seq = '1'
    #print timestamp

    data = generateEASpcmData('EAS', 'RWT', '029091', '0030', timestamp, 'KXYZ/FM', sampRate, 
	    sampWidth, peakLevel, numCh)
    #data = generateSimplePCMToneData(freq, freq, sampRate, duration, sampWidth, peakLevel, numCh)
    #data = applyLinearFade(-100, 0, numCh, sampWidth, data)
    #data = changeLevelPCMdata(sampRate, sampWidth, -6, numCh, data)
    #data = makeDTMF(dtmf_seq, 0.3, 0.08, peakLevel, sampRate, sampWidth, numCh)
    file = wave.open('testfile.wav', 'wb')
    file.setparams( (numCh, sampWidth/8 , sampRate, duration * sampRate, 'NONE', '') )
    file.writeframes(data)
    file.close()

    #data = generateAFSKpcmData(2083.33, 1562.5, 521, sampRate, sampWidth, peakLevel, numCh, message)
