#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
'''
Vectorized (fast) implementation of the radiation model[1], the extended radiation model[2], and the gravity model with power and exponential law decay[3].

All implementations have a `slowMode` flag which, when true, calculates the results using a nested for loop (instead of in a vectorized manner).
We inlcude tests that assert the results of the vectorized implementation against the "slowMode" implementations.

[1] Simini, Filippo, et al. "A universal model for mobility and migration patterns." Nature 484.7392 (2012): 96-100.
[2] Yang, Yingxiang, et al. "Limits of Predictability in Commuting Flows in the Absence of Data for Calibration." Scientific Reports 4 (2014).
[3] Lenormand, Maxime, Aleix Bassolas, and José J. Ramasco. "Systematic comparison of trip distribution laws and models." Journal of Transport Geography 51 (2016): 158-169.
'''
import sys
import os
import time

import numpy as np

#-----------------------------------------------------------------------------------------------------------------------------------
# Misc methods
#-----------------------------------------------------------------------------------------------------------------------------------
def productionFunction(population, P, beta=0.03):
    return P * (population*beta)

def row_normalize(P):
    assert len(P.shape) == 2
    return P / P.sum(axis=1, keepdims=True)

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def extendedRadiationModel(origins, destinations, s, alpha, slowMode=False):
    assert len(origins.shape) == 2 and origins.shape[1] == 1, "`origins` and `destinations` must be 2D with a single column"
    assert len(destinations.shape) == 2 and destinations.shape[1] == 1, "`origins` and `destinations` must be 2D with a single column"

    n = origins.shape[0]
    m = destinations.shape[0]

    assert len(s.shape) == 2 and s.shape[0] == n and s.shape[1] == m, "`s` must be a square matrix with same length/width as the origin and destination features"

    origins = origins.astype(np.float)
    destinations = destinations.astype(np.float)
    P = np.zeros((n,m), dtype=float)

    if slowMode:
        for i in range(n):
            for j in range(m):
                numerator = ((origins[i] + destinations[j] + s[i,j])**alpha - (origins[i] + s[i,j])**alpha) * (origins[i]**alpha + 1)
                denominator = ((origins[i] + s[i,j])**alpha + 1) * ((origins[i] + destinations[j] + s[i,j])**alpha + 1)
                P[i,j] = numerator/denominator
    else:
        numerator = ((s + origins + destinations.T)**alpha - (s + origins)**alpha) * (origins**alpha + 1)
        denominator = ((s+origins)**alpha + 1) * ((s + origins  + destinations.T)**alpha + 1)
        P = np.divide(numerator,denominator)

    P[np.isnan(P) | np.isinf(P)] = 0.0
    assert not np.any(np.isnan(P))
    assert not np.any(np.isinf(P))

    return P

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def radiationModel(origins, destinations, s, slowMode=False):
    assert len(origins.shape) == 2 and origins.shape[1] == 1, "`origins` and `destinations` must be 2D with a single column"
    assert len(destinations.shape) == 2 and destinations.shape[1] == 1, "`origins` and `destinations` must be 2D with a single column"

    n = origins.shape[0]
    m = destinations.shape[0]

    assert len(s.shape) == 2 and s.shape[0] == n and s.shape[1] == m, "`s` must be a square matrix with same length/width as the origin and destination features"

    origins = origins.astype(np.float)
    destinations = destinations.astype(np.float)
    P = np.zeros((n,m), dtype=float)

    if slowMode:
        for i in range(n):
            for j in range(m):
                P[i,j] = (origins[i] * destinations[j]) / ((s[i,j] + origins[i]) * (s[i,j] + origins[i] + destinations[j]))
    else:
        numerator = np.dot(origins,destinations.T)
        denominator = (s + origins) * (s + origins + destinations.T) 
        
        P = np.divide(numerator,denominator)

    P[np.isnan(P) | np.isinf(P)] = 0.0
    assert not np.any(np.isnan(P))
    assert not np.any(np.isinf(P))

    return P

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def gravityModel(origins, destinations, d, alpha, decay="power", slowMode=False):
    assert len(origins.shape) == 2 and origins.shape[1] == 1, "`origins` and `destinations` must be 2D with a single column"
    assert len(destinations.shape) == 2 and destinations.shape[1] == 1, "`origins` and `destinations` must be 2D with a single column"

    n = origins.shape[0]
    m = destinations.shape[0]

    assert len(d.shape) == 2 and d.shape[0] == n and d.shape[1] == m, "`d` must be a square matrix with same length/width as the origin and destination features"

    assert decay in ["power", "exponential"], "`decay` must be either 'power' or 'exponential'"

    origins = origins.astype(np.float)
    destinations = destinations.astype(np.float)
    d = d.astype(np.float)

    P = np.zeros((n,m), dtype=float)

    if slowMode:
        for i in range(n):
            for j in range(m):
                if i!=j: # on the diagonal the distance matrix will be zero, so we ignore these
                    if decay=="power":
                        P[i,j] = (origins[i] * destinations[j]) / (d[i,j]**alpha)
                    elif decay=="exponential":
                        P[i,j] = (origins[i] * destinations[j]) / (np.exp(d[i,j]*alpha))                
    else:
        numerator = np.dot(origins,destinations.T)
        denominator = None
        if decay=="power":
            denominator = d**(alpha)
        elif decay=="exponential":
            denominator = np.exp(d*alpha)
        # the denominator will be 0 where d[i,j] == 0, causing a divide by zero error 
        mask = denominator==0 # record where there are 0's
        denominator[mask]=1.0 # set the 0's to 1.0, avoiding the divide by 0
        P = np.divide(numerator,denominator)
        P[mask] = 0.0 # set the results that would have been divided by 0, to 0

    P[np.isnan(P) | np.isinf(P)] = 0.0
    assert not np.any(np.isnan(P))
    assert not np.any(np.isinf(P))

    return P

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def getInterveningOpportunities(features, distanceMatrix, slowMode=False):
    assert len(features.shape) == 2
    assert features.shape[1] == 1

    n = features.shape[0]

    assert len(distanceMatrix.shape)==2
    assert distanceMatrix.shape[0] == distanceMatrix.shape[1]
    assert distanceMatrix.shape[0] == n

    S = np.zeros((n, n), dtype=np.float32)
    
    if slowMode:
        # Naively iterate over all locations, sort distances to others, assign intervening opportunities
        for i in range(n):
            otherPatches = []
            for j in range(n):
                otherPatches.append((distanceMatrix[i,j], j))
            otherPatches.sort(key=lambda x: x[0]) # this is a stable sort

            cumSum = 0.0
            for distance, j in otherPatches[1:]:
                S[i,j] = cumSum
                cumSum += features[j]
    else:
        # Very important that we use mergesort here as it is a stable sort
        d = np.argsort(distanceMatrix, kind="mergesort", axis=1)

        for i in range(n):
            tempFeatures = features[d[i]]
            newFeatures = [0,0] + list(np.cumsum(tempFeatures[1:-1]))
            S[i,d[i]] =  newFeatures

    return S


if __name__ == "__main__":
    pass