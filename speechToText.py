""" Record audio from the microphone and encode as x-speex-with-header-byte to pass to Google
    for speech recognition.

    Aaron J. Miller, 2012. No copyright held. Use freely for your purposes.
    I provide this code for informational purposes only.
"""

import sys
import pyaudio
import speex
import numpy as np  # just for doing a standard deviation for audio level checks
import urllib2
import time
import textToSpeech


class SpeechToText():

    def __init__(self):
        self.chunk = 320  # tried other numbers... some don't work
        self.bytespersample = 2
        self.CHANNELS = 1
        self.RATE = 16000  # "wideband" mode for speex. May work with 8000. Haven't tried it.

    def startRecording(self, waitTime, conf=False):
        self.p = pyaudio.PyAudio()
        self.e = speex.Encoder()
        self.d = speex.Decoder()
        self.e.initialize(speex.SPEEX_MODEID_WB)
        self.d.initialize(speex.SPEEX_MODEID_WB)
        self.FORMAT = pyaudio.paInt16
        self.waitTime = waitTime
        self.conf = conf

        self.operator = textToSpeech.TextToSpeech()

        # Start the stream to record the audio
        stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        output=True,
                        frames_per_buffer=self.chunk)

        print "Listening."

        threshold = 200  # Adjust this to be slightly above the noise level of your recordings.
        nquit = 40  # number of silent frames before terminating the program
        nover = 0
        keepgoing = True
        spxlist = []  # list of the encoded speex packets/frames
        start = time.time()
        while keepgoing:
            data = stream.read(self.chunk)  # grab 320 samples from the microphone
            spxdata = self.e.encode(data)  # encode using the speex dll
            print "Length encoded: %d" % len(spxdata)  # print the length, after encoding. Can't exceed 255!
            spxlist.append(chr(len(spxdata)) + spxdata)  # add the length "header" onto the front of the frame

            a = np.frombuffer(data, np.int16)  # convert to numpy array to check for silence or audio
            audiolevel = np.std(a)
            if audiolevel < threshold:  # too quiet
                nover += 1
            else:
                nover = 0

            #if nover >= nquit:
                #keepgoing = False

            #print '%2.1f (%d%% quiet)' % (audiolevel, nover * 100 / nquit)
            end = time.time()
            elapsed = end - start
            if elapsed > self.waitTime:
                keepgoing = False

        print "I'm stopping now."
        stream.stop_stream()
        stream.close()
        self.p.terminate()
        if self.conf is False:
            self.operator.speak('let me look that up', 2)

        fullspx = ''.join(spxlist)  # make a string of all the header-ized speex packets
        #print 'Length before speex: %d, Length after speex: %d' % (len(spxlist) * self.chunk, len(fullspx))

        print 'Sending to google.'

        # see http://sebastian.germes.in/blog/2011/09/googles-speech-api/ for a good description of the url
        url = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&pfilter=1&client=chromium&lang=en-US&maxresults=4'
        header = {'Content-Type': 'audio/x-speex-with-header-byte; rate=16000'}
        req = urllib2.Request(url, fullspx, header)
        data = urllib2.urlopen(req)
        print 'Google says:'
        dataString = str(data.read())
        print dataString
        dataString = dataString.split('"')
        if len(dataString) > 10:
            phoneNumber = []
            phoneNumber.append(dataString[11])
            #print phoneNumber
            return phoneNumber
        else:
            return


        #yes!

