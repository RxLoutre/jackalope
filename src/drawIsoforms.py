"""
A script which can read a GFF3, using the parser 'parse_gff3',
and reorganize data into structures, using annotation.py, to make
them easier to use.

Once it has read and store data, it generate a SVG file, using svgwrite,
to draw a representation of the gene and all his transcript.

The script is able to produce two kind of drawing :
	- a draw with introns/exons represented proportionnaly with their positions in the chromosome
	- a draw where introns length are fixed (to sigma) between differents groups of overlapping exons (called connected component)
	
"""
import annotation
import parse_gff3
import svgwrite
import networkx as nx
import argparse

#********Constants********#

line_height = 25
exon_height = 17
left_margin = 10
text_margin = 200
right_margin = 20
minStartDessin = float(200)
maxEndDessin = float(1150)
espaceDessin = maxEndDessin - minStartDessin
sigma = 30
#drawDimension = 1200

#******Class and functions******#

class con_com:
	"""
	con_com => Connected Component
	This class contain a list of connected component,
	which here represent all the groups of overlapping exons
	between all transcripts
	It also contain the minimum start of one of his exon
	and the maximum end of another exon, allowing to
	calculate the maximum space of a connected component
	which is maxLen
	"""
	def __init__(self,liste):
		self.connected_comp = []
		self.connected_comp = liste
		self.maxLen = 0
		self.minStart = 0
		self.maxEnd = 0
		
	def __str__(self):
		s = ""
		compteur = 0
		for c in self.connected_comp:
			compteur +=1
			s += "Composante " + str(compteur)
			for elem in c:
				s += str(elem)
				s += "\n"
		return s
		
	def __eq__(self,other):
		 return ((self.connected_comp[0].seqStart)  == (other.connected_comp[0].seqStart))
		 
	def __lt__(self,other):
		 return ((self.connected_comp[0].seqStart)  < (other.connected_comp[0].seqStart))
		 
	def __gt__(self,other):
		 return ((self.connected_comp[0].seqStart)  > (other.connected_comp[0].seqStart))	 		

def genesFromGFF(fileName):
	"""
	A function who read a gff3 file called "fileName" (argument given by the calling function)
	and produce three dictionnary which respectively contains genes, transcripts and exons
	Data are stored like this :
	EnsemblID => Structure
	Where Ensembl ID is something like 'ENST0000001' 
	And structure is a annotation.gene, annotation.transcript or annotation.exon
	"""
	dicogene = {}
	dicotrans = {}
	dicoexons = {}
	for record in parse_gff3.parseGFF3(fileName):
		if(record.type == "gene"):
			g = annotation.gene(record.attributes["ID"],record.seqid,record.start,record.end,record.strand)
			dicogene[record.attributes['ID']] = g
		elif(record.type == "mRNA"):
			t = annotation.transcript(record.attributes["ID"],record.attributes["Parent"],record.seqid,record.start,record.end,record.strand)
			if record.attributes["ID"] in dicotrans:
				dicotrans[record.attributes["ID"]].parentId.append(record.attributes["Parent"])
			else:
				dicotrans[record.attributes["ID"]] = t
				dicogene[record.attributes["Parent"]].appendTranscript(t)
		elif(record.type == "exon"):
			e = annotation.exon(record.attributes["ID"],record.attributes["Parent"],record.seqid,record.start,record.end,record.strand)
			if record.attributes["ID"] in dicoexons:
				dicoexons[record.attributes["ID"]].parentId.append(record.attributes["Parent"])
				if dicoexons[record.attributes["ID"]] not in dicotrans[record.attributes["Parent"]].exons :
					dicotrans[record.attributes["Parent"]].appendExon(dicoexons[record.attributes["ID"]])
			else:
				dicoexons[record.attributes["ID"]] = e
				dicotrans[record.attributes["Parent"]].appendExon(e)
	return [dicogene,dicotrans,dicoexons]

def initDraw(name,dimX,dimY):
	"""
	A function which oppen a new draw, called "name", and write a white rectangle
	of drawingDimension*drawingDimension
	"""
	dwg = svgwrite.Drawing(name,size=(dimX,dimY), profile='full')
	dwg.add(dwg.rect((0,0),(dimX,dimY),fill=svgwrite.rgb(255,255,255)))
	dwg.add_stylesheet("../styleSVG.css","styleSVG.css")
	return dwg

def drawExon(dwg,lineNumber,start,end,rvb,idExon):
	"""
	A function which draw a new exon on a opened dwg draw
	it draw that exon from 'start', to 'end' (x position)
	at the line 'lineNumber' (y position) with the color
	'rvb'
	"""
	dwg.add(dwg.rect((start,lineNumber*line_height),(end - start, exon_height),fill=svgwrite.rgb(rvb[0],rvb[1],rvb[2]),id="exon",onmouseover="evt.target.setAttribute('opacity', '0.5');",onmouseout="evt.target.setAttribute('opacity','1)');"))

def drawHighlightExon(dwg,lineNumber,start,end,rvb,idExon):
	"""
	A function which draw a new exon in a highlight way
	"""
	dwg.add(dwg.rect((start,lineNumber*line_height),(end - start, exon_height),stroke=svgwrite.rgb(231, 62, 1,'%'),fill=svgwrite.rgb(255,255,255),id="exon",onmouseover="evt.target.setAttribute('opacity', '0.5');",onmouseout="evt.target.setAttribute('opacity','1)');"))
	

def startNewTranscript(dwg,trNb,lineNumber,idTranscrit):
	"""
	A function which write on the left of the draw, at line
	'lineNumber' the name of the transcript 'idTranscrit' on 
	an opened dwg draw
	"""
	dwg.add(dwg.text(idTranscrit, insert=(left_margin,(lineNumber*line_height+3*exon_height/4.0))))

def buildGraph(dicogene):
	"""
	A function which is able to build a graph of all exons from a gene dict
	Nodes are exons, and edge are made between any overlapping exon.
	"""
	G=nx.Graph()	
	for genes in dicogene:	
		for transcrits in dicogene[genes].transcripts:		
			for exon in transcrits.exons:
				G.add_node(exon)
				for n in G.nodes():
					if ((n.seqStart <= exon.seqStart) and (n.seqEnd >= exon.seqEnd)) or ((exon.seqStart <= n.seqStart) and (exon.seqEnd >= n.seqEnd)):
						G.add_edge(n,exon)
	return G

def findMinMax(C):
	"""
	A function which determined, from each connected_component of C
	(a list of all the connected component of the exon graph),
	the minimum start, the maximum end and then the space between
	them, called 'maxLen'
	"""
	for composante in C:
		minStart = float(composante.connected_comp[0].seqStart)
		maxEnd = float(composante.connected_comp[0].seqEnd)
		for exon in composante.connected_comp:	
			if exon.seqStart < minStart:
				minStart = float(exon.seqStart)
			if exon.seqEnd > maxEnd:
				maxEnd = float(exon.seqEnd)
		composante.maxLen = maxEnd - minStart
		composante.minStart = minStart
		composante.maxEnd = maxEnd
	
def buildConnectedComp(G):
	"""
	A function which is able to build a list with all the
	group of overlapping exons, called connected component
	"""
	listeConComp = []
	for elem in nx.connected_components(G):
		conComp = con_com(elem)
		listeConComp.append(conComp)
	findMinMax(listeConComp)
	listeConComp.sort()
	return listeConComp
	
def drawDimension(nbConnectedComponent,nbTranscript):
	nbIntrons = nbConnectedComponent - 1;
	dimX = sigma * nbIntrons + (nbConnectedComponent) * 40 + 200
	dimY = (exon_height*3) * nbTranscript + 100
	return (dimX,dimY)
	
#**************************MAIN********************************	

parser = argparse.ArgumentParser()
parser.add_argument("file", help="The GFF3 input file (.gz allowed)")
parser.add_argument("output", help="The SVG output file")
parser.add_argument("--print-count", help="Print number of gene, exons and transcript", action="store_true")
parser.add_argument("--fixed", help="The resulting draw will not be proportionnal, intron betweend a group of overlapping exons will be fixed to a length", action="store_true")
parser.add_argument("--proportionnal", help="The resulting draw will be proportionnal to chromosomal coordinate", action="store_true")
parser.add_argument("--listed", help="The resulting draw will only show a visual list of all exons and their positions on the chromosom", action="store_true")
parser.add_argument("--specific-exon", help="You can specify a file name which contain a list of Ensembl ID of some exons you want to be highlighted")
args = parser.parse_args()
[dicogene,dicotrans,dicoexons] = genesFromGFF(args.file);	
espaceTotalDessin = maxEndDessin - minStartDessin

if args.print_count:
	print "Total gene : " + str(len(dicogene)) + "\n"
	print "Total transcrits : " + str(len(dicotrans)) + "\n"
	print "Total exons : " + str(len(dicoexons)) + "\n"


listeCouleur = [[231,62,1],[116,208,241],[240,195,0],[223,109,20],[76,166,107],[254, 150, 160],[165,38,10],[131,166,151],[223,255,0],[0,0,255],[253,108,158],[225,206,154],[222,228,196],[248,142,85],[198,8,0],[239,155,15],[1,215,88],[159,232,85],[189,51,164],[75,0,130],[128, 128, 0],[231, 168, 84],[11, 22, 22],[153, 122, 144]]
espacement = 2
couleur = 0
i = 0

if args.fixed:
	
	G = buildGraph(dicogene)
	C = buildConnectedComp(G)			
	K = nx.number_connected_components(G)
	nbTrans = len(dicotrans)
	(dimensionX,dimensionY) = drawDimension(K,nbTrans)
	dwg = initDraw(args.output,dimensionX,dimensionY)
	#Calcul de Alpha => coefficient de proportionnalite entre coordonnees ecran et coordonnees chromosomiques
	sumMaxLen = 0
	for elem in C:
		sumMaxLen += elem.maxLen
	alpha = ( (dimensionX-(text_margin + left_margin + right_margin)) - (K - 1) * sigma) / sumMaxLen
	#calcul de la position de depart du dessin
	i=1
	sumtemp = 0
	numeroLigne = 1
	listeTrans = dicotrans.keys()
	listeTrans.sort()
	for trans in range(len(listeTrans)):
		startNewTranscript(dwg,numeroLigne+1,espacement+numeroLigne,listeTrans[trans])
		for elem in C:
			debutComposante = (left_margin + (i - 1) * sigma + alpha * sumtemp) + text_margin
			finComposante = debutComposante + alpha * elem.maxLen
			minStart = elem.minStart
			for exon in elem.connected_comp:
				if(listeTrans[trans] in exon.parentId):
					debutExon = float(exon.seqStart)
					finExon = float(exon.seqEnd)
					interExon = finExon - debutExon
					debutDessin = ((finComposante-debutComposante)/(elem.maxEnd - elem.minStart))*(debutExon-elem.minStart) + debutComposante
					finDessin = ((finComposante-debutComposante)/(elem.maxEnd - elem.minStart))*(finExon-elem.minStart) + debutComposante
					if(args.specific_exon and args.specific_exon == exon.ensemblId):
						drawHighlightExon(dwg,espacement+numeroLigne,debutDessin,finDessin,listeCouleur[couleur],exon.ensemblId)
					else:
						drawExon(dwg,espacement+numeroLigne,debutDessin,finDessin,listeCouleur[couleur],exon.ensemblId)
			i += 1
			sumtemp += elem.maxLen
		couleur = (couleur + 1) % len(listeCouleur)	
		espacement += 0.5
		numeroLigne += 1
		sumtemp = 0
		i=1			
	dwg.save()
	
elif args.proportionnal:
	drawDimension = 1200
	nbTrans = len(dicotrans)
	dimY = (exon_height*3) * nbTrans + 100
	dwg = initDraw(args.output,drawDimension,dimY)
	for genes in dicogene:
		minStart = float(dicogene[genes].transcripts[0].exons[0].seqStart)
		maxEnd = float(dicogene[genes].transcripts[0].exons[0].seqEnd)
		for transcrits in dicogene[genes].transcripts:		
			for exon in transcrits.exons:
				if exon.seqStart < minStart:
					minStart = float(exon.seqStart)
				if exon.seqEnd > maxEnd:
					maxEnd = float(exon.seqEnd)
		espaceTotal = float(maxEnd - minStart)
		dicogene[genes].transcripts.sort()
		for transcrits in dicogene[genes].transcripts:	
			startNewTranscript(dwg,i+1,espacement+i,transcrits.ensemblId)					
			for exon in transcrits.exons:
				debutExon = float(exon.seqStart)
				finExon = float(exon.seqEnd)
				debutDessin = (espaceTotalDessin/espaceTotal)*(debutExon-minStart)+minStartDessin
				finDessin = (espaceTotalDessin/espaceTotal)*(finExon-minStart)+minStartDessin
				if(args.specific_exon and args.specific_exon == exon.ensemblId):
					drawHighlightExon(dwg,espacement+i,debutDessin,finDessin,listeCouleur[couleur],exon.ensemblId)
				else:
					drawExon(dwg,espacement+i,debutDessin,finDessin,listeCouleur[couleur],exon.ensemblId)
			espacement += 0.5
			couleur = (couleur + 1) % len(listeCouleur)		
			i += 1
		
	dwg.save()
	
elif args.listed:
	G = buildGraph(dicogene)
	C = buildConnectedComp(G)			
	K = nx.number_connected_components(G)
	nbTrans = len(dicotrans)
	listEx = dicoexons.keys()
	(dimensionX,dimensionY) = drawDimension(K,nbTrans)
	dwg = initDraw(args.output,dimensionX,dimensionY)
	#Calcul de Alpha => coefficient de proportionnalite entre coordonnees ecran et coordonnees chromosomiques
	sumMaxLen = 0
	for elem in C:
		sumMaxLen += elem.maxLen
	alpha = ( (dimensionX-(text_margin + left_margin + right_margin)) - (K - 1) * sigma) / sumMaxLen
	#calcul de la position de depart du dessin
	i=1
	sumtemp = 0
	numeroLigne = 1
	currentExons = []
	for cc in C:
		debutComposante = (left_margin + (i - 1) * sigma + alpha * sumtemp) + text_margin
		finComposante = debutComposante + alpha * cc.maxLen
		minStart = cc.minStart
		for exon in cc.connected_comp:		
			for wex in currentExons:
				if(wex.overlaps(exon)):
					numeroLigne += 1
					currentExons = []
					break;
			debutExon = float(exon.seqStart)
			finExon = float(exon.seqEnd)
			interExon = finExon - debutExon
			debutDessin = ((finComposante-debutComposante)/(cc.maxEnd - cc.minStart))*(debutExon-cc.minStart) + debutComposante
			finDessin = ((finComposante-debutComposante)/(cc.maxEnd - cc.minStart))*(finExon-cc.minStart) + debutComposante
			drawExon(dwg,numeroLigne,debutDessin,finDessin,listeCouleur[couleur],exon.ensemblId)
			currentExons.append(exon)
			
		i += 1
		sumtemp += cc.maxLen
		couleur = (couleur + 1) % len(listeCouleur)
		numeroLigne = 1
		dwg.save()
	
	
