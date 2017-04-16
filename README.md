
# What is PANNOVAR?
PANNOVAR is a package that provides a way to annotate VCF files in a parallel and fast way. 
The script uses PBS job schedular to execute annotation jobs in parallel.

# How PANNOVAR works?
PANNOVAR accepts a VCF file and annotate it against ALL the databases exist in supported_databases.csv file.
Using macro-parallelism, It will create jobs as many as the databases you will annotate against (which exists
in supported_databases.csv), each annotation command works on the whole VCF file (no data splitting) then it
will merge all the different annotation results into annotation_table.txt

# How to use?
Before you use pannovar script you have to adjust config.ini file with the databases directory
path and annovar scripts path.
PANNOVAR will annotate against databases exist in supported_databases.csv, it will annotate against
whatever databases in that file, if the database exists it will annotate, if the database exists in
supported_databases.csv and not exist in the databases directory it won't annotate.

# Prerequistes: 
1. PBS job schdular must be installed
2. All databases exist in the directory specified in config.ini
3. Rscript must be installed

# COMMAND:
./pannovar -i <vcf_file> <output_directory>
vcf_file	Input VCF file
output_directory	the output directory which will contain the output (the script will create it)

# OUTPUT:
In the specified output directory you will have 3 files:
1- annotation_table.txt: contains annotation results. 
2- annotation_report.csv: annotation results in CSV format.
3- annotated.log: a log file which contains all the database and whether it annotated successfully or there is an error.
