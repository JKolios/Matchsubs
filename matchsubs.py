import sys
import re
import shutil
import os
import os.path
import argparse

def main():
	parser = argparse.ArgumentParser(description='Match sub and video files by season and episode number.')
	#parser.add_argument('-r',action='store_true',help='Recurse to subdirectories')
	parser.add_argument('-v',action='store_true',help='Display matching dirs for subs and videos.')
	parser.add_argument('match_target',metavar ='matchdirname',help='Target directory' )
	args = parser.parse_args()
	
	matchsubs(args)
	

def matchsubs(args):

	rename_dir = os.path.abspath(args.match_target) + "/"
	if args.v == True :
		print (rename_dir)
	if  os.path.isdir(rename_dir) == False:
		print ("Cannot find directory " + rename_dir)
		return
		
	fileList = [file for file in os.listdir(rename_dir) if os.path.isfile(os.path.join(rename_dir,file)) == True]
	if args.v == True :
		print ("File List:\n"+"\n".join(fileList)+"\n")
		
	videoFileList = [file for file in fileList if (os.path.splitext( file )[1] in [".mkv",".avi",".wmv",".ogg",".divx","m2ts"])]
	if args.v == True :
		print ("Video File List:\n"+"\n".join(videoFileList)+"\n")
	
	subFileList = [file for file in fileList if (os.path.splitext( file )[1] in [".srt",".ssa",".ass","sub"])]
	if args.v == True :
		print ("Subtitle File List:\n"+"\n".join(subFileList)+"\n")
	
	seFormat = re.compile(r'.*s0?(\d\d|\d)e0?(\d\d|\d).*',re.I|re.S)
	xFormat = re.compile(r'.*0?(\d\d|\d)x0?(\d\d|\d).*',re.I|re.S)
	numFormat = re.compile(r'.*(?:0([1-9])0([1-9]))|(?:([1-9])([1-9]\d)).*',re.I|re.S) # single digit season numbers only
	
	videoDict = {}
	for fname in videoFileList:
		
		matchResult = seFormat.search(fname)
		if matchResult == None:matchResult = xFormat.search(fname)
		if matchResult == None:matchResult = numFormat.search(fname)
		if matchResult == None:continue
		SEnumbers = matchResult.groups()
		
		if len(SEnumbers) > 2:
			SEnumbers = filter(clear_none_values,SEnumbers)				
		videoDict[SEnumbers] = fname 
		
	if args.v == True :
		print ("\nVideo Dictionary:")
		for x in videoDict.keys():
			print(x)
			print(videoDict[x])
	
	subDict = {}
	for fname in subFileList:
		
		matchResult = seFormat.search(fname)
		if matchResult == None:matchResult = xFormat.search(fname)
		if matchResult == None:matchResult = numFormat.search(fname)
		if matchResult == None:continue
		SEnumbers = matchResult.groups()
		
		if len(SEnumbers) > 2:
			SEnumbers = filter(clear_none_values,SEnumbers)
		subDict[SEnumbers] = fname
	
	if args.v == True :
		print ("\nSubtitle Dictionary:")
		for x in subDict.keys():
			print(x)
			print(subDict[x])
	
	renameDir = common_keys(videoDict,subDict)

	if args.v == True :
		print ("\nFile Pairs:")
		for x in renameDir.keys():
			print(x)
			print(renameDir[x]+"\n")
		
	renameCount = 0
	for vFileName,sFileName in renameDir.items():
		if (os.path.splitext(vFileName)[0] != os.path.splitext(sFileName)[0]):
			os.rename(sFileName,os.path.splitext(vFileName)[0]+os.path.splitext(sFileName)[1])
			renameCount +=1
	print ("Renamed " + str(renameCount) +" files.")
	return
			
	
def common_keys(dict1,dict2):
	common = {}
	for k1 in dict1.keys():
		for k2 in dict2.keys():
			if k1 == k2 :
				common[dict1.get(k1)] = dict2.get(k2)
	return common
	
def clear_none_values(value):
	if value != None: return True
	else: return False
		
		
if __name__ == '__main__':
  main()