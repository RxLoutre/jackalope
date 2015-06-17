cd results
i=0
for directory in $(ls)
do
if
	[ -d $directory ]
then
	rep[$i]=$(basename $directory)
	((i++))
fi
done
for k in $(seq $i)
do
	echo "<a href=\"jackalope_svg1_\""<li>""${rep[$k]}""</li>" >> analyzedGenesList.txt
done
