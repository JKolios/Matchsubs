import os
import os.path
import argparse
import re

VIDEO_FORMATS = [".mkv", ".avi", ".wmv", ".ogg", ".divx", "m2ts", "mpg", "mpeg", ".mp4", ".m4v", ".3gp", ".asf",
                 ".avchd", ".dat", ".flv", ".m1v", ".m2v", ".wrap", ".mov", ".mpe", ".rm", ".swf"]

SUBTITLE_FORMATS = [".srt", ".ssa", ".ass", ".sub"]


def main():
    # Receives arguments from argparse and calls the main matching function
    parser = argparse.ArgumentParser(description='Match sub and video files by season and episode number.')
    parser.add_argument('-r', action='store_true', help='Recurse to subdirectories')
    parser.add_argument('-v', action='store_true', help='Display matching dirs for subs and videos.')
    parser.add_argument('-i', action='store_true',
                        help='Display the elements of a filename as interpreted by the regex.\n \
                             The final argument should be a file name. All other arguments are ignored.')
    parser.add_argument('-n', action='store',
                        help='Standardize all filenames with the string *s* given.\n \
                             All video and subtitle files found will be converted to: *s*.S*xx*E*xx*.*extension*')
    parser.add_argument('match_target', metavar='matchdirname', help='Target directory or file')
    args = parser.parse_args()

    if args.i:
        args.v = True
        parse_name(args.match_target, args.v)
        return

    if args.r:
        match_subs(args.match_target, args.v, True, args.n)
        for root, dirs, files in os.walk(args.match_target):
            for subdir in dirs:
                match_subs(os.path.join(root, subdir), args.v, True, args.n)
        return

    match_subs(args.match_target, args.v, False, args.n)


def match_subs(directory, verbose, showdir, normalize=None):
    # Matches subtitle and video files for given dir(args.match_target)

    # check if the given directory exists and is a directory
    rename_dir = os.path.abspath(directory)
    if verbose or showdir:
        print "Scanning directory:{0}".format(rename_dir)
    if not os.path.isdir(rename_dir):
        print "Cannot find directory {0}".format(rename_dir)
        return

    # create list of files in given directory
    file_list = [f for f in os.listdir(rename_dir) if os.path.isfile(os.path.join(rename_dir, f))]
    if verbose:
        print "File List:\n" + "\n".join(file_list) + "\n"

    # filter file list into a video file list
    videofile_list = [f for f in file_list if (os.path.splitext(f)[1] in VIDEO_FORMATS)]
    if verbose:
        print "Video File List:\n" + "\n".join(videofile_list) + "\n"

    # filter file list into a subtitle file list
    subfile_list = [f for f in file_list if (os.path.splitext(f)[1] in SUBTITLE_FORMATS)]
    if verbose:
        print "Subtitle File List:\n" + "\n".join(subfile_list) + "\n"

    # Create a dictionary that matches every video file name with a(season number,episode number) tuple
    #The tuple is the dict's key
    video_dict = {}
    for fname in videofile_list:
        senumbers = parse_name(os.path.join(rename_dir, fname), verbose)

        #If none match skip the file
        if not senumbers:
            continue

        #Add the (season number,episode number) tuple to the dict
        video_dict[senumbers] = fname

    if verbose:
        print "\nVideo Dictionary:"
        for x in video_dict.keys():
            print x
            print video_dict[x]

    #Name normalization for video files
    if normalize is not None:
        if verbose:
            print "Normalizing Video File names:"
        for filename in video_dict.items():
            new_filename = normalize + '.S' + filename[0][0] + 'E' + filename[0][1] + os.path.splitext(filename[1])[1]
            try:
                os.rename(os.path.join(directory, filename[1]), os.path.join(directory, new_filename))
            except OSError:
                print " Cannot rename " + os.path.join(directory, new_filename)
            if verbose:
                print "Normalized " + filename[1] + " to " + new_filename
        match_subs(directory, verbose, showdir, None)
        return

    #Create a dictionary for subtitle files in the same way
    subdict = {}
    for fname in subfile_list:
        senumbers = parse_name(os.path.join(rename_dir, fname), verbose)

        #If none match skip the file
        if senumbers == ():
            continue

        #Add the (season number,episode number) tuple to the dict
        subdict[senumbers] = fname

    if verbose:
        print "\nSubtitle Dictionary:"
        for x in subdict.keys():
            print x
            print subdict[x]

    #Create a dictionary that matches video and subtitle file names
    #by joining video_dict and subdict on their common keys
    renamedict = common_keys(video_dict, subdict)

    if verbose:
        print "\nFile Pairs:"
        for x in renamedict.keys():
            print x + " -> " + renamedict[x] + "\n"

    #Rename all subtitle files in renamedict
    #Each subtitle file gets the filename of the video file it is paired with
    #while preserving its extension.
    renamecount = 0
    for vFileName, sFileName in renamedict.items():
        if os.path.splitext(vFileName)[0] != os.path.splitext(sFileName)[0]:
            try:
                os.rename(os.path.join(directory, sFileName), os.path.splitext(os.path.join(directory, vFileName))[0] +
                          os.path.splitext(os.path.join(directory, sFileName))[1])
            except OSError:
                print " Cannot rename " + os.path.join(directory, sFileName)
            renamecount += 1
    print "Renamed " + str(renamecount) + " files."


def parse_name(file_name, verbose):
    # Check if the given file exists and is a regular file.
    if verbose:
        print 'Analyzing ' + file_name

    if not os.path.isfile(file_name):
        print 'Cannot find file ' + file_name + ' or not a regular file.'
        return

    # Compile regexes for the 3 most used season and episode naming formats
    # format 1:S(Season no.)E(Episode no.)
    # ex:S02E03
    seformat = re.compile(r'.*s0?(\d\d|\d)e0?(\d\d|\d).*', re.I | re.S)
    # format 2:(Season no.)x(Episode no.)
    # ex:1x06
    xformat = re.compile(r'.*0?(\d\d|\d)x0?(\d\d|\d).*', re.I | re.S)
    #format 3:(Season no.)(Episode no.)
    #ex:313
    numformat = re.compile(r'.*(?:0([1-9])0([1-9]))|(?:([1-9])([1-9]\d)).*',
                           re.I | re.S)  # single digit season numbers only

    matchresult = seformat.search(file_name)
    if matchresult is not None:
        if verbose:
            print "S Season E Episode format detected"
    else:
        matchresult = xformat.search(file_name)
        if matchresult is not None:
            if verbose:
                print "Season x Episode format detected"
        else:

            matchresult = numformat.search(file_name)
            if matchresult is not None:
                if verbose:
                    print "Numeric format detected"
            else:
                print "Not a known format"
                return ()

    senumbers = matchresult.groups()

    if verbose:
        print "Results before None filtering:"
        print senumbers

    if len(senumbers) > 2:
        senumbers = [num for num in senumbers if num is not None]

    if verbose:
        print "Results after None filtering:"
        print senumbers

    return senumbers


def common_keys(dict1, dict2):
    #Join two dictionaries by their common keys
    common = {}
    for k1 in dict1.keys():
        for k2 in dict2.keys():
            if k1 == k2:
                common[dict1.get(k1)] = dict2.get(k2)
    return common


if __name__ == '__main__':
    main()
