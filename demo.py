"""
Function: Demo Code
Python Ver: 2.7
Author: Taewoo Kim
Contact: twkim0812@gmail.com
"""

import sys
import time
from naoqi import ALProxy

from CommonObject import *
from threading import Thread
import motion

HOST = "localhost"
PORT = 5007


def send_and_recv(motionProxy, dummy=None):
    conn = SocketCom(HOST, PORT)
    conn.open_host()

    heads = ["HeadYaw", "HeadPitch"]
    LArm = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand"]
    RArm = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
    names = heads + LArm + RArm

    # for reward calc
    LArm2 = ["LShoulderPitch", "LElbowYaw", "LHand"]
    RArm2 = ["RShoulderPitch", "RElbowYaw", "RHand"]
    names2 = LArm2 + RArm2

    recv = conn.read_socket('{', '}')  # receive inferred motor data.
    print 'Beginning Msg: ', recv

    useSensors = False
    fractionMaxSpeed = 1.0
    space = motion.FRAME_TORSO

    # LPF params
    useLFP = False
    alpha = 0.99
    prev_motor = np.array([])
    while True:
        recv = conn.read_socket('{', '}')  # receive inferred motor data.
        try:
            header = recv['header']
            data = recv['data']
        except TypeError:
            print 'Type Error..'
            print 'recv: ', recv
            continue

        if header == 'SetMotor':
            if useLFP:
                if prev_motor.size == 0:
                    prev_motor = np.array(data)

                data = (alpha) * np.array(data) + (1-alpha) * prev_motor
                motionProxy.setAngles(names, data.tolist(), fractionMaxSpeed)
                prev_motor = data
            else:
                motionProxy.setAngles(names, data, fractionMaxSpeed)

        elif header == 'GetMotor':
            print 'getAngles'
            motor_values = motionProxy.getAngles(names, useSensors)
            motor_positions = []
            for i in names2:
                motor_positions += motionProxy.getPosition(i, space, useSensors)[:3]    # only positions of [x,y,z,wx,wy,wz]
            conn.write_socket({'header': 'NAO motor', 'NAO_angle': motor_values, 'NAO_jposition': motor_positions})

        elif header == 'Analytic':
            LArm = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]
            RArm = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            names = LArm + RArm

            if useLFP:
                if prev_motor.size == 0:
                    prev_motor = np.array(data)

                motors = (alpha) * np.array(data) + (1 - alpha) * prev_motor
                motionProxy.setAngles(names, motors.tolist(), fractionMaxSpeed)
                prev_motor = motors
            else:
                motionProxy.setAngles(names, data, fractionMaxSpeed)
        else:
            print 'Unknown header..'

    conn.socket_close()


def main(robotIP, robotPort):
    try:
        motionProxy = ALProxy("ALMotion", robotIP, robotPort)
        postureProxy = ALProxy("ALRobotPosture", robotIP, robotPort)

        motionProxy.wakeUp()
        postureProxy.goToPosture("Stand", 0.5)

        # Anti-Collision Setting
        chainName = "Arms"
        enable = True
        isSuccess = motionProxy.setCollisionProtectionEnabled(chainName, enable)
        print "Anticollision activation on arms: " + str(isSuccess)
        time.sleep(3)

    except Exception, e:
        print "Could not create proxy to ALMotion"
        print "Error was: ", e

    try:
        sock = Thread(target=send_and_recv, args=(motionProxy, None))
        sock.start()
        sock.join()
    except RuntimeError:
        print "RunTime Error"
        sys.exit(1)

    motionProxy.rest()
    print motionProxy.getSummary()


if __name__ == "__main__":
    # target list: ['SIM', 'REAL']
    target = 'SIM'

    if target == 'SIM':
        robotIp = "localhost"
        robotPort = 56499   # set your own port number
    elif target == 'REAL':
        """
        For wifi connection with NAO, refer:
        http://doc.aldebaran.com/1-14/nao/nao-connecting.html
        """
        robotIp = "192.168.0.7"  # set your own IP address
        robotPort = 9559  # fixed port number
    else:
        print 'Unknown Target..'
        raise ValueError

    main(robotIp, robotPort)
