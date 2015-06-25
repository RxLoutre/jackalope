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

def frange(x, y, jump):
		while x <= y:
			yield x
			x += jump

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
		 
class exon_box:
	"""
	An intermediary class which allow to store properly all the needed
	informations to draw an exon. Start is (x1,y), width is (x2-x1)
	height is fixed by the programm. A RGB color is given, and also
	the exon ensembl id to allow a tool tip
	"""
	def __init__(self,y,x1,x2,color,id_exon,id_transcript):
		self.y = y * line_height + exon_height
		self.x = x1
		self.height = exon_height
		self.width = (x2 - x1)
		self.color = color
		self.id_exon = id_exon
		self.id_transcript = id_transcript
		
class legend_text:
	"""
	An intermediary class which allow to complete the draw with 
	a legend containing the ensembl id of the transcript of the y line
	"""
	def __init__(self,lineNumber,id_transcript):
		self.x = left_margin
		self.y = lineNumber*line_height+3*exon_height/4.0
		self.text = id_transcript
		
class exon_edge:
	"""
	An intermediary class which allow to complete the draw with 
	lines between the different exons boxes.
	It's composed by two lines, one wich goes to (x1,y1) to 
	(x2,y2), and the other from (x2,y2) to (x3,y3)
	The middle point (x2,y2) must be calculated later, once
	all the edges between the exons are added.
	This is in order to create a range [-1,1,1/X] to add to
	y2 in order to see all the edges even if
	there is X time the same edge between two exon_box
	"""
	def __init__(self,x1,y1,x3,y3,transcript_id,ex1_id,ex2_id):
		self.x1 = float(x1)
		self.y1 = float(y1)
		self.x3 = float(x3)
		self.y3 = float(y3)
		self.x2 = float((x1+x3)/2)
		self.y2 = float((y1+y3)/2)
		self.transcript_id = transcript_id
		self.ex1_id = ex1_id
		self.ex2_id = ex2_id
		
class drawing:
	"""
	An intermediary class which contains all data for drawing all
	the transcript of a gene
	"""
	def __init__(self,width,height):
		self.list_exon_boxes = []
		self.list_legend = []
		self.list_exon_edges = []
		self.width = width
		self.height = height
		
	def append_exon_box(self,exon_box):
		self.list_exon_boxes.append(exon_box)
		
	def append_legend(self,legend):
		self.list_legend.append(legend)
		
	def append_exon_edge(self,edge):
		self.list_exon_edges.append(edge)
		
	def calculate_edges(self,dicotrans):
		dic_edge= {}
		for trans in dicotrans:
			for i in range(len(dicotrans[trans].exons)-1):
				compteur = 0
				box1 = dicotrans[trans].exons[i].ensemblId
				box2 = dicotrans[trans].exons[i+1].ensemblId
				for edges in self.list_exon_edges:
					if(edges.ex1_id == box1 and edges.ex2_id == box2):
						compteur += 1
				jump = float(5.0/compteur)
				start = 0.0
				end = 5.0
				for edges in self.list_exon_edges:
					if(edges.ex1_id == box1 and edges.ex2_id == box2):
						edges.y2 += start
						start += jump
						if(start > end):
							break
				
		
	def draw_SVG(self,fileName):
		dwg = initDraw(fileName,self.width,self.height)
		for ex in self.list_exon_boxes:
			drawExon(dwg,ex.y,ex.x,(ex.x + ex.width),ex.color,ex.id_exon)
		for tr in self.list_legend:
			startNewTranscript(dwg,tr.x,tr.y,tr.text)
		dwg.save()
		
	def draw_JSON(self,nameFile,draw_edge):
		cptr = 0
		mon_fichier = open(nameFile, "w")
		mon_fichier.write("{")
		mon_fichier.write("\"xdessin\" : "+str(self.width)+",")
		mon_fichier.write("\"ydessin\" : "+str(self.height)+",")
		mon_fichier.write("\"exons\" : [ ")
		for ex in self.list_exon_boxes:
			mon_fichier.write("{\"x\" : "+str(ex.x)+",")
			mon_fichier.write("\"y\" : "+str(ex.y)+",")
			mon_fichier.write("\"width\" : "+str(ex.width)+",")
			mon_fichier.write("\"height\" : "+str(ex.height)+",")
			mon_fichier.write("\"color\" : { \"r\" : "+str(ex.color[0])+", \"v\" : "+str(ex.color[1])+", \"b\" : "+str(ex.color[2])+"},")
			mon_fichier.write("\"id_exon\" : \""+ex.id_exon+"\"}")
			if(cptr != len(self.list_exon_boxes) - 1):
				mon_fichier.write(",")
			cptr += 1
		mon_fichier.write("],")
		mon_fichier.write("\"text_transcripts\" : [ ")
		cptr = 0
		for tr in self.list_legend:
			mon_fichier.write("{ \"x\" : "+str(tr.x)+",")
			mon_fichier.write("\"y\" : "+str(tr.y)+",")
			mon_fichier.write("\"id_transcript\" : \""+tr.text+"\"}")
			if(cptr != len(self.list_legend) - 1):
				mon_fichier.write(",")
			cptr += 1
		if(draw_edge):
			mon_fichier.write("],")
			mon_fichier.write("\"edges\" : [ ")	
			cptr = 0
			for edge in self.list_exon_edges:
				mon_fichier.write("{\"path\" : [")
				mon_fichier.write("{ \"x\" : "+str(edge.x1)+",")
				mon_fichier.write(" \"y\" : "+str(edge.y1)+"},")
				mon_fichier.write("{\"x\" : "+str(edge.x2)+",")
				mon_fichier.write(" \"y\" : "+str(edge.y2)+"},")
				mon_fichier.write("{\"x\" : "+str(edge.x3)+",")
				mon_fichier.write(" \"y\" : "+str(edge.y3)+"}],")
				mon_fichier.write("\"id_transcript\" : \""+edge.transcript_id+"\"}")				
				if(cptr != len(self.list_exon_edges) - 1):
					mon_fichier.write(",")
				cptr += 1
			mon_fichier.write("]")
		else:
			mon_fichier.write("]")
		mon_fichier.write("}")
		mon_fichier.close()

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
	return dwg

def drawExon(dwg,lineNumber,start,end,rvb,idExon):
	"""
	A function which draw a new exon on a opened dwg draw
	it draw that exon from 'start', to 'end' (x position)
	at the line 'lineNumber' (y position) with the color
	'rvb'
	"""
	dwg.add(dwg.rect((start,lineNumber),(end - start, exon_height),fill=svgwrite.rgb(rvb[0],rvb[1],rvb[2]),id="exon",onmouseover="evt.target.setAttribute('opacity', '0.5');",onmouseout="evt.target.setAttribute('opacity','1)');"))

def drawHighlightExon(dwg,lineNumber,start,end,rvb,idExon):
	"""
	A function which draw a new exon in a highlight way
	"""
	dwg.add(dwg.rect((start,lineNumber*line_height),(end - start, exon_height),stroke=svgwrite.rgb(231, 62, 1,'%'),fill=svgwrite.rgb(255,255,255),id="exon",onmouseover="evt.target.setAttribute('opacity', '0.5');",onmouseout="evt.target.setAttribute('opacity','1)');"))
	

def startNewTranscript(dwg,x,y,idTranscrit):
	"""
	A function which write on the left of the draw, at line
	'lineNumber' the name of the transcript 'idTranscrit' on 
	an opened dwg draw
	"""
	dwg.add(dwg.text(idTranscrit, insert=(x,y)))

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
parser.add_argument("--svg-output", help="By default, this programm will generate a JSON output. With this option, the programm will generate directly SVG file instead of JSON file.")
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
	draw = drawing(dimensionX,dimensionY)
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
		transcript_legend = legend_text(numeroLigne,listeTrans[trans])
		draw.append_legend(transcript_legend)
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
					exBx = exon_box(numeroLigne,debutDessin,finDessin,listeCouleur[couleur],exon.ensemblId,exon.parentId)
					draw.append_exon_box(exBx)
			i += 1
			sumtemp += elem.maxLen
		couleur = (couleur + 1) % len(listeCouleur)	
		espacement += 0.5
		numeroLigne += 1
		sumtemp = 0
		i=1
	if (args.svg_output):
		draw.draw_SVG(args.output)
	else:
		draw.draw_JSON(args.output,False)
	
elif args.proportionnal:
	drawDimension = 1200
	nbTrans = len(dicotrans)
	numeroLigne = 1
	dimY = (exon_height*3) * nbTrans + 100
	draw = drawing(drawDimension,dimY)
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
			transcript_legend = legend_text(numeroLigne,transcrits.ensemblId)
			draw.append_legend(transcript_legend)					
			for exon in transcrits.exons:
				debutExon = float(exon.seqStart)
				finExon = float(exon.seqEnd)
				debutDessin = (espaceTotalDessin/espaceTotal)*(debutExon-minStart)+minStartDessin
				finDessin = (espaceTotalDessin/espaceTotal)*(finExon-minStart)+minStartDessin
				exBx = exon_box(numeroLigne,debutDessin,finDessin,listeCouleur[couleur],exon.ensemblId,exon.parentId)
				draw.append_exon_box(exBx)
			couleur = (couleur + 1) % len(listeCouleur)		
			numeroLigne += 1
		
	if (args.svg_output):
		draw.draw_SVG(args.output)
	else:
		draw.draw_JSON(args.output,False)
	
elif args.listed:
	G = buildGraph(dicogene)
	C = buildConnectedComp(G)			
	K = nx.number_connected_components(G)
	nbTrans = len(dicotrans)
	listEx = dicoexons.keys()
	(dimensionX,dimensionY) = drawDimension(K,nbTrans)
	draw = drawing(dimensionX,dimensionY)
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
			exBx = exon_box(numeroLigne,debutDessin,finDessin,listeCouleur[couleur],exon.ensemblId,exon.parentId)
			draw.append_exon_box(exBx)
			currentExons.append(exon)
			
		i += 1
		sumtemp += cc.maxLen
		couleur = (couleur + 1) % len(listeCouleur)
		numeroLigne = 1
					
	for trans in dicotrans:
		for i in range(len(dicotrans[trans].exons)-1):
			for ex_box in draw.list_exon_boxes:
				if(dicotrans[trans].exons[i].ensemblId == ex_box.id_exon):
					box1 = ex_box
				if(dicotrans[trans].exons[i+1].ensemblId == ex_box.id_exon):
					box2 = ex_box
			if(box1.x < box2.x):
				x1 = float(box1.x + box1.width)
				y1 = float(box1.y) 
				x3 = float(box2.x)
				y3 = float(box2.y)
			else:
				x1 = float(box2.x + box2.width)
				y1 = float(box2.y) 
				x3 = float(box1.x)
				y3 = float(box1.y)
			edge = exon_edge(x1,y1,x3,y3,trans,box1.id_exon,box2.id_exon)
			draw.append_exon_edge(edge)
	draw.calculate_edges(dicotrans)	
	if (args.svg_output):
		draw.draw_SVG(args.output)
	else:
		draw.draw_JSON(args.output,True)
	
	
