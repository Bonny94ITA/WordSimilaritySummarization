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

def writeOutput(outputfile, data, similarity, correlations):
	outputfile.write(data[0].upper()+" "+data[1].upper()+" Value: "+str(data[2])+"\n")
	
	for sim in similarity:
		#outputfile.write("\tWuPalmer: "+sim+" Pearson:"+correlations[0].upper+"\n")
		outputfile.write("\tWuPalmer: "+str(sim)+"\n\n")

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

def checkHyperonims(hyper1, hyper2, depth): # true se c'è intersezione tra gli iperonimi di questo livello
	intersection = set(hyper1["all"]).intersection(hyper2["all"])
	#print("hyper 1", hyper1["all"])
	#print("hyper 2", hyper2["all"])
	#print("Intersezione", intersection)
	return len(intersection) > 0

def leveling(sense1, sense2, depth1, depth2):
	hyper1 = {}
	hyper2 = {}

	hyper1[depth1-1] = sense1.hypernyms()
	hyper2[depth2-1] = sense2.hypernyms()
	hyper1["all"] = sense1.hypernyms()
	hyper2["all"] = sense2.hypernyms()
	
	while(depth1 > depth2 or depth1 < depth2):
		if(depth2 > depth1):         #salgo con il senso 2
			depth2-=1
			hyper2[depth2-1] = []                        
			for hyp in hyper2[depth2]:
				hyper2[depth2-1].extend(hyp.hypernyms())
				hyper2["all"].extend(hyp.hypernyms())

		elif(depth1 > depth2):       #salgo con il senso 1
			depth1-=1
			hyper1[depth1-1] = []                        
			for hyp in hyper1[depth1]:
				hyper1[depth1-1].extend(hyp.hypernyms())
				hyper1["all"].extend(hyp.hypernyms())
	
	return hyper1, hyper2, depth1, depth2

def computeCommonParentDepth(sense1, sense2, depth1, depth2):
	if(depth1 == 0 or depth2 == 0):
		return 0

	hyper1, hyper2, depth1, depth2 = leveling(sense1, sense2, depth1, depth2)

	depth1-=1

	if (sense1 in hyper2["all"] or sense2 in hyper1["all"]): #controllo un senso è iperonimo dell'altro le profondità a questo punto sono uguali
		return depth1
	else:
		while(not checkHyperonims(hyper1, hyper2, depth1) and depth1 > 0):
			#print("SONO IN UN BEL WHILE", depth1)          
			hyper1[depth1-1] = []
			hyper2[depth1-1] = [] 
			
			for hyp in hyper1[depth1]:
				hyper1[depth1-1].extend(hyp.hypernyms())
				hyper1["all"].extend(hyp.hypernyms())

			for hyp in hyper2[depth1]:
				hyper2[depth1-1].extend(hyp.hypernyms())
				hyper2["all"].extend(hyp.hypernyms())
			
			depth1-=1
	
	return depth1

def WuPalmer(words):
	senses1 = wn.synsets(words[0])
	senses2 = wn.synsets(words[1])
	
	max = 0
	#bestSimilar = None

	for sense1 in senses1:
		for sense2 in senses2:
			depth1 = computeDepthMin(sense1, 0)       #si potrebbe usare min_depth o max_depth
			depth2 = computeDepthMin(sense2, 0)
			commonParentDepth = computeCommonParentDepth(sense1, sense2, depth1, depth2)
			depthSum = depth1 + depth2 + 1
			wupalmValue = 2 * commonParentDepth / depthSum

			if(wupalmValue > max):
				#bestSimilar = [sense1, sense2]
				max = wupalmValue

	return max

def computeSimilarity(words):
	similarity = []

	similarity.append(WuPalmer(words))
	#similarity.append(shortestPath(words))
	#similarity.append(LeacockChodorow(words))

	return similarity

#def computeCorrelations(similarity, correctValue):

def computeSimilarityFile(inputname, outputname):    
	
	with open(inputname, 'r') as inputfile:
		with open(outputname, 'w') as outputfile:
			for line in inputfile:
				data = parseLine(line)
				
				if(data != None):
					similarity = computeSimilarity(data[0:2])
					#correlations = computeCorrelations(similarity, data[3])
					writeOutput(outputfile, data, similarity, None)

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
			computeSimilarity(words)
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