/**
 * Copyright (C) 2014 CoDyCo
 * @author: Francesco Romano
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

#include "MinimumJerkTrajectoryGenerator.h"
#include <iCub/ctrl/minJerkCtrl.h>
#include <yarp/sig/Vector.h>

namespace codyco {
    namespace torquebalancing {
        
        MinimumJerkTrajectoryGenerator::MinimumJerkTrajectoryGenerator(int dimension)
        : m_size(dimension)
        , m_minimumJerkGenerator(0)
        , m_computedPosition(m_size)
        , m_sampleTime(0.01)
        , m_duration(1)
        , m_yarpReference(0)
        , m_yarpInitialValue(0)
        {
            m_minimumJerkGenerator = new iCub::ctrl::minJerkTrajGen(m_size, m_sampleTime, m_duration); //fake parameters for time and duration. They are reset on the initializeTimeParameter method
            m_yarpReference = new yarp::sig::Vector(m_size);
            m_yarpInitialValue = new yarp::sig::Vector(m_size);
        }
        
        MinimumJerkTrajectoryGenerator::~MinimumJerkTrajectoryGenerator()
        {
            if (m_minimumJerkGenerator) {
                delete m_minimumJerkGenerator;
                m_minimumJerkGenerator = 0;
            }
            if (m_yarpReference) {
                delete m_yarpReference;
                m_yarpReference = 0;
            }
            if (m_yarpInitialValue) {
                delete m_yarpInitialValue;
                m_yarpInitialValue = 0;
            }
        }
        
        ReferenceFilter* MinimumJerkTrajectoryGenerator::clone() const
        {
            ReferenceFilter* newObject = new MinimumJerkTrajectoryGenerator(m_size);
            newObject->initializeTimeParameters(m_sampleTime, m_duration);
            return newObject;
        }
        
        bool MinimumJerkTrajectoryGenerator::initializeTimeParameters(double sampleTime,
                                                                      double duration)
        {
            if (!m_minimumJerkGenerator) return false;
            m_sampleTime = sampleTime;
            m_duration = duration;
            bool result;
            result = m_minimumJerkGenerator->setT(duration);
            result = result && m_minimumJerkGenerator->setTs(sampleTime);
            return result;
        }
        
        bool MinimumJerkTrajectoryGenerator::computeReference(const Eigen::VectorXd& setPoint,
                                                              const Eigen::VectorXd& currentValue,
                                                              double /*initialTime*/)
        {
            if (!m_minimumJerkGenerator || !m_yarpReference || !m_yarpInitialValue) return false;
            if (setPoint.size() != m_size || currentValue.size() != m_size) return false;
            
            for (int i = 0; i < m_size; i++) {
                (*m_yarpReference)(i) = setPoint(i);
                (*m_yarpInitialValue)(i) = currentValue(i);
            }
            m_minimumJerkGenerator->init(*m_yarpInitialValue);
            return true;
        }
        
        Eigen::VectorXd MinimumJerkTrajectoryGenerator::getValueForCurrentTime(double /*currentTime*/)
        {
            if (!m_minimumJerkGenerator || !m_yarpReference) return Eigen::VectorXd::Zero(m_size);
            
            m_minimumJerkGenerator->computeNextValues(*m_yarpReference);
            yarp::sig::Vector yarpPosition = m_minimumJerkGenerator->getPos();
            for (int i = 0; i < m_size; i++) {
                m_computedPosition(i) = yarpPosition(i);
            }
            return m_computedPosition;
        }
                
    }
}
