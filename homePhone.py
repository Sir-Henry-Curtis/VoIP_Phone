import Adafruit_BBIO.GPIO as gpio
import linphone
import speechToText
import textToSpeech
import time


class HomePhone():
    def __init__(self):
        self.inUse = None
        self.prevHookState = 'Low'

        self.hook1 = "P8_19"  # Output1 - Wht
        self.hook2 = "P8_26"  # Output2 - Red
        self.hook3 = "P8_18"  # Input - Blk
        self.ringer1 = "P8_9"
        self.ringer2 = "P8_10"

        print 'Pins Set: True'

        gpio.setup(self.hook1, gpio.OUT)
        gpio.setup(self.hook2, gpio.OUT)
        gpio.setup(self.hook3, gpio.IN)
        gpio.output(self.hook1, gpio.HIGH)
        gpio.output(self.hook2, gpio.HIGH)

        gpio.setup(self.ringer1, gpio.OUT)
        gpio.output(self.ringer1, gpio.LOW)
        gpio.setup(self.ringer2, gpio.OUT)
        gpio.output(self.ringer2, gpio.LOW)

        print 'GPIO Setup: True'

        self.operator = textToSpeech.TextToSpeech()
        self.dialer = linphone.Linphone()
        self.userInput = speechToText.SpeechToText()

        print 'Libraries Assigned: True'

        self.run()

    def answerIncoming(self):
        self.dialer.answer()
        self.inUse = True
        return

    def makeCall(self):
        time.sleep(1)
        self.operator.speak("who can i connect you with?", 2)
        #time.sleep(2)
        phoneNumber = self.userInput.startRecording(15)
        #print phoneNumber
        if phoneNumber is not None and phoneNumber[0] != '':
            phoneNumber = phoneNumber[0]
            phoneNumber = phoneNumber.split(' ')
            dialNumber = ''
            print dialNumber
            for i in phoneNumber:
                dialNumber += i
            if len(dialNumber) < 10:
                success = False
            else:
                conf = False
                while not conf:
                    conf, wrongNumber = self.confirmNumber(dialNumber)
                if wrongNumber is True:
                    success = False
                else:
                    success = True
        else:
            success = False

        return success

    def confirmNumber(self, dialNumber):
        self.operator.speak("did you say", 2)
        for n in dialNumber:
            self.operator.speak(n, 2)
        confirmation = self.userInput.startRecording(15, 'conf')
        time.sleep(2)
        print confirmation
        if confirmation is not None and 'yes' in confirmation:
            self.operator.speak("i'll connect you now'", 2)
            self.dialer.call(dialNumber)
            conf = True
            wrongNumber = False
        elif confirmation is not None and 'yes' not in confirmation:
            conf = True
            wrongNumber = True
        else:
            self.operator.speak('i am sorry i couldnt understand you', 2)
            conf = False
            wrongNumber = None

        return conf, wrongNumber

    def run(self):
        # Create new threads
        self.dialer.start()
        self.dialer.spawn()

        print 'Linphone Running: ' + str(self.dialer.isrunning())
        self.inUse = False
        while True:
            feedback = self.dialer.getLineStatus()
            if feedback == 'Incoming Call' and self.inUse is False:
                self.answerIncoming()
            elif feedback == 'Call ended':
                self.inUse = False
            else:
                pass

            if gpio.input(self.hook3) and self.dialer.isOnCall() is False and self.inUse is False and self.prevHookState == 'Low':
                self.inUse = True
                self.prevHookState = 'High'
                success = False
                while not success and gpio.input(self.hook3):
                    success = self.makeCall()
            elif not gpio.input(self.hook3) and self.prevHookState == 'High':
                if self.dialer.isOnCall():
                    self.dialer.terminateCall()
            else:
                pass

if __name__ == "__main__":

    app = HomePhone()
    sys.exit(app.exec_())