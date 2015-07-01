#Jackalope
Jackalope is a **visualization tool** for **GFF3** datas.
It offer a perl tool to get a GFF3 file directly from
ENSEMBL with a gene ENSEMBL Id you give.
It offer a python tool to analyse your GFF3 data in order
to produce a representative and dynamic scheme of your
gene structure (transcript and exons).
Dynamical events on the generated draw are powered by
JavaScript scripts and D3.js.

###Authors
Roxane Boyer => Contact at roxane.boyer18@gmail.com

###Dependencies
To be fully functionnal, Jackalope requires a few stuff like :
- **Python 2.7.6**
- **svgwrite 1.1.6**, a python module which allow svg draw with python
  Download here => [Get SVGwrite](https://pypi.python.org/pypi/svgwrite/)
- **networkx 1.10rc2**, a python module which allow to use graphs
  Download here => [Get networkx](https://pypi.python.org/pypi/networkx/)
  
###How does it works
You can use Jackalope in two different way:
- **You have an ENSEMBL id of a gene you want to study but no GFF3 file ?**

Then, just give this ID to jackalope, it will find it for you, and directly
analyse it.
- **You have your own GFF3 file and you want to analyze it ?**

You can also, but be careful... The GFF3 file have to fit to specific criterias.

*That's how is built a proper GFF3 file read by Jackalope : *

```
chr10	ENSEMBL	gene	103967201	104029233	.	+	.	ID=ENSG00000065613,species=Human
chr10	ENSEMBL	mRNA	103967201	104029233	.	+	.	ID=ENST00000335753,Parent=ENSG00000065613,species=Human
chr10	ENSEMBL	exon	103967201	103967895	.	+	.	ID=ENSE00001319269,Parent=ENST00000335753,species=Human

```

Important stuff for GFF3 files :
- Must contain only one gene by GFF
- Must always contains only thoses three tags (gene, then mRNA, then exon)
- Must have the last field with parental links between gene, transcripts (mRNA) and exons
- It recommanded to insert the species like in the example.
- Of course, the entire file will contains many mRNAs and many exons...

###How to get started with jackalope

#####*With an ENSEMBL id*
You must give first a "analysis name" that will be used at many times.
It recommended that this name fit to the gene name.
Then, you also have to give the gene ENSEMBL ID.
In the jackalope directory, try the lines below:

```
./draw_transcript.sh SLK ENSG00000065613

```
If it's your first try, it will create a "results" directory, where all your results
will be stored later.
Otherwise, it will create inside the results directory a new one, with your analysis name.

#####*With my one GFF3*
You must give first a "analysis name" that will be used at many times.
It recommended that this name fit to the gene name.
Then, you also have to give the GFF3 file, which must be
in the jackalope directoy.
In the jackalope directory, create SLK.gff3 and try the lines below:

```
./draw_transcript_ext.sh SLK SLK.gff3 

```

It work exactly the same that with an ensemblID, but it will be faster, because
you don't have to connect to ENSEMBL database.

###How do I get my results

In your "results" directory, you will soon have a huge list of directory containing
each of us the same structure :
- FASTA : contains, for each exon, a fasta file with the ensembl ID of the exon and his sequence
- GFF : it will contains, in any case, the GFF3 file used for the analysis
- SVG : it is possible to specify to the python programm to make an SVG output, with statics draw...
  But by default JSON output is used.
- JSON : this directory isn't the one your looking for... It's only used to store data between python and javascript
- report : Ah ! This is the one you are looking for, in this directory, you will have your HTML results page, waiting for you
  just open it with your favorite browser. Choose one of the three html file ! (you can naviguate between theeses differents pages after all)
