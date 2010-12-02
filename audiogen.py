import math, struct, random, array

pi = math.pi

def makeMorse(sequence, wpm, tone, peakLevel, sampRate, sampWidth, numCh):
    element = 1.2 / wpm #in samples
    print element
    alphabet = {'a':'.-', 'b':'-...', 'c':'-.-.', 'd':'-..', 'e':'.',
	        'f':'..-.', 'g':'--.', 'h':'....', 'i':'..', 'j':'.---',
		'k':'-.-', 'l':'.-..', 'm':'--', 'n':'-.', 'o':'---',
		'p':'.--.', 'q':'--.-', 'r':'.-.', 's':'...', 't':'-',
		'u':'..-', 'v':'...-', 'w':'.--', 'x':'-..-', 'y':'-.--',
		'z':'--..', '1':'.----', '2':'..---', '3':'...--',
		'4':'....-', '5':'.....', '6':'-....', '7':'--...',
		'8':'---..', '9':'----.', '0':'-----' }
    pcm_data = ''
    ditdahs = ''
    level = convertdbFStoInt(peakLevel, sampWidth)
    #sequence = "... --- ... --. -.- --- .. . --. - .-"
    silence = generateSimplePCMToneData(1000, 1000, sampRate, element, sampWidth,
	    -110, numCh)

    for a in sequence.lower():
	if a == ' ': ditdahs += '|'
	else: ditdahs = ditdahs + alphabet[a] + ' '

    for a in ditdahs:
	if a == ".":
	    pcm_data += generateSimplePCMToneData(tone, tone, sampRate, element,
		    sampWidth, peakLevel, numCh)
	    pcm_data += silence
	elif a == "-":
	    pcm_data += generateSimplePCMToneData(tone, tone, sampRate, element * 3,
		    sampWidth, peakLevel, numCh)
	    pcm_data += silence
	elif a == " ":
	    pcm_data += silence * 3
	elif a == "|":
	    pcm_data += silence * 7

    return pcm_data

def convertdbFStoInt( level, sampWidth):
    return math.pow(10, (float(level) / 20)) * 32767

def makeDTMF(sequence, duration, pause, peakLevel, sampRate, sampWidth, numCh):
    dtmf_values = {
        '1':(1209, 697), '2':(1336, 697), '3':(1477, 697), 'A':(1633, 697),
	'4':(1209, 770), '5':(1336, 770), '6':(1477, 770), 'B':(1633, 770),
	'7':(1209, 852), '8':(1336, 852), '9':(1477, 852), 'C':(1633, 852),
	'*':(1209, 941), '0':(1336, 941), '#':(1477, 941), 'D':(1633, 941) }
    data_out = ''
    phase = 0 * pi
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
	                   (freq1 * 2 * pi * i)/ sampRate + phase) )) 
		    sample += int(math.ceil( level * math.sin(
			   (freq2 * 2 * pi * i)/ sampRate + phase) ))
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

def genNonSinePCMToneData(freq, sampRate, duration, sampWidth, peakLevel, numCh):
    def saw(t):
	return 2 * (t/(pi * 2) - math.floor(t/(pi * 2) + 0.5))

    def tri(t):
	return math.fabs(saw(t)) * 2 - 1

    def squ(t):
	sign = math.sin(t)
	if sign > 0 : return 1
	if sign < 0 : return -1
	else: return 0

    phase = 0
    level = convertdbFStoInt(peakLevel, sampWidth)
    pcm_data = ''
    #freq = startfreq
    #print duration * sampRate

    for i in range(0, int(round(sampRate * duration))):
        for ch in range(numCh):
	    sample =  int(( level * squ((freq * 2 * pi * i)/ sampRate + phase) ))
	    #print sample
	    pcm_data += struct.pack('<h', sample)

    return pcm_data

def generateSimplePCMToneData(startfreq, endfreq, sampRate, duration, sampWidth, peakLevel, numCh):
    """Generate a string of binary data formatted as a PCM sample stream. Freq is in Hz,
    sampRate is in Samples per second, duration is in seconds, sampWidth is in bits, 
    peakLevel is in dBFS, and numCh is either 1 or 2."""

    phase = 0 * pi
    level = convertdbFStoInt(peakLevel, sampWidth)
    pcm_data = ''
    freq = startfreq
    #print duration * sampRate

    for i in range(0, int(round(sampRate * duration))):
        for ch in range(numCh):
	    sample =  int(( level * math.sin(
	                   (freq * 2 * pi * i)/ sampRate + phase) ))
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

def generateAFSK(markF, spaceF, bitrate, sampRate, sampWidth, peakLevel, numCh,
	         stringData):
    "Generate a string of binary data of AFSK audio"

    x = 0
    c = 0
    cor = 0
    pcm_data = ''
    bitstream = ''
    make_fractional = False
    phase = 0 * pi
    level = convertdbFStoInt(peakLevel, sampWidth)
    bitduration, bitextra = divmod(sampRate, bitrate)
    d = 0
    print bitduration, bitextra / bitrate, sampRate / bitrate
    
    print stringData
    for byte in stringData:
	bytebits = "{0:08b}".format( ord(byte))
	bitstream += bytebits[::-1]
	#bitstream += bytebits
    print bitstream
    bitstream = '1'
    
    for bit in bitstream:
	if make_fractional:
	    #print last_bit + bit
	    if last_bit + bit == '01':
		freq = bitextra / bitrate * (markF - spaceF) + spaceF
	    if last_bit + bit == '10':
		freq = bitextra / bitrate * (spaceF - markF) + markF
	    #print freq
	    sample = int(( level * math.sin(
		     (freq * 2 * pi * x)/ sampRate + phase) ))
	    #print sample
	    pcm_data += struct.pack('<h', sample)
	x = 0
	if bit == '1':
	    freq = markF
	else:
	    freq = spaceF
	for i in range(d, int(bitduration) + 1):
	    sample =  int(( level * math.sin(
	              (freq * 2 * pi * (x - cor)/ sampRate + phase) )))
	    #print sample
	    pcm_data += struct.pack('<h', sample)
	    x += 1
	    #print x
	cor = (1 - (bitextra / bitrate)) * 0 # * 2 * pi / sampRate 
	#if cor < 0: cor += 1
	#if cor > 1: cor -= 1
	print cor
	#if d == 0: d = 1
	#else: d = 0
	#phase = phase + (bitextra / bitrate / sampRate * 2 * pi)
	#print phase
	if bitextra > 0:
	    make_fractional = False
	    last_bit = bit
    
    return pcm_data

def genFMwaveform(carrierF, modF, sampRate, sampWidth, peakLevel, dev, duration, numCh):
    pcm_data = ''
    sample = 0
    phase = 0 * pi
    level = convertdbFStoInt(peakLevel, sampWidth)

    for i in range(0, int(math.floor(sampRate * duration))):
	phase = dev * math.sin(
		    (modF * 2 * pi * i) / sampRate)
       
	#phase = dev * 0
	#freq = carrierF + (dev * 0)
	freq = carrierF
	for ch in range(numCh):
	    sample =  int(( level * math.sin(
	                   (freq * 2 * pi * i)/ sampRate + phase) ))
	    #print sample
	    pcm_data += struct.pack('<h', sample)

    return pcm_data

def generateEASpcmData(org, event, fips, eventDuration, timestamp, stationId, sampRate, sampWidth, 
	                peakLevel, numCh):
    "Put together info to generate an EAS message"

    markF = 2083.3
    spaceF = 1562.5
    bitrate = 520.5
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

    freq = 1025
    sampRate = 44100
    duration = 10
    sampWidth = 16
    peakLevel = -10
    numCh = 1
    now = time.gmtime()
    timestamp = time.strftime('%j%H%M', now) 
    #dtmf_seq = ' 1 2 3 4 5 6 7 8 9 A B C D * # '
    dtmf_seq = '      1   4 1 7   8 3 6   6 2 5 5      '
    #dtmf_seq = '1234'
    #dtmf_seq = '1'
    #print timestamp
    easmsg = '\xab' * 16
    easmsg += 'ZCZC-EAS-RWT-029091+0100-3300015-KXYZ/FM -'

    #data = makeMorse("Four score and seven years ago", 25, freq, peakLevel, sampRate, sampWidth, numCh)
    data = genNonSinePCMToneData(freq, sampRate, duration, sampWidth, peakLevel, numCh)
    #data = genFMwaveform(1562.5, 0.5, sampRate, sampWidth, peakLevel, 10000, duration, numCh)
    #data = generateAFSK(2083, 1562.5, 520.5, sampRate, sampWidth, peakLevel, numCh, easmsg)
    #data = generateEASpcmData('EAS', 'RWT', '029091', '0030', timestamp, 'KXYZ/FM', sampRate, 
	#    sampWidth, peakLevel, numCh)
    #data = generateSimplePCMToneData(freq, freq, sampRate, duration, sampWidth, peakLevel, numCh)
    #data = applyLinearFade(-100, 0, numCh, sampWidth, data)
    #data = changeLevelPCMdata(sampRate, sampWidth, -6, numCh, data)
    #data = makeDTMF(dtmf_seq, 0.3, 0.08, peakLevel, sampRate, sampWidth, numCh)
    file = wave.open('testfile.wav', 'wb')
    file.setparams( (numCh, sampWidth/8 , sampRate, duration * sampRate, 'NONE', '') )
    file.writeframes(data)
    file.close()

    #data = generateAFSKpcmData(2083.33, 1562.5, 521, sampRate, sampWidth, peakLevel, numCh, message)
