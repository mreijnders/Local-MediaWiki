# Disable buffering of stdout to make console work propperly in notepad++
class Unbuffered:
	def __init__(self, stream):
		self.stream = stream
	def write(self, data):
		self.stream.write(data)
		self.stream.flush()
	def __getattr__(self, attr):
		return getattr(self.stream, attr)

import sys
sys.stdout=Unbuffered(sys.stdout)

# Import libaries
import urllib
import http.cookiejar
import lxml.html
import re
import os
import concurrent.futures
import time
import datetime
import calendar

# Imports used for debugging and timing
import pprint
from time import clock

# Setup some initial settings
global dSettings
dSettings = {
			'core'			: 'http://2012.igem.org/',
			#'root'			: 'Team:Amsterdam/ernst/',
			'root'			: 'Team:Amsterdam',
			'localfolder'	: 'LocalCopy',
			'safemode'		: True
			}

# Setup some hard coded variables
global sPrintIndent
sPrintIndent = ''
			
# Setup windows safe filesystem substitution dictionary
global dWinSafeSubs
dWinSafeSubs = 	{
				'/'		: '%2F',
				'\\'	: '%5C',
				':'		: '%3A',
				'*'		: '%2A',
				'?'		: '%3F',
				'"'		: '%22',
				'<'		: '%3C',
				'>'		: '%3E',
				'|'		: '%7C'
				}

# Function that encodes string to be windows file system compliant
def encodeFileSystemPath(sPath):
	# Loop to subsititute occurences in the words
	for sSubWhat, sSubWith in dWinSafeSubs.items():
		sPath = sPath.replace(sSubWhat, sSubWith)
	
	return sPath
	
# Function that decodes windows file system compliant string
def decodeFileSystemPath(sPath):
	# Loop to subsititute occurences in the words
	for sSubWith, sSubWhat in dWinSafeSubs.items():
		sPath = sPath.replace(sSubWhat, sSubWith)
	
	return sPath

# Function that logs into the igem mediawiki using given credentials and returns a OpenDirector session
def loginToIGEM(sUsername, sPassword):

	# Construct login (POST) data dictionary
	dLoginData = 	{
					'username'	: sUsername,
					'password'	: sPassword,
					'Login'		: 'Log in'
					}

	# Construct OpenDirector with associated CookieJar (Maintains session cookie for login)
	oCookieJar = http.cookiejar.CookieJar()
	oOpenDirector = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(oCookieJar))

	# Login to iGEM using logindata
	try:
		oOpenDirector.open('http://igem.org/Login', urllib.parse.urlencode(dLoginData).encode())
	except urllib.request.HTTPError as oError:
		# Check if false alarm error was given (HTTP Error 302: The HTTP server returned a redirect error that would lead to an infinite loop.)
		if oError.code == 302:
			pass
		else:
			raise

	return oOpenDirector

# Function that gets directory listing behind specific page
def getIGEMDirList(oOpenDirector, sRoot, iNamespace=0):
	# Setup post data
	dPostData = {
				'title'		: 'Special:PrefixIndex',
				'prefix'	: sRoot,
				'namespace'	: str(iNamespace) #Namespace 0 is Main (there is the possebility to get other stuff)
				}
	
	# Retrieve and parse page listing for specific page
	oResponse = oOpenDirector.open(dSettings['core']+'wiki/index.php', urllib.parse.urlencode(dPostData).encode())
	oHtml = lxml.html.parse(oResponse)
	lFiles = oHtml.xpath('//table[@id = \'mw-prefixindex-list-table\']//tr/td/a/@href')
	
	# Setup name space prefix fix list (only Main and Template are supported
	dPrefixFix = 	{
					0	: '', 			# Main namspace (does not need a prefix)
					10	: 'Template:' 	# Template namespace
					}
	
	# Generate fixed prefix
	sFixedPrefix = re.sub('%2F$', '/', encodeFileSystemPath(dPrefixFix[iNamespace] + dPostData['prefix'])) # Fix prefix to be windows compliant
	# Loop to remove (and append fixed) prefixes from the files
	for i, sFile in enumerate(lFiles):
		lFiles[i] = re.sub('^/?.*:?'+re.escape(dPostData['prefix']), sFixedPrefix, sFile)
		# If file ends with a / subsititute this with %2F
		lFiles[i] = re.sub('/$', '%2F', lFiles[i])
		#print(lDirs[i])	
	
	# Create a dictionary to resemble the directory structure
	dDirs = {}
	for sFile in lFiles:
		dTempDirs = dDirs
		for sSubDir in sFile.split('/'):
			dTempDirs = dTempDirs.setdefault(encodeFileSystemPath(sSubDir), {})
	
	# Helper Function to remove empty dirs (files)
	def removeEmptyDirs(dDict):
		dDictTemp = dDict.copy()
		for k, v in dDict.items():
			if not v: 
				del dDictTemp[k]
			elif type(v) is dict: 
				dDictTemp[k] = removeEmptyDirs(v)
		return dDictTemp
	
	dDirs = removeEmptyDirs(dDirs)
	
	return (lFiles, dDirs)


# Function that creates directories at appropriate place
def buildDirStruct(sPathToLocal, dDirs):
	for sPath, value in dDirs.items():
		sPathToDir = sPathToLocal+'\\'+sPath+'.dir'
		if value: 
			buildDirStruct(sPathToDir, value)
		else:
			if not os.path.exists(sPathToDir):
				os.makedirs(sPathToDir)

# Function to set wiki time settings (for higher precision and time zone consistency)
def changeWikiPreferences(oOpenDirector, dPreferencesToChange=None, sWpEditToken=None):
	# Setup post data
	dPostData = {
				'title'		: 'Special:Preferences'
				}
	
	# Setup preferences to change if not specified
	if not dPreferencesToChange:
		dPreferencesToChange =  {
								'wpdate'				: 'ISO 8601',
								'wptimecorrection'		: 'System|',
								'wptimecorrection-other': None
								}
	
	dOldPostParams = dict()
	# Get the wpEditToken (else cant edit) if not specified
	if not sWpEditToken:
		oResponse = oOpenDirector.open(dSettings['core']+'wiki/index.php', urllib.parse.urlencode(dPostData).encode())
		oHtml = lxml.html.parse(oResponse)
		sWpEditToken = oHtml.xpath('//input[@id = \'wpEditToken\']/@value')[0]
	

		# Loop that extracts old preferences
		for sPostParam in dPreferencesToChange.keys():
			# Handle radio button type
			lRadioResults = oHtml.xpath('//input[@type = \'radio\' and @name = \''+sPostParam+'\' and @checked = \'checked\']/@value')
			if lRadioResults:
				dOldPostParams[sPostParam] = lRadioResults[0]
				continue
			
			# Handle option select
			lOptSelect = oHtml.xpath('//select[@name = \''+sPostParam+'\']//option[@selected = \'selected\']/@value')
			if lOptSelect:
				dOldPostParams[sPostParam] = lOptSelect[0]
				continue
			
			# Handle value input
			lValueInput = oHtml.xpath('//input[@name = \''+sPostParam+'\' and @size]/@value')
			if lValueInput:
				dOldPostParams[sPostParam] = lValueInput[0]
				continue
	
	# Update post parameters
	dPostData['wpEditToken'] = sWpEditToken
	dPostData.update(dPreferencesToChange)
	
	# Submit request to change the time and date settings
	oOpenDirector.open(dSettings['core']+'wiki/index.php', urllib.parse.urlencode(dPostData).encode())
	
	return dOldPostParams, sWpEditToken

# Function that retrieves most recent change times for list of files
def getLastChangeTimes(oOpenDirector, lFiles):

	# Helper Function to get the last change time of a single page
	def getLastChangeTime(oOpenDirector, sFile):
		# Setup post data
		dPostData = {
					'title'		: decodeFileSystemPath(sFile),
					'action'	: 'history'
					}
		
		# Retrieve and parse page listing the history of the page
		oResponse = oOpenDirector.open(dSettings['core']+'wiki/index.php', urllib.parse.urlencode(dPostData).encode())
		oHtml = lxml.html.parse(oResponse)
		sLastChange = oHtml.xpath('//ul[@id = \'pagehistory\']/li/a/text()')[0]
		
		print(sPrintIndent + dPostData['title'] + ' ('+sLastChange+')')
		
		# Helper Function to propperly format the time
		def formatTime(sTime):
			#return time.strptime(sTime, "%H:%M, %d %B %Y")
			#return time.strptime(sTime, '%Y-%m-%dT%H:%M:%S')
			return datetime.datetime.strptime(sTime, '%Y-%m-%dT%H:%M:%S')

		return formatTime(sLastChange)
	
	# Get change time using a threadpool to speed up the process
	iMaxWorkers = len(lFiles) # Number of concurrent threads
	dJobResults = dict()
	with concurrent.futures.ThreadPoolExecutor(max_workers=iMaxWorkers) as oExecutor:
		dJobs = dict((oExecutor.submit(getLastChangeTime, oOpenDirector, sFile), sFile) for sFile in lFiles)
		
		# Loop that collects results from the concurrent jobs
		for oCompletedJob in concurrent.futures.as_completed(dJobs):
			dJobResults[dJobs[oCompletedJob]] = oCompletedJob.result()
	
	return dJobResults

# Function to strip dir extention from an a sPath, or a list or dict containing them
def stripDirExtentions(oPath, sDirExtention='.dir'):
	# What to do if the oPath is a string
	if type(oPath) == type(str()):
		return oPath.replace(sDirExtention, '')
	# What to do if the oPath is a list
	elif type(oPath) == type(list()):
		for iIndex, oValue in enumerate(oPath):
			oPath[iIndex] = stripDirExtentions(oValue, sDirExtention)
		return oPath
	# What to do if the oPath is a dict
	elif type(oPath) == type(dict()):
		dTempDict = dict()
		for sKey, oValue in oPath.items():
			dTempDict[stripDirExtentions(sKey, sDirExtention)] = stripDirExtentions(oValue, sDirExtention)
		return dTempDict
	
# Function that gets Local folders and files in a directory
def getLocalFoldersAndFiles(sStartPath):
	# Loop that walks over all files and folders
	lAllFiles = list()
	for sRoot, lDirs, lFiles in os.walk(sStartPath):
		# Loop over files
		for sFileName in lFiles:
			lAllFiles.append( sRoot+'\\'+sFileName )
	
	# Loop that strips the sStartPath from each entity in the list
	for iIndex, sPath in enumerate(lAllFiles):
		lAllFiles[iIndex] = sPath[len(sStartPath+'\\'):]
	
	# Create a dictionary to resemble the directory structure
	dDirs = {}
	for sFile in lAllFiles:
		dTempDirs = dDirs
		for sSubDir in sFile.split('\\'):
			dTempDirs = dTempDirs.setdefault(encodeFileSystemPath(sSubDir), {})
	
	# Helper Function to remove empty dirs (files)
	def removeEmptyDirs(dDict):
		dDictTemp = dDict.copy()
		for k, v in dDict.items():
			if not v: 
				del dDictTemp[k]
			elif type(v) is dict: 
				dDictTemp[k] = removeEmptyDirs(v)
		return dDictTemp
	
	dDirs = removeEmptyDirs(dDirs)
	
	return lAllFiles, dDirs

# Function to retrieve last modification times for local files
def getLocalLastChangeTimes(sLocalFolder, lFilePaths):
	dLastChangeTimes = dict()
	# Loop over all file paths in the list
	for sFilePath in lFilePaths:
		fChangeTime = os.stat(sLocalFolder + '//' + sFilePath).st_mtime
		#oChangeTime = time.gmtime(fChangeTime)
		oChangeTime = datetime.datetime(*(time.gmtime(fChangeTime)[0:6]))
		dLastChangeTimes[sFilePath] = oChangeTime
		#print(sPrintIndent + stripDirExtentions(sFilePath) + ' (' + time.strftime('%Y-%m-%dT%H:%M:%S', oChangeTime) + ')')
		print(sPrintIndent + stripDirExtentions(sFilePath) + ' (' + oChangeTime.strftime('%Y-%m-%dT%H:%M:%S') + ')')
	
	return dLastChangeTimes

# Function to generate overview of files
def generateOverview(dServerChangeTimes, dLocalChangeTimes):
	dServerLocalLookupTable = dict()
	# Generate dict to be a lookup table
	for sLocalPath in dLocalChangeTimes.keys():
		sServerPath = stripDirExtentions(sLocalPath).replace('\\', '/')
		dServerLocalLookupTable[sServerPath] = sLocalPath
	
	dUniqueToServer = dict()
	dSharedBetweenServerAndLocal = dict()
	# Get files unique to server (and build the ones that are shared)
	for sServerPath, oTime in dServerChangeTimes.items():
		if sServerPath not in dServerLocalLookupTable:
			dUniqueToServer[sServerPath] = (oTime, None)
		else:
			dSharedBetweenServerAndLocal[sServerPath] = (oTime, dLocalChangeTimes[dServerLocalLookupTable[sServerPath]])
	
	dUniqueToLocal = dict()
	# Get files unique to local
	for sLocalPathServerComparable, sLocalPath in dServerLocalLookupTable.items():
		if sLocalPathServerComparable not in dServerChangeTimes:
			dUniqueToLocal[sLocalPathServerComparable] = (None, dLocalChangeTimes[sLocalPath])
	
	# Build complete overvieuw
	dOverview = dict()
	dOverview.update(dUniqueToServer)
	dOverview.update(dSharedBetweenServerAndLocal)
	dOverview.update(dUniqueToLocal)
	
	# Add (or regenerate) local paths to complete the overview
	dCompleteOverview = dict()
	for sServerPath, oDateTimes in dOverview.items():
		if sServerPath in dServerLocalLookupTable:
			tServerAndLocalPaths = (sServerPath, dServerLocalLookupTable[sServerPath])
		else:
			tServerAndLocalPaths = (sServerPath, sServerPath.replace('/', '.dir\\'))
			
		dCompleteOverview[tServerAndLocalPaths] = oDateTimes
	
	return dCompleteOverview

# Function to retrieve raw page
def getRawPage(oOpenDirector, sFile):
	# Setup post data
	dPostData = {
				'title'		: decodeFileSystemPath(sFile),
				'action'	: 'raw'
				}
	
	# Retrieve and parse page listing the history of the page
	oResponse = oOpenDirector.open(dSettings['core']+'wiki/index.php', urllib.parse.urlencode(dPostData).encode())
	return oResponse.read()

# Function to upload page
def uploadTextToPage(oOpenDirector, sPathToPage, sText, sWpEditToken):
	# Setup post data
	dPostData = {
				'title'			: decodeFileSystemPath(sPathToPage),
				'action'		: 'submit',
				'wpEdittime'	: None, #Required
				'wpTextbox1'	: sText,	
				'wpEditToken'	: sWpEditToken				
				}
	
	# Retrieve and parse page listing the history of the page
	oOpenDirector.open(dSettings['core']+'wiki/index.php', urllib.parse.urlencode(dPostData).encode())

# Function to act on overview
def actOnOverview(oOpenDirector, sLocalFolder, dOverview, sWpEditToken, bSafemode=True):
	# Get lenght of longest filepath for pretty printing purpouses
	iLengthLongestPath = 0
	for sServerPath, sLocalPath in dOverview:
		if len(sServerPath) > iLengthLongestPath: iLengthLongestPath = len(sServerPath)
	print(sPrintIndent + 'Files path:' + ' '*(iLengthLongestPath-11) + ' File version status:       Action:')
	
	# List some file statuses
	tFileStatuses = (
					'Server had most recent    ',
					'Local copy was more recent',
					'Did not exist localy      ',
					'Did not exist on server   ',
					'Same localy and on server '
					)
	
	# List some actions
	tAction = 	(
				'Downloaded server version',
				'Uploaded local version',
				'None',
				'None (due to safemode)'
				)
	
	# Helper function to be sent to the thread proccessor
	def threadHelper(
					oOpenDirector, sLocalFolder, sWpEditToken, bSafemode, # Variables from parrent function parameters
					iLengthLongestPath,	tFileStatuses, tAction, # Variables from inside the parrent function
					tOverviewItem): # Special variable
		# Segregate contents of overview item to variables
		(sServerPath, sLocalPath), (oServerTime, oLocalTime) = tOverviewItem
		
		# Prepare some often used variables
		sPrintString = sPrintIndent + sServerPath + ' '*(iLengthLongestPath-len(sServerPath)) + ' '
		sPathToFile = sLocalFolder + '\\' + sLocalPath
		
		# Helper Function to do a bigger than that treast None as always smaller
		def fixedBiggerThan(oDateTimeOne, oDateTimeTwo):
			if not oDateTimeOne:
				return False
			elif not oDateTimeTwo:
				return True
			else:
				return oDateTimeOne > oDateTimeTwo
		
		# Handle files that do not exist localy (this means download and store) or have newer on the server
		if fixedBiggerThan(oServerTime, oLocalTime):
			# Get the raw page as a binary string
			oRawPage = getRawPage(oOpenDirector, sServerPath)
			
			# Create file (directory structure should already exist due to previos function)
			with open(sPathToFile, 'wb') as oFile:
				oFile.write(oRawPage)
			
			# Set modification time of this file
			tStat = os.stat(sPathToFile)
			#print(str(tStat.st_mtime))
			os.utime(sPathToFile, (tStat.st_atime, calendar.timegm(oServerTime.utctimetuple())))
			
			# Print what was done
			if oServerTime and oLocalTime:
				sFileStatus = tFileStatuses[0]
			else:
				sFileStatus = tFileStatuses[2]
			print(sPrintString + sFileStatus + ' ' + tAction[0])
			
		# Handle files that do not exist on the server (this means upload to server) or have newer version localy
		elif fixedBiggerThan(oLocalTime, oServerTime):
			if not bSafemode:
				# Upload the file (or alteast its content) to the page
				uploadTextToPage(oOpenDirector, sServerPath, open(sPathToFile, 'rb').read(), sWpEditToken)
				sAction = tAction[1]
			else:
				sAction = tAction[3]

			# Print what was done			
			if oServerTime and oLocalTime:
				sFileStatus = tFileStatuses[1]
			else:
				sFileStatus = tFileStatuses[3]
			print(sPrintString + sFileStatus + ' ' + sAction)
			
		# Handle files are the same on bought server and local (do nothing)			
		elif oServerTime == oLocalTime:
			print(sPrintString + tFileStatuses[4] + ' ' + tAction[2])
	
	# Use threadpool proccessor to handle multiple updates to proccess the overview concerntly
	iMaxWorkers = len(dOverview) # Number of concurrent threads
	with concurrent.futures.ThreadPoolExecutor(max_workers=iMaxWorkers) as oExecutor:
		dJobs = dict((oExecutor.submit(threadHelper, 
										oOpenDirector, sLocalFolder, sWpEditToken, bSafemode,
										iLengthLongestPath, tFileStatuses, tAction,
										tOverviewItem), tOverviewItem) for tOverviewItem in dOverview.items())
	
# Login to iGEM wiki
print('Note: Logging into iGEM', end='')
oSession = loginToIGEM('YourUserName', 'YourPassword')
print(' - Done')

# Retrieve directory listing of main namespace
print('Note: Retrieving Main directory listing for \''+dSettings['root']+'\'', end='')
tMainDirListing = getIGEMDirList(oSession, dSettings['root'], 0)
print(' - Done')

# Retrieve directory listing of template namespace
print('Note: Retrieving Template directory listing for \''+dSettings['root']+'\'', end='')
tTemplateDirListing = getIGEMDirList(oSession, dSettings['root'], 10)
print(' - Done')

# Retrieve directory listing of template namespace
print('Note: Merge Main directory listing and Template directory listing', end='')
tFinalDirLisiting = (
					tMainDirListing[0] + tTemplateDirListing[0], 
					dict(list(tMainDirListing[1].items()) + list(tTemplateDirListing[1].items()))
					)
print(' - Done')

# Build local directory structure
print('Note: Building local directory structure at \''+dSettings['localfolder']+'\'', end='')
buildDirStruct(dSettings['localfolder'], tFinalDirLisiting[1])
print(' - Done')

# Set wiki date and time settings to higher precision and matching UTC
print('Note: Setting wiki time zone and format to UTC (servertime) and ISO 8601', end='')
dOldPrefs, sWpEditToken = changeWikiPreferences(oSession)
print(' - Done')
#pprint.pprint(dOldPrefs)

# Retrieve list of last change times for all pages
print('Note: Retrieving time of last change for pages:')
sPrintIndent = '      '
fStartTime = clock()
dLastChangeTimes = getLastChangeTimes(oSession, tFinalDirLisiting[0])
fEndTime = clock()
sPrintIndent = ''
print('Note: Done ('+ str(fEndTime-fStartTime) + ')')
#pprint.pprint(dLastChangeTimes)

# Retrieve local directory and file structure
print('Note: Retrieving filelist and directory strucutre for local \''+dSettings['localfolder']+'\'', end='')
lLocalFileList, dLocalDirList = getLocalFoldersAndFiles(dSettings['localfolder'])
print(' - Done')
#pprint.pprint(lLocalFileList)

# Retrieve times of last modification for the files
print('Note: Retrieving time of last change for files:')
sPrintIndent = '      '
fStartTime = clock()
dLocalLastChangeTimes = getLocalLastChangeTimes(dSettings['localfolder'], lLocalFileList)
fEndTime = clock()
sPrintIndent = ''
print('Note: Done ('+ str(fEndTime-fStartTime) + ')')
#pprint.pprint(dLocalLastChangeTimes)

# Generating overview
print('Note: Comparing server files to local files', end='')
dOverview = generateOverview(dLastChangeTimes, dLocalLastChangeTimes)
print(' - Done')

# Print print the overview
print('Note: Providing file modification time overview:')
sPrintIndent = '      '
iLengthLongestPath = 0
for sServerPath, sLocalPath in dOverview:
	if len(sServerPath) > iLengthLongestPath: iLengthLongestPath = len(sServerPath)
print(sPrintIndent + 'Files path:' + ' '*(iLengthLongestPath-11) + ' Server mod time:      Local mod time:')
for (sServerPath, sLocalPath), (oServerTime, oLocalTime) in dOverview.items():
	if oServerTime:	oServerTime = oServerTime.strftime('%Y-%m-%dT%H:%M:%S')
	else: oServerTime = '                   '
	
	if oLocalTime: oLocalTime = oLocalTime.strftime('%Y-%m-%dT%H:%M:%S')
	else: oLocalTime = '                   '
	
	if oServerTime and oLocalTime:
		if oServerTime == oLocalTime: sSign = ' = '
		elif oServerTime > oLocalTime: sSign = ' > '
		elif oServerTime < oLocalTime: sSign = ' < '
	else:
		sSign = '   '
		
	print(sPrintIndent + sServerPath + ' '*(iLengthLongestPath-len(sServerPath)) + ' ' + oServerTime + sSign + oLocalTime)

sPrintIndent = ''

# Act procces the files and act accordingly
print('Note: Proccessing files:')
sPrintIndent = '      '
fStartTime = clock()
actOnOverview(oSession, dSettings['localfolder'], dOverview, sWpEditToken, dSettings['safemode'])
fEndTime = clock()
sPrintIndent = ''
print('Note: Done ('+ str(fEndTime-fStartTime) + ')')

# Reset wiki date and time settings to pervios settings
print('Note: Reverting wiki time zone and format settings', end='')
changeWikiPreferences(oSession, dOldPrefs, sWpEditToken)
print(' - Done')
#pprint.pprint(dOldPrefs)