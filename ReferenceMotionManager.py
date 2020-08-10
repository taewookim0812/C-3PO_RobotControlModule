"""
Function: Generation, sampling, and augmentation of the robot reference motion
Python Ver: 2.7
Author: Taewoo Kim
Contact: twkim0812@gmail.com
"""

"""Example: Use run Method"""
"""http://doc.aldebaran.com/2-4/naoqi/core/albehaviormanager.html"""

import qi
import argparse
import sys, time, os
import numpy as np


class ReferenceMotion:
    def __init__(self, IPAddr, PORT):
        self.IPAddr = IPAddr
        self.PORT = PORT
        self.session = self.initSession()

        """
        When you add another reference motion in the choregraphe project, 
        insert its folder name to the NTU_TargetMotionList
        """
        self.NTU_TargetMotionList = ['cheer_up', 'hand_waving', 'pointing_with_finger',
                                     'salute', 'wipe_face', 'put_the_palms_together']
        self.ref_data_path = 'ref_motions'
        self.aug_data_path = 'aug_motions'
        self.aug_merged_data_path = 'aug_motions_merged'

    def initSession(self):
        session = qi.Session()
        try:
            session.connect("tcp://" + self.IPAddr + ":" + str(self.PORT))
            print "Connection success !"
        except RuntimeError:
            print ("Can't connect to Naoqi at ip \"" + self.IPAddr + "\" on port " + str(self.PORT) + ".\n"
                   "Please check your script arguments. Run with -h option for help.")
            sys.exit(1)
        return session

    def NTU_motion_class_sampling(self):
        behavior_mng_service = self.session.service("ALBehaviorManager")
        motionProxy = self.session.service("ALMotion")

        names = behavior_mng_service.getInstalledBehaviors()
        fNames = filter(lambda x: '.lastUploadedChoregrapheBehavior' in x, names)  # filtered names
        print 'Len:', len(fNames), 'bh names: ', fNames, 'names: ', names

        for target in self.NTU_TargetMotionList:
            bh_to_run = [s for s in fNames if target in s]
            if not bh_to_run:
                print 'The target behavior does not exist'
                return
            bh_to_run = bh_to_run[0]
            print 'bh to run:', bh_to_run

            # Check if there are already running behaviors in choregraphe
            r_bhs = behavior_mng_service.getRunningBehaviors()

            if r_bhs:   # Stop if there is a running behavior
                print "Running behaviors:", r_bhs
                running_bh = r_bhs[0]
                if (behavior_mng_service.isBehaviorRunning(running_bh)):
                    behavior_mng_service.stopBehavior(running_bh)
                    time.sleep(1.0)
                else:
                    print "Running Behavior is not found."

            # Check that the behavior exists.
            if (behavior_mng_service.isBehaviorInstalled(bh_to_run)):
                # Check that it is not already running.
                if (not behavior_mng_service.isBehaviorRunning(bh_to_run)):
                    # Launch behavior. This is a blocking call, use _async=True if you do not
                    # want to wait for the behavior to finish.
                    init_pose = [s for s in fNames if 'init_pose' in s]
                    if not init_pose:
                        print 'init_pose was not found..'
                        raise ValueError

                    # make initial position
                    init_pose = init_pose[0]
                    behavior_mng_service.runBehavior(init_pose, _async=True)
                    time.sleep(2.0)

                    # run our target task
                    behavior_mng_service.runBehavior(bh_to_run, _async=True)
                    time.sleep(0.2)

                    useSensors = True
                    angle_list = np.array([])
                    start = time.time()
                    while (len(behavior_mng_service.getRunningBehaviors())):
                        joint_angles = motionProxy.getAngles("Body", useSensors)
                        phase = time.time() - start
                        joint_angles = [phase] + joint_angles  # [motion phase, angles...]
                        if len(angle_list) == 0:
                            angle_list = np.array(joint_angles)
                        else:
                            angle_list = np.vstack((angle_list, np.array(joint_angles)))

                        # NAO motion generation frequency: 25 fps(= 0.04 T).
                        # Thus, we sample the motion signals by 50 fps(= 0.02)
                        time.sleep(1 / 50.0)

                    # Angle order given from the getAngles()
                    # [HeadYaw, HeadPitch,
                    # LShoulderPitch, LShoulderRoll, LElbowYaw, LElbowRoll, LWristYaw, LHand,
                    # LHipYawPitch, LHipRoll, LHipPitch, LKneePitch, LAnklePitch, LAnkleRoll,
                    # RHipYawPitch, RHipRoll, RHipPitch, RKneePitch, RAnklePitch, RAnkleRoll,
                    # RShoulderPitch, RShoulderRoll, RElbowYaw, RElbowRoll, RWristYaw, RHand]
                    print 'Done!, shape: ', angle_list.shape, ' data:', angle_list

                    try:
                        if not os.path.exists(self.ref_data_path):
                            os.makedirs(self.ref_data_path)
                    except OSError:
                        print 'Error: Failed to create the folder' + self.ref_data_path

                    path = os.path.join(self.ref_data_path, 'Reference_Motion[' + target + '].txt')
                    np.savetxt(path, angle_list)
                else:
                    print "The behavior is already running."
            else:
                print "The behavior was not found."

    def RefMotionAugmentation(self, aug_length=20000, uni_noise_scale=0.5):
        self.CheckFileAndFolder(self.ref_data_path)

        # check the augmented folder
        ref_file_list = os.listdir(self.ref_data_path)
        try:
            if not os.path.exists(self.aug_data_path):
                os.makedirs(self.aug_data_path)
        except OSError:
            print 'Error: Failed to create the folder' + self.aug_data_path

        # Data load
        aug_data = np.zeros([aug_length, 26])   # Each line contains: [phase, 26 joints]
        for file_name in ref_file_list:
            refMotion = np.loadtxt(os.path.join(self.ref_data_path, file_name), delimiter=' ', dtype=np.float32)

            # Reference Motion Augmentation
            j = 0
            for i in range(aug_length):
                if i % 1000 == 0:
                    print i
                # set angles of reference motion
                idx = i % len(refMotion)
                refMotion[idx, :] += (np.random.rand() - 0.5) * uni_noise_scale
                aug_data[j, :] = refMotion[idx, 1:]
                j += 1
            print 'File Name: {}, Ref. Motion Shape: {}, Aug. Data Shape: {}'.format(file_name, refMotion.shape, aug_data.shape)

            # Save the augmented data
            target = file_name[file_name.find('[')+1:file_name.find(']')]
            save_file = '(AUG)Reference_Motion[' + target + ']_' + str(aug_length) + '_.txt'
            save_path = os.path.join(self.aug_data_path, save_file)
            np.savetxt(save_path, aug_data)
            print save_file + ' is saved..'

    def MergeAugData(self, shuffle=True):
        self.CheckFileAndFolder(self.aug_data_path)
        try:
            if not os.path.exists(self.aug_merged_data_path):
                os.makedirs(self.aug_merged_data_path)
        except OSError:
            print 'Error: Failed to create the folder' + self.aug_merged_data_path

        aug_file_list = os.listdir(self.aug_data_path)
        aug_merged_file = np.array([])
        for file_name in aug_file_list:
            augMotion = np.loadtxt(os.path.join(self.aug_data_path, file_name), delimiter=' ', dtype=np.float32)

            if len(aug_merged_file) == 0:
                aug_merged_file = np.array(augMotion)
            else:
                aug_merged_file = np.vstack((aug_merged_file, augMotion))

            print aug_merged_file.shape

        if shuffle:
            np.random.shuffle(aug_merged_file)

        file_name = '(AUG)Reference_Motion[Merged]_' + str(aug_merged_file.shape[0]) + '_.txt'
        np.savetxt(os.path.join(self.aug_merged_data_path, file_name), aug_merged_file)

    def CheckFileAndFolder(self, target_folder):
        if not os.path.exists(target_folder):
            print target_folder + ' does not exist'
            raise ValueError

        file_list = os.listdir(target_folder)
        file_count = 0
        for name in self.NTU_TargetMotionList:
            if any(name in s for s in file_list):
                file_count += 1

        if file_count != len(self.NTU_TargetMotionList):
            print 'File count mismatch'
            raise ValueError

        print '[{}]::'.format(target_folder) + ' Target file and folder are confirmed'

    def ReplayReferenceMotion(self, full_path):
        print('replay from sampled trajectories')
        motionProxy = self.session.service("ALMotion")

        # load reference motion
        refMotion = np.loadtxt(full_path, delimiter=' ', dtype=np.float32)
        print 'refMotion: ', refMotion.shape

        useSensors = False
        fractionMaxSpeed = 1.0
        heads = ["HeadYaw", "HeadPitch"]
        LArm = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand"]
        RArm = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
        jnames = heads + LArm + RArm

        for i in range(len(refMotion)):
            if i % 100 == 0:
                print 'i: ', i
            # set angles of reference motion
            headFrame = refMotion[i, 0:2].tolist()
            LArmFrame = refMotion[i, 2:8].tolist()
            RArmFrame = refMotion[i, 20:26].tolist()
            data = headFrame + LArmFrame + RArmFrame

            motionProxy.setAngles(jnames, data, fractionMaxSpeed)
            time.sleep(0.1)


def main(IPAddr, PORT):
    ref = ReferenceMotion(IPAddr, PORT)
    # ref.NTU_motion_class_sampling()
    # ref.RefMotionAugmentation(aug_length=20000, uni_noise_scale=0.5)
    # ref.MergeAugData(shuffle=True)

    # Example file for replay
    file_name = '(AUG)Reference_Motion[Merged]_120000_.txt'
    full_path = os.path.join(ref.aug_merged_data_path, file_name)
    ref.ReplayReferenceMotion(full_path)


if __name__ == "__main__":
    # target list: ['SIM', 'REAL']
    target = 'SIM'

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