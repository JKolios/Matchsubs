import re
import os
from guessit import guess_episode_info


VIDEO_FORMATS = [".mkv", ".avi", ".wmv", ".ogg", ".divx", "m2ts", "mpg", "mpeg", ".mp4", ".m4v", ".3gp", ".asf",
                 ".avchd", ".dat", ".flv", ".m1v", ".m2v", ".wrap", ".mov", ".mpe", ".rm", ".swf"]

SUBTITLE_FORMATS = [".srt", ".ssa", ".ass", ".sub"]

# Compile regexes for the 3 most used season and episode naming formats
# format 1:S(Season no.)E(Episode no.)
# ex:S02E03
seformat = re.compile(r'.*s0?(\d\d|\d)e0?(\d\d|\d).*', re.I | re.S)
# format 2:(Season no.)x(Episode no.)
# ex:1x06
xformat = re.compile(r'.*0?(\d\d|\d)x0?(\d\d|\d).*', re.I | re.S)
# format 3:(Season no.)(Episode no.)
# ex:313
numformat = re.compile(r'.*(?:0([1-9])0([1-9]))|(?:([1-9])([1-9]\d)).*',
                       re.I | re.S)  # single digit season numbers only


class SubMatcher(object):
    def __init__(self, directory, normalized_name=None, verbose=False, showdir=False):
        self.directory = directory
        self.verbose = verbose
        self.showdir = showdir
        self.normalized_name = normalized_name

    def rename_pairs(self, renamedict):
        """ Rename all subtitle files in renamedict
         Each subtitle file gets the filename of the video file it is paired with
         while preserving its extension."""

        renamecount = 0
        for vFileName, sFileName in renamedict.items():
            if os.path.splitext(vFileName)[0] != os.path.splitext(sFileName)[0]:
                try:
                    os.rename(os.path.join(self.directory, sFileName),
                              os.path.splitext(os.path.join(self.directory, vFileName))[0] +
                              os.path.splitext(os.path.join(self.directory, sFileName))[1])
                except OSError:
                    print " Cannot rename " + os.path.join(self.directory, sFileName)
                renamecount += 1
        print "Renamed " + str(renamecount) + " files."

    def match_subs(self):
        """ Matches subtitle and video files for the class's given dir"""

        # check if the given directory exists and is a directory
        rename_dir = os.path.abspath(self.directory)
        if self.verbose or self.showdir:
            print "Scanning self.directory: %s" % rename_dir
        if not os.path.isdir(rename_dir):
            print "Cannot find self.directory: %s" % rename_dir
            return

        # create list of files in given directory
        file_list = [f for f in os.listdir(rename_dir) if os.path.isfile(os.path.join(rename_dir, f))]
        if self.verbose:
            print "File List:\n" + "\n".join(file_list) + "\n"

        # filter file list into a video file list
        videofile_list = [f for f in file_list if (os.path.splitext(f)[1] in VIDEO_FORMATS)]
        if self.verbose:
            print "Video File List:\n" + "\n".join(videofile_list) + "\n"

        # filter file list into a subtitle file list
        subfile_list = [f for f in file_list if (os.path.splitext(f)[1] in SUBTITLE_FORMATS)]
        if self.verbose:
            print "Subtitle File List:\n" + "\n".join(subfile_list) + "\n"

        # Create a dictionary that matches every video file name with a(season number,episode number) tuple
        # The tuple is the dict's key
        video_dict = {}
        for fname in videofile_list:
            try:
                senumbers = self.parse_name_guessit(os.path.join(rename_dir, fname))
            except Exception as e:
                if self.verbose:
                    print 'Guessit exception occured: %s Defaulting to regular expression detection'
                senumbers = self.parse_name_re(os.path.join(rename_dir, fname))

            # If there is no match, skip the file
            if not senumbers:
                continue

            # Add the (season number,episode number) tuple to the dict
            video_dict[senumbers] = fname

        if self.verbose:
            print "Video Dictionary:"
            for x in video_dict.keys():
                print x
                print video_dict[x]

        # Name normalization for video files
        if self.normalized_name:
            if self.verbose:
                print "Normalizing Video File names:"
            for filename in video_dict.items():
                new_filename = '%s.S%sE%s.%s' % (
                    self.normalized_name,
                    filename[0][0],
                    filename[0][1],
                    os.path.splitext(filename[1])[1])
                try:
                    os.rename(os.path.join(self.directory, filename[1]), os.path.join(self.directory, new_filename))
                except OSError:
                    print " Cannot rename " + os.path.join(self.directory, new_filename)
                if self.verbose:
                    print "Normalized " + filename[1] + " to " + new_filename
            self.match_subs()
            return

        # Create a dictionary for subtitle files in the same way
        sub_dict = {}
        for fname in subfile_list:
            try:
                senumbers = self.parse_name_guessit(os.path.join(rename_dir, fname))
            except Exception as e:
                if self.verbose:
                    print 'Guessit exception occured: %s Defaulting to regular expression detection' % e
                senumbers = self.parse_name_re(os.path.join(rename_dir, fname))

            # If none match skip the file
            if senumbers == ():
                continue

            # Add the (season number,episode number) tuple to the dict
            sub_dict[senumbers] = fname

        if self.verbose:
            print "Subtitle Dictionary:"
            for x in sub_dict.keys():
                print x
                print sub_dict[x]

        # Create a dictionary that matches video and subtitle file names
        # by joining video_dict and sub_dict on their common keys
        renamedict = {video_dict[key]: sub_dict[key] for key in [k for k in video_dict.keys() if k in sub_dict.keys()]}

        if self.verbose:
            print "File Pairs:"
            for k, v in renamedict.items():
                print k + " -> " + v + "\n"

        self.rename_pairs(renamedict)

    def parse_name_re(self, file_name):
        # Check if the given file exists and is a regular file.
        if self.verbose:
            print 'Trying regular expression match.\nAnalyzing ' + file_name

        if not os.path.isfile(file_name):
            print 'Cannot find file ' + file_name + ' or not a regular file.'
            return

        matchresult = seformat.search(file_name)
        if matchresult is not None:
            if self.verbose:
                print "S Season E Episode format detected"
        else:
            matchresult = xformat.search(file_name)
            if matchresult is not None:
                if self.verbose:
                    print "Season x Episode format detected"
            else:

                matchresult = numformat.search(file_name)
                if matchresult is not None:
                    if self.verbose:
                        print "Numeric format detected"
                else:
                    if self.verbose:
                        print "Not a known format"
                    return ()

        senumbers = matchresult.groups()

        if self.verbose:
            print "Results before None filtering:"
            print senumbers

        if len(senumbers) > 2:
            senumbers = (num for num in senumbers if num is not None)

        if self.verbose:
            print "Results after None filtering:"
            print senumbers

        return senumbers

    def parse_name_guessit(self, file_name):

        # Check if the given file exists and is a regular file.
        if self.verbose:
            print 'Trying guessit match.\nAnalyzing ' + file_name
        info = guess_episode_info(file_name, info=['hash_mpc'])
        guessed_senumbers = (info['season'], info['episodeNumber'])
        if self.verbose:
            print 'Guessit results: %s' % guessed_senumbers
        print guessed_senumbers
        return guessed_senumbers



