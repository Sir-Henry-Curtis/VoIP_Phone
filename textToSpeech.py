# -*- coding: utf-8 -*-
#!/usr/bin/python

import time  # for delay

try:
    import gi  # for playing mp3 stream
    #gi.require('Gst', '1.0')
    from gi.repository import GObject
    from gi.repository import Gst
    gi1 = True
except:
    print "Using gst 0.10"
    import pygst  # for playing mp3 stream
    pygst.require('0.10')
    import gst
    gi1 = False


class TextToSpeech():
    def __init__(self):
        pass

    def speak(self, text, sleepTime=0):
        if gi1:
            GObject.threads_init()
            Gst.init(None)
        else:
            pass
        #take command line args as the input string
        text = text.split(' ')
        input_string = text

        #convert to google friendly url (with + replacing spaces)
        tts_string = '+'.join(input_string)

        #print tts_string

        #use string in combination with the translate url as the stream to be played
        music_stream_uri = 'http://translate.google.com/translate_tts?tl=en&q=' + tts_string

        if gi1:
            player = Gst.ElementFactory.make("playbin", None)
        else:
            player = gst.element_factory_make("playbin", "player")

        player.set_property('uri', music_stream_uri)
        player.set_property('volume', 1)

        if gi1:
            player.set_state(Gst.State.PLAYING)
        else:
            player.set_state(gst.STATE_PLAYING)

        #requires a delay, if the py process closes before the mp3 has finished it will be cut off.
        time.sleep(sleepTime)

        player = None
        text = None
        input_string = None
        tts_string = None
        music_stream_uri = None
