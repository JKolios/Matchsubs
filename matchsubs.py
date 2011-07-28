#! /usr/bin/python

import sys
import re
import shutil
import os
import os.path
import argparse

#Receives arguments from argparse and calls the main matching function
def main():
	parser = argparse.ArgumentParser(description='Match sub and video files by season and episode number.')
	parser.add_argument('-r',action='store_true',help='Recurse to subdirectories')
	parser.add_argument('-v',action='store_true',help='Display matching dirs for subs and videos.')
	parser.add_argument('match_target',metavar ='matchdirname',help='Target directory' )
	args = parser.parse_args()
	
	if args.r == True:
		for root,dirs,files in os.walk(args.match_target):
			for subdir in dirs :
				matchsubs(os.path.join(root,subdir),args.v,True)
				
	else :
		  matchsubs(args.match_target,args.v,False)
	

#Matches subtitle and video files for given dir(args.match_target)
def matchsubs(dir,verbose,showdir):

	#check if the given dir exists and is a dir 
	rename_dir = os.path.abspath(dir) + "/"
	if (verbose == True) or (showdir == True):
		print ("Scanning directory" +rename_dir)
	if  os.path.isdir(rename_dir) == False:
		print ("Cannot find directory " + rename_dir)
		return
		
	#create list of files in given dir
	fileList = [file for file in os.listdir(rename_dir) if os.path.isfile(os.path.join(rename_dir,file)) == True]
	if verbose == True :
		print ("File List:\n"+"\n".join(fileList)+"\n")
		
	#filter file list into a video file list
	videoFileList = [file for file in fileList if (os.path.splitext( file )[1] in [".mkv",".avi",".wmv",".ogg",".divx","m2ts","mpg","mpeg"])]
	if verbose == True :
		print ("Video File List:\n"+"\n".join(videoFileList)+"\n")
	
	#filter file list into a subtitle file list
	subFileList = [file for file in fileList if (os.path.splitext( file )[1] in [".srt",".ssa",".ass","sub"])]
	if verbose == True :
		print ("Subtitle File List:\n"+"\n".join(subFileList)+"\n")
	
	# Compile regexes for the 3 most used season and episode naming formats
	
	#format 1:S(Season no.)E(Episode no.)
	#ex:S02E03
	seFormat = re.compile(r'.*s0?(\d\d|\d)e0?(\d\d|\d).*',re.I|re.S)
	#format 2:(Season no.)x(Episode no.)
	#ex:1x06
	xFormat = re.compile(r'.*0?(\d\d|\d)x0?(\d\d|\d).*',re.I|re.S)
	#format 3:(Season no.)(Episode no.)
	#ex:313
	numFormat = re.compile(r'.*(?:0([1-9])0([1-9]))|(?:([1-9])([1-9]\d)).*',re.I|re.S) # single digit season numbers only
	
	#Create a dictionary that matches every video file name with a(season number,episode number) tuple
	#The tuple is the dict's key
	videoDict = {}	
	for fname in videoFileList:
		
		#Apply all 3 regular expressions on evey video file name 
		#until its season and episode number are found
		matchResult = seFormat.search(fname)
		if matchResult == None:matchResult = xFormat.search(fname)
		if matchResult == None:matchResult = numFormat.search(fname)
		#If none match skip the file
		if matchResult == None:continue
		SEnumbers = matchResult.groups()
		
		if len(SEnumbers) > 2:
			SEnumbers = filter(clear_none_values,SEnumbers)				
		#Add the (season number,episode number) tuple to the dict
		videoDict[SEnumbers] = fname 
		
	if verbose == True :
		print ("\nVideo Dictionary:")
		for x in videoDict.keys():
			print(x)
			print(videoDict[x])
	
	#Create a dictionary for subtitle files in the same way
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
	
	if verbose == True :
		print ("\nSubtitle Dictionary:")
		for x in subDict.keys():
			print(x)
			print(subDict[x])
	
	#Create a dictionary that matches video and subtitle file names
	#by joining videoDict and subDict on their common keys
	renameDir = common_keys(videoDict,subDict)

	if verbose == True :
		print ("\nFile Pairs:")
		for x in renameDir.keys():
			print(x)
			print(renameDir[x]+"\n")
		
	#Rename all subtitle files in renameDir
	#Each subtitle file gets the filename of the video file it is paired with
	#while preserving its extension.
	renameCount = 0
	for vFileName,sFileName in renameDir.items():
		if (os.path.splitext(vFileName)[0] != os.path.splitext(sFileName)[0]):
			os.rename(os.path.join(dir,sFileName),os.path.splitext(os.path.join(dir,sFileName))[0]+os.path.splitext(os.path.join(dir,sFileName))[1])
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
