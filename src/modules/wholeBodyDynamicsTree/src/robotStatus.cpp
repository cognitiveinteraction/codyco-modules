/*
 * Copyright (C) 2014 RobotCub Consortium, European Commission FP6 Project IST-004370
 * Author: Silvio Traversaro
 * email:  silvio.traversaro@iit.it
 * website: www.icub.org
 * Permission is granted to copy, distribute, and/or modify this program
 * under the terms of the GNU General Public License, version 2 or any
 * later version published by the Free Software Foundation.
 *
 * A copy of the license can be found at
 * http://www.robotcub.org/icub/license/gpl.txt
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
 * Public License for more details
*/

#include "wholeBodyDynamicsTree/robotStatus.h"

#include <iCub/iDynTree/yarp_kdl.h>

#include <wbi/iWholeBodySensors.h>

RobotJointStatus::RobotJointStatus(int nrOfDOFs)
{
    setNrOfDOFs(nrOfDOFs);

    this->zero();
}

bool RobotJointStatus::setNrOfDOFs(int nrOfDOFs)
{

    qj.resize(nrOfDOFs);
    dqj.resize(nrOfDOFs);
    ddqj.resize(nrOfDOFs);
    torquesj.resize(nrOfDOFs);

    qj_kdl.resize(nrOfDOFs);
    dqj_kdl.resize(nrOfDOFs);
    ddqj_kdl.resize(nrOfDOFs);
    torquesj_kdl.resize(nrOfDOFs);

    return zero();
}

bool RobotJointStatus::zero()
{
    qj.zero();
    dqj.zero();
    ddqj.zero();
    torquesj.zero();

    SetToZero(qj_kdl);
    SetToZero(dqj_kdl);
    SetToZero(ddqj_kdl);
    SetToZero(torquesj_kdl);

    return true;
}

bool RobotJointStatus::setJointPosYARP(const yarp::sig::Vector& _qj)
{
    qj = _qj;
    return YarptoKDL(qj,qj_kdl);
}

bool RobotJointStatus::setJointVelYARP(const yarp::sig::Vector& _dqj)
{
    dqj = _dqj;
    return YarptoKDL(dqj,dqj_kdl);
}

bool RobotJointStatus::setJointAccYARP(const yarp::sig::Vector& _ddqj)
{
    ddqj = _ddqj;
    return YarptoKDL(ddqj,ddqj_kdl);
}

bool RobotJointStatus::setJointTorquesYARP(const yarp::sig::Vector& _torquesj)
{
    torquesj = _torquesj;
    return YarptoKDL(torquesj,torquesj_kdl);
}


bool RobotJointStatus::setJointPosKDL(const KDL::JntArray& _qj)
{
    qj_kdl = _qj;
    return KDLtoYarp(qj_kdl,qj);
}

bool RobotJointStatus::setJointVelKDL(const KDL::JntArray& _dqj)
{
    dqj_kdl = _dqj;
    return KDLtoYarp(dqj_kdl,dqj);
}

bool RobotJointStatus::setJointAccKDL(const KDL::JntArray& _ddqj)
{
    ddqj_kdl = _ddqj;
    return KDLtoYarp(ddqj_kdl,ddqj);
}

bool RobotJointStatus::setJointTorquesKDL(const KDL::JntArray& _torquesj)
{
    torquesj_kdl = _torquesj;
    return KDLtoYarp(torquesj_kdl,torquesj);
}

KDL::JntArray& RobotJointStatus::getJointPosKDL()
{
    return qj_kdl;
}

KDL::JntArray& RobotJointStatus::getJointVelKDL()
{
    return dqj_kdl;
}

KDL::JntArray& RobotJointStatus::getJointAccKDL()
{
    return ddqj_kdl;
}

KDL::JntArray& RobotJointStatus::getJointTorquesKDL()
{
    return torquesj_kdl;
}

const yarp::sig::Vector& RobotJointStatus::getJointPosYARP() const
{
    return qj;
}

const yarp::sig::Vector& RobotJointStatus::getJointVelYARP() const
{
    return dqj;
}

const yarp::sig::Vector& RobotJointStatus::getJointAccYARP() const
{
    return ddqj;
}

const yarp::sig::Vector& RobotJointStatus::getJointTorquesYARP() const
{
    return torquesj;
}

bool RobotJointStatus::updateYarpBuffers()
{
    bool ok = true;
    ok = ok && KDLtoYarp(qj_kdl,qj);
    ok = ok && KDLtoYarp(dqj_kdl,dqj);
    ok = ok && KDLtoYarp(ddqj_kdl,ddqj);
    ok = ok && KDLtoYarp(torquesj_kdl,torquesj);
	return ok;
}



RobotSensorStatus::RobotSensorStatus(int nrOfFTSensors)
{
    setNrOfFTSensors(nrOfFTSensors);

    this->zero();
}


bool RobotSensorStatus::zero()
{
    domega_imu.zero();
    omega_imu.zero();
    proper_ddp_imu.zero();
    wbi_imu.zero();
    for(unsigned int i=0; i < estimated_ft_sensors.size(); i++ ) {
        estimated_ft_sensors[i].zero();
        measured_ft_sensors[i].zero();
        ft_sensors_offset[i].zero();
        model_ft_sensors[i].zero();
    }
    return true;
}

bool RobotSensorStatus::setNrOfFTSensors(int nrOfFTsensors)
{
    domega_imu.resize(3);
    omega_imu.resize(3);
    proper_ddp_imu.resize(3);
    wbi_imu.resize(wbi::sensorTypeDescriptions[wbi::SENSOR_IMU].dataSize);

    estimated_ft_sensors.resize(nrOfFTsensors,yarp::sig::Vector(6,0.0));
    measured_ft_sensors.resize(nrOfFTsensors,yarp::sig::Vector(6,0.0));
    ft_sensors_offset.resize(nrOfFTsensors,yarp::sig::Vector(6,0.0));
    model_ft_sensors.resize(nrOfFTsensors,yarp::sig::Vector(6,0.0));
    zero();
    return true;
}
