#!/usr/bin/perl
use Bio::EnsEMBL::Registry;
use Getopt::Long;
use strict;
my $registry = 'Bio::EnsEMBL::Registry';
my $nomFichier;
my $nomSortie;
my $nomEspece;
$registry->load_registry_from_db(
    -host => 'ensembldb.ensembl.org', # alternatively 'useastdb.ensembl.org'
    -user => 'anonymous'
    -verbose => '0'
    -DB_VERSION => 'GRCh37.p13'
);

GetOptions ("in=s" => \$nomFichier, "out=s" => \$nomSortie, "specie=s" => \$nomEspece) or die ("Impossible de recuperer les options !");   
open(liste,"<".$nomFichier) or die("Impossible d'ouvrir le fichier listeIdGene.txt");
my @geneList = <liste>;
close(liste);
my $nbGene = 1;
foreach my $mygene (@geneList){
	chomp($mygene);
	&searchExon($nomEspece,$mygene,$registry,$nbGene,$nomSortie);
	$nbGene = $nbGene + 1;	
}

sub convertStrand {
	my $strand = $_[0];
	if($strand == 1){
		return "+";
	}
	else{
		return "-";
	}
}

sub writeGFF {
	my $seqid = $_[0];
	my $type = $_[1];
	my $start = $_[2];
	my $end = $_[3];
	my $score = $_[4];
	my $strand = $_[5];
	my $attributs = $_[6];
	my $nomFic = $_[7];
	open(f,">>".$nomFic) || die ("Vous ne pouvez pas créer/ouvrir le fichier");
	my $gff = $seqid . "\t" . "ENSEMBL" . "\t" . $type . "\t" . $start . "\t" . $end . "\t" . $score . "\t" . $strand . "\t" . "." . "\t" . $attributs . "\n";
	print f $gff;
	close(f);	
}

sub searchExon {
	#Récupération des arguments
	my $species = $_[0];
	my $geneId = $_[1];
	my $r = $_[2];
	my $nbGene = $_[3];
	my $nomSortie = $_[4];
	#Récupération du gène...
	my $gene_adaptor = $r->get_adaptor($species, 'Core', 'Gene' );
	my $gene = $gene_adaptor->fetch_by_stable_id($geneId);
	#...et de ses informations
	my $geneStart = $gene->seq_region_start();
	my $geneEnd = $gene->seq_region_end();
	my $geneStrand = $gene->seq_region_strand();
	$geneStrand = &convertStrand($geneStrand);
	#Ecriture de la première ligne du fichier GFF3 correspondant au gène
	&writeGFF("chr".$gene->slice->seq_region_name(),"gene",$geneStart,$geneEnd,".",$geneStrand,"ID=".$geneId.",species=".$species,$nomSortie);
	
	#Récupération des transcrits
	my @transcripts = @{ $gene->get_all_Transcripts() };
	foreach my $trans (@transcripts) {
		#Récupération de l'information concernant chaque transcrit
		my $transId = $trans->stable_id();
		my $transStart = $trans->seq_region_start();
		my $transEnd = $trans->seq_region_end();
		my $transStrand = $trans->seq_region_strand();
		$transStrand = &convertStrand($transStrand);
		#Ecriture d'un transcrit
		&writeGFF("chr".$gene->slice->seq_region_name(),"mRNA",$transStart,$transEnd,".",$transStrand,"ID=".$transId.",Parent=".$geneId.",species=".$species,$nomSortie);
		
		#Récupération des exons
		my @exons = @{ $trans->get_all_Exons };
		foreach my $exon (@exons) {
			#Récupération de l'information concernant chaque exon
			my $exonId = $exon->stable_id();
			my $exonStart = $exon->seq_region_start();
			my $exonEnd = $exon->seq_region_end();
			my $exonStrand = $exon->seq_region_strand();
			$exonStrand = &convertStrand($exonStrand);
			#Ecriture d'un exon
			&writeGFF("chr".$gene->slice->seq_region_name(),"exon",$exonStart,$exonEnd,".",$exonStrand,"ID=".$exonId.",Parent=".$transId.",species=".$species,$nomSortie);
		}
	}
	
}


