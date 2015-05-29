#!/usr/bin/python
import Tkinter as tk, Tkconstants, tkFileDialog

class GuiTraceFileAnalyzer(tk.Frame):

  filename = ' '
  output_dir = '.'

  def __init__(self, root):

    tk.Frame.__init__(self, root)

    # options for buttons
    button_opt = {'fill': Tkconstants.BOTH, 'padx': 5, 'pady': 5}

    # define buttons
    tk.Button(self, text='Trace File', command=self.askopenfilename).pack(**button_opt)
    tk.Button(self, text='Output directory', command=self.askdirectory).pack(**button_opt)
    tk.Button(self, text='Analyze', command=self.analyze_trace).pack(**button_opt)

    # define options for opening or saving a file
    self.file_opt = options = {}
    options['defaultextension'] = '.dbg'
    options['filetypes'] = [('all files', '.*'), ('text files', '.dbg')]
    options['initialdir'] = '/home'
    options['initialfile'] = 'L49MB001.dbg'
    options['parent'] = root
    options['title'] = 'Select a dbg file'

    # This is only available on the Macintosh, and only when Navigation Services are installed.
    #options['message'] = 'message'

    # if you use the multiple file version of the module functions this option is set automatically.
    #options['multiple'] = 1

    # defining options for opening a directory
    self.dir_opt = options = {}
    options['initialdir'] = '/home'
    options['mustexist'] = False
    options['parent'] = root
    options['title'] = 'Result directory'

  def askopenfilename(self):
    """Returns an opened file in read mode.
    This time the dialog just returns a filename and the file is opened by your own code.
    """

    # get filename
    self.filename = tkFileDialog.askopenfilename(**self.file_opt)

    # open file on your own
    if self.filename:
      # return open(filename, 'r')
      print 'Open this file' + self.filename

  def askdirectory(self):
    """Returns a selected directoryname."""
    self.output_dir = tkFileDialog.askdirectory(**self.dir_opt)
    print 'Directory selevcted ' +  self.output_dir

  def analyze_trace(self):
    """Starts the analyze of the given trace file """
    if self.filename == ' ':
      print 'Have no filename, no action done'
    else:
      if self.output_dir == '.':
        print 'Have no output directory, use .'
      else:
        print 'Using output directory ' + self.output_dir
      print 'Do action ' + self.filename

if __name__=='__main__':
  print 'Start select functionality'
  root = tk.Tk()
  GuiTraceFileAnalyzer(root).pack()
  root.mainloop()