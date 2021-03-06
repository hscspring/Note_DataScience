critics = {'Lisa Rose' : {'Lady in the Water' : 2.5, 'Snakes on a Plane' : 3.5, 'Just My Luck' : 3.0,
						  'Superman Returns' : 3.5, 'You, Me and Dupree' : 2.5, 'The Night Listener' : 3.0},
		   'Gene Seymour': {'Lady in the Water' : 3.0, 'Snakes on a Plane' : 3.5, 'Just My Luck' : 1.5,
						  'Superman Returns' : 5.0, 'You, Me and Dupree' : 3.5, 'The Night Listener' : 3.0},
		   'Michael Phillips': {'Lady in the Water' : 2.5, 'Snakes on a Plane' : 3.0, 'Superman Returns' : 3.5,
		    					'The Night Listener' : 4.0},
		   'Claudia Puig': {'Snakes on a Plane' : 3.5, 'Just My Luck' : 3.0, 'The Night Listener' : 4.5,
						  'Superman Returns' : 4.0, 'You, Me and Dupree' : 2.5},
		   'Mick LaSalle': {'Lady in the Water' : 3.0, 'Snakes on a Plane' : 4.0, 'Just My Luck' : 2.0,
						  'Superman Returns' : 3.0, 'You, Me and Dupree' : 2.0, 'The Night Listener' : 3.0},
		   'Jack Matthews': {'Lady in the Water' : 3.0, 'Snakes on a Plane' : 4.0, 'The Night Listener' : 3.0, 
						  'Superman Returns' : 5.0, 'You, Me and Dupree' : 3.5},
		   'Toby': {'Snakes on a Plane' : 4.5, 'Superman Returns' : 4.0, 'You, Me and Dupree' : 1.0}}

from math import sqrt

def sim_distance(prefs, person1, person2):
    
    # get the goods list evaluated by both
	si = {}
    
    # list of goods(movies) evaluated by person1
	for item in prefs[person1]:
        # if the list of person1 is in the list of person2
		if item in prefs[person2]:
            # put the goods which are evaluated by each other into si, one by one with the loop
            # si is a dict, each value equal to 1
			si[item] = 1
	
	# if they are different, return 0
	if len(si) == 0: return 0
    
	# calculate sqrt of the sum
	sum_of_squares = sum([pow(prefs[person1][item]-prefs[person2][item],2)
						  for item in prefs[person1] if item in prefs[person2]])
    
	return 1/(1+sqrt(sum_of_squares))


def sim_pearson(prefs, p1, p2):
	
	# get the goods list evaluated by both
	si = {}
	for item in prefs[p1]:
		if item in prefs[p2] : si[item] = 1

	# get the number of the list
	n = len(si)
	
	# if both p1 and p2 do not get a same movie, return 1
	if n == 0 : return 1

	# sum of all prefers for both p1 and p2
	sum1 = sum([prefs[p1][it] for it in si])
	sum2 = sum([prefs[p2][it] for it in si])

	# sum of squares
	sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
	sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])

	# sum of products
	pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

	# calculate pearson value
	num = pSum - (sum1 * sum2) / n
	den = sqrt (( sum1Sq - pow(sum1, 2) / n ) * (sum2Sq - pow(sum2, 2) / n))
	if den == 0 : return 0

	r = num/den
	return r

# return the best match persons in the prefer dict
# return number and the similarity function are optional parameters
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores=[(similarity(prefs, person, other), other)
                   for other in prefs if other != person]
# sort the list from high to low
    scores.sort()
    scores.reverse()
    return scores[0:n]

# use the weighted average of others evaluated values to give advice to sb 
def getRecommendations(prefs, person, similarity=sim_pearson):
	totals = {}
	simSums = {}
	for other in prefs:
		# do not need to compare with the person himself
		if other == person : continue
		sim = similarity(prefs, person, other)

		# ignore values less or equal to 0
		if sim <=0 : continue
		for item in prefs[other]:

			# only evaluate those never seen
			if item not in prefs[person] or prefs[person][item] == 0:
				# similarity * evaluated values
				totals.setdefault(item, 0)
				totals[item] += prefs[other][item] * sim
				# sum of similarities
				simSums.setdefault(item, 0)
				simSums[item] += sim

	# create a normalized list 
	rankings = [(total/simSums[item], item) for item, total in totals.items()]

	# return sorted list
	rankings.sort()
	rankings.reverse()
	return rankings

def transformPrefs(prefs):
	result = {}
	for person in prefs:
		for item in prefs[person]:
			result.setdefault(item, {})
			# exchange person and things
			result[item][person] = prefs[person][item]
	return result

def calculateSimilarItems(prefs, n=10):
    
    # create dict, to present the nearest goods of these goods
    result = {}
    
    # tansform the pref by center of goods
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # for big data, update status variable
        c += 1
        if c%100 == 0:
            print "%d / %d" % (c, len(itemPrefs))
        # find the nearest goods
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result

def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    
    # loop goods of current user ever evaluated
    for (item, rating) in userRatings.items():
        
        # loop the nearest goods of current goods
        for (similarity, item2) in itemMatch[item]:
            
            # if user evaluated current good, ignore
            if item2 in userRatings: continue
                
            # sum score * similarity by weighted
            scores.setdefault(item2, 0)
            scores[item2] += similarity*rating
                
            # sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity
            
    # average
    rankings = [(score/totalSim[item], item) for item, score in scores.items()]
            
    # sort
    rankings.sort()
    rankings.reverse()
    return rankings

# get data
def loadMovieLens(path='data/'):
    
    # get title of movies
    movies={}
    for line in open(path+'movies.csv'):
        #(id,title)=line.split('|')[0:2]
        (id,title)=line.strip().split(',')[0:2]
        movies[id]=title
    
    # load data
    prefs={}
    for line in open(path+'ratings.csv'):
        (user,movieid,rating,ts)=line.strip().split(',')
        prefs.setdefault(user,{})
        prefs[user][movies[movieid]]=rating
    return prefs