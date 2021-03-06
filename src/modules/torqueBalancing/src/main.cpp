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

#include <iostream>

#include <yarp/os/Network.h>
#include <yarp/os/ResourceFinder.h>

#include "TorqueBalancingModule.h"

#include <codyco/ModelParsing.h>

int main(int argc, char **argv)
{
    //initialize the network
    yarp::os::Network yarp;
    if (!yarp::os::Network::checkNetwork(5)) {
        std::cerr << "YARP network is not available" << std::endl;
        return -1;
    }

    yarp::os::ResourceFinder resourceFinder;
    
    resourceFinder.setVerbose(true);
    resourceFinder.setDefaultConfigFile("torqueBalancing.ini");         //default config file name.
    resourceFinder.setDefaultContext("torqueBalancing"); //when no parameters are given to the module this is the default context
    resourceFinder.configure(argc, argv);
    
    if (resourceFinder.check("help")) {
        std::cout<< "Possible parameters" << std::endl << std::endl;
        std::cout<< "\t--context          :Where to find a user defined .ini file within $ICUB_ROOT/app e.g. /adaptiveControl/conf" << std::endl;
        std::cout<< "\t--rate             :Period used by the module. Default set to 10ms." << std::endl;
        std::cout<< "\t--robot            :Robot name (icubSim or icub). Set to icub by default." << std::endl;
        std::cout<< "\t--local            :Prefix of the ports opened by the module. Set to the module name by default, i.e. adaptiveControl." << std::endl;
//        codyco::iCubPartVersionOptionsPrint();
        return 0;
    }

    //module and robot name can be moved inside paramhelp/similar class
    codyco::torquebalancing::TorqueBalancingModule mainModule;
    return mainModule.runModule(resourceFinder);
}
