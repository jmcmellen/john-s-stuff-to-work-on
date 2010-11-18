import math, struct, random

def generateSimplePCMToneData(freq, sampRate, duration, sampWidth, peakLevel, numCh):
    """Generate a string of binary data formatted as a PCM sample stream. Freq is in Hz,
    sampRate is in Samples per second, duration is in seconds, sampWidth is in bits, 
    peakLevel is in dBFS, and numCh is either 1 or 2."""

    phase = 0 * math.pi
    level = math.pow(10, (float(peakLevel) / 20)) * 32767 #Should depend on sampWidth
    pcm_data = ''

    for i in range(0, int(math.floor(sampRate * duration))):
	for ch in range(numCh):
	    pcm_data += struct.pack('<h', int(math.ceil( level * math.sin(
	             (freq * 2 * math.pi * i)/ sampRate + phase) )))

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
    #print bitstream
    one_bit = generateSimplePCMToneData(markF, sampRate, bitduration, sampWidth,
		           peakLevel, numCh)
    zero_bit = generateSimplePCMToneData(spaceF, sampRate, bitduration, sampWidth,
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
    bitrate = 520.83
    pcm_data = ''

    preamble = '\xab' * 16
    message = 'ZCZC-{0}-{1}-{2}+{3}-{4}-{5: <8}-'.format(org, event, fips, eventDuration,
	    timestamp, stationId[0:8])
    endOfMessage = 'NNNN'
    header = generateAFSKpcmData(markF, spaceF, bitrate, sampRate, sampWidth, peakLevel,
	                 numCh, preamble + message.upper())
    eom = generateAFSKpcmData(markF, spaceF, bitrate, sampRate, sampWidth, peakLevel,
	                 numCh, preamble + endOfMessage)
    silence = generateSimplePCMToneData(100, sampRate, 1, sampWidth, -94, numCh)

    for i in range(3):
	pcm_data = pcm_data + header + silence
    for i in range(3):
	pcm_data = pcm_data + eom + silence

    return pcm_data

if __name__ == "__main__":
    import wave, time

    freq = 2000
    sampRate = 44100
    duration = 10
    sampWidth = 16
    peakLevel = -10
    numCh = 1
    now = time.gmtime()
    timestamp = time.strftime('%j%H%M', now) 
    #print timestamp

    data = generateEASpcmData('EAS', 'RWT', '000000', '0100', timestamp, 'KXYZ/FM', sampRate, 
	    sampWidth, peakLevel, numCh)
    file = wave.open('testfile.wav', 'wb')
    file.setparams( (numCh, sampWidth/8 , sampRate, duration * sampRate, 'NONE', '') )
    file.writeframes(data)
    file.close()

    #data = generateAFSKpcmData(2083.33, 1562.5, 521, sampRate, sampWidth, peakLevel, numCh, message)
