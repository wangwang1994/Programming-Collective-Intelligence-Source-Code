critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 3.5},
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0,
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0},
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}
from math import sqrt
import pprint

#欧几里得相关度，就是距离的平方差，再开方得到一个开方值称为距离，最后用1加上这个值取倒数，
# 如果这个开方值很小的，证明这个距离很近，那么加上1再取倒数后，就越接近1

def sim_distance(prefs,person1,person2):
  # Get the list of shared_items
  si={}
  for item in prefs[person1]:
    if item in prefs[person2]: si[item]=1

  # if they have no ratings in common, return 0
  if len(si)==0: return 0

  # Add up the squares of all the differences
  sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
                      for item in prefs[person1] if item in prefs[person2]])
    # 上面这行代码需要自己多学习学习
  return 1/(1+sqrt(sum_of_squares))
# print(sim_distance(critics,'Lisa Rose','Gene Seymour'))


def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1

    # if they are no ratings in common, return 0
    if len(si) == 0: return 0

    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

    # Sum of the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # Calculate r (Pearson score)
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0

    r = num / den

    return r

# 下面的算法是找出与自己相似的人员，通过similarity选项可以选择不同的选择算法
# 参数n用来确定要找几个和自己相似的人员.
# Returns the best matches for person from the prefs dictionary.
# Number of results and similarity function are optional params.
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person]
    # 这个写法也值得注意，先是采用了一个函数，然后函数的变量在后面用for循环进行选择
    scores.sort()
    scores.reverse()
    return scores[0:n]


def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        # don't compare me to myself
        # 下面解释了从其他人开始找电影，首先上面的这个for循环就是选择其他人的
        # 过程，所以下面的continue就是指当选到了自己时，跳出当前的这个循环来
        # 选择后面的循环。
        if other == person: continue
        sim = similarity(prefs, person, other)
        #上面这行是计算当前这个人的相似度
        # ignore scores of zero or lower
        if sim <= 0: continue
        for item in prefs[other]:
        #相似度计算出来以后，这个other就是确定的了，所以能够
        # 开始对这个人的不同的电影进行评价，但是仅仅只评价，我自己
        # 还没有看过的电影，下面的代码实现这个功能。
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # Similarity * Score
                totals.setdefault(item, 0)
                #上面的代码，是先初始化key出来，将他的值设定为0
                # 下面这个才是对item的键进行初始化，即other这个人对
                # 他的评价值乘以我和other这个人的相似度。
                totals[item] += prefs[other][item] * sim
                # Sum of similarities
                # 下面的代码是对这种评价值乘以相似度的和的累加。
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # Create the normalized list
    rankings = [(total / simSums[item], item) for item, total in totals.items()]

    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings

# 下面这个是将评价者和物品的矩阵进行倒置，变成同一个物品，多个评价者对他的打分情况
def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            # Flip item and person
            result[item][person] = prefs[person][item]
    return result

def calculateSimilarItems(prefs,n=10):
  # Create a dictionary of items showing which other items they
  # are most similar to.
  result={}
  # Invert the preference matrix to be item-centric
  itemPrefs=transformPrefs(prefs)
  c=0
  for item in itemPrefs:
    # Status updates for large datasets
    c+=1
    if c%100==0: print ("%d / %d" % (c,len(itemPrefs)))
    # Find the most similar items to this one
    scores=topMatches(itemPrefs,item,n=n,similarity=sim_distance)
    result[item]=scores
  print(c)
  return result

pprint.pprint(calculateSimilarItems(critics))

# print(topMatches(critics,'Toby',n=1))
# print(getRecommendations(critics,'Toby'))