
"""
OSS List Detector.
Author:		Seunghoon Woo (seunghoonwoo@korea.ac.kr)
Modified: 	December 16, 2020.
Modified:	Oct.31. 2022 By Yoonjong Na
Modified:	Nov.06. 2023 By Duyeong Kim
"""

import os
import sys
import re
import shutil
import json
# import tlsh
import subprocess
import ast
import pprint

"""GLOBALS"""
currentPath		= os.getcwd()
theta			= 0.1
DBPath          = currentPath
resultPath		= ""
finalDBPath		= DBPath + "/../testdb/preprocessor/componentDB/"
finalDBPathFile = DBPath + "/../testdb/preprocessor/componentDB_file/"
aveFuncPath		= DBPath + "/../testdb/preprocessor/metaInfos/aveFuncs"
aveFilePath		= DBPath + "/../testdb/preprocessor/metaInfos/aveFiles"
# ctagsPath		= currentPath + "/../../impl/bin/ctags"
verFuncPath		= DBPath + "/../testdb/preprocessor/verIDX_func/"
verFilePath		= DBPath + "/../testdb/preprocessor/verIDX_file/"

# shouldMake 	= [resultPath]
shouldMake = []
for eachRepo in shouldMake:
	if not os.path.isdir(eachRepo):
		os.mkdir(eachRepo)

# Generate TLSH
def computeTlsh(string):
	string 	= str.encode(string)
	hs 		= tlsh.forcehash(string)
	return hs


def removeComment(string):
	# Code for removing C/C++ style comments. (Imported from VUDDY and ReDeBug.)
	# ref: https://github.com/squizz617/vuddy
	c_regex = re.compile(
		r'(?P<comment>//.*?$|[{}]+)|(?P<multilinecomment>/\*.*?\*/)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"]*)',
		re.DOTALL | re.MULTILINE)
	return ''.join([c.group('noncomment') for c in c_regex.finditer(string) if c.group('noncomment')])

def normalize(string):
	# Code for normalizing the input string.
	# LF and TAB literals, curly braces, and spaces are removed,
	# and all characters are lowercased.
	# ref: https://github.com/squizz617/vuddy
	return ''.join(string.replace('\n', '').replace('\r', '').replace('\t', '').replace('{', '').replace('}', '').split(' ')).lower()

# def hashing(repoPath):
# 	# This function is for hashing C/C++ functions
# 	# Only consider ".c", ".cc", and ".cpp" files
# 	possible = (".c", ".cc", ".cpp", ".java", ".py")
	
# 	fileCnt  = 0
# 	funcCnt  = 0
# 	lineCnt  = 0

# 	resDict  = {}

# 	for path, dir, files in os.walk(repoPath):
# 		for file in files:
# 			filePath = os.path.join(path, file)

# 			if file.endswith(possible):
# 				try:
# 					# Execute Ctgas command
# 					functionList 	= subprocess.check_output(ctagsPath + ' -f - --kinds-C=* --fields=neKSt "' + filePath + '"', stderr=subprocess.STDOUT, shell=True).decode()

# 					f = open(filePath, 'r', encoding = "UTF-8")

# 					# For parsing functions
# 					lines 		= f.readlines()
# 					allFuncs 	= str(functionList).split('\n')
# 					func   		= re.compile(r'(function)')
# 					number 		= re.compile(r'(\d+)')
# 					funcSearch	= re.compile(r'{([\S\s]*)}')
# 					tmpString	= ""
# 					funcBody	= ""

# 					fileCnt 	+= 1

# 					for i in allFuncs:
# 						elemList	= re.sub(r'[\t\s ]{2,}', '', i)
# 						elemList 	= elemList.split('\t')
# 						funcBody 	= ""

# 						if i != '' and len(elemList) >= 8 and func.fullmatch(elemList[3]):
# 							funcStartLine 	 = int(number.search(elemList[4]).group(0))
# 							funcEndLine 	 = int(number.search(elemList[7]).group(0))

# 							tmpString	= ""
# 							tmpString	= tmpString.join(lines[funcStartLine - 1 : funcEndLine])

# 							if funcSearch.search(tmpString):
# 								funcBody = funcBody + funcSearch.search(tmpString).group(1)
# 							else:
# 								funcBody = " "

# 							funcBody = removeComment(funcBody)
# 							funcBody = normalize(funcBody)
# 							funcHash = computeTlsh(funcBody)

# 							if len(funcHash) == 72 and funcHash.startswith("T1"):
# 								funcHash = funcHash[2:]
# 							elif funcHash == "TNULL" or funcHash == "" or funcHash == "NULL":
# 								continue

# 							storedPath = filePath.replace(repoPath, "")
# 							resDict[funcHash] = storedPath

# 							lineCnt += len(lines)
# 							funcCnt += 1

# 				except subprocess.CalledProcessError as e:
# 					print("Parser Error:", e)
# 					continue
# 				except Exception as e:
# 					print ("Subprocess failed", e)
# 					continue

# 	return resDict, fileCnt, funcCnt, lineCnt 

def getAveFuncs():
	aveFuncs = {}
	with open(aveFuncPath, 'r', encoding = "UTF-8") as fp:
		aveFuncs = json.load(fp)
	return aveFuncs

## Temporary avefuncs
# def getAveFuncs():
# 	aveFuncs = {}
# 	ret = {}
# 	with open(aveFuncPath, 'r', encoding = "UTF-8") as fp:
# 		aveFuncs = json.load(fp)
# 		for eachOSS in aveFuncs:
# 			print(eachOSS)
# 			if("@@" in eachOSS):
# 				newName = eachOSS.split("@@")[1]
# 			else: newName = eachOSS
# 			ret[newName] = aveFuncs[eachOSS]
# 	return ret

def getAveFiles():
	aveFiles = {}
	with open(aveFilePath, 'r', encoding = "UTF-8") as fp:
		aveFiles = json.load(fp)
	return aveFiles

# def getVerFiles(repo):
# 	verInfos = {}
# 	with open(verFilePath, 'r', encoding = "UTF-8") as fp:
# 		aveFiles = json.load(fp)
# 	return aveFiles

def readComponentDB():
	componentDB = {}
	jsonLst 	= []

	for OSS in os.listdir(finalDBPath):
		componentDB[OSS] = []
		with open(finalDBPath + OSS, 'r', encoding = "UTF-8") as fp:
			jsonLst = json.load(fp)
			for eachHash in jsonLst:
				hashval = eachHash["hash"]
				componentDB[OSS].append(hashval)
	return componentDB

def detector_function(inputDict, inputRepo, res_json):
	# fres		= open(resultPath + "result_" + inputRepo, 'w')
	fres		= open(resultPath, 'w')
	aveFuncs 	= getAveFuncs()
	# verFuncs	= getVerFuncs()
	cnt = 0
	# res_json = {}

	for OSS in os.listdir(finalDBPath):


		OSSHashes = []
		commonFunc 	= []
		repoName 	= OSS.split('_sig')[0]
		# print(repoName)
		# print(OSS)
		totOSSFuncs = float(aveFuncs[repoName])
		if totOSSFuncs == 0.0:
			continue
		with open(finalDBPath + OSS, 'r', encoding = "UTF-8") as fp:
			jsonLst = json.load(fp)
			for eachHash in jsonLst:
				hashval = eachHash["hash"]
				ver = eachHash["vers"]
				OSSHashes.append([hashval, ver])

		comOSSFuncs = 0.0
		for hashval in OSSHashes:
			if hashval[0] in inputDict:
				commonFunc.append(hashval)
				comOSSFuncs += 1.0		

		if (comOSSFuncs/totOSSFuncs) >= theta:
			verinfo = []
			## Comment or modify below after component update or idx update
			# if("@@" in repoName):
			# 	repoName = repoName.split("@@")[1]
			verfile = repoName + ".txt"
			
			# if(os.isdir(verFilePath + verfile))
			if(verFuncPath):
				with open(verFuncPath + verfile) as f:
					# verinfo = ast.literal_eval(f)
					for eachline in f.readlines():
						if(eachline == ""):
							break
						verinfo.append({"ver":eachline.split()[1], "idx":eachline.split()[0]})
					### Update needed for below
					# verinfo = json.load(f)
			# print(verinfo)
			res_json[OSS] = {}
			compVer = 0
			compTag = ""
			res_json[OSS] = {
							"files":	{}, 
							"ver":		0,
							"common":	0,
							}	### Component version and fileList

			### Add files
			for eachFunc in commonFunc:
				funcHash = eachFunc[0]
				version = eachFunc[1][-1]
				verTag = ""

				## Find version information
				if verinfo:
					for eachTag in verinfo:
						if(eachTag['idx'] == version):
							verTag = eachTag['ver']
							break
				else:
					verTag = version

				if int(version) >= compVer:
					compVer = int(version)
					compTag = verTag

				fname = inputDict[funcHash]

				### Find if file exists inside
				if(fname not in res_json[OSS]["files"]):
					fileDict = {
							"funcs":	{},
							"ver":		version,
					}
					res_json[OSS]["files"][fname] = fileDict
				else:
					if int(version) > int(res_json[OSS]["files"][fname]["ver"]):
						res_json[OSS]["files"][fname]["ver"] = version

				res_json[OSS]["files"][fname]["funcs"][funcHash] = verTag

			### update file versions

			if verinfo:
				for eachFile in res_json[OSS]["files"]:
					fileVer = res_json[OSS]["files"][eachFile]["ver"]
				# print(fileVer)
					for eachTag in verinfo:
						# print((eachTag['idx']), (fileVer))
						if(eachTag['idx'] == fileVer):
							# print(3)
							fileVer = eachTag['ver']
							break
					# print(fileVer)
					res_json[OSS]["files"][eachFile]["ver"] = fileVer

			# ### update component versions
			res_json[OSS]["ver"] = str(compTag)
			res_json[OSS]["common"] = str(len(commonFunc))

	json.dump(res_json, fres)		
	fres.close()
	return res_json


def detector_files(inputDict, inputRepo, res_json):
	# fres		= open(resultPath + "result_" + inputRepo, 'w')
	fres		= open(resultPath, 'w')
	aveFiles 	= getAveFiles()
	# print(aveFiles)
	# verFiles	= getVerFiles()
	cnt = 0
	# res_json = {}

	for OSS in os.listdir(finalDBPathFile):
		OSSHashes = []
		commonFile 	= []
		repoName 	= OSS.split('_sig')[0]
		tmpRepoName = OSS.split('@@')[1]
		totOSSFiles = float(aveFiles[repoName])

		# print(totOSSFiles)
		if totOSSFiles == 0.0:
			continue
		with open(finalDBPathFile + OSS, 'r', encoding = "UTF-8") as fp:
			jsonLst = json.load(fp)
			for eachHash in jsonLst:
				hashval = eachHash["hash"]
				ver = eachHash["vers"]
				OSSHashes.append([hashval, ver])

		comOSSFiles = 0.0
		for hashval in OSSHashes:
			if hashval[0] in inputDict:
				commonFile.append(hashval)
				comOSSFiles += 1.0		
		# sim = comOSSFiles/totOSSFiles
		if (comOSSFiles/totOSSFiles) >= theta:
			verinfo = []
			verfile = repoName + "_idx"
			# if(os.isdir(verFilePath + verfile))
			if(verFilePath):
				with open(verFilePath + verfile) as f:
					verinfo = json.load(f)
			# print(verinfo)
			compVer = 0
			compTag = ""
			res_json[tmpRepoName] = {
							"files":	{}, 
							"ver":		0,
							"common":	0,
							}	### Component version and fileList

			### Add files
			for eachFile in commonFile:
				funcHash = eachFile[0]
				version = eachFile[1][-1]
				verTag = ""

				## Find version information
				if verinfo:
					for eachTag in verinfo:
						if(eachTag['idx'] == version):
							verTag = eachTag['ver']
							break
				else:
					verTag = version

				if int(version) >= compVer:
					compVer = int(version)
					if('@@' in verTag):
						verTag = verTag.split('@@')[1]
					compTag = verTag

				fname = inputDict[funcHash]

				### Find if file exists inside
				# if(fname not in res_json[OSS]["files"]):
				fileDict = {
						"funcs":	{},
						"ver":		verTag,
				}
				res_json[tmpRepoName]["files"][fname] = fileDict
			res_json[tmpRepoName]["ver"] = str(compTag)
			res_json[tmpRepoName]["common"] = str(len(commonFile))
	# pprint.pprint(res_json)
	json.dump(res_json, fres)	
	fres.close()

	resPathForCtree = resultPath.split("result")[0] + "res"
	#print(inputDict)

	with open(resPathForCtree, "w") as fp:
		for eachOSS in res_json:
			fp.write("OSS" + ": " + eachOSS + "\n")
			for eachPath in res_json[eachOSS]["files"]:
				### Add file hash eachPath -> hash +\t\t+ eachPath
				fHash = [k for k, v in inputDict.items() if eachPath == v]
				fp.write("\t"+fHash[0]+"\t\t" + eachPath + "\n")

def main(inputPath, inputRepo, testmode, osmode):
	global ctagsPath
	isFuncInput = False

	# #componentDB = readComponentDB()
	# if osmode == "win":
	# 	ctagsPath = currentPath + "/ctags_windows/ctags.exe"
	# elif osmode == "linux":
	# 	ctagsPath = currentPath + "/ctags_linux/ctags"
	# else:
	# 	print ("Please enter the correct OS mode! (win|linux)")
	# 	sys.exit()

	### function
	if testmode == "0":
		inputDict = {}
		with open(inputPath, 'r', encoding = "UTF-8") as fp:
			body = ''.join(fp.readlines()).strip()
			body = body.split("\n")
			title = body[0]
			if len(title.split()) == 5:	###Function
				isFuncInput = True
			if(isFuncInput): # function, for hmark compatibility
				body = ast.literal_eval(body[1])
				for eachLine in body:
					hashPat = eachLine["file"]
					hashVal = eachLine["hash value"]
					inputDict[hashVal] = hashPat
			else: # file
				for eachLine in body[1:]:
					hashVal = eachLine.split('\t')[0]
					hashPat = eachLine.split('\t')[1]
					inputDict[hashVal] = hashPat
	# else:
	# 	inputDict, fileCnt, funcCnt, lineCnt = hashing(inputPath)
	res_json = {}
	# res_json = detector_file(inputDict, inputRepo, res_json)
	if(isFuncInput):
		# print(inputDict)
		detector_function(inputDict, inputRepo, res_json)
	else:
		detector_files(inputDict, inputRepo, res_json)

	# print ("DONE")


Debugging = False
""" EXECUTE """
if __name__ == "__main__":

	if(Debugging):
		inputPath = "./testing/hashmark_0_redis.hidx"
		inputRepo = "redis"
	else:
		inputPath = sys.argv[1]
		if "hashmark_" in inputPath:
			resName = inputPath.split('/')[-1].replace('.hidx', '.result')
			resultPath = "./res/{}".format(resName)
			if not os.path.isdir(resultPath):
				os.mkdir(resultPath)
			resultPath = resultPath + "/" + resName
			inputRepo = inputPath.split('/')[-1].split('hashmark_0_')[1].replace('.hidx', '')
			

		else:
			# print(inputPath.split('/')[-1].split('md5_')[1].replace)
			inputRepo = inputPath.split('/')[-1].split('md5_')[1].replace('.hidx', '')
	testmode = "0"
	osmode = "linux"
	# testmode  = sys.argv[3]
	# osmode    = sys.argv[4]

	main(inputPath, inputRepo, testmode, osmode)
