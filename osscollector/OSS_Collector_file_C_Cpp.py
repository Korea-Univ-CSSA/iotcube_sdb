
"""
Dataset Collection Tool.
Author:		Seunghoon Woo (seunghoonwoo@korea.ac.kr)
Modified: 	December 16, 2020.
Modified by: Yoonjong (nooryyaa@korea.ac.kr)
Modified:	October, 18, 2023
Modified by: Duyeong (dino700072@gmail.com)
Modified:	October, 20, 2023
Modified by: Duyeong (dino700072@gmail.com)
Modified:	December, 09, 2024
"""

import os
import re
import sys
import hashlib
import subprocess

"""GLOBALS"""

currentPath	= os.getcwd()
gitCloneURLS= currentPath + "/sample_c_cpp_add" 			# Please change to the correct file (the "sample" file contains only 10 git-clone urls)
clonePath 	= "/mnt/sdb1/c_cpp/centris_repo/repo_src/"		# Default path
tagDatePath = "/mnt/sdb1/c_cpp/centris_repo/repo_date/"		# Default path
# resultPath	= currentPath + "/repo_file/"		# Default path
resultPathFile = "/mnt/sdb1/c_cpp/centris_repo/repo_files/"
# ctagsPath	= "/usr/local/bin/ctags" 			# Ctags binary path (please specify your own ctags path)
# ctagsPath	= "/usr/bin/ctags" 			# Ctags binary path (please specify your own ctags path)

# Generate directories
shouldMake = [clonePath, tagDatePath, resultPathFile]
for eachRepo in shouldMake:
	if not os.path.isdir(eachRepo):
		os.mkdir(eachRepo)



def md5File(fname, ext):
	hash_md5 = hashlib.md5()
	# try:
		# file_body = normalize(p.removeComment(''.join(lines),lang))
		# file_hash = hashlib.md5(file_body.encode('utf-8')).hexdigest()
		# mixed encoding: https://stackoverflow.com/questions/10009753/python-dealing-with-mixed-encoding-files
	with open(fname, "r", encoding="utf-8", errors="ignore") as f:
		fileContent = f.read()
		fileContent = normalize(removeComment(fileContent))
		
		hash = hashlib.md5(fileContent.encode("utf-8")).hexdigest()
		# for chunk in iter(lambda: f.read(4096), b""):
		# 	hash_md5.update(chunk)
	return hash

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

def hashing(repoPath):
	# This function is for hashing Go files
	# Only consider "go" files
	possible = (".c", ".cc", ".cpp")
	# possible = ()
	fileCnt  = 0
	lineCnt  = 0
	resDict  = {}

	for path, dir, files in os.walk(repoPath):
		for file in files:
			filePath = os.path.join(path, file)
			# print(filePath)

			if file.endswith(possible):
				# try:
					# Execute Ctgas command
					# ctagsResult 		= subprocess.check_output(ctagsPath + ' -f - --kinds-C=* --fields=* "' + filePath + '"', stderr=subprocess.STDOUT, shell=True).decode()

					# f = open(filePath, 'r', encoding = "latin1")
					ext = file.split('.')[-1]
					fileHash = md5File(filePath, ext)
					# For parsing functions
					# lineCnt		= len()
					with open(filePath, 'rb') as f:
						lineCnt  +=len(f.readlines())
					fileCnt 	+= 1
					if fileHash not in resDict:
						resDict[fileHash] = []
					storedPath = filePath.replace(repoPath, "")
					resDict[fileHash].append(storedPath)

				# except subprocess.CalledProcessError as e:
				# 	print("Parser Error:", e)
				# 	continue
				# except Exception as e:

				# 	print ("hashing Subprocess failed", e, ":", filePath)
				# 	continue

	return resDict, fileCnt, lineCnt 

def indexing(resDict, title, filePath):
	# For indexing each OSS

	fres = open(filePath, 'w')
	fres.write(title + '\n')

	for hashval in resDict:
		if hashval == '' or hashval == ' ':
			continue

		fres.write(hashval)
		fres.write('\t')
		for _ in resDict[hashval]:
			fres.write(_ + "\t")
		# fres.write(str(resDict[hashval]))
		fres.write('\n')

	fres.close()

def main():
	with open(gitCloneURLS, 'r', encoding = "UTF-8") as fp:
		funcDateDict = {}
		lines		 = [l.strip('\n\r') for l in fp.readlines()]
		
		for eachUrl in lines:
			os.chdir(currentPath)
			repoName 	= eachUrl.split("github.com/")[1].replace(".git", "").replace("/", "@@") # Replace '/' -> '@@' for convenience
			print ("[+] Processing", repoName)

			try:
				if not os.path.isdir(clonePath + repoName):
					cloneCommand 	= eachUrl + ' ' + clonePath + repoName
					cloneCommand = cloneCommand.replace('https://', 'http://')
					cloneResult 	= subprocess.check_output(cloneCommand, stderr = subprocess.STDOUT, shell = True).decode()

				os.chdir(clonePath + repoName)

				dateCommand 	= 'git log --tags --simplify-by-decoration --pretty="format:%ai %d"'  # For storing tag dates
				dateResult		= subprocess.check_output(dateCommand, stderr = subprocess.STDOUT, shell = True).decode()
				tagDateFile 	= open(tagDatePath + repoName, 'w')
				tagDateFile.write(str(dateResult))
				tagDateFile.close()


				tagCommand		= "git tag"
				tagResult		= subprocess.check_output(tagCommand, stderr = subprocess.STDOUT, shell = True).decode()

				resDict = {}
				fileCnt = 0
				funcCnt = 0
				lineCnt = 0


				# Indexing for latest commit
				print("current tag: latest commit")
				resDict, fileCnt, lineCnt = hashing(clonePath + repoName)
				if len(resDict) > 0:
					if not os.path.isdir(resultPathFile + repoName):
						os.mkdir(resultPathFile + repoName)
					title = '\t'.join([repoName, str(fileCnt), str(lineCnt)])
					resultFilePath 	= resultPathFile + repoName + '/md5_' + repoName + '.hidx' # Default file name: "fuzzy_OSSname.hidx"
					indexing(resDict, title, resultFilePath)

				# Indexing for previous tags
				for tag in str(tagResult).split('\n'):
					if not tag:
						continue

					# Generate function hashes for each tag (version)
					checkoutCommand	= subprocess.check_output("git checkout -f tags/" + tag, stderr = subprocess.STDOUT, shell = True)
					print("current tag: ", tag)
					resDict, fileCnt, lineCnt = hashing(clonePath + repoName)
					if len(resDict) > 0:
						if not os.path.isdir(resultPathFile + repoName):
							os.mkdir(resultPathFile + repoName)
						title = '\t'.join([repoName, str(fileCnt), str(lineCnt)])
						
						# Deal with tags that contain "/" character
						if "/" in tag:
							tag = tag.replace("/", "@@@")
						resultFilePath 	= resultPathFile + repoName + '/md5_' + tag + '.hidx'
						indexing(resDict, title, resultFilePath)
						

			except subprocess.CalledProcessError as e:
				print("Parser Error:", e)
				continue
			except Exception as e:
				print ("main Subprocess failed", e)
				continue

""" EXECUTE """
if __name__ == "__main__":
	main()