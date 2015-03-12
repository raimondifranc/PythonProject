#!/usr/bin/python3

from modules import *
from test import *

parser = argparse.ArgumentParser(description="This program manages user arguments")

parser.add_argument('-i', '--input',
	dest = "infile",
	action = "store", 
	default = None,
	nargs = '+', # One or more files as input
	help = "Input: Choose one FASTA file (.fa/.fasta) or two CLUSTALW alignment files (.aln)")

# parser.add_argument('-o', '--output',
#                 dest = "output",
#                 action = "store",
#                 default = "./",
#                 help = "Print output in an output file")

parser.add_argument('-v', '--verbose',
            dest = "verbose",
            action = "store_true",
            default = False,
            help = "Print log in stderr")

parser.add_argument('-e', '--evalue',
            dest = "evalue",
            action = "store",
            default = 0.00001,
            type = int,
            help = "Specify e-value thereshold for selection of hits in BLAST output")	

parser.add_argument('-id', '--identity',
            dest = "identity",
            action = "store",
            default = 30,
            type = int,
            help = "Specify identity thereshold for selection of hits in BLAST output (integer)")	


options = parser.parse_args()

input_list = options.infile
verbose = options.verbose
evalue = options.evalue
identity = options.identity

#CAPTURING THE INPUT FILE(S)
sys.stderr.write("#"*10 + "\nStarting mirrorTree\n" + "#"*10 + "\n\n\n")

if len(input_list) < 3:
	for input_file in input_list:

		if os.path.isdir(input_file):
			sys.stderr.write("This program cannot handle directories as input.\nPlease, use files.\nAborting...\n")
			sys.exit()

		if os.path.isfile(input_file) and (".fa" or ".fasta") in input_file:
			if len(input_list) is 1:
				if verbose:
					sys.stderr.write("You have selected '%s' file to execute this awesome MirrorTree script.\n" %(input_file))
			else:
				sys.stderr.write("Impossible to handle this input request. Please, check the documentation.\nAborting...\n")
				sys.exit()

		elif len(input_list) is 2:
			if os.path.isfile(input_list[0]) and (".aln") in input_list[0] and os.path.isfile(input_list[1]) and (".aln") in input_list[1]:
				if verbose:
					sys.stderr.write ("You have selected '%s' and '%s' file. Starting from alignment directly. \n"
					%(input_list[0], input_list[1],))
				break
			else:
				sys.stderr.write("Impossible to handle this input request. Please, check the documentation.\nAborting...\n")
				sys.exit()
		else:
			sys.stderr.write("Impossible to handle this input request. Please, check the documentation.\nAborting...\n")
			sys.exit()
else:
	sys.stderr.write("Only able to handle one or two files!\nAborting...\n")
	sys.exit()

#EXECUTE BLAST WITH INPUT FILE

#IF INPUT IS ONE FASTA FILE

if len(input_list) == 1:
	sys.stderr.write("Connecting to BLAST... \n\n")

	blastlist = doBlast(input_list[0])


	sys.stderr.write("BLAST has finished.\n\n")


	#EXTRACT BEST HITS FROM BLAST XML FILE 

	(protfile_list, aln) = ([],[])

	for xml in blastlist:
		if verbose:
			sys.stderr.write("Extracting sequencies with e-value: '%s' from %s file after BLAST...\n" %(evalue, xml))

		protfile_list.append(selectProt(xml, evalue, identity))

		if verbose:
			sys.stderr.write("Done!\n")
	if verbose:
		sys.stderr.write("Comparing both BLAST output files to extract hit sequences (BEWARE! They are the same species for both proteins)...\nPerforming ClustalW alignment...\n")

	for element in comparefiles(protfile_list,input_list[0]):
		doClustalW(element, path_clustal) #PERFORMING CLUSTALW ALIGNMENT
		aln.append(AlignIO.read("%s.aln" %(element[:-3]), 'clustal')) #BUILDING DISTANCE MATRIX

	if verbose:
		sys.stderr.write("Comparison and ClustalW for both files done!\n")
		sys.stderr.write("Obtaining distance matrices from the alignments...\n")


# IF INPUT ARE TWO .aln FILES

else:
	aln = []
	for element in input_list:
		aln.append(AlignIO.read(element, 'clustal')) #BUILDING DISTANCE MATRIX
	if verbose:
		sys.stderr.write("Obtaining distance matrices from the alignments...\n")

#BUILDING FILOGENETIC TREE

calculator = DistanceCalculator("blosum62") # You can use blosum62/identity
constructor = DistanceTreeConstructor(calculator, 'nj') #Neighbour Joining = 'nj'

trees = [] 
for element in aln:
	trees.append((calculator.get_distance(element), constructor.build_tree(element), element ))


#BOOSTRAP

final_tree = []
dm = []

for element in trees:
	boostrap = list(bootstrap_trees(element[2], 100, constructor))
	support_tree = get_support(element[1], boostrap, len_trees=None)
	final_tree.append(support_tree)
	Phylo.draw_ascii(support_tree)
	dm.append(element[0])

#COMPUTE R CORRELATION 
if verbose:
	sys.stderr.write("Phylogenetic tree done!\n")

sys.stdout.write("This is the correlation for both proteins: %.3f \n"%(compute_r(dm)))

if verbose:
	sys.stderr.write("Plotting linear regression. Saved as 'plot.png'\n")

#PLOT LINEAR REGRESSION BETWEEN BOTH MATRIX
#plotData(dm)


