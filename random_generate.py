import numpy as np
import random
import math
import copy


def randomLoc(lonLat, radius):
    """
    Generate one random point according to the given conditions.

    :param lonLat: the longitude and latitude of center. Tuple.
    :param radius: the radius for generating points randomly
    :return: location information, logitude and latitude.
    """
    lon = lonLat[1]
    lat = lonLat[2]
    r = radius # / 111300 # if need some unit transform
    u = np.random.uniform(0, 1)
    v = np.random.uniform(0, 1)
    w = r * u # random radius of the point # r * np.sqrt(u) for uniformly on a disc
    t = 2 * np.pi * v
    x = w * np.cos(t)
    x1 = x / np.cos(lat)
    y = w * np.sin(t)
    return lon + x1, lat + y


def randomRole(d_freq, obs):
    """
    randomly choose from driver and rider
    :param d_freq: the frequency of users who choose driver
    :param obs: the number of observations to be generated
    :return: driver or rider
    """
    # TODO: to determine the frequencies, driver:0.4, rider:0.6
    roles = ['driver', 'rider']
    d_num = obs*d_freq
    r_num = obs*(1-d_freq)

    ind = [0] * d_num + [1] * r_num

    return list(map(lambda x: roles[x], ind))



def randomSandD(obs, source_list, des_list):
    """
    To generate the indexes to extract from source location and destination for all the observations.
    To get same number of observations from each source location and same number of destination observations.
    :param source_list: a list of source location latitude and logitude
    :param des_list: a list of destination location latitude and longitude
    :param obs: number of observations to generate
    :return: indeces of source and destination. List of tuples.
    """
    len_source = len(source_list)
    len_des = len(des_list)

    num_source = math.floor(obs/len_source)
    num_des = math.floor(obs/len_des)

    source_list = list(range(len_source)) * num_source
    des_list = list(range(len_des)) * num_des

    if len(source_list) != obs:
        res = abs(obs - len(source_list))
        ran = random.sample(source_list, res)
        source_list = source_list + ran

    if len(des_list) != obs:
        res = abs(obs-len(des_list))
        ran = random.sample(des_list, res)
        des_list = des_list + ran


    random.shuffle(source_list)
    random.shuffle(des_list)

    return list(zip(source_list, des_list))



def randomCenter(indexes, source_list, des_list) :
    """
    To generate the center of source point from four different location accroding to their frequencies.

    :param index: the index of the locations. Tuple.
    :param source_list: a list of source location latitude and logitude
    :param des_list: a list of destination location latitude and longitude
    :return: the longitude and latitude of source and destination. Two tuples.
    """

    source_idx = indexes[0]
    des_idx = indexes[1]

    source = source_list[source_idx]
    des = des_list[des_idx]

    return source, des


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
    posses = list(map(lambda x: round(sumPossibility(slotDict, x), 3), subsets))
    pair_list = list(zip(subsets, posses))
    l_list = list(map(len, subsets))
    clusters = []

    for l in range(1, max_num+1):
        p_choice = numDict[l]
        obs_choice = p_choice*obs
        idx = [i for i, val in enumerate(l_list) if val == l]
        sub = [pair_list[i][0] for i in idx]
        poss = [pair_list[i][1] for i in idx]
        s = sum(poss)
        l_num = list(map(lambda x: int(round((x/s)*p_choice, 5)*obs), poss))

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

        newlist = list(zip(sub, l_num))
        cluster = list(map(lambda x: [x[0]]*x[1], newlist))
        flat_cluster = [item for sublist in cluster for item in sublist]

        clusters.extend(flat_cluster)

    if len(clusters) < obs:
        res = abs(len(clusters) - obs)
        l_res = random.sample(clusters, res)
        clusters.extend(l_res)
    if len(cluster) > obs:
        res = abs(len(clusters) - obs)
        l_res = random.sample(clusters, res)
        [clusters.remove(x) for x in l_res]


    random.shuffle(clusters)
    return clusters




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


a = randomSandD(100000, source, destination)
s = list(map(lambda x: randomCenter(x, source, destination), a))
print(type(s))


"""

all the functions return all the random variables at once
have to iterate through them to assign them to the users
"""

