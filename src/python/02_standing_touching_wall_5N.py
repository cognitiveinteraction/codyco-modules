#!/xde
#
# Copyright (C) 2013-7 CODYCO Project
# Author: Serena Ivaldi, Joseph Salini
# email:  serena.ivaldi@isir.upmc.fr
#
# Permission is granted to copy, distribute, and/or modify this program
# under the terms of the GNU General Public License, version 2 or any
# later version published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details
#

import xde_world_manager as xwm
import xde_robot_loader  as xrl
import xde_resources     as xr
import xde_isir_controller as xic
import lgsm
import time
import pylab as pl
import numpy

###################### PARAMETERS ##############################
pi = lgsm.np.pi
rad2deg = 180.0/pi;
# height of the waist
waist_z = 0.58
# minimum distance for computing the local distance between shapes in possible collision
local_minimal_distance = 0.05


########### CONTROLLER ###############

# formulation of the control problem
# False= use full problem (ddq, Fext, tau) => more stable, but slower (not inverse of mass matrix)
# True= use reduced problem (Fext, tau) => faster
use_reduced_problem_no_ddq = False

# solver for the quadratic problem 
# qld = more accurate
solver = "qld" # "quadprog"

###################### PARAMETERS ##############################





##### AGENTS
dt = 0.01
wm = xwm.WorldManager()
wm.createAllAgents(dt, lmd_max=local_minimal_distance)
wm.resizeWindow("mainWindow",  640, 480, 50, 50)


##### WORLD

## GROUND
#flat ground
groundWorld = xrl.createWorldFromUrdfFile(xr.ground, "ground", [0,0,0,1,0,0,0], True, 0.001, 0.001)
wm.addWorld(groundWorld)

## MOVING WALL
robotWorld = xrl.createWorldFromUrdfFile("resources/moving_wall.xml", "moving_wall", [-0.25,0.2,0.85,1,0,0,0], True, 0.001, 0.01)
wm.addWorld(robotWorld)
dynModel_moving_wall = xrl.getDynamicModelFromWorld(robotWorld)

## ROBOT
rname = "robot"
fixed_base = False
robotWorld = xrl.createWorldFromUrdfFile(xr.icub_simple, rname, [0,0,0.6,1,0,0,0], fixed_base, 0.001, 0.001)
wm.addWorld(robotWorld)
robot = wm.phy.s.GVM.Robot(rname)
robot.enableGravity(True)

N  = robot.getJointSpaceDim()
# get dynamic model of the robot
dynModel = xrl.getDynamicModelFromWorld(robotWorld)
jmap     = xrl.getJointMapping(xr.icub_simple, robot)

# suppress joint limits of the icub => to allow more movement
robot.setJointPositionsMin(-4.0*lgsm.ones(N))
robot.setJointPositionsMax(4.0*lgsm.ones(N))


##### SET CONTACT TYPES
#set contact law
# = material 1
# = material 2
# = 0=no friction, 1=cone, 2=cone+friction in rotation
# = mu=coeff of friction
wm.ms.setContactLawForMaterialPair("material.metal", "material.concrete", 1, 1.5)
wm.ms.setContactLawForMaterialPair("material.metal", "material.metal", 1, 1.5)

## enable contact with flat ground
robot.enableContactWithBody("ground.ground", True)
# this only displays the contacts ground with feet
wm.contact.showContacts([(rname+"."+b,"ground.ground") for b in ["l_foot", "r_foot"]]) 

## enable contact with moving wall
robot.enableContactWithBody("moving_wall.moving_wall", True)
# this displays all the contacts: whole body with wall
#wm.contact.showContacts([(b,"moving_wall.moving_wall") for b in robot.getSegmentNames()]) 



##### SET INITIAL STATE OF THE ROBOT
qinit = lgsm.zeros(N)
# correspond to:    l_elbow_pitch     r_elbow_pitch     l_knee             r_knee             l_ankle_pitch      r_ankle_pitch      l_shoulder_roll          r_shoulder_roll
for name, val in [("l_elbow_pitch", pi/8.), ("r_elbow_pitch", pi/8.), ("l_knee", -0.05), ("r_knee", -0.05), ("l_ankle_pitch", -0.05), ("r_ankle_pitch", -0.05), ("l_shoulder_roll", pi/8.), ("r_shoulder_roll", pi/8.)]:
    qinit[jmap[rname+"."+name]] = val

robot.setJointPositions(qinit)
dynModel.setJointPositions(qinit)
robot.setJointVelocities(lgsm.zeros(N))
dynModel.setJointVelocities(lgsm.zeros(N))


##### CONTROLLERS

## controller for the moving wall
ctrl_moving_wall = xic.ISIRController(dynModel_moving_wall, "moving_wall", wm.phy, wm.icsync, solver, use_reduced_problem_no_ddq)
gposdes = lgsm.zeros(1)
gveldes = lgsm.zeros(1)
# create full task with a very low weight for reference posture
fullTask = ctrl_moving_wall.createFullTask("zero_wall", w=1., kp=50)  
# lower if the spring of the wall is too rigid
#fullTask.setKpKd(50) --> now in create full task
#fullTask.update(gposdes, gveldes) --> now split into two
fullTask.set_q(gposdes)
fullTask.set_qdot(gveldes)



## controller for the robot

# flat ground
ctrl = xic.ISIRController(dynModel, rname, wm.phy, wm.icsync, solver, use_reduced_problem_no_ddq)




##### SET TASKS
# this ...
#N0 = 6 if fixed_base is False else 0
#partialTask = ctrl.createPartialTask("partial", range(N0, N+N0), 0.0001, kp=9., pos_des=qinit)
# ... is equivalent to that ("INTERNAL" can be omitted):

## full task: bring joints to the initial position
#default: Kd= 2*sqrt(Kp)
fullTask = ctrl.createFullTask("full", "INTERNAL", w=0.0001, kp=0., kd=9., q_des=qinit)

## waist task: better balance
Weight_waist_task = 1.0
waistTask   = ctrl.createFrameTask("waist", rname+'.waist', lgsm.Displacement(), "RXYZ", w=Weight_waist_task, kp=36., pose_des=lgsm.Displacement(0,0,.58,1,0,0,0))

## back task: to keep the back stable
back_dofs   = [jmap[rname+"."+n] for n in ['torso_pitch', 'torso_roll', 'torso_yaw']]
backTask    = ctrl.createPartialTask("back", back_dofs, w=0.001, kp=16., q_des=lgsm.zeros(3))

## COM task
Weight_COM_task = 10.0
CoMTask     = ctrl.createCoMTask("com", "XY", w=Weight_COM_task, kp=0.) #, kd=0.
# controller that generates the ZMP reference trajectory for stabilizing the COM
COM_reference_position = [[-0.0,0.0]]
ctrl.add_updater( xic.task_controller.ZMPController( CoMTask, ctrl.getModel(), COM_reference_position, RonQ=1e-6, horizon=1.8, dt=dt, H_0_planeXY=lgsm.Displacement(), stride=3, gravity=9.81) )

## contact tasks for the feet
sqrt2on2 = lgsm.np.sqrt(2.)/2.
RotLZdown = lgsm.Quaternion(-sqrt2on2,0.0,-sqrt2on2,0.0) * lgsm.Quaternion(0.0,1.0,0.0,0.0)
RotRZdown = lgsm.Quaternion(0.0, sqrt2on2,0.0, sqrt2on2) * lgsm.Quaternion(0.0,1.0,0.0,0.0)

ctrl.createContactTask("CLF0", rname+".l_foot", lgsm.Displacement([-.039,-.027,-.031]+ RotLZdown.tolist()), 1.5, 0.) # mu, margin
ctrl.createContactTask("CLF1", rname+".l_foot", lgsm.Displacement([-.039, .027,-.031]+ RotLZdown.tolist()), 1.5, 0.) # mu, margin
ctrl.createContactTask("CLF2", rname+".l_foot", lgsm.Displacement([-.039, .027, .099]+ RotLZdown.tolist()), 1.5, 0.) # mu, margin
ctrl.createContactTask("CLF3", rname+".l_foot", lgsm.Displacement([-.039,-.027, .099]+ RotLZdown.tolist()), 1.5, 0.) # mu, margin

ctrl.createContactTask("CRF0", rname+".r_foot", lgsm.Displacement([-.039,-.027, .031]+ RotRZdown.tolist()), 1.5, 0.) # mu, margin
ctrl.createContactTask("CRF1", rname+".r_foot", lgsm.Displacement([-.039, .027, .031]+ RotRZdown.tolist()), 1.5, 0.) # mu, margin
ctrl.createContactTask("CRF2", rname+".r_foot", lgsm.Displacement([-.039, .027,-.099]+ RotRZdown.tolist()), 1.5, 0.) # mu, margin
ctrl.createContactTask("CRF3", rname+".r_foot", lgsm.Displacement([-.039,-.027,-.099]+ RotRZdown.tolist()), 1.5, 0.) # mu, margin

## frame task for putting the hand in contact with the wall
# we have to split rotation and xyz posing - because controlling both at same time generates 
# rototranslation vector (xyz+o4)
H_hand_tool = lgsm.Displacement(0, 0.0, 0, 1, 0, 0, 0)
# rotation matrix hand in world frame
R_right_hand = numpy.matrix([[0, 0, -1],[0, -1, 0],[-1,0,0]])
o_right_hand = lgsm.Quaternion.fromMatrix(R_right_hand)
Weight_hand_task = 1.0
Weight_hand_task_or = 0.5
Task_hand_controlled_var = "RXYZ" # "RXYZ" "R" "XY" "Z" ..

# it is a frame task to displace the hand
touchWall_task = ctrl.createFrameTask("touchWall", rname+'.r_hand', H_hand_tool, "XYZ", w=Weight_hand_task, kp=36., pose_des=lgsm.Displacement([-0.25,0.15,waist_z+0.25]+o_right_hand.tolist()))

# it is a frame task to rotate the hand
touchWall_orient_task = ctrl.createFrameTask("touchWall_orient", rname+'.r_hand', H_hand_tool, "R", w=Weight_hand_task_or, kp=36., pose_des=lgsm.Displacement([-0.25,0.15,waist_z+0.25]+o_right_hand.tolist()))


## force task for touching the wall
# weight of the force task = 1.0 by default because we don't know how to weight it wrt the other tasks
Weight_force_task = 1.0
# create task
EETask = ctrl.createForceTask("EE", rname+".r_hand", H_hand_tool, w=Weight_force_task)
# update the task goal
# the desired force is expressed in the world frame
force_desired = lgsm.vector(0,0,0,-5.0,0,0) # mux, muy, muz, fx, fy,fz
is_expressed_in_world_frame = True
#EETask.update(force_desired, is_expressed_in_world_frame) -> API changed
EETask.setPosition(lgsm.Displacement()) #--> new "expressed in world frame"
EETask.setWrench(force_desired)
EETask.deactivate()



# if we want to transform a task into a constraint
# it will be a more priority task..... not a priori always verified, but..
#for n in ["CL"+str(s) for s in range(1,5)] + ["CR"+str(s) for s in range(1,5)]:
#    ctrl.s.activateTaskAsConstraint(n)

##### OBSERVERS

## OBSERVERS COM
cpobs = ctrl.add_updater(xic.observers.CoMPositionObserver(ctrl.getModel()))
fpobs = ctrl.add_updater(xic.observers.FramePoseObserver(ctrl.getModel(), rname+'.waist', lgsm.Displacement()))
obs_l_foot = ctrl.add_updater(xic.observers.FramePoseObserver(ctrl.getModel(), rname+'.l_foot', lgsm.Displacement()))
obs_r_foot = ctrl.add_updater(xic.observers.FramePoseObserver(ctrl.getModel(), rname+'.r_foot', lgsm.Displacement()))

## OBSERVERS ANKLE
all_joints_obs = ctrl.add_updater(xic.observers.JointPositionsObserver(ctrl.getModel()))

## OBSERVER MOVING WALL
tpobs = ctrl_moving_wall.add_updater(xic.observers.TorqueObserver(ctrl_moving_wall))


##### SIMULATE
ctrl.s.start()
ctrl_moving_wall.s.start()

# launch the simulation
wm.startAgents()
wm.phy.s.agent.triggerUpdate()

#import xdefw.interactive
#xdefw.interactive.shell_console()()

print "first sleep"

time.sleep(5.)

print "end sleep - change tasks" 

time.sleep(2.)

#backTask.deactivate()
EETask.activateAsObjective()

time.sleep(0.5)
touchWall_task.deactivate()

#time.sleep(5.)
time.sleep(15.)



wm.stopAgents()
ctrl.s.stop()
ctrl_moving_wall.s.stop()

##### RESULTS
comtraj = numpy.array(cpobs.get_record())
wtraj = numpy.array(fpobs.get_record())
jtraj = numpy.array(all_joints_obs.get_record())
rf_traj = numpy.array(obs_r_foot.get_record())
lf_traj = numpy.array(obs_l_foot.get_record())
tpos = tpobs.get_record()

pl.figure()
pl.plot(comtraj[:,0],label="com x")
pl.plot(comtraj[:,1],label="com y")
pl.plot(comtraj[:,2],label="com z")
pl.legend()
pl.savefig("results/02_touch_wall_5N_COM.pdf", bbox_inches='tight' )

#pl.figure()
#pl.plot(wtraj[:,0],label="waist x")
#pl.plot(wtraj[:,1],label="waist y")
#pl.plot(wtraj[:,2],label="waist z")
#pl.legend()

#pl.figure()
#pl.plot(rf_traj[:,0],label="right foot x")
#pl.plot(rf_traj[:,1],label="right foot y")
#pl.plot(rf_traj[:,2],label="right foot z")
#pl.legend()

#pl.figure()
#pl.plot(lf_traj[:,0],label="left foot x")
#pl.plot(lf_traj[:,1],label="left foot y")
#pl.plot(lf_traj[:,2],label="left foot z")
#pl.legend()

#pl.figure()
#pl.plot(jtraj[:,0]*rad2deg,label="0")
#pl.plot(jtraj[:,1]*rad2deg,label="1")
#pl.plot(jtraj[:,2]*rad2deg,label="2")
#pl.plot(jtraj[:,3]*rad2deg,label="3")
#pl.plot(jtraj[:,4]*rad2deg,label="4")
#pl.plot(jtraj[:,5]*rad2deg,label="5")
#pl.title("left leg")
#pl.legend()

#pl.figure()
#pl.plot(jtraj[:,26]*rad2deg,label="26")
#pl.plot(jtraj[:,27]*rad2deg,label="27")
#pl.plot(jtraj[:,28]*rad2deg,label="28")
#pl.plot(jtraj[:,29]*rad2deg,label="29")
#pl.plot(jtraj[:,30]*rad2deg,label="30")
#pl.plot(jtraj[:,31]*rad2deg,label="31")
#pl.legend()
#pl.title("right leg")

pl.figure()
pl.plot(tpos)
pl.legend()
pl.title("force on wall")
pl.savefig("results/02_touch_wall_5N_force.pdf", bbox_inches='tight' )

#the last to show all plots
pl.show()






