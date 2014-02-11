
import sys
import re
import os
import os.path
import argparse

VIDEO_FORMATS = [".mkv",".avi",".wmv",".ogg",".divx","m2ts","mpg","mpeg",".mp4",".m4v",".3gp",".asf",".avchd",".dat",".flv",".m1v",".m2v",".wrap",".mov",".mpe",".rm",".swf"]
SUBTITLE_FORMATS = [".srt",".ssa",".ass",".sub"]

#Receives arguments from argparse and calls the main matching function
def main():
	parser = argparse.ArgumentParser(description='Match sub and video files by season and episode number.')
	parser.add_argument('-r',action='store_true',help='Recurse to subdirectories')
	parser.add_argument('-v',action='store_true',help='Display matching dirs for subs and videos.')
	parser.add_argument('-i',action='store_true',help='Display the elements of a filename as interpreted by the regex.\n The final argument should be a file name. All other arguments are ignored.')
	parser.add_argument('-n',action='store',help='Standardize all filenames with the string *s* given.\n All video and subtitle files found will be converted to: *s*.S*xx*E*xx*.*extension*')
	parser.add_argument('match_target',metavar ='matchdirname',help='Target directory or file' )
	args = parser.parse_args()

	if args.i == True:
		args.v = True
		parse_name(args.match_target,args.v)
		return
			 
	if args.r == True:
		match_subs(args.match_target,args.v,True,args.n)
		for root,dirs,files in os.walk(args.match_target):
			for subdir in dirs :
				match_subs(os.path.join(root,subdir),args.v,True,args.n)
		return			

	match_subs(args.match_target,args.v,False,args.n)
		
#Matches subtitle and video files for given dir(args.match_target)
def match_subs(dir,verbose,showdir,normalize=None):

	#check if the given dir exists and is a dir 
	rename_dir = os.path.abspath(dir)
	if (verbose == True) or (showdir == True):
		print ("Scanning directory:" + rename_dir)
	if  os.path.isdir(rename_dir) == False:
		print ("Cannot find directory " + rename_dir)
		return
		
	#create list of files in given dir
	fileList = [file for file in os.listdir(rename_dir) if os.path.isfile(os.path.join(rename_dir,file)) == True]
	if verbose == True :
		print ("File List:\n"+"\n".join(fileList)+"\n")
		
	#filter file list into a video file list
	videoFileList = [file for file in fileList if (os.path.splitext( file )[1] in VIDEO_FORMATS)]
	if verbose == True :
		print ("Video File List:\n"+"\n".join(videoFileList)+"\n")

	#filter file list into a subtitle file list
	subFileList = [file for file in fileList if (os.path.splitext( file )[1] in SUBTITLE_FORMATS)]
	if verbose == True :
		print ("Subtitle File List:\n"+"\n".join(subFileList)+"\n")
	
	#Create a dictionary that matches every video file name with a(season number,episode number) tuple
	#The tuple is the dict's key
	videoDict = {}	
	for fname in videoFileList:
		SEnumbers = ()
		SEnumbers = parse_name(os.path.join(rename_dir,fname),verbose)

		#If none match skip the file
		if SEnumbers == ():continue
				
		#Add the (season number,episode number) tuple to the dict
		videoDict[SEnumbers] = fname 
		
	if verbose == True :
		print ("\nVideo Dictionary:")
		for x in videoDict.keys():
			print(x)
			print(videoDict[x])
	
	#Name normalization for video files
	if normalize != None:
		if verbose:
			print "Normalizing Video Filenames:"
		for filename in videoDict.items():
			new_filename = normalize + '.S' + filename[0][0] +'E' + filename[0][1] + os.path.splitext(filename[1])[1]			
			try:
				os.rename(os.path.join(dir,filename[1]),os.path.join(dir,new_filename))
			except OSError:
				print " Cannot rename " + os.path.join(dir,sFileName)
			if verbose:
				print "Normalized " + filename[1] + " to " + new_filename
		match_subs(dir,verbose,showdir,None)
		return
	
	#Create a dictionary for subtitle files in the same way
	subDict = {}
	for fname in subFileList:
		SEnumbers = ()
		SEnumbers = parse_name(os.path.join(rename_dir,fname),verbose)

		#If none match skip the file
		if SEnumbers == ():continue
				
		#Add the (season number,episode number) tuple to the dict
		subDict[SEnumbers] = fname 
			
	if verbose == True :
		print ("\nSubtitle Dictionary:")
		for x in subDict.keys():
			print(x)
			print(subDict[x])
	
	#Create a dictionary that matches video and subtitle file names
	#by joining videoDict and subDict on their common keys
	renameDict = common_keys(videoDict,subDict)

	if verbose == True :
		print ("\nFile Pairs:")
		for x in renameDict.keys():
			print(x) + " -> " + renameDict[x]+"\n"
		
	#Rename all subtitle files in renameDict
	#Each subtitle file gets the filename of the video file it is paired with
	#while preserving its extension.
	renameCount = 0
	for vFileName,sFileName in renameDict.items():
		if (os.path.splitext(vFileName)[0] != os.path.splitext(sFileName)[0]):
			try:
				os.rename(os.path.join(dir,sFileName),os.path.splitext(os.path.join(dir,vFileName))[0]+os.path.splitext(os.path.join(dir,sFileName))[1])
			except OSError:
				print " Cannot rename " + os.path.join(dir,sFileName)
			renameCount +=1
	print ("Renamed " + str(renameCount) +" files.")
	
def parse_name(file_name,verbose):
	if verbose:
		print ("Analyzing " + file_name)
	#Check if the given file exists and is a regular file.
	if  os.path.isfile(file_name) == False:
		print ("Cannot find file " + file_name + " or not a regular file.")
		return
	
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
	
	matchResult = seFormat.search(file_name)
	if matchResult != None: 
		if (verbose == True): print ("S Season E Episode format detected")
	else:
		matchResult = xFormat.search(file_name)
		if matchResult != None:
				if (verbose == True): print ("Season x Episode format detected")
		else:
			
			matchResult = numFormat.search(file_name)
			if matchResult != None:
				if (verbose == True): print ("Numeric format detected")
			else:
				print "Not a known format"
				return (())
	
	SEnumbers = matchResult.groups()
		
	if (verbose == True): 
		print "Results before None filtering:"
		print SEnumbers
		
	if len(SEnumbers) > 2:
		SEnumbers = filter(clear_none_values,SEnumbers)
	
	if (verbose == True): 
		print "Results after None filtering:"
		print SEnumbers
	
	return SEnumbers
					
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
