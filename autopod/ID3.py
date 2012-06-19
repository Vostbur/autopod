#!/usr/bin/env python
# coding: utf-8

''' ID3.py: Set 'tracknumber', 'title', 'album', 'version', 'artist', 'date' MP3 tags '''

from mutagen.easyid3 import EasyID3

class ID3(object):
    
    audio_file = ''
    
    def __init__(self, audio):
        self.audio_file = audio
        self._audio = EasyID3(self.audio_file)
        
    
    def setTags(self, **args):
        if 'tracknumber' in args: self._audio['tracknumber'] = args['tracknumber']
        if 'title' in args: self._audio['title'] = args['title']   
        if 'album' in args: self._audio['album'] = args['album']
        if 'version' in args: self._audio['version'] = args['version']
        if 'artist' in args: self._audio['artist'] = args['artist']
        if 'date' in args: self._audio['date'] = args['date']
        self._audio.save()