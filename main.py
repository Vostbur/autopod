#!/usr/bin/env python
# coding: utf-8

#============================ DEPENDENCY =================================
# lxml            2.3    Powerful and Pythonic XML processing library
# mutagen         1.20   read and write audio tags for many formats
# python-dateutil 2.1    Extensions to the standard Python datetime module
# six             1.1.0  Python 2 and 3 compatibility utilities
#=========================================================================

import sys, argparse
from autopod import Evernote, ID3    
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description=u'Sets ID3 tags from Evernote note.')
    parser.add_argument(u'-f', u'--file',
                        dest=u'file',
                        help=u'podcast mp3 file')
    args = parser.parse_args()
  
    if not args.file or '.mp3' not in args.file:
        print 'Run with -h or --help key.'
        sys.exit(1)
    
    album = u'Мелочи жизни'
    artist = u'Алексей Рубцов'
    date = '2012'
    podcast = Evernote.Evernote(album)
    
    title = podcast.last_title
    tracknumber = podcast.last_number
    version = podcast.last_shownotes
    
    tags = ID3.ID3(args.file)
    tags.setTags(album=album, title=title, tracknumber=tracknumber, version=' '.join(version.split('\n')), artist=artist, date=date)