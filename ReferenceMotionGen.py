"""
Function: Reference motion generation by touching interface
Python Ver: 2.7
Author: Taewoo Kim
Contact: twkim0812@gmail.com

Notice: Before you running this ReferenceMotionGen.py, you must copy the sound files shown below to the NAO hardware
From(PC):
./nao_touch_sound/grab_hand.ogg
./nao_touch_sound/release_hand.ogg

To(NAO):
/home/nao/wav/grab_hand.ogg
/home/nao/wav/release_hand.ogg

Please refer to the following link for a detailed information about file transfer
http://doc.aldebaran.com/2-1/software/choregraphe/file_upload_download.html
"""

import sys
import functools
import qi
from naoqi import ALProxy


class ReactToTouch(object):
    def __init__(self, app):
        super(ReactToTouch, self).__init__()

        # Get the services ALMemory, ALTextToSpeech.
        app.start()
        session = app.session
        self.memory_service = session.service("ALMemory")
        self.motion = session.service("ALMotion")
        self.audio = session.service("ALAudioPlayer")

        self.grabFileId = self.audio.loadFile("/home/nao/wav/grab_hand.ogg")
        self.releaseFileId = self.audio.loadFile("/home/nao/wav/release_hand.ogg")

        # Connect to an Naoqi Event.
        self.touch = self.memory_service.subscriber("TouchChanged")
        self.id = self.touch.signal.connect(functools.partial(self.onTouched, "TouchChanged"))

    def onTouched(self, strVarName, value):
        """ This will be called each time a touch
        is detected.
        """
        # Disconnect to the event when talking,
        # to avoid repetitions
        self.touch.signal.disconnect(self.id)

        lArms = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw"]
        rArms = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
        heads = ["HeadYaw", "HeadPitch"]
        pNames = lArms + rArms + heads

        pTimeLists = 0.01
        for p in value:
            if p[0]=='RHand/Touch/Back':    # 'RArm'
                if p[1]:
                    pStiffnessLists = 0.0
                    self.audio.play(self.grabFileId, _async=True)
                    print 'RArm is grabbed'
                else:
                    pStiffnessLists = 1.0
                    self.audio.play(self.releaseFileId, _async=True)
                    print 'RArm is released'
                self.motion.stiffnessInterpolation(rArms+heads, pStiffnessLists, pTimeLists)  # blocking-call

            if p[0]=='LHand/Touch/Back':
                if p[1]:
                    pStiffnessLists = 0.0
                    self.audio.play(self.grabFileId, _async=True)
                    print 'LArm is grabbed'
                else:
                    pStiffnessLists = 1.0
                    self.audio.play(self.releaseFileId, _async=True)
                    print 'LArm is released'
                self.motion.stiffnessInterpolation(lArms+heads, pStiffnessLists, pTimeLists)  # blocking-call

        # Reconnect again to the event
        self.id = self.touch.signal.connect(functools.partial(self.onTouched, "TouchChanged"))


def main(robotIP, robotPort):
    try:
        motionProxy = ALProxy("ALMotion", robotIP, robotPort)
        motionProxy.wakeUp()
    except Exception, e:
        print "Could not create a proxy to ALMotion"
        print "Error was: ", e

    try:
        # Initialize qi framework.
        connection_url = "tcp://" + robotIP + ":" + str(robotPort)
        app = qi.Application(["ReactToTouch", "--qi-url=" + connection_url])
    except RuntimeError:
        print "RunTime Error"
        sys.exit(1)
    react_to_touch = ReactToTouch(app)
    app.run()


if __name__ == "__main__":
    # target list: ['SIM', 'REAL']
    target = 'REAL'

    if target == 'SIM':
        robotIp = "localhost"
        robotPort = 57543  # !!! set your own port number
    elif target == 'REAL':
        """
        For wifi connection with NAO, refer to:
        http://doc.aldebaran.com/1-14/nao/nao-connecting.html
        """
        robotIp = "192.168.0.7"  # set your own IP address
        robotPort = 9559  # fixed port number
    else:
        print 'Unknown Target..'
        raise ValueError

    main(robotIp, robotPort)
