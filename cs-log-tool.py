#!/usr/bin/python3
import argparse
import re
import os
import threading
import webbrowser
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, askdirectory
# --------------------------------------
#    Astro log file analyzer
#
#    ToDo: - Links to ===WRAPPED and ===END yes but it jumps strange
#          - Log with only XML-In / XML-Out
#          - Put MdiDump in a sperat file
#          - General full seak indication at top.
#          - Improve APPL-ERROR to indicate some
#            vellknown types. libmdi.FullScan. Shoe what table it is done on
#                   APPL-ERROR: :      : 13:............./home/sebenpo/projects/x.x/master/src/mdi/libmdi.c:3627,libmdi.FullScan, Caller: /home/sebenpo/projects/x.x/cosmos2/src/ObjG/ObjG09T1.c:2882, Table: SSG10001.shorto42
#          - Events that are not deffined indicated at the top
#          - Make a separat html file where Real Time spent is indicated.
#            With a in parameter decide if you whant Real Time data
#            and indication on what level.
#            "RealTimeSpent=0.000065" and "Real=0020851.669305"
#          - Make the file refernces to places in the source code
#            into actual links that can start a
#            editor at the right place
#            Open Groc "http://localhost:8888/opengrok/xref/x.x/goods2/src/ObjG/ObjG32T1.c#5804"
#          - Is it possible to make the links from one file GWF be connected to
#            the corresponding Trace lines trough links. It would be sufficient to be able to end up in the same minute.
#            So when we pres on a line id or a now ref icone you will get to the first line of that econd in the original trace
#          - Display who is logged in
#          - Use CSS to reduce html size in all parts
#
# --------------------------------------
# Argument parser
parser = argparse.ArgumentParser(description='Process a logfile from Astro.')
parser.add_argument('-gui', help='Run it with a GUI', action="store_true")
parser.add_argument('-l', dest='log_file_name', help='Log file to analyze')
parser.add_argument('-o', dest='html_log_file_name', help='Output in html format. With no filetype given')
parser.add_argument('-d', dest='html_log_file_dir', help='Output folder for the result')
# parser.add_argument('-s', dest='show_all', help='Show all lines')

#-----------------
# Classes

# Row class
class LogRow(object):
   """Common base class for a line of trace data"""
   tot_row = 0

   def __init__(self, row_id, time_stamp, row_text, row_type):
        self.row_id = row_id
        self.time_stamp = time_stamp
        self.row_text = do_remove_real_time_spent( do_code_indent( html_escape( row_text.rstrip())))
        self.row_type = row_type
        LogRow.tot_row += 1


# GWF Row class
class GWFRow:
   'Common base class for a line of GWF trace data'
   tot_row = 0

   def __init__(self, row_id, time_stamp, row_text, row_type):
        self.row_id = row_id
        self.time_stamp = time_stamp
        self.row_text = html_escape(row_text.rstrip())
        self.row_type = row_type
        GWFRow.tot_row += 1

# GWF config class
class GwfConf:
   'Common base class for a Gwf color config data'
   tot_row = 0

   def __init__(self, ident_text, color_text):
        self.ident_text = ident_text
        self.color_text = color_text
        GwfConf.tot_row += 1

# Trace config class
class TraceConf:
   'Common base class for Trace css class config data'
   tot_row = 0

   def __init__(self, ident_text, class_text):
        self.ident_text = ident_text
        self.class_text = class_text
        TraceConf.tot_row += 1

# Trace config class
class TraceIgnore:
   'Common base class for Trace ignore data'
   tot_row = 0

   def __init__(self, ident_text):
        self.ident_text = ident_text
        TraceIgnore.tot_row += 1

# GWF select  class
class GWFSelect:
   'Common base class for GWF select config data'
   tot_row = 0

   def __init__(self, ident_text):
        self.ident_text = ident_text
        GWFSelect.tot_row += 1

# Goods Workflow ignore class
class GwfIgnore:
   'Common base class for Gwf Ignore config data'
   tot_row = 0

   def __init__(self, ident_text):
        self.ident_text = ident_text
        GwfIgnore.tot_row += 1

# DB Error class
class DbError:
   'Common base class for a DbError'
   error_count = 0

   def __init__(self, row_id):
        self.row_id = row_id
        DbError.error_count += 1

# APPL Error class
class ApplError:
   'Common base class for a APPL-ERROR'
   appl_count = 0

   def __init__(self, row_id):
        self.row_id = row_id
        ApplError.appl_count += 1

# Call Trace class
class CallTrace:
   'Common base class for a CallTrace'
   trace_count = 0

   def __init__(self, row_id):
        self.row_id = row_id
        CallTrace.trace_count += 1

# System paramater error class
class SysParTrace:
   'Common base class for a SysParTrace'
   syspar_count = 0
   syspar_txt = 'System parameter not defined'


   def __init__(self, row_id,text):
        self.row_id = row_id
        # Example trace text to extract from "System parameter not defined: MovSplitChgLdCT"
        syspar_offset = text.find(syspar_txt);
        self.syspar = text[(syspar_offset + 29):]
        SysParTrace.syspar_count += 1

# Location search  class
class LocationSearch:
   'Common base class for LocationSearch config data'
   tot_row = 0

   def __init__(self, ident_text):
        self.ident_text = ident_text
        LocationSearch.tot_row += 1

# Location Search Row class
class LocSearchRow:
   'Common base class for a line of Location Search trace data'
   tot_row = 0

   def __init__(self, row_id, time_stamp, row_text, row_type):
        self.row_id = row_id
        self.time_stamp = time_stamp
        self.row_text = html_escape(row_text.rstrip())
        self.row_type = row_type
        LocSearchRow.tot_row += 1

# Location Search color config class
class LocationSearchConf:
   'Common base class for a Location Search color config data'
   tot_row = 0

   def __init__(self, ident_text, color_text):
        self.ident_text = ident_text
        self.color_text = color_text
        LocationSearchConf.tot_row += 1

# Location Search ignore class
class LocSearchIgnore:
   """Common base class for Location Search Ignore config data"""
   tot_row = 0

   def __init__(self, ident_text):
        self.ident_text = ident_text
        LocSearchIgnore.tot_row += 1

# Box Calc  class
class BoxCalc:
   'Common base class for BoxCalc config data'
   tot_row = 0

   def __init__(self, ident_text):
        self.ident_text = ident_text
        BoxCalc.tot_row += 1

# Box Calc Row class
class BoxCalcRow:
   'Common base class for a line of Box Calc trace data'
   tot_row = 0

   def __init__(self, row_id, time_stamp, row_text, row_type):
        self.row_id = row_id
        self.time_stamp = time_stamp
        self.row_text = html_escape(row_text.rstrip())
        self.row_type = row_type
        BoxCalcRow.tot_row += 1

# Box Calc color config class
class BoxCalcConf:
   'Common base class for a Box Calc color config data'
   tot_row = 0

   def __init__(self, ident_text, color_text):
        self.ident_text = ident_text
        self.color_text = color_text
        BoxCalcConf.tot_row += 1

# End Classes
#-----------------


#-----------------
# Functions

def get_row_type(row_class_list, text):
    """Determine row type from text."""
    for index in range(len(row_class_list)):
        if text.find(row_class_list[index].ident_text) != -1:
            return index
    return -1

def get_row_class(class_list, id):
    """Get row class """
    if id == -1:
        return '"norm"'
    return '"' + class_list[id].class_text + '"'

def get_gwf_row_type(conf_list, text):
    """Determine gwf row type from text."""
    for index in range(len(conf_list)):
        if text.find(conf_list[index].ident_text) != -1:
            return index
    return -1

def get_gwf_row_color(conf_list, id):
    """Get gwf row color """
    if id == -1:
        return '"black"'
    return '"' + conf_list[id].color_text + '"'

def limit_trace(ignore_list, text):
    """Determine if row should be ignored."""
    for index in range(len(ignore_list)):
        if text.find(ignore_list[index].ident_text) != -1:
            return True
    return False

def limit_gwf_trace(ignore_list, text):
    """Determine gwf row that should be ignored."""
    for index in range(len(ignore_list)):
        if text.find(ignore_list[index].ident_text) != -1:
            return True
    return False

def is_gwf_trace(select_conf_list, text):
    """Determine if text is gwf trace that should be included."""
    for index in range(len(select_conf_list)):
        if text.find(select_conf_list[index].ident_text) != -1:
            return True
    return False


def is_loc_search_trace(conf_list, text):
    """Determine if text is location search that should be included."""
    for index in range(len(conf_list)):
        if text.find(conf_list[index].ident_text) != -1:
            return True
    return False

def get_loc_search_row_type(color_conf_list, text):
    """Determine Location Search row type from text."""
    for index in range(len(color_conf_list)):
        if text.find(color_conf_list[index].ident_text) != -1:
            return index
    return -1

def get_loc_search_row_color(color_conf_list, id):
    """Get Location Search row color """
    if id == -1:
        return '"black"'
    return '"' + color_conf_list[id].color_text + '"'

def limit_loacsearch_trace(ignore_list, text):
    """Determine location search row that should be ignored."""
    for index in range(len(ignore_list)):
        if text.find(ignore_list[index].ident_text) != -1:
            return True
    return False

#
# TODO Is this not a candidate for a general function to check config data
#
def is_box_calc_trace(conf_list, text):
    """Determine if text is Box Calc that should be included."""
    for index in range(len(conf_list)):
        if text.find(conf_list[index].ident_text) != -1:
            return True
    return False

def get_box_calc_row_type(color_conf_list, text):
    """Determine Box Calc row type from text."""
    for index in range(len(color_conf_list)):
        if text.find(color_conf_list[index].ident_text) != -1:
            return index
    return -1

# TODO Yet another candidate for generic function
def get_box_calc_row_color(color_conf_list, id):
    """Get Box Calc row color """
    if id == -1:
        return '"black"'
    return '"' + color_conf_list[id].color_text + '"'

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

def do_set_end_mark(end_line, row_id, text):
    """If the line is the ===END marker."""
    if text.find('===END') != -1:
        end_line = row_id;

def do_set_wrapped_mark(wrapped_line, row_id, text):
    """If the line is the ===WRAPPED marker."""
    if text.find('===WRAPPED') != -1:
        wrapped_line = row_id;

def do_db_error(db_list, row_id, text):
    """If the line is a DB error then add it to the list."""
    if text.find('DB  -ERROR') != -1:
        # ,F,s01param,EQ :
        matchObj = re.search( '[,]{1}.[,]{1}[0-9a-xA-X]*[,].. :', text, re.M|re.I)
        if not matchObj:
            add_dberror = DbError(row_id)
            db_list.append(add_dberror)

def do_syspar_error(syspar_error_list, row_id, text):
    """If the line is a "System parameter not defined" error then add it to the list."""

    if text.find(SysParTrace.syspar_txt) != -1:
        add_syspar_error = SysParTrace(row_id,text)
        syspar_error_list.append(add_syspar_error)

def do_db_error_table(db_list, out_file):
    """Write a scrollable list with all db errors."""

    db_line = "<p class=%s>" % ('"dberror-scroll"')
    out_file.write(db_line)
    out_file.write("  DB  -ERROR\n")

    for index in range(len(db_list)):
        db_line = "  <a href=%s>%s</a>\n" % ('"#' + str(db_list[index].row_id) + '"', db_list[index].row_id)
        out_file.write(db_line)
    out_file.write("</p>\n")


def do_appl_error(appl_list, row_id, text):
    """If the line is a APPL-ERROR then add it to the list."""
    if text.find('APPL-ERROR') != -1:
        add_appl_error = ApplError(row_id)
        appl_list.append(add_appl_error)

def do_appl_error_table(appl_list, out_file):
    """Write a scrollable list with all APPL-ERROR."""

    appl_line = "<p class=%s>" % ('"applerror-scroll"')
    out_file.write(appl_line)
    out_file.write("  APPL-ERROR\n")

    for index in range(len(appl_list)):
        appl_line = "  <a href=%s>%s</a>\n" % ('"#' + str(appl_list[index].row_id) + '"', appl_list[index].row_id)
        out_file.write(appl_line)
    out_file.write("</p>\n")


def do_call_trace(trace_list, row_id, text):
    """If the line is a CallTrace start then add it to the list."""
    if text.find('CallTrace :  0') != -1:
        add_call_trace = CallTrace(row_id)
        trace_list.append(add_call_trace)

def do_call_trace_table(trace_list, out_file):
    """Write a scrollable list with all Calltrace."""

    trace_line = "<p class=%s>" % ('"trace-scroll"')
    out_file.write(trace_line)
    out_file.write("  CallTrace\n")

    for index in range(len(trace_list)):
        trace_line = "  <a href=%s>%s</a>\n" % ('"#' + str(trace_list[index].row_id) + '"', trace_list[index].row_id)
        out_file.write(trace_line)
    out_file.write("</p>\n")

def do_syspar_trace_table(syspar_list, out_file):
    """Write a scrollable list with all System Parameter errors."""

    trace_line = "<p class=%s >" % ('"syspar-scroll"')
    out_file.write(trace_line)
    out_file.write("  SysPar missing\n")

    for index in range(len(syspar_list)):
        syspar_line = "  <a href=%s>%s</a> %s \n" % ('"#' + str(syspar_list[index].row_id) + '"', syspar_list[index].row_id, syspar_list[index].syspar)
        out_file.write(syspar_line)
    out_file.write("</p>\n")

def do_code_indent(text):
    """ If the line is a "APPL-OK   : :      :  X:" line then do a indention according to the level given at x. """
    """ And do some rearanging of the actual test to make it more readable                                      """
    if text.find('APPL-OK   : :      :') != -1:
        offset = text.find('OK   : :      :')
        if offset == -1:
            print(' This line must be wrong')
            print (text)
            return text
        else:
            num = text[(offset + 16):(offset + 20)].split(':',2)
            indent_number = int (num[0])
            indent_str = '                                                              '
            offset_tail = text.find('./')
            if offset == -1:
                print(' This line must be wrong')
                print (text)
                return text
            # Now we have indented the text. Lets move some stuf around to make it mor readable
            # split this into several parts /ikea/lpp/astrodev/cosmos2/src/ObjL/ObjL54T1.c:3816,Assignment.SetUnderProcessing, Caller: /ikea/lpp/astrodev/cosmos2/src/ObjL/ObjL47T1.c:2223, RetOk
            file_parts = text[(offset_tail + 1 ):].split(',',4)
            # print file_parts[1] + ' .' + file_parts[0] + ',' + file_parts[2] + ',' + file_parts[3]
            return text[:(offset + 2)] + indent_str[:(indent_number * 4)] + num[0] + '. ' + file_parts[1] + '   .' + file_parts[0] + ',' + file_parts[2] + ',' + file_parts[3]
    else:
       return text

def do_remove_real_time_spent(text):
    """If the line has a RealTimeSpent content then remove this """
    #if text.find('RealTimeSpent') != -1:
    offset = text.find('RealTimeSpent');
    if offset != -1:
        text_length = len(text)
        # RealTimeSpent=0.000211
        if (text_length - offset) == 22:
            # offset -2 to remove a ','
            return text[:(offset - 2)]
        return text
    else:
        return text

def remove_pure_xml_row(text):
    # Return false if the row begins with < and in
    # parameter is not set to "show"
    tmp_text = text.strip()
    if tmp_text.startswith( '<' ):
        return True
    return False

def do_html_file_header(out_file, file_name):
    """Write html file header info."""

    out_file.write("<!DOCTYPE html>\n<html><head><title>#Consafe Astro log analysis</title></head><body>\n")
    # Set style for table boarders
    out_file.write("<style>table,th,td{border:1px solid black;}</style>\n")
    # Write a header
    out_file.write("<hr>\n<h1>    Astro Trace analyzer </h1>\n</hr>\n")
    # Write file name analyzed
    print_h_line = "<hr>\n<h3>File analyzed %s</h3>\n</hr>\n" % (file_name)
    out_file.write(print_h_line)

def do_html_file_reference(out_file, file_text, to_file, css_class):
    """Write html link to other files."""

    print_h_line = "<h3 class=%s> <a href=%s>%s</a></h3>\n" % ('"' + css_class + '"', '"' + to_file + '"', file_text)
    out_file.write(print_h_line)

def do_html_file_stop_float(out_file):
    """Write html line to stop float."""

    print_h_line = "<h3 class=%s></h3>\n" % ('"stop-float"')
    out_file.write(print_h_line)

def do_html_end_wrapped_mark(wrapped_line, end_line, out_file):
    """Write end / wrapped mark info."""

    print_h_line = "<div class=%s>\n<p>" % ('"wrapp"')
    out_file.write(print_h_line)
    if wrapped_line < 0:
        out_file.write("File not wrapped")
    else:
        # Indicate that file is wrapped
        print_h_line = "File is wrapped here <a href=%s>%s</a> and ends here <a href=%s>%s</a> " % ('"#' + str(wrapped_line) + '"',
                                                                                                                   wrapped_line,
                                                                                                                   '"#' + str(end_line) + '"',
                                                                                                                   end_line)
        out_file.write(print_h_line)
    out_file.write("</p>\n</div>\n")

def do_html_file_end(out_file):
    """Write html file end info."""
    out_file.write("</body></html>")

def do_write_css_to_file(css_text, out_file):
    """Write css data to file"""
    for line in css_text:
        out_file.write(line)

def get_config_path():
    """ Try to find where the config files are. Using env variable PATH """
    env_path = os.environ['PATH']
    env_parts = env_path.split(':')
    for dir in env_parts:
        if os.path.isfile(dir + '/trace-color.conf'):
            return dir + '/'
    return ''


def read_log_file_config( ignore_list ):
    """ Read the different configuration files.
       Ignore lines,
       Colour setings """

    config_path = get_config_path()

    try:
        trace_ignore_file    = open(config_path + 'trace-ignore.conf')
        for ignore_line in trace_ignore_file:
            add_row = TraceIgnore(ignore_line.rstrip())
            ignore_list.append(add_row)
        trace_ignore_file.close()
    except IOError:
        print ("Error: can\'t find file or read data " + 'trace-ignore.conf')
        raise

def read_gwf_config(select_list, conf_list, ignore_list):
    """ Read the GWF configuration files.
       Ignore lines,
       Colour settings """

    config_path = get_config_path()

    try:
        gwf_select_file    = open(config_path + 'gwf-select.conf')
        for gwf_select_line in gwf_select_file:
            add_row = GWFSelect(gwf_select_line.rstrip())
            select_list.append(add_row)
        gwf_select_file.close()
    except IOError:
        print ("Error: can\'t find file or read data " + 'gwf-select.conf')
        raise

    try:
        gwf_config_file    = open(config_path + 'gwf-color.conf')
        for conf_line in gwf_config_file:
            tmp_conf = conf_line.rstrip()
            parts = tmp_conf.split(';',2)
            add_row = GwfConf(parts[0],parts[1])
            conf_list.append(add_row)
        gwf_config_file.close()
    except IOError:
        print ("Error: can\'t find file or read data " + 'gwf-color.conf')
        raise

    try:
        gwf_ignore_file    = open(config_path + 'gwf-ignore.conf')
        for ignore_line in gwf_ignore_file:
            add_row = GwfIgnore(ignore_line.rstrip())
            ignore_list.append(add_row)
        gwf_ignore_file.close()
    except IOError:
        print ("Error: can\'t find file or read data " + 'gwf-ignore.conf')
        raise

def read_location_search_config(color_list, ignore_list, search_list):
    """ Read the location search configuration files.
       Ignore lines,
       Colour settings """

    config_path = get_config_path()

    try:
        loc_search_color_config_file    = open(config_path + 'loc-search-color.conf')
        for conf_line in loc_search_color_config_file:
            tmp_conf = conf_line.rstrip()
            parts = tmp_conf.split(';',2)
            add_row = LocationSearchConf(parts[0],parts[1])
            color_list.append(add_row)
        loc_search_color_config_file.close()
    except IOError:
        print ("Error: can\'t find file or read data " + 'loc-search-color.conf')
        raise

    try:
        loc_ignore_file    = open(config_path + 'loc-search-ignore.conf')
        for ignore_line in loc_ignore_file:
            add_row = LocSearchIgnore(ignore_line.rstrip())
            ignore_list.append(add_row)
        loc_ignore_file.close()
    except IOError:
        print ("Error: can\'t find file or read data " + '-ignore.conf')
        raise

    try:
        loc_search_file    = open(config_path + 'loc-search.conf')
        for loc_search_line in loc_search_file:
            add_row = LocationSearch(loc_search_line.rstrip())
            search_list.append(add_row)
        loc_search_file.close()
    except IOError:
        print ("Error: can\'t find file or read data " + 'loc-search.conf')
        raise

def read_box_calc_config(color_list, conf_list):
    """ Read the box calck configuration files.
       Ignore lines,
       Colour settings """

    config_path = get_config_path()

    try:
        box_calc_color_config_file    = open(config_path + 'box-calc-color.conf')
        for conf_line in box_calc_color_config_file:
            tmp_conf = conf_line.rstrip()
            parts = tmp_conf.split(';',2)
            add_row = BoxCalcConf(parts[0],parts[1])
            color_list.append(add_row)
        box_calc_color_config_file.close()
    except IOError:
        print ("Error: can\'t find file or read data " + 'box-calc-color.conf')
        raise

    try:
        box_calc_file    = open(config_path + 'box-calc.conf')
        for box_calc_line in box_calc_file:
            add_row = BoxCalc(box_calc_line.rstrip())
            conf_list.append(add_row)
        box_calc_file.close()
    except IOError:
        print ("Error: can\'t find file or read data " + 'box-calc.conf')
        raise

def read_css_config(class_list, css_text_list):
    """ Read the configuration files for css."""

    config_path = get_config_path()

    try:
        trace_config_file    = open(config_path + 'trace-class.conf')
        for conf_line in trace_config_file:
            tmp_conf = conf_line.rstrip()
            parts = tmp_conf.split(';',2)
            add_row = TraceConf(parts[0],parts[1])
            class_list.append(add_row)
        trace_config_file.close()
    except IOError:
        print ("Error: can\'t find file or read data " + 'trace-color.conf')
        raise

    try:
        css_text_file    = open(config_path + 'css.conf')
        for css_line in css_text_file:
            # add_row = BoxCalc(box_calc_line.rstrip())
            css_text_list.append(css_line)
        css_text_file.close()
    except IOError:
        print ("Error: can\'t find file or read data " + 'css.conf')
        raise



class SessionGuiData:
    """Common base class for saving data between user gui sessions """
    def __init__(self, save_file_name):
        self.file_name_token = 'filename='
        self.out_dir_token   = 'outdir='
        self.html_token      = 'html='
        self.file_name       = ' '
        self.out_dir         = ' '
        self.html_name       = ' '
        self.gui_save_file_name = save_file_name
        self.config_path = get_config_path()
        # Try to get data from old runs
        try:
            gui_save_file    = open(self.config_path + self.gui_save_file_name)
            for line in gui_save_file:
                offset = line.find(self.file_name_token)
                if offset != -1:
                    # This is filename
                    self.file_name = line[offset + len(self.file_name_token):].strip('\n')
                    #print ('Filename  ' + line[offset + len(file_name_token):])
                offset = line.find(self.out_dir_token)
                if offset != -1:
                    # This is outdir
                    self.out_dir = line[offset + len(self.out_dir_token):].strip('\n')
                    # print ('Outdir  ' + line[offset + len(out_dir_token):])
                offset = line.find(self.html_token)
                if offset != -1:
                    # This is result html name
                    self.html_name = line[offset + len(self.html_token):].strip('\n')
                    #print ('Html name  ' + line[offset + len(html_token):])
            gui_save_file.close()
        except IOError:
            # No gui-save file found create one
            print('No Gui save file found, creating a new one' + self.config_path + self.gui_save_file_name)
            self.file_name       = os.getcwd()
            self.out_dir         = os.getcwd()
            self.html_name       = 'new'
            new_gui_save_file = open(self.config_path + self.gui_save_file_name , 'w')
            new_gui_save_file.write(self.file_name_token + self.file_name + "\n")
            new_gui_save_file.write(self.out_dir_token + self.out_dir + "\n")
            new_gui_save_file.write(self.html_token + self.html_name + "\n")
            new_gui_save_file.close()

    def get_file_name(self):
        """
        Get the file name from the saved data
        """
        return self.file_name

    def set_file_name(self,file_name):
        """
        Set the file name
        """
        self.file_name = file_name

    def get_out_dir(self):
        """
        Get the output directory from the saved data
        """
        return self.out_dir

    def set_out_dir(self,out_dir):
        """
        Set the output directory
        """
        self.out_dir = out_dir

    def get_html_name(self):
        """
        Get the name of the html file from the saved data
        """
        return self.html_name

    def set_html_name(self,html_name):
        """
        Set the html name
        """
        self.html_name = html_name

    def save_gui_input(self):
        """
        Save the input field values for future runs
        """
        try:
            # No gui-save file found create one
            gui_save_file = open(self.config_path + self.gui_save_file_name , 'w')
            gui_save_file.seek(0)
            gui_save_file.truncate()
            gui_save_file.write(self.file_name_token + str(self.file_name) + "\n")
            gui_save_file.write(self.out_dir_token   + str(self.out_dir)   + "\n")
            gui_save_file.write(self.html_token      + str(self.html_name) + "\n")
            gui_save_file.close()
        except IOError:
            print('Not able to save gui save data')
            return

        return

def parse_file(file_to_parse, output_name, output_dir):
    """
    Will pars a given Astro log file

    Will produce output HTML files
      - Main file with
        - Info on the whole file
        - Links to the specific sub files
        - Entier log colour coded and cleaned
    """

    line_list = []

    #-----------------
    # Main trace lists
    trace_class_list = []
    trace_ignore_list = []
    db_list = []
    appl_list = []
    trace_list = []
    syspar_list = []
    end_line = -1
    wrapped_line = -1

    #-----------------
    # GWF trace lists
    gwf_list = []
    gwf_select_conf_list = []
    gwf_conf_list = []
    gwf_ignore_list = []

    #-----------------
    # Location search trace lists
    loc_search_list = []
    loc_search_conf_list = []
    loc_search_color_conf_list = []
    loc_ignore_list = []

    #-----------------
    # BoxCalc trace lists
    box_calc_list = []
    box_calc_conf_list = []
    box_calc_color_conf_list = []

    #-----------------
    # CSS text list
    css_text = []

    save_row_type = 0

    trace_file_full_name = str(output_dir) + '/' + str(output_name) + '.html'
    gwf_trace_file_full_name = str(output_dir) + '/' + 'GWF-' + str(output_name) + '.html'
    loc_search_trace_file_full_name = str(output_dir) + '/' + 'LocSearch-' + str(output_name) + '.html'
    box_calc_trace_file_full_name = str(output_dir) + '/' + 'BoxCalc-' + str(output_name) + '.html'

    trace_file_name = str(output_name) + '.html'
    gwf_trace_file_name = 'GWF-' + str(output_name) + '.html'
    loc_search_trace_file_name = 'LocSearch-' + str(output_name) + '.html'
    box_calc_trace_file_name = 'BoxCalc-' + str(output_name) + '.html'

    # Debug
    #print ('Astro log file = ' + file_to_parse)
    #print ('Output file    = ' + trace_file_full_name)
    #print ('Output file GWF  = ' + gwf_trace_file_full_name)
    #print ('Output file LocSearch  = ' + loc_search_trace_file_full_name)
    #print ('Output file BoxCalc  = ' + box_calc_trace_file_full_name)

    # Open files
    log_file                = open(file=file_to_parse, encoding='iso-8859-1')
    output_file             = open(trace_file_full_name, 'w')
    gwf_output_file         = open(gwf_trace_file_full_name, 'w')
    loc_search_output_file  = open(loc_search_trace_file_full_name, 'w')
    box_calc_output_file    = open(box_calc_trace_file_full_name, 'w')

    # Read the configuration files
    read_log_file_config(trace_ignore_list)
    read_gwf_config(gwf_select_conf_list, gwf_conf_list, gwf_ignore_list)
    read_location_search_config(loc_search_color_conf_list, loc_ignore_list, loc_search_conf_list)
    read_box_calc_config(box_calc_color_conf_list, box_calc_conf_list)
    read_css_config(trace_class_list, css_text)


    #------------------------------
    # Rip the logs apart and find out some basic data about the log.
    # The ripped log will later be used to generate a HTML page.
    #------------------------------
    line_id = 0
    gwf_line_id = 0
    loc_line_id = 0
    box_line_id = 0
    for line in log_file:
        if not limit_trace(trace_ignore_list, line):
            do_set_end_mark(end_line, line_id, line)
            do_set_wrapped_mark(wrapped_line, line_id, line)
            matchObj = re.match( r'[0-9]{2}-[0-9]{2}-[0-9]{2}', line, re.M|re.I)
            if matchObj:
                offset = line.find("Real=")
                if offset == -1:
                    add_row = LogRow(line_id,line[0:17],' ' + line[(19):],get_row_type(trace_class_list, line))
                else:
                    add_row = LogRow(line_id,line[0:17],line[(offset + 21):],get_row_type(trace_class_list, line))
                save_row_type = get_row_type(trace_class_list, line)
                do_db_error(db_list, line_id, line)
                do_appl_error(appl_list, line_id, line)
                do_call_trace(trace_list, line_id, line)
                do_syspar_error(syspar_list, line_id, line)
                line_list.append(add_row)
                line_id = line_id + 1
            else:
                if not remove_pure_xml_row(line):
                    add_row = LogRow(line_id,' ',line[0:],save_row_type)
                    line_list.append(add_row)
                    line_id = line_id + 1

        #------------------------------
        matchObj = re.match( r'[0-9]{2}-[0-9]{2}-[0-9]{2}', line, re.M|re.I)
        if matchObj:
            offset = line.find("Real=");
            #------------------------------
            # Find gwf data
            if is_gwf_trace(gwf_select_conf_list, line):
                if not limit_gwf_trace(gwf_ignore_list, line):
                    add_row = GWFRow(gwf_line_id,line[0:17],line[(offset + 21):],get_gwf_row_type(gwf_conf_list, line))
                    gwf_list.append(add_row)
                    gwf_line_id = gwf_line_id + 1
            #------------------------------
            # Find Location Search data
            if is_loc_search_trace(loc_search_conf_list, line):
                if not limit_loacsearch_trace(loc_ignore_list, line):
                    add_row = LocSearchRow(loc_line_id,line[0:17],line[(offset + 21):],get_loc_search_row_type(loc_search_conf_list, line))
                    loc_search_list.append(add_row)
                    loc_line_id = loc_line_id + 1
            #------------------------------
            # Find Box Calc data
            if is_box_calc_trace(box_calc_conf_list, line):
                offset = line.find("Real=");
                add_row = BoxCalcRow(box_line_id,line[0:17],line[(offset + 21):],get_box_calc_row_type(box_calc_color_conf_list, line))
                box_calc_list.append(add_row)
                box_line_id = box_line_id + 1

    log_file.close()

    #---------------
    # Result of file runtrough
    #---------------
    #print ("Number of DB Errors = %d" % DbError.error_count)
    #print ("Number of APPL-ERROR = %d" % ApplError.appl_count)
    #print ("Number of CallTrace = %d" % CallTrace.trace_count)
    #print ("Number of SysPar errors = %d" % SysParTrace.syspar_count)
    #print ("Total rows %d" % LogRow.tot_row)
    #print ("Total GWF rows %d" % GWFRow.tot_row)
    #print ("Total Location Search rows %d" % LocSearchRow.tot_row)
    #print ("Total Box Calc rows %d" % BoxCalcRow.tot_row)
    #print ("End mark %d" % end_line)
    #print ("Wrapped mark %d" % wrapped_line)

    #---------------
    # Start making the HTML files
    #------------------------------
    #--- Goods Workflow
    #---------------
    if len(gwf_list) > 0:
        do_html_file_header(gwf_output_file, file_to_parse)
        do_html_file_reference(gwf_output_file, "Main trace ", trace_file_name, 'm-file')

        print_h_line = "<p style=%s >\n" % ('"background-color:#F8F8F8"')
        gwf_output_file.write(print_h_line)
        save_row_type = gwf_list[0].row_type
        list_number = len(gwf_list)

        for index in range(len(gwf_list)):
            print_text = gwf_list[index].row_text

            if print_text.find('Goods workflow completed') != -1:
                print_text = gwf_list[index].row_text + ' <<<<<<<<<<<<<<<<<<<'
            elif print_text.find('AllPalletsInReceipt : Ente') != -1:
                print_text = '----' + gwf_list[index].row_text + '===>'
            elif print_text.find('AllPalletsInReceipt : Leaving ok') != -1:
                print_text = '----' + gwf_list[index].row_text + '......<==='
            elif print_text.find('AllPalletsInShipment : Ente') != -1:
                print_text = '----' + gwf_list[index].row_text + '===>'
            elif print_text.find('AllPalletsInShipment : Leaving ok') != -1:
                print_text = '----' + gwf_list[index].row_text + '......<==='
            elif print_text.find(': Entered') != -1:
                print_text = gwf_list[index].row_text + ' >>>>>>>>>>>>>>>>>>>'
            elif print_text.find('Leaving ok') != -1:
                print_text = gwf_list[index].row_text + ' <<<<<<<<'

            elif print_text.find('GWF : Do') != -1:
                print_text = '----' + gwf_list[index].row_text
            elif print_text.find('Skipped - handled earlier in code') != -1:
                print_text = '--------' + gwf_list[index].row_text
            elif print_text.find('not active') != -1:
                print_text = '--------' + gwf_list[index].row_text
            elif print_text.find('Verb is') != -1:
                print_text = '----' + gwf_list[index].row_text
            elif print_text.find('Global data cleared') != -1:
                print_text = '----' + gwf_list[index].row_text
            elif print_text.find('Print queue cleared') != -1:
                print_text = '----' + gwf_list[index].row_text
            elif print_text.find('No queued workflows to execute') != -1:
                print_text = '----' + gwf_list[index].row_text
            elif print_text.find('Print queue was empty. Nothing to print') != -1:
                print_text = '----' + gwf_list[index].row_text
            elif print_text.find('Term caching enabled') != -1:
                print_text = '----' + gwf_list[index].row_text
            elif print_text.find('Breaking current flow') != -1:
                print_text = '--------' + gwf_list[index].row_text
            elif print_text.find(', action') != -1:
                print_text = '--------' + gwf_list[index].row_text
            elif print_text.find('Divcode is') != -1:
                print_text = '----' + gwf_list[index].row_text
            elif print_text.find('Event prefix') != -1:
                print_text = '------------' + gwf_list[index].row_text
            elif print_text.find('Event object') != -1:
                print_text = '------------' + gwf_list[index].row_text
            elif print_text.find('Can not get inorderline') != -1:
                print_text = '--------' + gwf_list[index].row_text
            elif print_text.find('Event verb') != -1:
                print_text = '------------' + gwf_list[index].row_text
            else:
                print_text = gwf_list[index].row_text

            print_line = "<FONT COLOR=%s>%8.1d <a name=%s></a> <FONT COLOR=%s>%s <FONT COLOR=%s>%s" % ('"grey"',index, '"' + str(index) + '"', '"green"',gwf_list[index].time_stamp, get_gwf_row_color(gwf_conf_list, gwf_list[index].row_type),print_text)
            gwf_output_file.write(print_line)

            if (index + 1) < list_number:
                if gwf_list[index+1].row_type == save_row_type:
                    gwf_output_file.write("<br>\n")
                else:
                    save_row_type = gwf_list[index + 1].row_type
                    print_line = "</p> \n<p style=%s >\n" % ('"background-color:#F8F8F8"')
                    gwf_output_file.write(print_line)
    else:
        do_html_file_header(gwf_output_file, file_to_parse)
        do_html_file_reference(gwf_output_file, "Main trace ", trace_file_name, 'm-file')

        do_html_file_end(gwf_output_file)
        gwf_output_file.close()

    #------------------------------
    #--- Location Search
    #---------------
    if len(loc_search_list) > 0:
        do_html_file_header(loc_search_output_file, file_to_parse)
        do_html_file_reference(loc_search_output_file, "Main trace ", trace_file_name, 'm-file')

        print_h_line = "<p style=%s >\n" % ('"background-color:#F8F8F8"')
        loc_search_output_file.write(print_h_line)
        save_row_type = loc_search_list[0].row_type
        list_number = len(loc_search_list)

        for index in range(len(loc_search_list)):
            print_text = loc_search_list[index].row_text
            print_line = "<FONT COLOR=%s>%8.1d <a name=%s></a> <FONT COLOR=%s>%s <FONT COLOR=%s>%s" % ('"grey"',index, '"' + str(index) + '"', '"green"',loc_search_list[index].time_stamp, get_loc_search_row_color(loc_search_color_conf_list, loc_search_list[index].row_type),print_text)
            loc_search_output_file.write(print_line)

            if (index + 1) < list_number:
                if loc_search_list[index+1].row_type == save_row_type:
                    loc_search_output_file.write("<br>\n")
                else:
                    save_row_type = loc_search_list[index + 1].row_type
                    print_line = "</p> \n<p style=%s >\n" % ('"background-color:#F8F8F8"')
                    loc_search_output_file.write(print_line)
    else:
        do_html_file_header(loc_search_output_file, file_to_parse)
        do_html_file_reference(loc_search_output_file, "Main trace ", trace_file_name, 'm-file')

        do_html_file_end(loc_search_output_file)
        loc_search_output_file.close()

    #------------------------------
    #--- Box Calc
    #---------------
    if len(box_calc_list) > 0:
        do_html_file_header(box_calc_output_file, file_to_parse)
        do_html_file_reference(box_calc_output_file, "Main trace ", trace_file_name, 'm-file')

        print_h_line = "<p style=%s >\n" % ('"background-color:#F8F8F8"')
        box_calc_output_file.write(print_h_line)
        save_row_type = box_calc_list[0].row_type
        list_number = len(box_calc_list)

        for index in range(len(box_calc_list)):
            print_text = box_calc_list[index].row_text
            print_line = "<FONT COLOR=%s>%8.1d <a name=%s></a> <FONT COLOR=%s>%s <FONT COLOR=%s>%s" % ('"grey"',index, '"' + str(index) + '"', '"green"',box_calc_list[index].time_stamp, get_box_calc_row_color(box_calc_color_conf_list, box_calc_list[index].row_type),print_text)
            box_calc_output_file.write(print_line)

            if (index + 1) < list_number:
                if box_calc_list[index+1].row_type == save_row_type:
                    box_calc_output_file.write("<br>\n")
                else:
                    save_row_type = box_calc_list[index + 1].row_type
                    print_line = "</p> \n<p style=%s >\n" % ('"background-color:#F8F8F8"')
                    box_calc_output_file.write(print_line)
    else:
        do_html_file_header(box_calc_output_file, file_to_parse)
        do_html_file_reference(box_calc_output_file, "Main trace ", trace_file_name, 'm-file')

        do_html_file_end(box_calc_output_file)
        box_calc_output_file.close()

    #---------------
    #--- Trace file
    #---------------
    do_html_file_header(output_file, file_to_parse)
    do_write_css_to_file(css_text, output_file)
    do_html_file_reference(output_file, "GWF trace ", gwf_trace_file_name, 'gwf-file')
    do_html_file_reference(output_file, "Location Search ", loc_search_trace_file_name, 'ls-file')
    do_html_file_reference(output_file, "Box Calc ", box_calc_trace_file_name, 'box-file')
    do_html_file_stop_float(output_file)
    do_html_end_wrapped_mark(wrapped_line, end_line, output_file)

    do_db_error_table(db_list, output_file)
    do_appl_error_table(appl_list, output_file)
    do_call_trace_table(trace_list, output_file)
    do_syspar_trace_table(syspar_list, output_file)
    do_html_file_stop_float(output_file)

    save_row_type = line_list[0].row_type
    print_h_line = "<p class=%s >" % (get_row_class(trace_class_list, line_list[0].row_type))
    output_file.write(print_h_line)

    list_number = len(line_list)

    for index in range(len(line_list)):

        print_line = " <a name=%s>%8.1d</a> <mark class=%s>%s</mark> %s" % ('"' + str(index) + '"', index, '"x1"', line_list[index].time_stamp, line_list[index].row_text)
        output_file.write(print_line)

        if (index + 1) < list_number:
            if line_list[index+1].row_type == save_row_type:
                output_file.write("\n")
            else:
                save_row_type = line_list[index + 1].row_type
                print_line = "</p> \n<p class=%s >" % (get_row_class(trace_class_list, line_list[index+1].row_type))
                output_file.write(print_line)

    output_file.write("</p>")
    do_html_file_end(output_file)

    output_file.close()

class MyThread (threading.Thread):
    def __init__(self, threadID, trace_file, html_name, out_dir):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.trace_file = trace_file
        self.html_name = html_name
        self.out_dir = out_dir
    def run(self):
        #print ('Do action {0} with name {1} to output {2}'.format(self.trace_file, self.html_name, self.out_dir))
        parse_file( self.trace_file, self.html_name, self.out_dir)
        #print ('Exiting ' + self.trace_file )
        url_result = self.out_dir + '/' + self.html_name + '.html'
        webbrowser.open(url_result)

class GuiTraceFileAnalyzer(Frame):
    """ The Gui selection of files and destination  """

    def __init__(self, root):

        Frame.__init__(self, root)

        self.filename = 'Dummy'
        self.output_dir = 'Dummy'
        self.html_name = 'Dummy'

        # options for buttons
        button_opt = {'fill': BOTH, 'padx': 5, 'pady': 5}

        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.selected_file  = StringVar()
        self.selected_dir   = StringVar()
        self.html_file_name = StringVar()

        # Get old used directories if exists

        self.saved_gui_input = SessionGuiData('gui-save')

        self.filename = self.saved_gui_input.get_file_name()
        self.output_dir = self.saved_gui_input.get_out_dir()
        self.html_name = self.saved_gui_input.get_html_name()

        self.selected_file.set(self.saved_gui_input.get_file_name())
        self.selected_dir.set(self.saved_gui_input.get_out_dir())
        self.html_file_name.set(self.saved_gui_input.get_html_name())

        self.selected_file_entry = Entry(self, width=27, textvariable=self.selected_file)
        self.selected_file_entry.grid(column=2, row=1, sticky=(W, E))

        self.selected_dir_entry = Entry(self, width=17, textvariable=self.selected_dir)
        self.selected_dir_entry.grid(column=2, row=2, sticky=(W, E))

        self.html_file_name_entry = Entry(self, width=17, textvariable=self.html_file_name)
        self.html_file_name_entry.grid(column=2, row=3, sticky=(W, E))

        self.selected_file_entry.focus()

        # define buttons
        Button(self, text='Trace File',       command=self.askopenfilename).grid(column=1, row=1, sticky=W)
        Button(self, text='Output directory', command=self.askdirectory   ).grid(column=1, row=2, sticky=W)
        Label (self, text='Result name'                                   ).grid(column=1, row=3, sticky=W)
        Button(self, text='Analyze',          command=self.analyze_trace  ).grid(column=1, row=4, sticky=E)
        Button(self, text='Cancel',           command=self.analyze_cancel ).grid(column=2, row=4, sticky=E)

        # define options for opening or saving a file
        self.file_opt = options = {}
        options['defaultextension'] = '.dbg'
        options['filetypes'] = [('all files', '.*'), ('text files', '.dbg')]
        options['initialdir'] = self.saved_gui_input.get_out_dir()
        options['initialfile'] = self.saved_gui_input.get_file_name()
        options['parent'] = root
        options['title'] = 'Select a dbg file'

        # This is only available on the Macintosh, and only when Navigation Services are installed.
        #options['message'] = 'message'

        # if you use the multiple file version of the module functions this option is set automatically.
        #options['multiple'] = 1

        # defining options for opening a directory
        self.dir_opt = options = {}
        options['initialdir'] = self.saved_gui_input.get_out_dir()
        options['mustexist'] = False
        options['parent'] = root
        options['title'] = 'Result directory'

    def askopenfilename(self):
        """Returns an opened file in read mode.
        This time the dialog just returns a filename and the file is opened by your own code.
        """

        # get filename
        self.filename = askopenfilename(**self.file_opt)

        # Update UI
        if self.filename:
            self.selected_file.set(self.filename)
            #print ('File selected ' + self.filename)
            self.saved_gui_input.set_file_name(self.filename)

    def askdirectory(self):
        """Returns a selected directoryname."""
        self.output_dir = askdirectory(**self.dir_opt)

        # Update UI
        if self.output_dir:
            self.selected_dir.set(self.output_dir)
            #print ('Directory selected ' + self.output_dir)
            self.saved_gui_input.set_out_dir(self.output_dir)

    def analyze_trace(self):
        """Starts the analyze of the given trace file """

        # Get the current html output name
        self.html_name = self.html_file_name.get()
        self.saved_gui_input.set_html_name(self.html_name)

        if self.filename == ' ':
            messagebox.showerror("Trace file", "No trace file given")
        elif self.html_name == ' ':
            messagebox.showerror("Output file name", "No name given")
        else:
            if self.output_dir == '.':
                messagebox.showerror("Trace destination", "No result destination given")

            # Create new thread
            thread1 = MyThread(1, self.filename, self.html_name, self.output_dir)
            # Start new Threads
            thread1.start()

    def analyze_cancel(self):
        """Exit the program """
        self.saved_gui_input.save_gui_input()
        quit()

#----------------------
#  Main starts
#----------------------

args = parser.parse_args()

if args.gui:
    root = Tk()
    root.title(" Astro Trace Analazer ")
    GuiTraceFileAnalyzer(root).pack()
    root.mainloop()
else:
    parse_file( args.log_file_name, args.html_log_file_name, args.html_log_file_dir)
