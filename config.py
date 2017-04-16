import ConfigParser
import os
import sys


mainPath='/storage/Tavaxy/tavaxy-dev'

configFile = os.path.join(mainPath , 'files/configuration/config.cfg')
config = ConfigParser.RawConfigParser()
config.read(configFile)

galaxy = os.path.join(mainPath , config.get('Galaxy','galaxy'))
galaxySchema = config.get('Galaxy', 'schema')
connectionString = config.get('Galaxy', 'connectionString')
database = connectionString + galaxySchema
dataset = os.path.join(mainPath ,  config.get('Galaxy', 'dataset'))
datasets = os.path.join(mainPath ,  config.get('Galaxy', 'datasets'))
galaxySession = config.get('Galaxy', 'session')
galaxyScripts = os.path.join(mainPath ,  config.get('Galaxy', 'scripts'))
sharedData = os.path.join(mainPath ,  config.get('Galaxy', 'sharedData'))

cloudRunner = os.path.join(mainPath , config.get('Tavaxy','cloudRunner'))
binFolder = os.path.join(mainPath , config.get('Tavaxy','bin'))
scriptsPath = os.path.join(binFolder , config.get('Tavaxy','scriptsPath'))
s2tScriptsPath = os.path.join(binFolder,"scufl2tavaxy")
t2flow2tScriptsPath = os.path.join(binFolder,"t2flow2tavaxy")
packagesPath = os.path.join(binFolder,config.get('Tavaxy','packages'))
workflows = os.path.join(mainPath ,  config.get('Data', 'workflows'))
inputs = os.path.join(mainPath ,  config.get('Data', 'inputs'))
inputs_base = config.get('Data', 'inputs')
tavernaWorkflows = os.path.join(mainPath ,  config.get('Data','tavernaWorkflows'))
logFile = os.path.join(mainPath ,  config.get('Data','logFile'))
toolDesc = os.path.join(mainPath ,  config.get('Data','toolDesc'))
scripts = os.path.join(mainPath , config.get('Data','scripts'))
portalWorkflows = os.path.join(mainPath ,  config.get('Tools', 'portalWorkflows'))
t2flowWorkflows = os.path.join(mainPath ,  config.get('Tools', 't2flowWorkflows'))
_results = config.get('Data','results')
results = os.path.join(mainPath , _results)
temp = os.path.join(mainPath ,  config.get('Data','temp'))

toolsConfig = os.path.join(mainPath ,  config.get('Tools', 'TavaxyConfigFile'))
galaxyToolsConfig = os.path.join(mainPath ,  config.get('Tools','GalaxyConfigFile'))
toolsDirect = os.path.join(mainPath ,  config.get('Tools', 'directory'))
patterns = config.get('Tools','patterns')

usersDBhost = config.get('usersDB','host')
usersDBport = config.get('usersDB','port')
usersDBun = config.get('usersDB','username')
usersDBpwd = config.get('usersDB','password')
usersDB = config.get('usersDB','schema')
dbScript = os.path.join(mainPath , 'files/configuration/',config.get('usersDB','script'))

WebBaseStorageFolder = os.path.join(mainPath ,config.get('myCloud','BaseStorageFolder'))

taverna = os.path.join(mainPath ,  config.get('Taverna','taverna'))

cluster = config.get('Execution','cluster') 
mainNode = config.get('Execution','mainNode')
user = config.get('Execution','user')
parallelJobs = config.get('Execution','parallel')

host = config.get('Options','host')
port = config.get('Options','port')

webAddress = config.get('Options','webAddress')

packages = [p for p in os.listdir(packagesPath) if os.path.isdir(os.path.join(packagesPath,p))]
for package in packages:
	packagePath = os.path.join(packagesPath,package)
	if packagePath not in sys.path:
		sys.path.append(packagePath)