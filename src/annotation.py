"""
Differents class allowing to store data coming from a GFF3 file
"""
import parse_gff3

class location:
	"""
	A location is a place en the genome
	Contain a chromosome, the positions (start/end/strand) of this location on the chromosom
	"""
	def __init__(self,chromosome,start,end,strand):
		if(end<start):
			raise Exception("Le debut de l'exon est superieur a sa fin")
		self.chromosome = chromosome
		self.seqStart = start
		self.seqEnd = end
		self.seqStrand = strand
		
			
	def __str__(self):
		s=self.chromosome + "\t" + str(self.seqStart) +\
		"\t" + str(self.seqEnd) + "\t" +\
		"\t" + self.seqStrand
		return s
		
	def overlaps(self,other):
		if((self.seqStart <= other.seqEnd) and (other.seqStart <= self.seqEnd)) or ((other.seqStart <= self.seqEnd) and (self.seqStart <= other.seqEnd)):
			return True
		else:
			return False
				
class exon(location):
	"""
	An exon is a location
	He also have an ensemblId and a list of all its parents transcripts
	"""
	def __init__(self,ensemblID,parentID,chromosome,start,end,strand):
		location.__init__(self,chromosome,start,end,strand)
		self.ensemblId = ensemblID
		self.parentId = []
		self.parentId.append(parentID)

	def __str__(self):
		s="Exn : " + self.ensemblId + "\t" +\
		self.chromosome + "\t" + str(self.seqStart) +\
		"\t" + str(self.seqEnd) + "\t" +\
		self.seqStrand + "\t" +"Parent="
		for i in range(len(self.parentId)):
			s += self.parentId[i]
			s += ","
		return s
		
class transcript(location):
		"""
		A transcript is a location
		He also have an ensemblId, a list of all its parents genes and a list of all exons it contained
		"""
		def __init__(self,ensemblID,parentID,chromosome,start,end,strand):
			location.__init__(self,chromosome,start,end,strand)
			self.ensemblId = ensemblID
			self.parentId = []
			self.exons = []
			self.parentId.append(parentID)
		
		def appendExon(self, e):
			if(e.chromosome != self.chromosome):
				raise Exception("L'exon n'est pas place sur le meme chromosome que le transcrit parent.")
			self.exons.append(e)
				
		def __str__(self):
			s="Trs : " + self.ensemblId + "\t" +\
			self.chromosome + "\t" + str(self.seqStart) +\
			"\t" + str(self.seqEnd) + "\t" +\
			self.seqStrand + "\t" +"Parent="
			for i in range(len(self.parentId)):
				s += self.parentId[i]
				s += ","
			s += "\t" + "Nb Exons : " + str(len(self.exons))
			return s
			
				
		def __eq__(self,other):
			return ((self.ensemblId)  == (other.ensemblId))
		 
		def __lt__(self,other):
			return ((self.ensemblId)  < (other.ensemblId))
		 
		def __gt__(self,other):
			return ((self.ensemblId)  > (other.ensemblId))	
		
class gene(location):
	"""
	A gene is a location
	He also have an ensemblId and a list of all transcripts it could generate
	"""
	def __init__(self,ensemblID,chromosome,start,end,strand):
		location.__init__(self,chromosome,start,end,strand)
		self.ensemblId = ensemblID
		self.transcripts = []
		
	def appendTranscript(self,t):
		if(t.chromosome != self.chromosome):
			raise Exception("Le transcrit n'est pas place sur le meme chromosome que le gene parent.")
		self.transcripts.append(t)
		
	def __str__(self):
		s="Gne : " + self.ensemblId + "\t" +\
		self.chromosome + "\t" + str(self.seqStart) +\
		"\t" + str(self.seqEnd) + "\t" +\
		"\t" + self.seqStrand + "\t" +\
		"Nb transcripts : " + str(len(self.transcripts))
		return s
			
	def showAllTranscripts(self):
		for i in range(0,len(self.transcripts),1):
			print str(self.transcripts[i])
	
	def showAllExons(self):
		cpt = 0
		for i in range(len(self.transcripts)):
			for j in range(len(self.transcripts[i].exons)):
				print str(self.transcripts[i].exons[j])
				cpt += 1
		print "Nombre total d'exons : "
		print str(cpt)		
