import os
import time
import random
import MySQLdb
import string
import subprocess
import mimetypes
import config
import xml.dom.minidom
import simplejson


validChars  = set(string.letters + string.digits + " -=_.()/+*^,:?!")

# characters that are allowed but need to be escaped
mappedChars = { '>' :'__gt__', 
                 '<' :'__lt__', 
                 "'" :'__sq__',
                 '"' :'__dq__',
                 '[' :'__ob__',
                 ']' :'__cb__',
                 '{' :'__oc__',
                 '}' :'__cc__',
                 '@' : '__at__',
                 '\n' : '__cn__',
                 '\r' : '__cr__',
                 '\t' : '__tc__'
                 }

def signin(userName,password):
	db = MySQLdb.connect(host=config.usersDBhost, user=config.usersDBun, passwd=config.usersDBpwd,db=config.usersDB)
	cursor=db.cursor()
	cursor.execute("Select Rand from users where username = '" + userName + "' and password='" + password + "'" )
	c = cursor.fetchone()
	#cursor.close()
	if (c !=    None):
		uuid = c[0]
		"""
		if "demo" in userName:
			demoFilePath = os.path.join(config.workflows,"demo")
			if os.path.isfile(demoFilePath):	
				demoFile = open(demoFilePath)
				demoAccounts = loads(demoFile.read())
				if len(demoAccounts) > 0:					
					demoAccount = demoAccounts[0]
					demoAccounts = demoAccounts[1:]
					demoFile = open(demoFilePath,"w")
					demoFile.write(dumps(demoAccounts))
					demoFile.close()
					cursor.execute("Select Rand from users where username = '" + demoAccount + "'")
					c = cursor.fetchone()
					if (c !=    None):
						uuid = c[0]
				else:
					demoFile = open(demoFilePath,"w")
					demoFile.write(dumps(["demo","demo1","demo2","demo3","demo4"]))
					demoFile.close()
		"""
		return uuid
	return None

def RestoreText(text):
    """Restores sanitized text"""
    for key, value in mappedChars.items():
        text = text.replace(value, key)
    return text

def SanitizeText(text):
    """Restricts the characters that are allowed in a text"""
    out = []
    for c in text:
        if c in validChars:
            out.append(c)
        elif c in mappedChars:
            out.append(mappedChars[c])
        else:
            out.append('X') # makes debugging easier
    return ''.join(out)


def ListDirFiles(dirPath):
	if os.path.isdir(dirPath):
		fileNames = [f for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, f)) and f[len(f)-1] != "~"]
		fileNames = sorted(fileNames)
		return fileNames
	else:
		return []
		
def ListDirDirs(dirPath):
	if os.path.isdir(dirPath):
		fileNames = [f for f in os.listdir(dirPath) if os.path.isdir(os.path.join(dirPath, f)) and f[0] != "."]
		fileNames = sorted(fileNames)
		return fileNames
	else:
		return []
		
def ListDirContents(dirPath):
	if os.path.isdir(dirPath):
		fileNames = [f for f in os.listdir(dirPath) if f[len(f)-1] != "~"]
		fileNames = sorted(fileNames)
		return fileNames
	else:
		return []

def GetXmlText(element,name):
	if element.hasAttribute(name):
		return element.getAttribute(name)
	else:
		nameElements = element.getElementsByTagName(name)
		if len(nameElements) == 1:
			return nameElements[0].firstChild.nodeValue
		else:
			return ""
def iterparent(tree):
    for parent in tree.getiterator():
        for child in parent:
            yield parent, child
	
			
def StringAsBool( string ):
    if str( string ).lower() in ( 'true', 'yes', 'on' , '1' ):
        return True
    else:
        return False

def GetAttribute(element,attributeName,defaultValue):
	if element.hasAttribute(attributeName):
		return element.getAttribute(attributeName)
	else:
		return defaultValue

def GetRandomString():
	rand = random.random()
	rand = str(rand)
	rand = rand[2:len(rand)]
	return rand

def GetRandomPath(directory):
	rand = GetRandomString()
	while os.path.isfile(os.path.join(directory,rand)):
		rand = GetRandomString()
	return os.path.join(directory,rand)

def GetNumOfListElements(input,count=0):
	for item in input:
		if isinstance(item,list):
			count = GetNumOfListElements(item,count)
		else:
			count += 1
	return count
	
def GetProperList(input):
	if isinstance(input,list):
		if len(input) == 1:
			return GetProperList(input[0])
	return input
	
def RemoveEmptyList(input):
	input = GetProperList(input)
	if isinstance(input,list):
		if len(input) == 0:
			return None
		for i in range(0,len(input)):
			input[i] = RemoveEmptyList(input[i])
		toBeDeleted = []
		for i in range(0,len(input)):
			if input[i] == None:
				toBeDeleted.append(i)
		toBeDeleted.reverse()
		for index in toBeDeleted:
			del input[index]
		if len(input) == 0:
			return None
	else:
		return input
	return input

def CollectUnreferencedFiles(filesList):
	if isinstance(filesList,list):
		for j in range(0,len(filesList)):
			if isinstance(filesList[j],list):
				filesList[j] =  CollectUnreferencedFiles(filesList[j])
			else:
				dirName = os.path.dirname(filesList[j])
				baseName = os.path.basename(filesList[j])+"."
				unreferencedFiles = [os.path.join(dirName,f) for f in os.listdir(dirName) if f.startswith(baseName) and f[len(f)-1]!="~"]
				if len(unreferencedFiles) > 0:
					filesList[j] = sorted(unreferencedFiles)
		return filesList
	else:
		dirName = os.path.dirname(filesList)
		baseName = os.path.basename(filesList)+"."
		unreferencedFiles = [os.path.join(dirName,f) for f in os.listdir(dirName) if f.startswith(baseName) and f[len(f)-1]!="~"]
		if len(unreferencedFiles) > 0:
			return sorted(unreferencedFiles)
		else:
			return filesList


def GetRefFileContents(refFilePath):
	input = simplejson.loads(open(refFilePath).read().strip())
	input = GetProperList(input)
	return CollectRefFileContent(input)

def CollectRefFileContent(input):
	if isinstance(input,list):
		for i in range(0,len(input)):
			if isinstance(input[i],list):
				input[i] = CollectRefFileContent(input[i])
			else:
				if os.path.isfile(input[i]):
					input[i] = open(input[i]).read().strip()
				else:
					input[i] = ""
		return input
	else:
		return open(input).read().strip()

#seed to file type
def GetFileType(path):
	try:
		mime = subprocess.Popen("/usr/bin/file -i "+path, shell=True,stdout=subprocess.PIPE).communicate()[0].split(" ")[1][:-1]
	except:
		mime = "text/plain"
	return mime
	if mime.startswith("image"):
		return "image"
	elif mime.startswith("text"):
		return "plain text"
	else:
		return mime
			
def GetFileExtension(type):
	types = {}
	types["application/postscript"] = ".ps"
	types["application/pdf"] = ".pdf"
	types["image/png"] = ".png"
	types["image/jpeg"] = ".jpeg"
	types["image/pjpeg"] = ".jpeg"
	types["image/gif"] = ".gif"
	types["image/tiff"] = ".tif"
	types["image/jpeg"] = "."
	if type in types:
		return types[type]
	else:
		extension = mimetypes.guess_extension(type)
		if extension is None:
			return ".txt"
		else:
			return extension

def PrepareData(filePath):
	if os.path.getsize(filePath) == 0:
		return ""
	dataType = GetFileType(filePath)
	if dataType.startswith("image"):
		return "This is an image file, click on the link above to view it."
	elif dataType == "text/plain":
		return str(open(filePath).read(100)).replace("<","&lt;").replace(">","&gt;").replace("\"","&quot;")
	else:
		return dataType
	
		

def PrepareListHtml(input,i=0,output=""):
	input = GetProperList(input)
	if isinstance(input,list):
		output += "<ul>"
		for item in input:
			i += 1
			if i >= 5:
				break
			if not isinstance(item,list):
				if os.path.isfile(item):
					data = PrepareData(item)
					if len(data) > 0:
						output += "<li>"+data+"</li>"
			else:
				rV = PrepareListHtml(item,i,output)
				output = rV[0]
				i = rV[1]
		i -= 1
		output +=  "</ul>"
		if output == "<ul></ul>":
			output = ""
		return output,i
	else:
		if os.path.isfile(input):
			data = PrepareData(input)
			return data,i
		else:
			return "",i

def DisplayList(input):
	return PrepareListHtml(input)[0]
	
"""	
def DisplayList(input,i=0,output=""):
	output += "-----------------" + "\n"
	for item in input:
		if not isinstance(item,list):
			tabs = i* "      "
			output += tabs + str(open(item).read(100)) + "\n"
		else:
			#output += "-----------------" + "\n"	
			i += 1
			output = DisplayList(item,i,output)
	i -= 1
	output +=  "-----------------" + "\n"
	return output
"""


def CheckIfWorkflowExists(workflowName,uuid):
	workflowsPath = os.path.join(config.workflows,uuid)
	return os.path.isfile(os.path.join(workflowsPath,workflowName))


def ExtractUUID(req,owner=""):
	"""
	this method to exrtact user id (uuid) from the cookies on the user machine.
	if owner is supplied the fn return owner
	
	Input
	
	:req: the Request object to find the uuid associated with it
	
	:owner: (String) the uuid of the request if it is unknown dont pass it
	
	Output
	
	:uuid: Output is (String) the uuid of the request 
	
	"""
	if owner != "":
		return owner
	from mod_python import Cookie
	uuid =  ""
	if not isinstance(req,str):
		cookies = Cookie.get_cookies(req)
		if "mart.Login" in cookies:
			uuidString = str(cookies["mart.Login"]).split("=")[1]
			if uuidString != "":
				uuid = uuidString
	return uuid



#support multiple users

def lower_if_possible(x):
    try:
        return x.lower()
    except AttributeError:
        return x

def SortDictionary(adict,substitute=True):
	if substitute:
		iTuples = [(v,k) for k,v in adict.items()]
		iTuples.sort(key=lambda x: map(lower_if_possible,x))
		iTuples = [(k,v) for (v,k) in iTuples]
	else:
		iTuples = [(k,v) for k,v in adict.items()]
		iTuples.sort(key=lambda x: map(lower_if_possible,x))
	return iTuples


def GetToolPath(toolId):
	doc = xml.dom.minidom.parse(config.toolsConfig)
	if toolId in config.patterns.split(','):
		node = doc.getElementsByTagName("controlbox")[0]
		nodes = node.getElementsByTagName("control")
	else:
		node = doc.getElementsByTagName("toolbox")[0]
		nodes = node.getElementsByTagName("tool")
	for node in nodes :
            if node.getAttribute("id") == toolId:
                return node.getAttribute("file")
	return ""
	
def GetAvailableScripts(uuid):
	return ListDirFiles(os.path.join(config.scripts,uuid))
def GetNumberOfOutputs(toolId) :
	toolPath = GetToolPath(toolId)
	if toolPath == "" : 
		return 0
	else :
		toolPath = os.path.join(config.toolsDirec,toolPath)
		doc = xml.dom.minidom.parse(toolPath)
		toolNodes = doc.getElementsByTagName("tool")
		i = 0
		outputNode = toolNodes[0].getElementsByTagName("outputs")[0]
		for outputNode in outputNode.getElementsByTagName("data") :
			i += 1
		return i

def GetOutputsDetails(toolId) :
	toolPath = GetToolPath(toolId)
	outputs = []
	if toolPath == "" : 
		return outputs
	else :
		toolPath = os.path.join(config.toolsDirect,toolPath)
		doc = xml.dom.minidom.parse(toolPath)
		toolNodes = doc.getElementsByTagName("tool")
		i = 0
		outputNode = toolNodes[0].getElementsByTagName("outputs")[0]
		for outputNode in outputNode.getElementsByTagName("data") :
			outputs.append(outputNode.getAttribute("name"))			
		return outputs


def GetNumOutputs(steps) :
	outputs = 0
	for step in steps :
		outputs += GetNumberOfOutputs(step.ToolID)
	return outputs

def findParents(element):
	parents = {}
	if element.parentNode.parentNode.nodeName == "#document":
		parents[0]=element.parentNode
	else:
		parentName = element.parentNode.parentNode.nodeName
		index = 0
		while parentName != "#document":
			parents[index]=element.parentNode
			index += 1 
			parentName = element.parentNode.parentNode.nodeName
			element = element.parentNode.parentNode

	return parents

def GetPortType(processorID,portName,direction):
	toolPath = os.path.join(config.toolsDirect,GetToolPath(processorID))
	toolDoc = xml.dom.minidom.parse(toolPath)
	if direction == "in":
		inputElements = toolDoc.getElementsByTagName("inputs")[0].getElementsByTagName("param")
		for inputElement in inputElements:
			if inputElement.getAttribute("name") == portName:
				return inputElement.getAttribute("listed")
	else:
		outputElements = toolDoc.getElementsByTagName("outputs")[0].getElementsByTagName("data")
		for outputElement in outputElements:
			if outputElement.getAttribute("name") == portName:
				return outputElement.getAttribute("listed")
	

def CheckInputLists(doc):
	sources = {}
	sourceElements = doc.getElementsByTagName("s:source")
	for sourceElement in sourceElements:
		sources[sourceElement.getAttribute("name")] = sourceElement
	
	processorElements = doc.getElementsByTagName("s:processor")
	processors = {}
	for processorElement in processorElements:
		processors[processorElement.getAttribute("name")] = {}
		processors[processorElement.getAttribute("name")]["element"] = processorElement
		processors[processorElement.getAttribute("name")]["listEnabled"] = 1
		
	linkElements = doc.getElementsByTagName("s:link")
	for linkElement in linkElements:
		sinkElementName = linkElement.getAttribute("sink").split(":")[0]
		sinkElementPortName = linkElement.getAttribute("sink").split(":")[1]
		sinkElementID = processors[sinkElementName]["element"].getAttribute("id")
		processors[sinkElementName]["listEnabled"] = not int(GetPortType(sinkElementID,sinkElementPortName,"in"))
		"""
		if not int(type):
			sourceElementName = linkElement.getAttribute("source").split(":")[0]
			if len(linkElement.getAttribute("source").split(":")) > 1:
				sourceElementID = processors[sourceElementName]["element"].getAttribute("id")
				if sourceElementID == "beanshellRunner":
					type = 0
				else:
					sourceElementPortName = linkElement.getAttribute("source").split(":")[1]
					type = int(GetPortType(sourceElementName,sourceElementPortName,"out"))
			else:
				type = sources[sourceElementName].getAttribute("listEnabled")
				
			if int(type):
				processors[sinkElementName]["listEnabled"] = 1
		"""
	for processor in processors:
		if processors[processor]["listEnabled"]:
			parameterElement = doc.createElementNS("","s:parameter")
			parameterElement.setAttributeNS("","name","listEnabled")
			value = doc.createTextNode(str(processors[processor]["listEnabled"]))
			parameterElement.appendChild(value)
			processors[processor]["element"].appendChild(parameterElement)
	
	return doc

def PrepareLinks(workflow,uuid,prepared=1):
	doc = workflow
	#doc = CheckInputLists(doc)
	scuflElement = doc.getElementsByTagName("s:scufl")[0]
	processor_parents = {}
	iterateElements = {}
	processorElements = doc.getElementsByTagName("s:processor")
	subworkflowElements = {}
	for processorElement in processorElements:
		if processorElement.getAttribute("id") != "iteration":
			processor_parents[processorElement.getAttribute("name")] = findParents(processorElement)
			if processorElement.getAttribute("id") == "subworkflow":
				subworkflowElements[processorElement.getAttribute("name")] =  processorElement
		else:
			processor_parents[processorElement.getAttribute("name")] = findParents(processorElement)
			iterateElements[processorElement.getAttribute("name")] = {}
			iterateElements[processorElement.getAttribute("name")]['sources'] = 1
			iterateElements[processorElement.getAttribute("name")]['sinks'] = 1

	source_parents = {}
	sourceElements = doc.getElementsByTagName("s:source")
	for sourceElement in sourceElements:
		processor_parents[sourceElement.getAttribute("name")] = findParents(sourceElement)

	sink_parents = {}
	sinkElements = doc.getElementsByTagName("s:sink")
	for sinkElement in sinkElements:
		processor_parents[sinkElement.getAttribute("name")] = findParents(sinkElement)

	linkElements = doc.getElementsByTagName("s:link")
	#for linkElement in linkElements:
		#if linkElement.getAttribute("source").split(":")[0] in subworkflowElements:
		#linkElement.setAttributeNS("","source",linkElement.getAttribute("source").split(":")[0]+":"+GetActualSubworkflowPortName(linkElement.getAttribute("source"),subworkflowElements,uuid))			

	linkElements = doc.getElementsByTagName("s:link")
	for linkElement in linkElements:
		sourceName = linkElement.getAttribute("source").split(":")[0]
		if len(linkElement.getAttribute("source").split(":")) == 2:
			sourcePortName = linkElement.getAttribute("source").split(":")[1] 
		sinkName = linkElement.getAttribute("sink").split(":")[0]
		if len(linkElement.getAttribute("sink").split(":")) == 2:
			sinkPortName = linkElement.getAttribute("sink").split(":")[1] 
		if processor_parents[sourceName][0] == processor_parents[sinkName][0]:
			if processor_parents[sourceName][0].getAttribute("name") != "#document":
				processor_parents[sourceName][0].appendChild(linkElement)
		elif str(len(processor_parents[sourceName])) < str(len(processor_parents[sinkName])):
			while processor_parents[sourceName][0] != processor_parents[sinkName][0]:
				linkElement.setAttributeNS('','sink',processor_parents[sinkName][0].parentNode.getAttribute("name")+':input'+str(iterateElements[processor_parents[sinkName][0].parentNode.getAttribute("name")]['sources']))
				processor_parents[sourceName][0].appendChild(linkElement)
				sourceElement = doc.createElementNS('','s:source')
				sourceElement.setAttributeNS('','name','input'+str(iterateElements[processor_parents[sinkName][0].parentNode.getAttribute("name")]['sources']))
				processor_parents[sinkName][0].appendChild(sourceElement)
				_linkElement = doc.createElementNS('','s:link')
				_linkElement.setAttributeNS('','source','input'+str(iterateElements[processor_parents[sinkName][0].parentNode.getAttribute("name")]['sources']))
				_linkElement.setAttributeNS('','sink',sinkName+":"+sinkPortName)
				processor_parents[sinkName][0].appendChild(_linkElement)
				iterateElements[processor_parents[sinkName][0].parentNode.getAttribute("name")]['sources'] += 1
				sourceName = linkElement.getAttribute("source").split(":")[0]
				if len(linkElement.getAttribute("source").split(":")) == 2:
					sourcePortName = linkElement.getAttribute("source").split(":")[1] 
				sinkName = linkElement.getAttribute("sink").split(":")[0]
				if len(linkElement.getAttribute("sink").split(":")) == 2:
					sinkPortName = linkElement.getAttribute("sink").split(":")[1] 
		else:
			while processor_parents[sourceName][0] != processor_parents[sinkName][0]:
				_linkElement = doc.createElementNS('','s:link')
				_linkElement.setAttributeNS('','source',sourceName+":"+sourcePortName)
				_linkElement.setAttributeNS('','sink',"output"+str(iterateElements[processor_parents[sourceName][0].parentNode.getAttribute("name")]['sinks']))
				processor_parents[sourceName][0].appendChild(_linkElement)
				sinkElement = doc.createElementNS('','s:sink')
				sinkElement.setAttributeNS('','name',"output"+str(iterateElements[processor_parents[sourceName][0].parentNode.getAttribute("name")]['sinks']))
				processor_parents[sourceName][0].appendChild(sinkElement)
				linkElement.setAttributeNS('','source',processor_parents[sourceName][0].parentNode.getAttribute("name")+":output"+str(iterateElements[processor_parents[sourceName][0].parentNode.getAttribute("name")]['sinks']))
				linkElement.setAttributeNS('','sink',sinkName+":"+sinkPortName)
				processor_parents[processor_parents[sourceName][0].parentNode.getAttribute("name")][0].appendChild(linkElement)
				iterateElements[processor_parents[sourceName][0].parentNode.getAttribute("name")]['sinks'] += 1
				sourceName = linkElement.getAttribute("source").split(":")[0]
				if len(linkElement.getAttribute("source").split(":")) == 2:
					sourcePortName = linkElement.getAttribute("source").split(":")[1] 
				sinkName = linkElement.getAttribute("sink").split(":")[0]
				if len(linkElement.getAttribute("sink").split(":")) == 2:
					sinkPortName = linkElement.getAttribute("sink").split(":")[1] 
	
	return doc

def GetActualSubworkflowPortName(virtualName,subworkflowElements,uuid):
	nodeName = virtualName.split(":")[0]
	nodePortName = virtualName.split(":")[1]

	subworkflowElement = subworkflowElements[nodeName]

	parameterElements = subworkflowElement.getElementsByTagName("s:parameter")
	if len(parameterElements) > 0:
		parameterElement = parameterElements[0]

	workflowName = parameterElement.firstChild.nodeValue.strip()
	workflowsPath = os.path.join(config.workflows,uuid)

	doc = xml.dom.minidom.parse(os.path.join(workflowsPath,workflowName))

	sinkElements = doc.getElementsByTagName("s:sink")
	for sinkElement in sinkElements:
		if sinkElement.getAttribute("mappedTo") == nodePortName:
			return sinkElement.getAttribute("name")

def ReplaceInputNamesWithInputPaths(inputs,uuid):
	if isinstance(inputs,list):
		for i in range(0,len(inputs)):
			if isinstance(inputs[i],list):
				inputs[i] = ReplaceInputNamesWithInputPaths(inputs[i],uuid)
			else:
				#if inputs[i][0:4] == "ref.":
				path = os.path.join(uuid,inputs[i])
				path = os.path.join(config.inputs,path)
				refContent = simplejson.loads(open(path).read().strip())
				inputs[i] = GetProperList(refContent)
				#else:
				#	inputs[i] = os.path.join(uuid,inputs[i])
				#	inputs[i] = os.path.join(config.inputs,inputs[i])
		return inputs
	else:
		#if inputs[0:4] == "ref.":
		path = os.path.join(uuid,inputs)
		path = os.path.join(config.inputs,path)
		refContent = simplejson.loads(open(path).read().strip())
		return GetProperList(refContent)
		#else:
		#	inputPath = os.path.join(uuid,inputs)		
		#	return os.path.join(config.inputs,inputPath) 


def PrepareInputs(workflowName,inputs,StepsArray,uuid):
	DataSet_Dict = {}
	for input in inputs:
		inputs[input] = GetProperList(inputs[input])
		inputs[input] = ReplaceInputNamesWithInputPaths(inputs[input],uuid)
		for Step in StepsArray:
			if Step.Name == input:
				path = GetRandomPath(config.temp)
				open(path,'w').write(simplejson.dumps(inputs[input]))
				os.system("chmod 777 " + path)
				DataSet_Dict[Step.id] = path
				break	
	return DataSet_Dict
