add_subdirectory(wholeBodyDynamicsTree)
add_subdirectory(wholeBodyGaze)
add_subdirectory(adaptiveControl)
#add_subdirectory(staticInertiaIdentification)
if(NOT MSVC)
add_subdirectory(insituFTSensorCalibration)
endif()
add_subdirectory(codycoDemoY2/app)
add_subdirectory(torqueGraspManager)
add_subdirectory(eventRepeater)

if(${CODYCO_USES_EIGEN_320})
   add_subdirectory(locomotionControl)
   add_subdirectory(locomotionPlanner)
   add_subdirectory(torqueBalancing)
   #add_subdirectory(motorFrictionExcitation)
   #add_subdirectory(motorFrictionIdentification)
   add_subdirectory(wholeBodyReach)
endif()

add_subdirectory(walkPlayer)

add_subdirectory(codycoCoordinatorDemoY1)
if(NOT MSVC)
add_subdirectory(codycoTrajGenDemoY2)
endif()
add_subdirectory(graspAndStepDemo)

#add_subdirectory(wholeBodyNeckVelocity)
