#!/usr/bin/env python
# coding: utf-8

''' Evernote.py: Gets notes with Evernote local API '''

import _winreg
import os
import sys
import subprocess
import re
import time
import warnings
import locale
from getpass import getpass
from dateutil.parser import parse
from lxml import etree
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint

__author__ = 'Alexey Rubtsov'
__copyright__ = 'Copyright 2012, Alexey Rubtsov'
__license__ = 'GPL'
__version__ = '1.0'
__maintainer__ = 'Alexey Rubtsov'
__email__ = 'vostbur@gmail.com'
__status__ = 'Development'

class RawData(HTMLParser):

    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.data = ''

    def handle_endtag(self, tag):
        if tag == 'div': self.data += '\n'

    def handle_startendtag(self, tag, attrs):
        if tag == 'br': self.data += '\n'

    def handle_data(self, data):
        self.data += data

    def close(self):
        return self.data

    def handle_entityref(self, name):
        try:
            self.data += unicode(chr(name2codepoint[name]))
        except:
            if name == 'nbsp': self.data += ' '
            if name == 'apos': self.data += "'"
            pass # unknown HTML entity

class Evernote(object):
    '''Returns only plain text without any tags, pictures and links.
       Looking at all notebooks if gets None.'''

    date_fmt = '%Y %m %d %H:%M:%S'
    notes = []
    notebook = None
    last_title, last_number, last_content, last_tags = '', '', '', []
    encoding = locale.getpreferredencoding()

    def __init__(self, notebook=None):
        if sys.platform != 'win32':
            print 'Works only for Windows'
            sys.exit(1)

        self.notebook = notebook

        self._evernote_path = self._getENScriptPath()
        self._tmp_enex_file = self._getEnexFile()
        self._xml_tree = self._loadXML()
        os.remove(self._tmp_enex_file)

        self.notes = self._getNotes()
        self.last_title = self.notes[0]['title']
        self.last_tags = self.notes[0]['tags']
        self.last_number = self.notes[0]['number']
        self.last_shownotes = self.notes[0]['content']

    def _getENScriptPath(self):
        '''Returns (Default) unicode registry entry with path to ENScript
           encoded to 'cp1251' for console. Else return 'None'.'''

        try:
            with _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                            r'SOFTWARE\Microsoft\Windows'
                            '\CurrentVersion\App Paths\ENScript.exe') as key:
                count = 0
                while True:
                    name, value, type = _winreg.EnumValue(key, count)
                    if name == '' and type == 1:
                        return value.encode(self.encoding)
                    count += 1

        except WindowsError:
            pass

    def _getEnexFile(self):
        '''Returns the Evernote notebook exported to ENEX-format
            file './tmp.enex'. Else return 'None'.'''

        tmt_enex = 'tmp.enex'

        if not self._evernote_path:
            print "Evernote is not installed on computer."
            sys.exit(1)

        if self.notebook:
            console_command = [self._evernote_path, 'exportNotes',
                '/q', r'notebook:"%s"' % self.notebook.encode(self.encoding),
                '/f', tmt_enex]
        else:
            console_command = [self._evernote_path, 'exportNotes',
                '/q', 'any:', '/f', tmt_enex]

        p = subprocess.Popen(console_command,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        result = p.communicate()

        while "Can't open database" in result[1]:
            print 'You are not login to Evernote.\n'
            user = raw_input('Login: ')
            passwd = getpass('Password: ')

            p = subprocess.Popen(console_command + ['/u', user, '/p', passwd],
                                 shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            result = p.communicate()

        if result[1]:
            print 'Error in run ENScript.exe'
            sys.exit(1)

        else:
            return tmt_enex

    def _loadXML(self):
        '''Returns parsed XML from ENEX-file'''

        with open(self._tmp_enex_file) as f:
            try:
                return etree.parse(f)

            except (etree.XMLSyntaxError, ), e:
                print 'Could not parse XML\n', e
                sys.exit(1)

    def _getNotes(self):
        '''Returns a dictionary sorted by time of creation'''

        notes, raw_notes = [], self._xml_tree.xpath('//note')

        original_filters = warnings.filters[:]
        # suppress UnicodeWarning in dateutil.parser.parse
        warnings.simplefilter("ignore")

        try:
            for note in raw_notes:
                note_dict = {}

                note_dict['title'] = note.xpath('title')[0].text

                # Save number if exists digits in title
                search = re.findall(r'\d+', note_dict['title'], re.UNICODE)
                note_dict['number'] = search[0] if search else ''

                note_dict['tags'] = [tag.text for tag in note.xpath('tag')]

                # Use dateutil.parser.parse to figure out
                # these dates: 20110610T182917Z
                created = parse(note.xpath('created')[0].text\
                                        .decode('utf-8').encode('ascii'))

                try:
                    updated = parse(note.xpath('updated')[0].text\
                                        .decode('utf-8').encode('ascii'))

                except IndexError:
                    updated = created  # if not updated yet

                note_dict['createdate'] = created.strftime(self.date_fmt)
                note_dict['modifydate'] = updated.strftime(self.date_fmt)

                note_dict['content'] = ''
                content = note.xpath('content')
                if content:
                    parser = RawData()
                    parser.feed(content[0].text)
                    note_dict['content'] = parser.close()
                notes.append(note_dict)

        finally:
            warnings.filters = original_filters
            warnings.simplefilter("default")  # restore warnings

        return sorted(notes, key=lambda x: time.strptime(x['createdate'],
                      self.date_fmt), reverse=True)


if __name__ == '__main__':
    ''' Example working with class '''
    import streamfilter
    streamfilter.console_mode()

    # Looking at all notebooks. Put title of notebook for getting one.
    podcast = Evernote()
    for note in podcast.notes:
        print 'Title:', note['title'], '\n'
        print 'Number:', note['number'], '\n'
        print 'Created:', note['createdate'],
        print 'Modified:', note['modifydate'], '\n'
        print 'Tags:', ' '.join(note['tags']), '\n'
        print 'Content:', note['content'], '\n\n'

    print 'Last title:', podcast.last_title, '\n'
    print 'Last tags:', podcast.last_tags, '\n'
    print 'Last number:', podcast.last_number, '\n'
    print 'Last note:', podcast.last_shownotes, '\n'
