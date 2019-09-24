from Tkinter import *
from string import ascii_letters, digits, punctuation, join
import re

class TextWithIndentation(Text):
    tags = {}
    tags['heading1'] = 'navy'
    for i in range (2, 26):
        tags['heading{}'.format(i)] = 'gray{}'.format(i)

    def __init__(self, master):
        Text.__init__(self, master)
        self.config_tags()
        self.characters = ascii_letters + digits + punctuation
        self.line = 1
        self.indent = []
        self.tag_config('heading1', font = 'Helvetica 20 bold')
        self.indent.append('<0>')
        for i in range (2, 26):
            self.tag_config('heading{}'.format(i), lmargin1 = 20*(i-1), lmargin2 = 20*(i-1))
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
                        self.tag_add('heading{}'.format(i), '%s.%d'%(cline, start), '%s.%d'%(cline, end))
                        break
                    else:
                        continue
            break
        self.line += 1

root = Tk()
text = TextWithIndentation(root)
text.config(wrap = WORD, font = 'Helvetica 10', spacing3 = 5)
text.pack()
data = open('instruction')
instruction = data.read().split('\n')
tab = '    ' #a tab is four space
for i in instruction:
    tabArray = [m.start() for m in re.finditer(tab, i)]
    i = i[len(tabArray)*len(tab):]
    key = "<{}>".format(len(tabArray)) 
    text.insert(END, "{}\n".format(i))
    text.key_press("{} {}".format(key, i))
root.mainloop()