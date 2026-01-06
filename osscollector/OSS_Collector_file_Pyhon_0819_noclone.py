
"""
Dataset Collection Tool.
Author:		Seunghoon Woo (seunghoonwoo@korea.ac.kr)
Modified: 	December 16, 2020.
Modified by: Yoonjong (nooryyaa@korea.ac.kr)
Modified:	October, 18, 2023
Modified by: Duyeong (dino700072@gmail.com)
Modified:	October, 20, 2023
"""

import os
import re
import sys
import ast
import astor
import hashlib
import subprocess

"""GLOBALS"""

currentPath	= os.getcwd()
gitCloneURLS= currentPath + "/sample_python_add" 			# Please change to the correct file (the "sample" file contains only 10 git-clone urls)
clonePath 	= "/mnt/sdb1/python/centris_repo/repo_src/"		# Default path
tagDatePath = "/mnt/sdb1/python/centris_repo/repo_date/"		# Default path
# resultPath	= currentPath + "/repo_file/"		# Default path
resultPathFile = "/mnt/sdb1/python/centris_repo/repo_files/"
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
	try:
		with open(fname, "r", encoding="utf-8", errors="ignore") as f:
			fileContent = f.read()
			if ext == "py":
				try:
					parsed = ast.parse(fileContent)
					fileContent = normalize(removePyComment(parsed))
				except:
					fileContent = normalize(removeComment(fileContent, "python"))
			
			hash = hashlib.md5(fileContent.encode("utf-8")).hexdigest()
			# for chunk in iter(lambda: f.read(4096), b""):
			# 	hash_md5.update(chunk)
		return hash
	except Exception as e:
		print(e)
		return None

def removeComment(string, language):
    # Code for removing comments
    c_regex = re.compile(r'(?P<comment>//.*?$|[{}]+)|(?P<multilinecomment>/\*.*?\*/)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"]*)',
        re.DOTALL | re.MULTILINE)
    pythonShortComRegex = re.compile(r'(?!.*\"|.*\')[\r\t\f\v]*(#).*(?!.*\"|.*\')')
    pythonLongComRegex = re.compile(r"(\"\"\")(.|\n)*(\"\"\")")
    # perlPodRegex1 = re.compile(r"^=(pod|begin|over)?.*?=(cut|end|back).*?\n\n", re.DOTALL | re.MULTILINE)     # Added regex for perlPOD (long comment for perl)
    # perlPodRegex2 = re.compile(r"^=(for|encoding|head).*?\n\n", re.DOTALL | re.MULTILINE)

    if language == "python" or language == "perl":
        string = pythonShortComRegex.sub("", string)
        return pythonLongComRegex.sub("", string)
    else:                   # Added comment removal for typescript
        return ''.join([c.group('noncomment') for c in c_regex.finditer(string) if c.group('noncomment')])

def removeDocstring(node):
	# Code for removing python stype comments and docstrings(multiline comments).
    if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
        node.body = [item for item in node.body if not (isinstance(item, ast.Expr) and hasattr(item, 'value') and isinstance(item.value, ast.Str))]

def removePyComment(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Module):
            node.body = [item for item in node.body if not (isinstance(item, ast.Expr) and hasattr(item, 'value') and isinstance(item.value, ast.Str))]
        else:
            removeDocstring(node)
    return astor.to_source(tree)

def normalize(string):
	# Code for normalizing the input string.
	# LF and TAB literals, curly braces, and spaces are removed,
	# and all characters are lowercased.
	# ref: https://github.com/squizz617/vuddy
	return ''.join(string.replace('\n', '').replace('\r', '').replace('\t', '').replace('{', '').replace('}', '').split(' ')).lower()

def hashing(repoPath):
	# This function is for hashing C/C++ functions
	# Only consider ".c", ".cc", and ".cpp" files
	possible = (".py")
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
					if fileHash is not None:
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
			repoName 	= eachUrl
			print ("[+] Processing", repoName)

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
						

			# except subprocess.CalledProcessError as e:
			# 	print("Parser Error:", e)
			# 	continue
			# except Exception as e:
			# 	print ("main Subprocess failed", e)
			# 	continue

""" EXECUTE """
if __name__ == "__main__":
	main()