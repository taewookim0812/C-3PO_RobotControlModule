 ## [Robot Control Module] C-3PO Motion Retargeting
This project is a robot control module for motion retargeting. 
Robot control module receives the retargeted motor values from motion retargeting module and 
set these to the real NAO/Pepper robot or choreography simulator. Following figure represents the overall 
structure of our C-3PO motion retargeting system. 

![Alt text](./figs/system.png)

### Getting Started
```buildoutcfg 
* Demo
1) Set the appropriate port numbers and run the "demo.py" file.
2) Run the "pykinect_stream.py" of the motion retargeting module and wait to be connected, then enjoy.

* Phase 1 training
0) Copy the sound files in "nao_touch_sound" folder to NAO hardware using choregraphe
1) Generate reference motions using "ReferenceMotionGen.py" or just utilize the project given in "choregraphe_project"
2) In "ReferenceMotionManager.py"
 2-1) Samples each reference motion trajectory by running "NTU_motion_class_sampling"
 2-2) Augment the trajectories by running "RefMotionAugmentation" 
 2-3) Merge the augmented trajectories by running "MergeAugData"
3) Once you finish the reference motion generation process, you can demonstrate the reference motion by running "ReplayReferenceMotion"

* In this Robot control module, there is nothing to do for Phase 2 training. 
```

### Update
```buildoutcfg
* Phase 3 training module will be updated.
* Phase 1 training module was updated.
* Demo module was updated.
```

### File descriptions
```buildoutcfg
    .
    ├── aug_motions         # Augmented reference motion files
    ├── aug_motions_merged  # Contains the merged file of augmented ref. motion data 
    ├── choregraphe_project # Choregraphe project files
    ├── figs    
    ├── nao_touch_sound     # Sound files used in touch based NAO manipulation
    ├── ref_motions         # Contains reference motion data of each class                                 
    │   └── system.png      # Figure for README file
    ├── CommonObject.py     # Commonly used functions and variables
    ├── demo.py             # Demo file
    ├── README.md
    ├── ReferenceMotionGen.py       # Direct-Teaching based reference motion generation
    ├── ReferenceMotionManager.py   # Manager class for reference motion generation           
    └── requirements.txt
```

### External Dependencies 
<pre>
Python 2.7
* <a href="https://developer.softbankrobotics.com/nao6/downloads/nao6-downloads-windows">naoqi download</a>
* <a href="http://doc.aldebaran.com/2-5/dev/python/install_guide.html">naoqi install guide</a>
* <a href="http://doc.aldebaran.com/2-4/dev/community_software.html">Choreographe</a>
</pre>

### Requirements
```buildoutcfg
pip install -r requirements.txt
```

### Publication
Please refer to the following paper and video for more detailed information.
* Kim and Lee, C-3PO: Cyclic-Three-Phase Optimization for Human-Robot Motion Retargeting based on 
Reinforcement Learning, ICRA 2020, 
[[Paper]](https://arxiv.org/abs/1909.11303), 
[[YouTube]](https://www.youtube.com/watch?v=C37Fip1X0Y0&t=19s)

```buildoutcfg
@article{kim2019c,
  title={C-3PO: Cyclic-Three-Phase Optimization for Human-Robot Motion Retargeting based on Reinforcement Learning},
  author={Kim, Taewoo and Lee, Joo-Haeng},
  journal={arXiv preprint arXiv:1909.11303},
  year={2019}
}
```

### Acknowledgment 
This work was supported by the ICT R&D program of MSIP/IITP [2017-0-00162, Development of Human-care 
Robot Technology for Aging Society].