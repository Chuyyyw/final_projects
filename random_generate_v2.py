# Xingnuo Duan

import numpy as np
import random
import math
import copy


def randomLoc(latLon, radius):
    """
    Generate one random point according to the given conditions.

    :param lonLat: the latitude and longitude of center. Tuple.
    :param radius: the radius for generating points randomly
    :return: location information, logitude and latitude.
    """
    lat = latLon[0]
    lon = latLon[1]
    r = radius/69 # / 111300 # if need some unit transform
    u = np.random.uniform(0, 1)
    v = np.random.uniform(0, 1)
    w = r * u # random radius of the point # r * np.sqrt(u) for uniformly on a disc
    t = 2 * np.pi * v
    x = w * np.cos(t)
    x1 = x / np.cos(lat)
    y = w * np.sin(t)
    return (lon + x1, lat + y)


def randomRole(d_num, obs):
    """
    randomly choose from driver and rider
    :param d_num: the number of users who choose driver
    :param obs: the number of observations to be generated
    :return: driver or rider
    """
    # TODO: to determine the frequencies, driver:0.4, rider:0.6
    roles = ['driver', 'rider']
    r_num = obs - d_num

    ind = [0] * d_num + [1] * r_num

    r = list(map(lambda x: roles[x], ind))
    random.shuffle(r)

    return r


def randomCenter(indexes, source_list, des_list) :
    """
    To generate the center of source point from four different location according to their frequencies.

    :param indexes: the index of the locations. Tuple.
    :param source_list: a list of source location latitude and logitude
    :param des_list: a list of destination location latitude and longitude
    :return: the longitude and latitude of source and destination. List of tuples.
    """

    source_idx = indexes[0]
    des_idx = indexes[1]

    source = source_list[source_idx]
    des = des_list[des_idx]


    return [source, des]


def randomSandD(obs, source_list, des_list):
    """
    To generate the indexes to extract from source location and destination for all the observations.
    To get same number of observations from each source location and same number of destination observations.
    :param source_list: a list of source location latitude and logitude
    :param des_list: a list of destination location latitude and longitude
    :param obs: number of observations to generate
    :return: latitude and longitude of source and destination. Two lists of tuples.
    """
    len_source = len(source_list)
    len_des = len(des_list)

    num_source = math.floor(obs/len_source)
    num_des = math.floor(obs/len_des)

    s_list = list(range(len_source)) * num_source
    d_list = list(range(len_des)) * num_des

    if len(s_list) != obs:
        res = abs(obs - len(s_list))
        ran = random.choices(s_list, k = res)
        s_list = s_list + ran

    if len(d_list) != obs:
        res = abs(obs-len(d_list))
        ran = random.choices(d_list, k = res)
        d_list = d_list + ran


    random.shuffle(s_list)
    random.shuffle(d_list)


    sAndD = list(zip(s_list, d_list))

    randCenter = list(map(lambda x: randomCenter(x, source_list, des_list), sAndD))

    randSource = list(map(lambda x: randomLoc(x[0], 0.5), randCenter))
    randDes = list(map(lambda x: randomLoc(x[1], 3), randCenter))

    return randSource, randDes

"""
# TODO: need to be imporved.

def sumPossibility(slotDict, slotIdxSeg):
    """
    A function to calculate the possibilities of each choice of indexes.
    subsets of slots as keys, possibilies as values.
    :param slotDict: A dictionary containing the possibilities for each slot
    :param slotIdxSeg: One choice of slots. List of integers.
    :return: Possibility of the choice. A number.
    """

    poss = sum(list(map(lambda x: slotDict[x], slotIdxSeg)))

    return poss
"""

def subSetLObs(slotDict, length, obsL, subsetL):
    """
    Calculate the possibility of each subset having same length.

    :param slotDict: a dictionary containing the possibilities for each slot
    :param subsetL: all the subsets with same length that are available
    :param length: the length of elements in subsetL
    :param obsL: the number of observations to get from this length of subsets
    :return: a list of paired up subsets and their possibilities
    """
    # random choose subsets from the distribution
    subAll = []
    slots = list(slotDict.keys())
    p = list(slotDict.values())
    for i in range(int(obsL**2)):
        a = list(np.random.choice(slots, length, p))
        a.sort()
        subAll.append(a)

    subAll = list(filter(lambda x: len(x) == length, subAll))
    subAll = list(filter(lambda x: max(x) - min(x) + 1 == len(x), subAll))

    l_num = list(map(lambda x: int(obsL*subAll.count(x)/len(subAll)), subsetL))

    return l_num




def randomSlots(slotDict, numDict, obs):
    """
    A function to randomly generate the time slots user chose.
    1. get all the subsets of the slots
    2. get rid of the subsets whose length is longer than maxNum
    3. get rid of the subsets whose slots are not continuous
    4. get the possibilities1 of each choice within different lengths of subsets, then scale them
    5. multiply the slots number preference possibilities2 with possibilities1 to get the final possibilities for each
       remaining subset
    6. generate slots with the new frequencies

    :param slotDict: a dictionary containing the possibilities for each slot
    :param numDict: a dictionary containing the possibilities for each number of slots
    :return: the list of slots. List.
    """
    # step 1: subsets
    nums = list(range(len(slotDict)))
    subsets = [[]]

    for n in nums:
        prev = copy.deepcopy(subsets)
        [k.append(n) for k in subsets]
        subsets.extend(prev)

    # step 2
    max_num = max(numDict.keys())
    subsets = list(filter(lambda x: len(x) <= max_num and len(x) != 0, subsets))

    # step 3
    subsets = list(filter(lambda x: max(x) - min(x) + 1 == len(x), subsets))

    # step 4 & step 5 & step 6
    """
    posses = list(map(lambda x: round(sumPossibility(slotDict, x), 3), subsets))
    pair_list = list(zip(subsets, posses))
    l_list = list(map(len, subsets))
    """
    clusters = []

    for l in range(1, max_num+1):
        p_choice = numDict[l]
        obs_choice = p_choice*obs
        subsetL = list(filter(lambda x: len(x) == l, subsets))
        """
        idx = [i for i, val in enumerate(l_list) if val == l]
        sub = [pair_list[i][0] for i in idx]
        poss = [pair_list[i][1] for i in idx]
        s = sum(poss)
        l_num = list(map(lambda x: int(round((x/s)*p_choice, 5)*obs), poss))
        """
        l_num = subSetLObs(slotDict, l, obs_choice, subsetL)

        if sum(l_num) > obs_choice:
            res = sum(l_num) - obs_choice
            n = int(math.floor(res/len(l_num)))
            fix = [n]*(len(l_num)-1)
            fix.extend([res - n*(len(l_num))])
            l_num = list(np.array(l_num)-np.array(fix))
        if sum(l_num) < obs_choice:
            res = abs(sum(l_num) - obs_choice)
            n = int(math.floor(res / len(l_num)))
            fix = [n] * (len(l_num) - 1)
            fix.extend([res - n * (len(l_num))])
            l_num = list(np.array(l_num) + np.array(fix))

        l_num = list(map(int, l_num))

        newlist = list(zip(subsetL, l_num))
        cluster = list(map(lambda x: [x[0]]*x[1], newlist))
        flat_cluster = [item for sublist in cluster for item in sublist]

        clusters.extend(flat_cluster)

    if len(clusters) < obs:
        res = abs(len(clusters) - obs)
        l_res = random.choices(clusters, k = res)
        clusters.extend(l_res)
    if len(cluster) > obs:
        res = abs(len(clusters) - obs)
        l_res = random.choices(clusters, k = res)
        [clusters.remove(x) for x in l_res]


    random.shuffle(clusters)
    return clusters


def outTxt(obs, d_num, source_list, des_list, slotDict, numDict, iterId):
    """
    Output the random variables generated for one trail.

    :param obs: number of observations
    :param d_num: number of drivers, determined by binomial random generation process
    :param source_list: list of source locations
    :param des_list: list of destination locations
    :param slotDict: dictionary of time slot and possibilities
    :param numDict: dictionary of length of slots and possibilities
    :param iterId: the id of the trail, which is mainly used to generate the file name
    """
    roleL = randomRole(d_num, obs)
    slotL = randomSlots(slotDict, numDict, obs)
    sourceL, desL = randomSandD(obs, source_list, des_list)
    print('output%s.txt has been output.'%iterId)

    output = open('output%s.txt' %iterId, 'w+')
    output.write('{0:<5} | '.format('id') + '{0:<7} | '.format('role') + '{0:<30} | '.format('slots')
                     + '{0:<40} | '.format('source') + '{0:<40} | '.format('destination') + '\n')
    for i in range(obs):
        output.write('{0:<5} | '.format(i+1) + '{0:<7} | '.format(roleL[i]) + '%30s | ' % slotL[i]
                     + '{} | '.format(sourceL[i]) + '{} | '.format(desL[i]) + '\n')
    output.close()


def dynamicOut(obs, d_freq, source_list, des_list, slotDict, numDict, iterNum):
    """

    A function to dynamically generate files for the random variables processes, with sequence names.

    :param obs: number of observations
    :param d_num: number of drivers, determined by binomial random generation process
    :param source_list: list of source locations
    :param des_list: list of destination locations
    :param slotDict: dictionary of time slot and possibilities
    :param numDict: dictionary of length of slots and possibilities
    :param iterNum: number of trails to be condected
    """

    d_num = list(np.random.binomial(obs, d_freq, iterNum))

    for i in range(iterNum):
        iterId = i+1
        outTxt(obs, d_num[i], source_list, des_list, slotDict, numDict, iterId)



users = []

# assign same number of observations to each source and destination location
# (latitude, longitude)
# radius = 3
destination = [(37.468319, -122.143936), (37.386051, -122.083855), (37.487846, -122.236115)]
# radius = 0.5
source = [(37.558153, -122.006811), (37.557710, -121.977105), (37.532314, -121.953163), (37.501887, -121.939521)]

p = [0.002, 0.003, 0.025, 0.03, 0.06, 0.055, 0.11, 0.10, 0.17, 0.14, 0.15, 0.10, 0.04, 0.01, 0.003, 0.002]
slots = list(range(len(p)))
slotDict = dict(zip(slots, p))

preference = [0.1, 0.2, 0.25, 0.25, 0.1, 0.05, 0.025, 0.025]
choice = list(range(1, len(preference)+1))
numDict = dict(zip(choice, preference))

"""
# a = randomSandD(100000, source, destination)
# s = list(map(lambda x: randomCenter(x, source, destination), a))
# print(type(s))

r = randomRole(0.4, 100)
# print(r)

s, d = randomSandD(100, source, destination)
# print(s)
# print(d)

slot = randomSlots(slotDict, numDict, 100)
# print(slot)
"""

dynamicOut(1000, 0.4, source, destination, slotDict, numDict, 10)

"""

all the functions return all the random variables at once
have to iterate through them to assign them to the users
"""

