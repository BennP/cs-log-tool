#!/usr/bin/env python
import Tkinter as tk

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        self.verLable = tk.Label(self, text='Astro Version')
        self.verLable.grid()
        self.verText = tk.Entry(self, width=10, validate='focus', validatecommand=(isVersionOkay, '%d', '%i', '%S'))
        self.verText.grid()
        self.verText.insert(1, '8.40')
        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.grid()

def isVersionOkay(self, why, where, what):
# Validate that the right version is entered
    print 'Gott why = '
    print why
    print 'Gott where = '
    print where
    print 'Gott what = ' + what
    if why == -1:
        print 'Got ' + what


app = Application()
app.master.title('Astro Trace analyzer')
app.mainloop()