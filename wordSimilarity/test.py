from nltk.corpus import wordnet as wn
import argparse

def parseWords(text):
	words = text.split()

	if(len(words)!=2):
		return None
	else:
		return words

def parseLine(line):    
	data= (line.strip()).split(",")

	try:
		data[2] = float(data[2])
		return data
	except ValueError:        
		return None

def computeDepth(sense):
	counter=0    
	hyper=sense.hypernyms()
	
	while(len(hyper) > 0):
			
			if(len(hyper) > 0):
				hyper=hyper[0].hypernyms()
				counter+=1
			else:
				hyper=[]

	return counter

def computeDepthMin(sense, counter):    
	hypers=sense.hypernyms()

	if(len(hypers)==0):
		return counter
	else:
		depths=[]
		for hyper in hypers:
			counter+=1
			depths.append(computeDepthMin(hyper, counter))

		return min(depths)


#def writeOutput(outputfile, words, correlations):

"""def WuPalmer(words):
	senses1 = wn.synsets(words[0])
	senses2 = wn.synsets(words[1])
	
	max = 0
	#bestSimilar = None

	for sense1 in senses1:
		for sense2 in senses2:
			commonParentDepth = computeCommonParentDepth(sense1, sense2)
			depthSum = computeDepth(sense1) + computeDepth(sense2)
			wupalmValue = 2 * commonParentDepth / depthSum

			if(wupalmValue > max):
				#bestSimilar = [sense1, sense2]
				max = wupalmValue

	return max"""

"""def computeSimilarity(words):
	similarity = []

   similarity.append(WuPalmer(words))
   similarity.append(shortestPath(words))
   similarity.append(LeacockChodorow(words))

	return similarity"""

#def computeCorrelations(similarity, correctValue):

"""
def computeSimilarityFile(inputname, outputname):    
	
	with open(inputname, 'r') as inputfile:
		with open(outputname, 'w') as outputfile:
			for line in lines:
				data = parseLine(line)
				
				if(data != None):
					similarity = computeSimilarity(data[0:2])
					correlations = computeCorrelations(similarity, data[3])
					writeOutput(outputfile, data[0:2], correlations)
"""

def checkHyperonims(sense1, sense2, hyper1, hyper2):
	if(sense1 in hyper2):
		print("uno iperonimo altro ", sense1)
		return True
	elif (sense2 in hyper1):
		print("uno iperonimo altro ", sense2)
		return True
	else:
		for hyper in hyper1:
			if(hyper in hyper2):
				print("iperonimo in comune ", hyper)
				return True
		return False

def computeCommonParentDepth(sense1, sense2, depth1, depth2): #si assume che i sensi abbiano sempre un antenato comune
	print(sense1, sense2)
	print(depth1, depth2)
	if(depth1 == 0 or depth2 == 0):
		return 0

	hyper1=sense1.hypernyms()
	hyper2=sense2.hypernyms()

	#controllo se un senso e iperonimo dell'altro o se hanno iperonimi in comune
	#se è verficata la condizione restuisco:
	#   primo caso i due sensi hanno un iperonimo comune
	#   secondo caso uno è iperonimo dell'altro
	if(checkHyperonims(sense1, sense2, hyper1, hyper2)):
		return depth1 - 1 if depth1 == depth2 else min(depth1, depth2)
	else:
		depths = []

		if(depth2 > depth1):          #salgo con il senso 2
			for hyper in hyper2:
				depths.append(computeCommonParentDepth(sense1, hyper, depth1, depth2-1))
		elif(depth1 > depth2):        #salgo con il senso 1
			for hyper in hyper1:
				depths.append(computeCommonParentDepth(hyper, sense2, depth1-1, depth2))
		else:                         #salgo con entrambi
			for hyp1 in hyper1:
				for hyp2 in hyper2:
					depths.append(computeCommonParentDepth(hyp1, hyp2, depth1-1, depth2-1))                

		#print(depths)
		if depths == []: #non ci sono iperonimi in comune in questo cammino
			return -1
		else:
			#return 1000 if all(d==1000 for d in depths) else max(d for d in depths if d < 1000)
			return -1 if all(d<0 for d in depths) else max(depths)

def computeCommonParentDepthSimple(sense1, sense2, depth1, depth2): #si assume che i sensi abbiano sempre un antenato comune

	if(depth1 == 0 or depth2 == 0):
		return 0

	hyper1=sense1.hypernyms()
	hyper2=sense2.hypernyms()

	#controllo se un senso e iperonimo dell'altro o se hanno iperonimi in comune
	#se è verficata la condizione restuisco:
	#   primo caso i due sensi hanno un iperonimo comune
	#   secondo caso uno è iperonimo dell'altro
	if(checkHyperonims(sense1, sense2, hyper1, hyper2)):
		return depth1 - 1 if depth1 == depth2 else min(depth1, depth2)
	
	depth = 0

	if(depth2 > depth1):          #salgo con il senso 2
		depth=computeCommonParentDepth(sense1, hyper2[0], depth1, depth2-1)
	elif(depth1 > depth2):        #salgo con il senso 1
		depth=computeCommonParentDepth(hyper1[0], sense2, depth1-1, depth2)
	else:                         #salgo con entrambi
		depth=computeCommonParentDepth(hyper1[0], hyper2[0], depth1-1, depth2-1)

	return depth

def checkCommonsIterative(senses1, senses2, depth): # true se c'è intersezione tra gli iperonimi di questo livello
	intersection = set(senses1["all"]).intersection(senses2["all"])
	#print("hyper 1", hyper1["all"])
	#print("hyper 2", hyper2["all"])
	print("Intersezione", intersection)
	return len(intersection) > 0

def addLevelDown(hypos):
	newHypos = []
	
	for hyp in hypos:
		newHypos.extend(hyp.hyponyms())

	return newHypos

def addLevelUp(hypers):
	newHypers = []
	
	for hyp in hypers:
		newHypers.extend(hyp.hypernyms())
	
	return newHypers

def levelingDown(sense1, sense2, depth1, depth2):
	hypos1 = {}
	hypos2 = {}

	hypos1[depth1] = [sense1]
	hypos2[depth2] = [sense2]

	if(depth1 > depth2):
		depth2 += 1
		hypos2[depth2] = sense2.hyponyms()
		hypos2["all"] = hypos2[depth2]
		hypos1["all"] = []
	else:
		depth1 += 1
		hypos1[depth1] = sense1.hyponyms()
		hypos1["all"] = hypos1[depth1]
		hypos2["all"] = []
	
	while(depth1 > depth2 or depth1 < depth2):
		if(depth2 < depth1):        #salgo con il senso 2            
			hypos2[depth2+1] = addLevelDown(hypos2[depth2])
			depth2+=1

			hypos2["all"].extend(hypos2[depth2])
		else:                       #salgo con il senso 1            
			hypos1[depth1+1] = addLevelDown(hypos1[depth1])
			depth1+=1

			hypos1["all"].extend(hypos1[depth1])
			
	
	return hypos1, hypos2, depth1, depth2

def levelingUp(sense1, sense2, depth1, depth2): #i dizionari con le profondità servono per capire su chi fare iperonimi o iponimi
	hyper1 = {}
	hyper2 = {}

	hyper1[depth1] = [sense1]
	hyper2[depth2] = [sense2]

	if(depth1 < depth2):
		depth2 -= 1
		hyper2[depth2] = sense2.hypernyms()
		hyper2["all"] = hyper2[depth2]
		hyper1["all"] = []
	else:
		depth1 -= 1
		hyper1[depth1] = sense1.hypernyms()
		hyper1["all"] = hyper1[depth1]
		hyper2["all"] = []
	
	while(depth1 > depth2 or depth1 < depth2):
		if(depth2 > depth1):        #salgo con il senso 2
			hyper2[depth2-1] = addLevelUp(hyper2[depth2])
			depth2-=1
			
			hyper2["all"].extend(hyper2[depth2])
		else:                       #salgo con il senso 1            
			hyper1[depth1-1] = addLevelUp(hyper1[depth1])
			depth1-=1

			hyper1["all"].extend(hyper1[depth1])
			
	return hyper1, hyper2, depth1, depth2

def computeCommonParentDepthIterative(sense1, sense2, depth1, depth2):
	print("PAR {} {}".format(depth1,depth2))
	if(sense1 == sense2):
		return depth1

	if(depth1 == 0 or depth2 == 0):
		return 0

	hyper1, hyper2, depth1, depth2 = levelingUp(sense1, sense2, depth1, depth2)    

	if (sense1 in hyper2["all"] or sense2 in hyper1["all"]): #controllo un senso è iperonimo dell'altro le profondità a questo punto sono uguali
		return depth1
	else:
		while(not checkCommonsIterative(hyper1, hyper2, depth1) and depth1 > 0):

			hyper1[depth1-1] = addLevelUp(hyper1[depth1])
			hyper1["all"].extend(hyper1[depth1-1])

			hyper2[depth1-1] = addLevelUp(hyper2[depth1])
			hyper2["all"].extend(hyper2[depth1-1])
			
			depth1-=1
	
	if(not checkCommonsIterative(hyper1, hyper2, depth1)):
		return None
	else:        
		return depth1

def computeCommonSonDepthIterative(sense1, sense2, depth1, depth2):
	print("SON {} {}".format(depth1,depth2))
	if(sense1 == sense2):
		return depth1
		
	if(sense1.hyponyms() == [] or sense2.hyponyms() == []):
		return None

	hypos1, hypos2, depth1, depth2 = levelingDown(sense1, sense2, depth1, depth2)    

	if (sense1 in hypos2["all"] or sense2 in hypos1["all"]): #controllo un senso è iponimo dell'altro le profondità a questo punto sono uguali        
		return depth1
	else:
		while(not checkCommonsIterative(hypos1, hypos2, depth1) and (len(addLevelDown(hypos1[depth1])) > 0 and len(addLevelDown(hypos2[depth1])) > 0)):            
			hypos1[depth1+1] = addLevelDown(hypos1[depth1])
			hypos1["all"].extend(hypos1[depth1+1])
			
			hypos2[depth1+1] = addLevelDown(hypos2[depth1])
			hypos2["all"].extend(hypos2[depth1+1])
			
			depth1+=1
		
	if(not checkCommonsIterative(hypos1, hypos2, depth1)):
		return None
	else:        
		return depth1

#calcola il cammino minimo tra due sensi
def minPath(sense1, sense2):
	depth1=computeDepthMin(sense1,0)
	depth2=computeDepthMin(sense2,0)

	#calcolo profondità genitore e figlio comune
	comParDepth = computeCommonParentDepthIterative(sense1, sense2, depth1, depth2)
	comSonDepth = computeCommonSonDepthIterative(sense1, sense2, depth1, depth2)

	realLCS = sense1.lowest_common_hypernyms(sense2, use_min_depth=False)

	for lcs in realLCS:
		print("realPar ", lcs)
		print("realParDepth ", lcs.min_depth())

	print("depth1 ", depth1)
	print("depth2 ", depth2)
	print("comPar ", comParDepth)
	print("comSon ", comSonDepth)
	#calcolo minimo cammino di sopra cammino di sotto
	if(comParDepth is not None and comSonDepth is None):
		pathUp = abs(depth1-comParDepth) + abs(depth2 - comParDepth)
		print("pathUp ", pathUp)
		return pathUp  
	elif(comParDepth is None and comSonDepth is not None):
		pathDown = abs(depth1-comSonDepth) + abs(depth2 - comSonDepth)
		print("pathDown ", pathDown)
		return pathDown
	elif(comParDepth is None and comSonDepth is None):
		return None
	else:    
		pathUp = abs(depth1-comParDepth) + abs(depth2 - comParDepth)
		pathDown = abs(depth1-comSonDepth) + abs(depth2 - comSonDepth)
		print("pathUp ", pathUp)
		print("pathDown ", pathDown)
		return min(pathUp, pathDown)

def testCommonDepth(word1, word2):
	senses1 = wn.synsets(word1)
	senses2 = wn.synsets(word2)
		
	#bestSimilar = None
	print(word1, word2)
	
	for sense1 in senses1:
		for sense2 in senses2:
			print(sense1, sense2)
			commonParDepth = computeCommonParentDepthIterative(sense1, sense2, computeDepthMin(sense1,0), computeDepthMin(sense2,0))
			comSonDepth = computeCommonSonDepthIterative(sense1, sense2, computeDepthMin(sense1,0), computeDepthMin(sense2,0))            

			lowest_hyper = sense1.lowest_common_hypernyms(sense2, use_min_depth=False)    

			if(lowest_hyper != []):
				print("REAL LOWEST HYPER ", lowest_hyper[0])
				print("commonParDepth: {} realDepth: {} commSonDepth: {}\n\n".format(commonParDepth, lowest_hyper[0].min_depth(), comSonDepth))
			else:
				print("commonDepth: {} realDepth: {} commSonDepth: {}\n\n".format(commonParDepth, 666, comSonDepth))

def testDepth(word):
	senses = wn.synsets(word)

	for sense in senses:
		depth=computeDepthMin(sense, 0)

		print("sense {} depth {} min_depth {} max_depth {}\n\n".format(sense, depth, sense.min_depth(), sense.max_depth()))

def testMinPath(word1, word2):
	senses1 = wn.synsets(word1)
	senses2 = wn.synsets(word2)
		
	#bestSimilar = None
	print("*********MIN PATH TEST {} {}*****".format(word1, word2))
	
	for sense1 in senses1:
		for sense2 in senses2:
			minP = minPath(sense1, sense2)
			print("minPath: {} realMinPath: {}\n\n".format(minP, sense1.shortest_path_distance(sense2)))


def main():
	word1 = "dog"
	word2 = "cat"
	testCommonDepth(word1, word2) 
	testMinPath(word1, word2)
	#testDepth("love") 
	

if __name__ == '__main__':
	main()