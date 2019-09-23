from Tkinter import *
from string import ascii_letters, digits, punctuation, join
import re

class TextWithIndentation(Text):
    tags = {}
    tags['heading1'] = 'navy'
    for i in range (2, 26): # assuming there is a max of 25 indentation
        if i >= 2 and i <= 5:
            tags['heading{}'.format(i)] = 'RoyalBlue{}'.format(i-1)
        else:
            tags['heading{}'.format(i)] = 'SteelBlue4'
        tags['paragraph{}'.format(i)] = 'gray{}'.format(i-1)

    def __init__(self, master):
        Text.__init__(self, master)
        self.config_tags()
        self.characters = ascii_letters + digits + punctuation
        self.line = 1
        self.indent = []
        self.tag_config('heading1', font = 'Helvetica 16 bold')
        self.indent.append('<0>')
        for i in range (2, 26):
            self.tag_config('heading{}'.format(i), lmargin1 = 40*(i-1), lmargin2 = 40*(i-1), font = 'Helvetica 12 bold')
            self.tag_config('paragraph{}'.format(i), lmargin1 = 40*(i-1), lmargin2 = 40*(i-1), font = 'Helvetica 12')
            self.indent.append('<{}>'.format(i-1))

    def config_tags(self):
        for tag, val in self.tags.items():
            self.tag_config(tag, foreground=val)

    def remove_tags(self, start, end):
        for tag in self.tags.keys():
            self.tag_remove(tag, start, end)
    
    def deleteAll(self):
        self.delete(1.0, END)
        self.line = 1

    def key_press(self, buffer):
        tokenized = buffer.split(' ')
        cline = self.line
        self.remove_tags('%s.%d'%(cline, 0), '%s.%d'%(cline, len(buffer)))

        start, end = 0, 0
        for token in tokenized:
            end = start + len(buffer) - 4
            if token in self.indent:
                for i in range (1, 26):
                    if token == self.indent[i-1]:
                        if i > 1:
                            if len(buffer.split('.')) == 1 and len(buffer) < 40: #if there is only 1 sentence in the paragraph and that sentence is shorter than 40 chars, it is regarded as a heading, else paragraph
                                self.tag_add('heading{}'.format(i), '%s.%d'%(cline, start), '%s.%d'%(cline, end))
                            else:
                                self.tag_add('paragraph{}'.format(i), '%s.%d'%(cline, start), '%s.%d'%(cline, end))
                            break
                        else:
                            self.tag_add('heading{}'.format(i), '%s.%d'%(cline, start), '%s.%d'%(cline, end))
                    else:
                        continue
            break
        self.line += 1