import subprocess
import sys
import os
import time

def getNumberOfCores():
	output = run("qnodes")
	lines = output.split("\n")
	cores = 0
	for line in lines:
		if "np" in line:
			cores += int(line.split("=")[-1].strip())
	return cores

def runAsPBSJob(owner,id,executer):
	file=open('/tmp/'+owner+'.'+id,'w')
	file.write("#! /bin/bash\n")
	file.write(executer)
	file.flush()
	file.close()
	order ="qsub -N " + owner+'.'+id + " /tmp/"+owner+'.'+id
	#print "order: " + order
	pbsID =run(order).strip()
	#print "PBSID: "+pbsID
	return pbsID
	
def checkPBSstatus(id):
	list= run("qstat -f "+ id).split("\n")
	for item in list:
		if "job_state" in item:
			return item.split('=')[-1].strip()
	return "E"

def getStdoutStderr(id):
	list= run("qstat -f "+ id).split("\n")
	checkNext = False
	for item in list:
		if checkNext:
			if item.startswith("\t"):
				if lastItem == "o":
					outputPath += item[1:].strip()
				elif lastItem == "e":
					errorPath += item[1:].strip()
			checkNext = False
		if "Output_Path" in item:
			outputPath = item.split('=')[-1].strip().split(":")[-1]
			checkNext = True
			lastItem = "o"
		elif "Error_Path" in item:
			errorPath = item.split('=')[-1].strip().split(":")[-1]
			checkNext = True
			lastItem = "e"
			
	stderr = ""
	if os.path.isfile(errorPath):
		stderr = open(errorPath).read().strip()
	if stderr != "":
		stdout = ""
		if os.path.isfile(outputPath):
			stdout = open(outputPath).read().strip()
		if stdout != "":
			stdout += "\n\n"
		if stderr != "":
			stderr += "\n\n"
		message = "output for the job with id: %s is \n %s \n"
	
		sys.stdout.write(stdout)
		sys.stderr.write(stderr)
		
	#if os.path.isfile(errorPath):
	#	stderr = open(errorPath).read().strip()
	


def run(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output = process.communicate()
    retcode = process.poll()
    while retcode:
		time.sleep(2)
		process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
		output = process.communicate()
		retcode = process.poll()
    return output[0]
     
