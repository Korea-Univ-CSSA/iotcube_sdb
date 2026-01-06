
"""
Preprocessor.
Author:		Seunghoon Woo (seunghoonwoo@korea.ac.kr)
Modified: 	December 16, 2020.
"""

import os
import sys
import re
import shutil
import json
import math

"""GLOBALS"""
currentPath		= os.getcwd()
separator 		= "#@#"	
sep_len			= len(separator)					
# So far, do not change

theta 			= 0.1										# Default value (0.1)
tagDatePath 	= "/mnt/sdb1/go/centris_repo/repo_date/" 							# Default path
resultPath		= "/mnt/sdb1/go/centris_repo/repo_files/" 							# Default path
# resultPath		= "../tmp_db/" 							# Default path
verIDXpath		= currentPath + "/../../../../../mnt/sdb1/go/preprocessor/verIDX_file/"				# Default path
initialDBPath	= currentPath + "/../../../../../mnt/sdb1/go/preprocessor/initialSigs/"  			# Default path
finalDBPath		= currentPath + "/../../../../../mnt/sdb1/go/preprocessor/componentDB_file/"  		# Default path of the final Component DB
metaPath		= currentPath + "/../../../../../mnt/sdb1/go/preprocessor/metaInfos/"				# Default path, for saving pieces of meta-information of collected repositories
weightPath		= metaPath 	  + "/../../../../../mnt/sdb1/go/preprocessor/weights/"					# Default path, for version prediction
fileDatePath	= currentPath + "/../../../../../mnt/sdb1/go/preprocessor/fileDate/"				# Default path

# Generate directories
shouldMake 	= [verIDXpath, initialDBPath, finalDBPath, metaPath, fileDatePath, weightPath]
for eachRepo in shouldMake:
	if not os.path.isdir(eachRepo):
		os.mkdir(eachRepo)

fileDateDict	= {}




def extractVerDate(repoName):
	# For extracting version (tag) date

	verDateDict = {}
	if os.path.isfile(os.path.join(tagDatePath, repoName)):
		with open(os.path.join(tagDatePath, repoName), 'r', encoding = "UTF-8", errors="ignore") as fp:
			# print(os.path.join(tagDatePath, repoName))
			body = ''.join(fp.readlines()).strip()
			for eachLine in body.split('\n'):
				versionList = []
				if "tag:" in eachLine and ("master" not in eachLine[27:] or "main" not in eachLine[27:]): # tag에 main, master 제외
					date = eachLine[0:10]

					if "," in eachLine:
						verList = [x for x in eachLine.split("tag: ")]
						for val in verList[1:]:
							if ',' in val:
								versionList.append(val.split(',')[0])
							elif ')' in val:
								versionList.append(val.split(')')[0])
					else:
						versionList = [(eachLine.split('tag: ')[1][:-1])]

					for eachVersion in versionList:
						verDateDict[eachVersion] = date
			
	return verDateDict

def redundancyElimination():
	for repoName in os.listdir(resultPath):
		print (repoName)

		fileDateDict			= {}
		tempDateDict			= {}
		verDateDict				= extractVerDate(repoName)
		

		# if os.path.isfile(os.path.join(initialDBPath, repoName + "_sig")):
		# 	continue
		## For skipping already generated Sigs

		verTempLst = []
		signature  = {}
		verDict    = {}
		idx        = 0		

		for eachVersion in os.listdir(os.path.join(resultPath, repoName)):
			versionName = eachVersion.split("md5_")[1].replace(".hidx", "")
			# if(repoName == "antirez@@sds"):
			# 	print("???:: ", versionName)
			if versionName == '' or versionName == ' ':
				continue
			# if(repoName == "antirez@@sds"):
			# 	print("!!!:: ", versionName)
			verTempLst.append(versionName)
		verTempLst.sort()
		# if(repoName == "antirez@@sds"):
			# print("!!!:: ", verTempLst)
		# try:
		for versionName in verTempLst:
			with open(os.path.join(resultPath, repoName, ("md5_" + versionName + ".hidx")), 'r', encoding = "UTF-8", errors="ignore") as fp:
				verDict[versionName] = idx
				idx += 1
				# print(resultPath, repoName, ("md5_" + versionName + ".hidx"))
				body = ''.join(fp.readlines()).strip()
				# if(repoName == "antirez@@sds"):
					# print("!;!:: ", body.split('\n')[1:-1])
				for eachLine in body.split('\n')[1:]:

					if eachLine == '' or eachLine == ' ':
						continue

					hashval = eachLine.split('\t')[0]
					if hashval not in signature:
						signature[hashval]	 	= []
						tempDateDict[hashval] 	= []
					signature[hashval].append(str(idx-1))
					
					if versionName in verDateDict:
						tempDateDict[hashval].append(verDateDict[versionName])
					else:
						tempDateDict[hashval].append("NODATE")

		# except Exception as e:
		# 	print ("Parsing error: ", e)
		# 	continue
		# if(repoName == "antirez@@sds"):
		# 	print("???:: ", tempDateDict)
		# For storing file birthdate
		for hashval in tempDateDict:
			tempDateDict[hashval].sort()
			fileDateDict[hashval] = tempDateDict[hashval][0]
		# if(fileDatePath + repoName + "_filedate" == "/home/pecentzero/Centris-public/src/preprocessor/fileDate/antirez@@sds_filedate"):
			# print(fileDateDict)
		fdate = open(fileDatePath + repoName + "_filedate", 'w')
		for hashval in fileDateDict:
			fdate.write(hashval + '\t' + fileDateDict[hashval] + '\n')
		fdate.close()


		# For storing version indexes
		fidx = open(verIDXpath + repoName + "_idx", 'w')
		saveJson = []

		for verName in verTempLst:
			temp = {}
			temp["ver"] = verName
			temp["idx"] = str(verDict[verName])
			saveJson.append(temp)

		fidx.write(json.dumps(saveJson))
		fidx.close()
		
		
		# For storing OSS signatures
		f = open(initialDBPath + repoName + "_sig", 'w')

		saveJson = []
		for hashval in signature:
			temp = {}
			temp["hash"] = hashval
			temp["vers"] = signature[hashval]
			saveJson.append(temp)
		f.write(json.dumps(saveJson))
		f.close()

def saveMetaInfos():
	aveFileJson = {}
	allFileJson = {}
	uniqueJson	= []
	unique 		= {}


	fave = open(metaPath + "aveFiles", 'w')
	fall = open(metaPath + "allFiles", 'w')
	funi = open(metaPath + "uniqueFiles", 'w')
	

	for OSS in os.listdir(initialDBPath):
		weightJson	= {}
		repoName 	= OSS.replace("_sig", "")
		# repoName 	= "_sig".join(OSS.split("_sig")[:-1]) ### changed for case Ebiroll@@esp32_sigrok_sig
		print(repoName)
		totFiles 	= 0
		totVers 	= len(os.listdir(resultPath + repoName))
	
		if totVers == 0:
			continue

		fwei = open(weightPath + "/" + repoName + "_weights", 'w')

		
		with open(initialDBPath + OSS, 'r', encoding = "UTF-8") as fs:
			jsonStr = json.load(fs)
			totFiles = len(jsonStr)
			
			for eachJson in jsonStr:
				hashval = eachJson['hash']
				verlst 	= eachJson['vers']

				if hashval not in unique:
					unique[hashval] = []

				unique[hashval].append(repoName)
				weightJson[hashval] = math.log(float(totVers)/float(len(verlst)))

		aveFileJson[repoName]	= int(totFiles/totVers)
		allFileJson[repoName] 	= int(totFiles)

		fwei.write(json.dumps(weightJson))
		fwei.close()

	for fileHash in unique:
		temp = {}
		temp["hash"] 	= fileHash
		temp["OSS"]		= unique[fileHash]
		uniqueJson.append(temp)


	fave.write(json.dumps(aveFileJson))
	fall.write(json.dumps(allFileJson))
	funi.write(json.dumps(uniqueJson))

	fave.close()
	fall.close()
	funi.close()


def readVerDate(verDateDict, repoName):
	verDateDict[repoName] = {}

	if os.path.isfile(fileDatePath + repoName + "_filedate"):
		# print(fileDatePath + repoName + "_filedate")
		with open(fileDatePath + repoName + "_filedate", 'r', encoding = "UTF-8") as fp:
			body = ''.join(fp.readlines()).strip()
			
			if(len(body)==0):
				return verDateDict
			for eachLine in body.split('\n'):
				hashval = eachLine.split('\t')[0]
				date 	= eachLine.split('\t')[1]
				verDateDict[repoName][hashval] = date
	return verDateDict

def getAveFiles():
	aveFiles = {}
	with open(metaPath + "aveFiles", 'r', encoding = "UTF-8") as fp:
		aveFiles = json.load(fp)
	return aveFiles


def codeSegmentation():
	aveFiles = getAveFiles()

	# For printing process #
	l 	= 1
	tot = len(os.listdir(initialDBPath))
	print ('[+] Read OSS signatures..')
	########################

	OSSList = os.listdir(initialDBPath)
	
	versSignatures 	= {}
	dateSignatures	= {}
	uniqueFiles	 	= {}

	with open(metaPath + "uniqueFiles", 'r', encoding = "UTF-8") as fp:
		jsonStr = json.load(fp)
		for eachVal in jsonStr:
			hashval 			 = eachVal['hash']
			uniqueFiles[hashval] = eachVal['OSS']
			

	verDateDict = {}

	for S_sig in OSSList:
		print (l, '/', tot, S_sig)
		
		S = S_sig.replace("_sig", "")
		# S = "_sig".join(S_sig.split("_sig")[:-1])
		l += 1

		possibleMembers	 	= {}
		candiX				= {}
		removedFiles		= []
		

		if S not in verDateDict:
			verDateDict = readVerDate(verDateDict, S)
		
		with open(initialDBPath + S_sig, 'r', encoding = "UTF-8") as fs:
			jsonStr = json.load(fs)
			if len(jsonStr) == 0:
				continue
			else:
				temp = {}
				for eachVal in jsonStr:
					hashval = eachVal['hash']
					
					for OSS in uniqueFiles[hashval]:
						if OSS == S:
							continue

						if OSS not in candiX:
							temp[OSS] 	= []
							candiX[OSS] = 0

						if OSS not in verDateDict:
							verDateDict = readVerDate(verDateDict, OSS)
						
						try:
							if hashval not in verDateDict[S]:
								continue

							if verDateDict[S][hashval] == "NODATE" or verDateDict[OSS][hashval] == "NODATE":
								candiX[OSS] += 1
								temp[OSS].append(hashval)
								
							elif verDateDict[OSS][hashval] <= verDateDict[S][hashval]:
								candiX[OSS] += 1
								temp[OSS].append(hashval)
						except:
							pass

				for X in candiX:
					if aveFiles[X] == 0:
						continue

					elif len(verDateDict[X]) ==0:
						continue

					elif (float(candiX[X])/float(aveFiles[X])) >= theta:
						if S not in possibleMembers:
							possibleMembers[S] = []

						possibleMembers[S].append(X)
						removedFiles.extend(temp[X])

				if S not in possibleMembers:
					shutil.copy(os.path.join(initialDBPath, S)+"_sig", os.path.join(finalDBPath, S)+"_sig")

				else:
					removedFiles = set(removedFiles)
					saveJson = []
					fres = open(os.path.join(finalDBPath, S)+"_sig", 'w')
				
					for eachVal in jsonStr:
						temp = {}
						hashval = eachVal['hash']

						if hashval not in removedFiles:
							versLst = eachVal['vers']
							temp["hash"] = hashval
							temp["vers"] = versLst
							saveJson.append(temp)
					
					fres.write(json.dumps(saveJson))
					fres.close()

def main():
	redundancyElimination()
	saveMetaInfos()
	codeSegmentation()


""" EXECUTE """
if __name__ == "__main__":
	main()
