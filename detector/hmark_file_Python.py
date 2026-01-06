
"""
Dataset Collection Tool.
Author:     Seunghoon Woo (seunghoonwoo@korea.ac.kr)
Modified:   December 16, 2020.
Modified by: Duyeong (dino700072@gmail.com)
Modified:   October, 20, 2023
"""

import os
import re
import sys
import ast
import astor
import hashlib
import subprocess

"""GLOBALS"""

currentPath = os.getcwd()
resultPathFile = currentPath + "/res_hmark_file/"

# Generate directories
shouldMake = [resultPathFile]
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
		if ext == "py":
			parsed = ast.parse(fileContent)
			fileContent = normalize(removePyComment(parsed))
		else:
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

def hashingFile(repoPath):
    # This function is for hashing C/C++ functions
    # Only consider ".c", ".cc", and ".cpp" files
    possible = (".py")
    fileCnt  = 0
    lineCnt  = 0
    resDict  = {}

    for path, dir, files in os.walk(repoPath):
        for file in files:
            filePath = os.path.join(path, file)
            # print(filePath)

            if file.endswith(possible):
                try:
                    # Execute Ctgas command
                    # ctagsResult       = subprocess.check_output(ctagsPath + ' -f - --kinds-C=* --fields=* "' + filePath + '"', stderr=subprocess.STDOUT, shell=True).decode()

                    # f = open(filePath, 'r', encoding = "latin1")
                    ext = file.split('.')[-1]
                    fileHash = md5File(filePath, ext)
                    # For parsing functions
                    # lineCnt       = len()
                    with open(filePath, 'rb') as f:
                        lineCnt += len(f.readlines())
                    fileCnt     += 1
                    if fileHash not in resDict:
                        resDict[fileHash] = []
                    # storedPath = filePath.replace(repoPath, "") Upadated on 0106
                    storedPath = filePath.replace(repoPath, "", 1)
                    # storedPath = filePath.
                    resDict[fileHash].append(storedPath)

                except subprocess.CalledProcessError as e:
                    print("Parser Error:", e)
                    continue
                except Exception as e:

                    print ("hashing Subprocess failed", e, ":", filePath)
                    continue

    return resDict, fileCnt, lineCnt 

def indexing_file(resDict, title, filePath):
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
    if(testmode):
        inputPath = "./testing/redis"
    else:
        inputPath = sys.argv[1]

    try:
        resDict = {}
        fileCnt = 0
        funcCnt = 0
        lineCnt = 0


        # Indexing for latest commit

        # ### File
        resDict, fileCnt, lineCnt = hashingFile(inputPath)
        repoName = inputPath.split("/")[-1]
        if len(resDict) > 0:
            # if not os.path.isdir(resultPathFile + repoName):
            #     os.mkdir(resultPathFile + repoName)
            
            title = ' '.join(["4.0.1", repoName, str(fileCnt), str(lineCnt)])
            resultFilePath  = resultPathFile + 'hashmark_0_' + repoName + '.hidx' # Default file name: "fuzzy_OSSname.hidx"
            print(resultFilePath)
            indexing_file(resDict, title, resultFilePath)


    except subprocess.CalledProcessError as e:
        print("Parser Error:", e)

    except Exception as e:
        print ("main Subprocess failed", e)


testmode = 0
""" EXECUTE """
if __name__ == "__main__":
    main()

