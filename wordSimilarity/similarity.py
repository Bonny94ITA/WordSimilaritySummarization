from nltk.corpus import wordnet as wn
import argparse
import math
import pandas as pd


MAX_DEPTH = max(max(len(hyp_path) for hyp_path in ss.hypernym_paths()) for ss in wn.all_synsets())
simLabels = ["WuPalmer", "shortestPath", "LeacockChodorow"]
corLabels = ["Pearson", "Spearman"]

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

def printSimilarity(similarity):
	text = ""
	for i, sim in enumerate(similarity):
		#outputfile.write("\tWuPalmer: "+sim+" Pearson:"+correlations[0].upper+"\n")
		text += "\t"+simLabels[i]+": "+str(sim)+"\n"
	
	return text+"\n"

def printCorrelations(cors):
	text = "CORRELATIONS:\n"
	for i, cor in enumerate(cors):
		#outputfile.write("\tWuPalmer: "+sim+" Pearson:"+correlations[0].upper+"\n")
		text += "\t"+corLabels[i]+": \n"+str(cor[1])+"\n"
	
	return text+"\n"

def printWords(words):
	return words[0].upper()+" "+words[1].upper()

def writeOutput(outputfile, data, similarity, correlations):
	outputfile.write(printWords(data[0:2])+" Value: "+str(data[2])+"\n")
	
	outputfile.write(printSimilarity(similarity))

#calcola la distanza minima del senso dalla radice
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

def checkCommons(senses1, senses2, depth): # true se c'è intersezione tra gli iperonimi di questo livello
	intersection = set(senses1["all"]).intersection(senses2["all"])
	#print("hyper 1", hyper1["all"])
	#print("hyper 2", hyper2["all"])
	#print("Intersezione", intersection)
	return len(intersection) > 0

def initiateCommon(UpDown, sense1, sense2, depth1, depth2):
	common1 = {}
	common2 = {}

	common1[depth1] = [sense1]
	common2[depth2] = [sense2]
	if(UpDown == "UP"):

		if(depth1 < depth2):
			depth2 -= 1
			common2[depth2] = sense2.hypernyms()
			common2["all"] = common2[depth2]
			common1["all"] = []
		else:
			depth1 -= 1
			common1[depth1] = sense1.hypernyms()
			common1["all"] = common1[depth1]
			common2["all"] = []
	else:

		if(depth1 > depth2):
			depth2 += 1
			common2[depth2] = sense2.hyponyms()
			common2["all"] = common2[depth2]
			common1["all"] = []
		else:
			depth1 += 1
			common1[depth1] = sense1.hyponyms()
			common1["all"] = common1[depth1]
			common2["all"] = []

	return common1, common2, depth1, depth2		

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
	
	hypos1, hypos2, depth1, depth2 = initiateCommon("DOWN", sense1, sense2, depth1, depth2)
	
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
	
	hyper1, hyper2, depth1, depth2 = initiateCommon("UP", sense1, sense2, depth1, depth2)
	
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

def computeCommonParentDepth(sense1, sense2, depth1, depth2):
	if(sense1 == sense2):
		return depth1

	if(depth1 == 0 or depth2 == 0):
		return 0

	hyper1, hyper2, depth1, depth2 = levelingUp(sense1, sense2, depth1, depth2)    

	if (sense1 in hyper2["all"] or sense2 in hyper1["all"]): #controllo un senso è iperonimo dell'altro le profondità a questo punto sono uguali
		return depth1
	else:
		while(not checkCommons(hyper1, hyper2, depth1) and depth1 > 0):
			hyper1[depth1-1] = addLevelUp(hyper1[depth1])
			hyper1["all"].extend(hyper1[depth1-1])

			hyper2[depth1-1] = addLevelUp(hyper2[depth1])
			hyper2["all"].extend(hyper2[depth1-1])
			
			depth1-=1
	
	if(not checkCommons(hyper1, hyper2, depth1)):
		return None
	else:        
		return depth1

def computeCommonSonDepth(sense1, sense2, depth1, depth2):
	if(sense1 == sense2):
		return depth1

	if(sense1.hyponyms() == [] or sense2.hyponyms() == []):
		return None

	hypos1, hypos2, depth1, depth2 = levelingDown(sense1, sense2, depth1, depth2)    

	if (sense1 in hypos2["all"] or sense2 in hypos1["all"]): #controllo un senso è iponimo dell'altro le profondità a questo punto sono uguali        
		return depth1
	else:
		while(not checkCommons(hypos1, hypos2, depth1) and (len(addLevelDown(hypos1[depth1])) > 0 and len(addLevelDown(hypos2[depth1])) > 0)):            
			hypos1[depth1+1] = addLevelDown(hypos1[depth1])
			hypos1["all"].extend(hypos1[depth1+1])
			
			hypos2[depth1+1] = addLevelDown(hypos2[depth1])
			hypos2["all"].extend(hypos2[depth1+1])
			
			depth1+=1
		
	if(not checkCommons(hypos1, hypos2, depth1)):
		return None
	else:        
		return depth1

#calcola il cammino minimo tra due sensi
def minPath(sense1, sense2):
	depth1=computeDepthMin(sense1,0)
	depth2=computeDepthMin(sense2,0)

	#calcolo profondità genitore e figlio comune
	#comParDepth = computeCommonParentDepth(sense1, sense2, depth1, depth2)
	comParDepth = minmin(sense1, sense2)
	comSonDepth = computeCommonSonDepth(sense1, sense2, depth1, depth2)

	if(comParDepth == 10000):
		comParDepth = None
	#calcolo minimo cammino di sopra cammino di sotto
	if(comParDepth is not None and comSonDepth is None):
		return abs(depth1-comParDepth) + abs(depth2 - comParDepth)                
	elif(comParDepth is None and comSonDepth is not None):
		return abs(depth1-comSonDepth) + abs(depth2 - comSonDepth)                
	elif(comParDepth is None and comSonDepth is None):
		return None
	else:    
		pathUp = abs(depth1-comParDepth) + abs(depth2 - comParDepth)
		pathDown = abs(depth1-comSonDepth) + abs(depth2 - comSonDepth)
		
		return min(pathUp, pathDown)

def minmin(sense1, sense2):
	minmin = 0
	hypers = sense1.lowest_common_hypernyms(sense2)

	if (hypers == []):
		return None
	else:
		for h in hypers:
			minmin = max(minmin, h.min_depth())
		
		return minmin

def WuPalmer(sense1, sense2):
	
	depth1 = computeDepthMin(sense1, 0)       #si potrebbe usare min_depth o max_depth
	depth2 = computeDepthMin(sense2, 0)
	#commonParentDepth = computeCommonParentDepth(sense1, sense2, depth1, depth2)
	commonParentDepth = minmin(sense1, sense2)
	depthSum = depth1 + depth2

	if(depthSum > 0 and commonParentDepth is not None):	
		return 2 * commonParentDepth / depthSum
	else:
		return 0

def shortestPath(sense1, sense2):
	minP = minPath(sense1, sense2)

	if(minP is None):
		return 0
	else:
		return 2 * MAX_DEPTH - minP

def LeacockChodorow(sense1, sense2):
	minP = minPath(sense1, sense2)

	if(minP is None):
		return 0
	else:
		return -math.log((minP + 1) / (2 * MAX_DEPTH + 1))

def computeSimilarity(words):
		
	similarity = {}

	senses1 = wn.synsets(words[0])
	senses2 = wn.synsets(words[1])

	if(len(senses1) == 0 or len(senses2) == 0):
		return None

	similarity = [[],[],[]]	

	#print(words)

	for sense1 in senses1:
		for sense2 in senses2:
			similarity[0].append(WuPalmer(sense1, sense2))
			similarity[1].append(shortestPath(sense1, sense2))
			similarity[2].append(LeacockChodorow(sense1, sense2))

	#print(similarity["WP"])
	#print(similarity["SP"])
	#print(similarity["LC"])
	similarity[0] = max(similarity[0])
	similarity[1] = max(similarity[1])
	similarity[2] = max(similarity[2])

	return similarity
	#return [["WuPalmer", max(similarity["WP"])], ["shortestPath", max(similarity["SP"])], ["LeacockChodorow", max(similarity["LC"])]]

def computeCorrelations(correlations):
	df = pd.DataFrame(correlations)
	
	corrs = []
	corrs.append(["Pearson",df.corr()])
	corrs.append(["Spearman",df.corr(method='spearman')])

	return corrs

def initCorr():
	correlations = {}
	correlations["real"] = []
	correlations["WP"] = []
	correlations["SP"] = []
	correlations["LC"] = []

	return correlations

def computeSimilarityFile(inputname, outputname):    
	
	with open(inputname, 'r') as inputfile:
		
		correlations = initCorr()

		with open(outputname, 'w') as outputfile:
			for line in inputfile:
				data = parseLine(line)
				
				if(data != None):
					similarity = computeSimilarity(data[0:2])										
					if(similarity is not None):
						correlations["WP"].append(similarity[0])
						correlations["SP"].append(similarity[1])
						correlations["LC"].append(similarity[2])
						correlations["real"].append(data[2])
						writeOutput(outputfile, data, similarity, None)
					else:
						outputfile.write(printWords(data[0:2])+" one of the words or both are not present in WordNet\n\n")

			corrs=computeCorrelations(correlations)
			outputfile.write(printCorrelations(corrs))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", help="specify input filename")
	parser.add_argument("-w", "--words", help="2 words space separated")
	parser.add_argument("-o", "--output", help="specify output filename")

	args = parser.parse_args()

	words=[]
	if(args.words):
		words = parseWords(args.words)

		if(words != None):
			similarity=computeSimilarity(words)
			print(printWords(words))
			print(printSimilarity(similarity))

		else:
			print("Insert exactly two words space separated")
	else:
		inputname = "WordSim353.csv"
		outputname = "output.txt"
		
		if(args.input):
			inputname = args.input
		
		if(args.output):
			outputname=args.output

		computeSimilarityFile(inputname, outputname)

if __name__ == '__main__':
	main()