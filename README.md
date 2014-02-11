#### Intelligent matching of subtitle and video files using regular expressions. 
============
Automatically matches the file names of all subtitle files in a given folder to their respective video files. Mainly meant for episodes of TV Series. Season and episode numbers are intelligently matched using regular expression 
pattern matching. Can interpret episode numbering in the three most common formats:

* S *Season Number* E *Episode Number*, as in: S03E02.
* *Season Number* x *Episode Number* as in: 1x05. 
* *Season Number* *Episode Number* as in: 0705


###Usage
positional arguments:
  matchdirname  Target directory or file

optional arguments:
  -h, --help    show this help message and exit
  -r            Recurse to subdirectories
  -v            Display matching dirs for subs and videos.
  -i            Display the elements of a filename as interpreted by the
                regex. The final argument should be a file name. All other
                arguments are ignored.
  -n N          Standardize all filenames with the string *s* given. All video
                and subtitle files found will be converted to:
                *s*.S*xx*E*xx*.*extension*

