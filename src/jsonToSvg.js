var elt = document.getElementById('file');
var monTexte = elt.innerText || elt.textContent;
var exonFile = "html_things/images/" + monTexte;
$.getJSON(exonFile, function(data) {
	var svgContainer = d3.select("body").append("svg")
										.attr("width",data.xdessin)
										.attr("height",data.ydessin);
	var div = d3.select("body").append("div")   
								.attr("class", "tooltip")               
								.style("opacity", 0);
	for (var i in data.exons) {
		var rectangle = svgContainer.append("rect")
								.attr("x",data.exons[i].x)
								.attr("y",data.exons[i].y)
								.attr("width",data.exons[i].width)
								.attr("height",data.exons[i].height)
								.style("fill","rgb("+data.exons[i].color.r+","+data.exons[i].color.v+","+data.exons[i].color.b+")")
								.attr("id","exons_box")
								.append("title")
								.text(function(d) { return data.exons[i].id_exon; });
									
	}	
	for (var j in data.text_transcripts){
		text = svgContainer.append('foreignObject')
                        .attr('x', data.text_transcripts[j].x)
                        .attr('y', data.text_transcripts[j].y)
                        .attr('width', 180)
                        .attr('height', 25)
                        .append("xhtml:body")
						.html('<div >'+data.text_transcripts[j].id_transcript+'</div>')

	}
	
	var lineFunction = d3.svg.line()
								.x(function(d) { return d.x;})
								.y(function(d) { return d.y;})
								.interpolate("linear");
	
	for (var k in data.edges){
		var lineGraph = svgContainer.append("path")
									.attr("d", lineFunction(data.edges[k].path))
									.attr("stroke", "grey")
									.attr("stroke-width",2)
									.attr("fill","none")
									.attr("stroke-opacity", 0.3)
									.attr("id",data.edges[k].id_transcript);
							
	}
	
});


