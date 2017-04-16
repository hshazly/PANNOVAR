#!/usr/bin/python
import csv
import ConfigParser
import os, re
import subprocess

def get_config_object():
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    return config

def read_dbs():
    config = get_config_object()
    #print config
    db_dir = config.get('General', 'Database')
    #db_dir = '/home/helshazly/genomekey-data/annovarext_data/annovar'
    db_info = {}
    for row in csv.DictReader(open('supported_databases.csv'), delimiter=','):
        row['db_directory'] = db_dir
        db_info[row['Database']] = row
    return db_info

def read_annotated_db(output_dir):
    dbs = []
    with open(os.path.join(output_dir, '.databases'), 'r') as f:
        dbs.append(f.read.strip)
    return dbs

def get_annovar_path():
    config = get_config_object()
    annovar_path = config.get('General', 'Annovar')
    return annovar_path



def vcf2annovar(vcf_file, out_dir):
    convert_script = os.path.join(get_annovar_path(), 'convert2annovar.pl')
    out_anno = os.path.join(out_dir, 'sample_anno')
    # | awk printf($1\"\t\"$2\"\t\"$3\"\t\"$4\"\t\"$5\"\t\"NR);for (i=6;i<=NF;i++) printf(\"\t\"$i); printf(\"\n\") > %s"
    cmd = "%s --allallele --format vcf4 %s --includeinfo | awk -f helper_script.awk > %s" % (convert_script, vcf_file, out_anno)
    #cmd = "%s --allallele --format vcf4 %s --includeinfo > %s" % (convert_script, vcf_file, out_anno)
  
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = process.communicate()
    return out_anno


def merge(input_vcf, out_dir, input_dirs):
    db_records = read_dbs()
    out_anno = os.path.abspath(vcf2annovar(input_vcf, out_dir))
    output_file = os.path.join(os.path.abspath(out_dir), 'annotation_table.txt')
    os.system('touch %s' % (output_file))
    

    ref_tables = dict(filter(lambda x: x[1]['columns or reference or standalone'] == 'r', db_records.items()))
     
    dirs_to_merge = filter(lambda d: d not in ref_tables, input_dirs)
    dirs_to_merge = dirs_to_merge.split("/")[:-1]
    dirs = []
    
    for dir in dirs_to_merge:
        dirs.append(dir.replace(" ", ""))

    input_files = []
   
    for dir in dirs:
        for file in os.listdir(os.path.join(os.path.dirname(out_dir), dir)):
            if file[-5:] == 'final':
               input_files.append(os.path.abspath(os.path.join(dir, file)))
    
    ccds_file = [file for file in input_files if 'CCDS_Gene' in file]
    input_files.remove(ccds_file[0])

    group1 = input_files[:9]
    group2 = input_files[9:18]
    group3 = input_files[18:26]
    #print (group1, group2, group3)

    g1_path = os.path.join(out_dir, 'group1.txt')
    cmd1 = '/usr/bin/Rscript %s %s %s %s' % ('merger.R', out_anno, g1_path, ",".join(group1))
    #print cmd1
    os.system('touch %s' % (g1_path))
    os.system(cmd1)

    g2_path = os.path.join(out_dir, 'group2.txt')
    cmd2 = '/usr/bin/Rscript %s %s %s %s' % ('merger.R', out_anno, g2_path, ",".join(group2))
    #print cmd2
    os.system('touch %s' % (g2_path))
    os.system(cmd2)

    cmd2_2 = 'cut -f9-17 %s > %s' % (g2_path, os.path.join(out_dir, 'tmp2'))
    os.system(cmd2_2)

    g3_path = os.path.join(out_dir, 'group3.txt')
    cmd3 = '/usr/bin/Rscript %s %s %s %s' % ('merger.R', out_anno, g3_path, ",".join(group3))
    #print cmd3
    os.system('touch %s' % (g3_path))
    os.system(cmd3)

    cmd3_2 = 'cut -f9-20 %s > %s' % (g3_path, os.path.join(out_dir, 'tmp3'))
    os.system(cmd3_2)

    g4_path = os.path.join(out_dir, 'group4.txt') 
    cmd4 = '/usr/bin/Rscript %s %s %s %s' % ('merger.R', out_anno, g4_path, ccds_file[0])
    #print cmd4
    os.system('touch %s' % (os.path.join(out_dir, 'group4.txt')))
    os.system(cmd4)

    cmd4_2 = 'cut -f9,10 %s > %s' % (g4_path, os.path.join(out_dir, 'tmp4'))
    os.system(cmd4_2)

    os.system('paste %s %s %s %s > %s' % (g1_path, os.path.join(out_dir, 'tmp2'), os.path.join(out_dir, 'tmp3'), os.path.join(out_dir, 'tmp4'), output_file))
    
    os.system('rm out/group* out/tmp*')

def annotate(dbname, input_vcf, output_dir):
    db_info = read_dbs()

    out_anno = os.path.abspath(vcf2annovar(input_vcf, output_dir))
    
    #create output dir
    db_output_dir = os.path.join(output_dir, dbname)
    os.system('mkdir -p %s' % (db_output_dir))
    #print db_output_dir

    #annovar path
    annovar_path = os.path.join(get_annovar_path(), 'annotate_variation.pl')
  
    db_record = db_info[dbname]
   
    annotation_type = db_record['annotation_type']
    buildver = db_record['builds']
    dbtype = db_record['dbtype']
    extra_args = ''
    
    if dbtype == 'generic':
       extra_args = '-genericdbfile %s_%s' % ('hg19', db_record['genericdbfile'])

    if db_record['dbtype_altered'] == 'T':
       dbtype = dbtype + '_altered'

    db_dir = db_record['db_directory']
    output_file = os.path.join(db_output_dir, 'annotated')

    cmd = "%s --%s --buildver %s -dbtype %s %s --outfile %s %s %s" % (annovar_path, annotation_type, buildver, dbtype, extra_args, output_file, out_anno, db_dir)   
    #print cmd
    return cmd


def cut(cut_in, columns):
    fields = ",".join(map(lambda x: str(x[1]), columns))
        
    #create final  annotated file with header
    cmd = 'cut -f%s %s' % (fields, cut_in)
    #print cmd
    process = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE)
    (out, err) = process.communicate()
    return out

def processAnnovar(annovar_output_files, annotation_type, dbname):
    #get list of cuts to make
    cuts_list = []
    #print (annovar_output_files, dbname)
    if annotation_type == "geneanno":
       #variant_func
       cuts_list.append({
           'columns': [(dbname + '_' + 'variantFunc', 1), (dbname + '_' + 'nearestGene', 2), ('ID', 8)],
           'cut_in': annovar_output_files[0],
       })
       #exonic_variant_func
       cuts_list.append({
           'columns': [(dbname + '_' + 'exonicFunc', 2), (dbname + '_' + 'exonInfo', 3), ('ID', 9)],
           'cut_in': annovar_output_files[1],
       })
    else: #filter and regionanno are the same
       cuts_list.append({
            'columns': [(dbname, 2), ('ID', 8)],
            'cut_in': annovar_output_files[0],
       })

    for cuts in cuts_list:
        columns, cut_in = cuts['columns'], cuts['cut_in']
        output_file = cut_in+'.cut.final'
        header = map(lambda x: x[0], columns)
        cut_stdout = cut(cut_in, columns)

    with open(output_file, 'w') as fwriter:
        fwriter.write("\t".join(header)+"\n")
        for line in cut_stdout:
            fwriter.write(line)

