/* 
 * Copyright (C) 2013 CoDyCo
 * Author: Andrea Del Prete
 * email:  andrea.delprete@iit.it
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

#include <motorFrictionIdentification/recursiveLinearEstimator.h>

using namespace Eigen;
using namespace motorFrictionIdentification;

RecursiveLinearEstimator::RecursiveLinearEstimator(unsigned int nParam) 
    : n(nParam), R(n)
{ 
    resizeAllVariables();
}

/*************************************************************************************************/
void RecursiveLinearEstimator::feedSample(const VectorXd &input, const double &output)
{
    assert(checkDomainSize(input));
    ///< update the Cholesky decomposition of the inverse covariance matrix
    R.rankUpdate(input);
    ///< update the right hand side of the equation
    b += input*output;
}

/*************************************************************************************************/
void RecursiveLinearEstimator::predictOutput(const VectorXd &input, double &output) const
{
    assert(checkDomainSize(input));
    output = input.dot(x);
}

/*************************************************************************************************/
void RecursiveLinearEstimator::getCurrentParameterEstimate(VectorXd &xEst) const
{
    assert(checkDomainSize(xEst));
    xEst = x;
}

/*************************************************************************************************/
void RecursiveLinearEstimator::updateParameterEstimation()
{
    x = b;
    bool res = R.solveInPlace(x);
    assert(res);
}

/*************************************************************************************************/
void RecursiveLinearEstimator::resizeAllVariables()
{
    R.setZero();
    b.resize(n);
    b.setZero();
    x.resize(n);
    x.setZero();
}