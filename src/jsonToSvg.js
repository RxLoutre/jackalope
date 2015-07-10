//The name of the studied gene is in a div named "file"
var elt = document.getElementById('file');
var monTexte = elt.innerText || elt.textContent;
//exonFile will contains the path where the .json file containing informations concerning the draw
var exonFile = "html_things/images/" + monTexte;
//structure is used to see which exon belong to which transcript
//legend is used to create a color code for each transcript
var structureFile = "html_things/images/structure.json";
var legendFile = "html_things/images/legend.json";
//Creation of the SVG draw without any dynamic event
$.getJSON(exonFile, function(data) {
	var svgContainer = d3.select("body").append("svg")
										.attr("width",data.xdessin)
										.attr("height",data.ydessin);
	var div = d3.select("body").append("div")   
								.attr("class", "tooltip")               
								.style("opacity", 0);
	if(document.title == "SVG1"){						
		var scaleLine = svgContainer.append("line")
									.attr("x1", data.startScale)
									.attr("y1", 0)
									.attr("x2",data.startScale)
									.attr("y2", data.ydessin)
									.attr("stroke-width", 1)
									.attr("stroke","grey")
									.attr("stroke-opacity", 0.8)
									.style("stroke-dasharray", ("2, 2"));
		var scaleLine = svgContainer.append("line")
									.attr("x1", data.endScale)
									.attr("y1", 0)
									.attr("x2",data.endScale)
									.attr("y2", data.ydessin)
									.attr("stroke-width", 1)
									.attr("stroke","grey")
									.attr("stroke-opacity", 0.8)
									.style("stroke-dasharray", ("2, 2"));
		var step = data.stepScale;													
		for (i = 0; i < 9; i++){
			var scaleLine = svgContainer.append("line")
									.attr("x1", data.startScale + step)
									.attr("y1", 0)
									.attr("x2", data.startScale + step)
									.attr("y2", data.ydessin)
									.attr("stroke-width", 1)
									.attr("stroke","grey")
									.attr("stroke-opacity", 0.8)
									.style("stroke-dasharray", ("2, 2"));
			step = step + data.stepScale;
		}
	}
	for (var i in data.exons) {
		var rectangle = svgContainer.append("rect")
								.attr("x",data.exons[i].x)
								.attr("y",data.exons[i].y)
								.attr("width",data.exons[i].width)
								.attr("height",data.exons[i].height)
								.attr("stroke","green")
								.style("fill","rgb("+data.exons[i].color.r+","+data.exons[i].color.v+","+data.exons[i].color.b+")")
								.attr("id", data.exons[i].id_exon)
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
						.html('<div >'+data.text_transcripts[j].id_transcript+'</div>');

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
									.attr("stroke-opacity", 0.2)
									.style("stroke-dasharray", ("3, 3"))
									.attr("id",data.edges[k].id_transcript);
							
	}
	
});
//Add dynamic event on exons
$.getJSON(structureFile, function(data) {
	d3.selectAll("rect")
		.on("mouseover", function() {
			d3.select(this).attr("opacity",0.5);
			var exon = d3.select(this).attr("id");			
			for (var i in data.exons){
				if(data.exons[i].id == exon){
					for (var ts in data.exons[i].parents_transcripts){
						d3.selectAll("#"+data.exons[i].parents_transcripts[ts].id)
							.attr("stroke-opacity" , 1)
							.attr("stroke","rgb("+data.exons[i].parents_transcripts[ts].color.r+","+data.exons[i].parents_transcripts[ts].color.v+","+data.exons[i].parents_transcripts[ts].color.b+")");
						for (var rel_ex in data.exons[i].parents_transcripts[ts].related_exons){
							d3.selectAll("#"+data.exons[i].parents_transcripts[ts].related_exons[rel_ex].id).attr("opacity",0.5);
						}
					}
				}
			
			}
		})
		.on("mouseout", function() {
			d3.select(this).attr("opacity",1);
			var exon = d3.select(this).attr("id");			
			for (var i in data.exons){
				if(data.exons[i].id == exon){
					for (var ts in data.exons[i].parents_transcripts){
						d3.selectAll("#"+data.exons[i].parents_transcripts[ts].id)
							.attr("stroke-opacity" , 0.2)
							.attr("stroke","grey");
						for (var rel_ex in data.exons[i].parents_transcripts[ts].related_exons){
							d3.selectAll("#"+data.exons[i].parents_transcripts[ts].related_exons[rel_ex].id).attr("opacity",1);
						}	
					}
				}
			}

		})
		.on("click", function() {
			var exon = d3.select(this).attr("id");	
			var start = document.getElementById("start").textContent;
			var end = d3.select("#end");
			var length = d3.select("#length");
			var parents = d3.select("#parents");
			for (var i in data.exons){
				if(data.exons[i].id == exon){
					var len = data.exons[i].end - data.exons[i].start;
					document.getElementById("exon_id").textContent = exon;
					document.getElementById("start").textContent =  data.exons[i].start;
					document.getElementById("end").textContent = data.exons[i].end;
					document.getElementById("length").textContent =  len;
					document.getElementById("parents").textContent = "";
					for (var ts in data.exons[i].parents_transcripts){
						document.getElementById("parents").textContent = document.getElementById("parents").textContent + data.exons[i].parents_transcripts[ts].id + ", ";
					}
				}
			}
		});
		
});
//Create a dynamic legend for transcript and their color (only for SVG3)
$.getJSON(legendFile, function(data) {
	
	var nb_ts = data.nb_trans;
	var h = 30 * nb_ts
	var svgFooter = d3.select("#legend").append("svg")
										.attr("width",460)
										.attr("height",h);
		
	for (var i in data.transcripts){
		var text = svgFooter.append('foreignObject')
							.attr('x', 10)
							.attr('y', i*20)
							.attr('width', 180)
							.attr('height', 25)
							.append("xhtml:body")
							.html('<div >'+data.transcripts[i].id+'</div>');
		var ellipse = svgFooter.append("ellipse")
								.attr("cx",250)
								.attr("cy",i*20+15)
								.attr("rx",20)
								.attr("ry",10)
								.attr("stroke","green")
								.style("fill","rgb("+data.transcripts[i].color.r+","+data.transcripts[i].color.v+","+data.transcripts[i].color.b+")")
								.attr("id", data.transcripts[i].id)
								.append("title")
								.text(function(d) { return data.transcripts[i].id });
								
								
									
	}
	d3.selectAll("ellipse").on("mouseover", function() {
			d3.select(this).attr("opacity",0.5);
			var id_ts = d3.select(this).attr("id");
			d3.selectAll("#"+id_ts).attr("stroke-opacity" , 1)
									.attr("stroke","black");
			for (var i in data.transcripts){
				if(data.transcripts[i].id == id_ts){
					for (var exon in data.transcripts[i].exons ){
						d3.select("#"+data.transcripts[i].exons[exon].id).attr("opacity",0.5);
					}
				}
			}
		})
		.on("mouseout", function() {
		d3.select(this).attr("opacity",1);
			var id_ts = d3.select(this).attr("id");
			d3.selectAll("#"+id_ts).attr("stroke-opacity" , 0.5)
									.attr("stroke","grey");
			for (var i in data.transcripts){
				if(data.transcripts[i].id == id_ts){
					for (var exon in data.transcripts[i].exons ){
						d3.select("#"+data.transcripts[i].exons[exon].id).attr("opacity",1);
					}
				}
			}
		})
	
	
		
});
//A function to search a particular exon ID on the document
function listenExonSearch() {
    var exon = document.getElementById('search_exon');
	var exon_id = exon.value;
	var selection = d3.selectAll("#"+exon_id).attr("stroke","red")
							.attr("stroke-width",4);  
	if(selection.empty()){
		alert("No exon matches witht his ID.");
	}
	else {
		alert("An exon with this ID matches !");
	}
	 
}
//A function to reset each highlighted exon
function resetExonSearch(){
	d3.selectAll("rect").attr("stroke","green")
	.attr("stroke-width",1);   
}
//A function to open a FASTA file of a selected exon
function getFasta(){
	var exon = document.getElementById("exon_id").textContent;
	var fastaLink = "FASTA/"+exon+".fasta";
	window.open(fastaLink);
}
