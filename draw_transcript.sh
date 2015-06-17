OUTPUTDIR=$1
GENELIST=$2
GFFFLAG=".gff3"
SVGFLAG=".svg"
GFFOUTPUT="$OUTPUTDIR""$GFFFLAG"
SVGOUTPUT1="$OUTPUTDIR""1""$SVGFLAG"
SVGOUTPUT2="$OUTPUTDIR""2""$SVGFLAG"
SVGOUTPUT3="$OUTPUTDIR""3""$SVGFLAG"
if [ -d "results" ]; then
 echo "Création nouveau dossier dans results"
else
 mkdir results
fi

mkdir results/${OUTPUTDIR}
mkdir results/${OUTPUTDIR}/GFF
mkdir results/${OUTPUTDIR}/SVG
mkdir results/${OUTPUTDIR}/report
echo ${GENELIST} >> results/${OUTPUTDIR}/geneList.txt
perl src/fetch_gene_annotation.pl -in results/${OUTPUTDIR}/geneList.txt -out results/${OUTPUTDIR}/GFF/${GFFOUTPUT}
python src/drawIsoforms.py --proportionnal --print-count results/${OUTPUTDIR}/GFF/${GFFOUTPUT} results/${OUTPUTDIR}/SVG/${SVGOUTPUT1}
python src/drawIsoforms.py --fixed results/${OUTPUTDIR}/GFF/${GFFOUTPUT} results/${OUTPUTDIR}/SVG/${SVGOUTPUT2}
python src/drawIsoforms.py --listed results/${OUTPUTDIR}/GFF/${GFFOUTPUT} results/${OUTPUTDIR}/SVG/${SVGOUTPUT3}
cp -R html_things results/${OUTPUTDIR}/report
cp results/${OUTPUTDIR}/SVG/${SVGOUTPUT1} results/${OUTPUTDIR}/report/html_things/images/${SVGOUTPUT1}
cp results/${OUTPUTDIR}/SVG/${SVGOUTPUT2} results/${OUTPUTDIR}/report/html_things/images/${SVGOUTPUT2}
cp results/${OUTPUTDIR}/SVG/${SVGOUTPUT3} results/${OUTPUTDIR}/report/html_things/images/${SVGOUTPUT3}
sed -e "s|%%AnalysisName%%|${OUTPUTDIR}|g" html_things/jackalope_svg1.html > html_things/jackalope_svg1Inter.html
sed -e "s|%%SVG1%%|html_things/images/${SVGOUTPUT1}|g" html_things/jackalope_svg1Inter.html > results/${OUTPUTDIR}/report/jackalope_svg1_${OUTPUTDIR}.html
sed -e "s|%%AnalysisName%%|${OUTPUTDIR}|g" html_things/jackalope_svg2.html > html_things/jackalope_svg2Inter.html
sed -e "s|%%SVG2%%|html_things/images/${SVGOUTPUT2}|g" html_things/jackalope_svg2Inter.html > results/${OUTPUTDIR}/report/jackalope_svg2_${OUTPUTDIR}.html
sed -e "s|%%AnalysisName%%|${OUTPUTDIR}|g" html_things/jackalope_svg3.html > html_things/jackalope_svg3Inter.html
sed -e "s|%%SVG3%%|html_things/images/${SVGOUTPUT3}|g" html_things/jackalope_svg3Inter.html > results/${OUTPUTDIR}/report/jackalope_svg3_${OUTPUTDIR}.html
