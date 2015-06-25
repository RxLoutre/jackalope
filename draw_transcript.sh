OUTPUTDIR=$1
GENELIST=$2
GFFFLAG=".gff3"
SVGFLAG=".svg"
JSONFLAG=".json"
GFFOUTPUT="$OUTPUTDIR""$GFFFLAG"
SVGOUTPUT1="$OUTPUTDIR""1""$SVGFLAG"
SVGOUTPUT2="$OUTPUTDIR""2""$SVGFLAG"
SVGOUTPUT3="$OUTPUTDIR""3""$SVGFLAG"
JSONOUTPUT1="$OUTPUTDIR""1""$JSONFLAG"
JSONOUTPUT2="$OUTPUTDIR""2""$JSONFLAG"
JSONOUTPUT3="$OUTPUTDIR""3""$JSONFLAG"

if [ -d "results" ]; then
 echo "Création nouveau dossier dans results"
else
 mkdir results
fi

mkdir results/${OUTPUTDIR}
mkdir results/${OUTPUTDIR}/GFF
mkdir results/${OUTPUTDIR}/SVG
mkdir results/${OUTPUTDIR}/JSON
mkdir results/${OUTPUTDIR}/report
echo ${GENELIST} >> results/${OUTPUTDIR}/geneList.txt
perl src/fetch_gene_annotation.pl -in results/${OUTPUTDIR}/geneList.txt -out results/${OUTPUTDIR}/GFF/${GFFOUTPUT} -specie Human
python src/drawIsoforms.py --proportionnal --print-count --annotation results/${OUTPUTDIR}/JSON/structure.json results/${OUTPUTDIR}/GFF/${GFFOUTPUT} results/${OUTPUTDIR}/JSON/${JSONOUTPUT1}
python src/drawIsoforms.py --fixed results/${OUTPUTDIR}/GFF/${GFFOUTPUT} results/${OUTPUTDIR}/JSON/${JSONOUTPUT2}
python src/drawIsoforms.py --listed results/${OUTPUTDIR}/GFF/${GFFOUTPUT} results/${OUTPUTDIR}/JSON/${JSONOUTPUT3}
cp -R html_things results/${OUTPUTDIR}/report
cp results/${OUTPUTDIR}/JSON/${JSONOUTPUT1} results/${OUTPUTDIR}/report/html_things/images/${JSONOUTPUT1}
cp results/${OUTPUTDIR}/JSON/${JSONOUTPUT2} results/${OUTPUTDIR}/report/html_things/images/${JSONOUTPUT2}
cp results/${OUTPUTDIR}/JSON/${JSONOUTPUT3} results/${OUTPUTDIR}/report/html_things/images/${JSONOUTPUT3}
cp src/jsonToSvg.js results/${OUTPUTDIR}/report/jsonToSvg.js
cp results/${OUTPUTDIR}/JSON/structure.json results/${OUTPUTDIR}/report/html_things/images/structure.json
sed -e "s|%%AnalysisName%%|${OUTPUTDIR}|g" html_things/jackalope_svg1.html > html_things/jackalope_svg1Inter1.html
sed -e "s|%%AnalysisTag%%|${JSONOUTPUT1}|g" html_things/jackalope_svg1Inter1.html > html_things/jackalope_svg1Inter2.html
sed -e "s|%%SVG1%%|html_things/images/${SVGOUTPUT1}|g" html_things/jackalope_svg1Inter2.html > results/${OUTPUTDIR}/report/jackalope_svg1_${OUTPUTDIR}.html
sed -e "s|%%AnalysisName%%|${OUTPUTDIR}|g" html_things/jackalope_svg2.html > html_things/jackalope_svg2Inter1.html
sed -e "s|%%AnalysisTag%%|${JSONOUTPUT2}|g" html_things/jackalope_svg2Inter1.html > html_things/jackalope_svg2Inter2.html
sed -e "s|%%SVG2%%|html_things/images/${SVGOUTPUT2}|g" html_things/jackalope_svg2Inter2.html > results/${OUTPUTDIR}/report/jackalope_svg2_${OUTPUTDIR}.html
sed -e "s|%%AnalysisName%%|${OUTPUTDIR}|g" html_things/jackalope_svg3.html > html_things/jackalope_svg3Inter1.html
sed -e "s|%%AnalysisTag%%|${JSONOUTPUT3}|g" html_things/jackalope_svg3Inter1.html > html_things/jackalope_svg3Inter2.html
sed -e "s|%%SVG3%%|html_things/images/${SVGOUTPUT3}|g" html_things/jackalope_svg3Inter2.html > results/${OUTPUTDIR}/report/jackalope_svg3_${OUTPUTDIR}.html
#firefox results/${OUTPUTDIR}/report/jackalope_svg3_${OUTPUTDIR}.html
