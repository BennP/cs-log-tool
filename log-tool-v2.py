#!/usr/bin/python
import argparse
import re
import os

# --------------------------------------
#    Astro log file analyzer
#
#    ToDo: - Links to ===WRAPPED and ===END yes but it jumps strange
#          - Log with only XML-In / XML-Out , location search
#          - Put MdiDump in a sperat file
#          - General full seak indication at top.
#          - Improve APPL-ERROR to indicate some
#            vellknown types. libmdi.FullScan. Shoe what table it is done on
#                   APPL-ERROR: :      : 13:............./home/sebenpo/projects/x.x/master/src/mdi/libmdi.c:3627,libmdi.FullScan, Caller: /home/sebenpo/projects/x.x/cosmos2/src/ObjG/ObjG09T1.c:2882, Table: SSG10001.shorto42
#          - Events that are not deffined indicated at the top
#          - With a in parameter decide if you whant Real Time data
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
#          - Use CSS to reduce html size
#
# --------------------------------------


# Argument parser
parser = argparse.ArgumentParser(description='Process a logfile from Astro.')
parser.add_argument('-l', dest='log_file_name', help='Log file to analyze')
parser.add_argument('-o', dest='html_log_file_name', help='Output in html format. With no filetype given')
parser.add_argument('-d', dest='html_log_file_dir', help='Output folder for the result')
parser.add_argument('-s', dest='show_all', help='Show all lines')

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

#-----------------
# BoxCalc trace lists
box_calc_list = []
box_calc_conf_list = []
box_calc_color_conf_list = []

#-----------------
# CSS text list
css_text = []

save_row_type = 0

syspar_txt = 'System parameter not defined'

#-----------------
# Classes

# Row class
class LogRow:
   'Common base class for a line of trace data'
   tot_row = 0

   def __init__(self, row_id, time_stamp, row_text, row_type):
        self.row_id = row_id
        self.time_stamp = time_stamp
        self.row_text = do_remove_real_time_spent( do_code_indent( html_escape( row_text.rstrip())))
        self.row_type = row_type
        LogRow.tot_row += 1

   def displayRowTimeStamp(self):
        print "Time " + self.time_stamp

   def displayRowText(self):
        print "- %s" % self.row_text

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

def get_row_type(text):
    """Determine row type from text."""
    for index in range(len(trace_class_list)):
        if text.find(trace_class_list[index].ident_text) != -1:
            return index;
    return -1;

def get_row_class(id):
    """Get row class """
    if id == -1:
        return '"norm"'
    return '"' + trace_class_list[id].class_text + '"'

def get_gwf_row_type(text):
    """Determine gwf row type from text."""
    for index in range(len(gwf_conf_list)):
        if text.find(gwf_conf_list[index].ident_text) != -1:
            return index;
    return -1;

def get_gwf_row_color(id):
    """Get gwf row color """
    if id == -1:
        return '"black"'
    return '"' + gwf_conf_list[id].color_text + '"'

def limit_trace(text):
    """Determine if row should be ignored."""
    if args.show_all:
        return False
    else:
        for index in range(len(trace_ignore_list)):
            if text.find(trace_ignore_list[index].ident_text) != -1:
                return True;
    return False;

def limit_gwf_trace(text):
    """Determine gwf row that should be ignored."""
    if args.show_all:
        return False
    else:
        for index in range(len(gwf_ignore_list)):
            if text.find(gwf_ignore_list[index].ident_text) != -1:
                return True;
    return False;

def is_gwf_trace(text):
    """Determine if text is gwf trace that should be included."""
    for index in range(len(gwf_select_conf_list)):
        if text.find(gwf_select_conf_list[index].ident_text) != -1:
            return True;
    return False;


def is_loc_search_trace(text):
    """Determine if text is location search that should be included."""
    for index in range(len(loc_search_conf_list)):
        if text.find(loc_search_conf_list[index].ident_text) != -1:
            return True;
    return False;

def get_loc_search_row_type(text):
    """Determine Location Search row type from text."""
    for index in range(len(loc_search_color_conf_list)):
        if text.find(loc_search_color_conf_list[index].ident_text) != -1:
            return index;
    return -1;

def get_loc_search_row_color(id):
    """Get Location Search row color """
    if id == -1:
        return '"black"'
    return '"' + loc_search_color_conf_list[id].color_text + '"'

def is_box_calc_trace(text):
    """Determine if text is Box Calc that should be included."""
    for index in range(len(box_calc_conf_list)):
        if text.find(box_calc_conf_list[index].ident_text) != -1:
            return True;
    return False;

def get_box_calc_row_type(text):
    """Determine Box Calc row type from text."""
    for index in range(len(box_calc_color_conf_list)):
        if text.find(box_calc_color_conf_list[index].ident_text) != -1:
            return index;
    return -1;

def get_box_calc_row_color(id):
    """Get Box Calc row color """
    if id == -1:
        return '"black"'
    return '"' + box_calc_color_conf_list[id].color_text + '"'

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

def do_set_end_mark(row_id, text):
    """If the line is the ===END marker."""
    global end_line
    if text.find('===END') != -1:
        end_line = row_id;

def do_set_wrapped_mark(row_id, text):
    """If the line is the ===WRAPPED marker."""
    global wrapped_line
    if text.find('===WRAPPED') != -1:
        wrapped_line = row_id;

def do_db_error(row_id, text):
    """If the line is a DB error then add it to the list."""
    if text.find('DB  -ERROR') != -1:
        # ,F,s01param,EQ :
        matchObj = re.search( '[,]{1}.[,]{1}[0-9a-xA-X]*[,].. :', line, re.M|re.I)
        if not matchObj:
            add_dberror = DbError(row_id)
            db_list.append(add_dberror)

def do_syspar_error(row_id, text):
    """If the line is a "System parameter not defined" error then add it to the list."""
    if text.find(syspar_txt) != -1:
        add_syspar_error = SysParTrace(row_id,text)
        syspar_list.append(add_syspar_error)

def do_db_error_table(out_file):
    """Write a scrollable list with all db errors."""

    db_line = "<p class=%s>" % ('"dberror-scroll"')
    out_file.write(db_line)
    out_file.write("  DB  -ERROR\n")

    for index in range(len(db_list)):
        db_line = "  <a href=%s>%s</a>\n" % ('"#' + str(db_list[index].row_id) + '"', db_list[index].row_id)
        out_file.write(db_line)
    out_file.write("</p>\n")


def do_appl_error(row_id, text):
    """If the line is a APPL-ERROR then add it to the list."""
    if text.find('APPL-ERROR') != -1:
        add_appl_error = ApplError(row_id)
        appl_list.append(add_appl_error)

def do_appl_error_table(out_file):
    """Write a scrollable list with all APPL-ERROR."""

    appl_line = "<p class=%s>" % ('"applerror-scroll"')
    out_file.write(appl_line)
    out_file.write("  APPL-ERROR\n")

    for index in range(len(appl_list)):
        appl_line = "  <a href=%s>%s</a>\n" % ('"#' + str(appl_list[index].row_id) + '"', appl_list[index].row_id)
        out_file.write(appl_line)
    out_file.write("</p>\n")


def do_call_trace(row_id, text):
    """If the line is a CallTrace start then add it to the list."""
    if text.find('CallTrace :  0') != -1:
        add_call_trace = CallTrace(row_id)
        trace_list.append(add_call_trace)

def do_call_trace_table(out_file):
    """Write a scrollable list with all Calltrace."""

    trace_line = "<p class=%s>" % ('"trace-scroll"')
    out_file.write(trace_line)
    out_file.write("  CallTrace\n")

    for index in range(len(trace_list)):
        trace_line = "  <a href=%s>%s</a>\n" % ('"#' + str(trace_list[index].row_id) + '"', trace_list[index].row_id)
        out_file.write(trace_line)
    out_file.write("</p>\n")

def do_syspar_trace_table(out_file):
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
        offset = text.find('OK   : :      :');
        if offset == -1:
            print ' This line must be wrong'
            print text
            return text
        else:
            num = text[(offset + 16):(offset + 20)].split(':',2)
            indent_number = int (num[0])
            indent_str = '                                                              '
            offset_tail = text.find('./');
            if offset == -1:
                print ' This line must be wrong'
                print text
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
    if args.show_all:
        return False
    else:
        tmp_text = text.strip()
        if tmp_text.startswith( '<' ):
            return True
    return False

def do_html_file_header(out_file):
    """Write html file header info."""

    out_file.write("<!DOCTYPE html>\n<html><head><title>#Consafe Astro log analysis</title></head><body>\n")
    # Set style for table boarders
    out_file.write("<style>table,th,td{border:1px solid black;}</style>\n")
    # Write a header
    out_file.write("<hr>\n<h1>    Astro Trace analyzer </h1>\n</hr>\n")
    # Write file name analyzed
    print_h_line = "<hr>\n<h3>File analyzed %s</h3>\n</hr>\n" % (args.log_file_name)
    out_file.write(print_h_line)

def do_html_file_reference(out_file, file_text, to_file, css_class):
    """Write html link to other files."""

    print_h_line = "<h3 class=%s> <a href=%s>%s</a></h3>\n" % ('"' + css_class + '"', '"' + to_file + '"', file_text)
    out_file.write(print_h_line)

def do_html_file_stop_float(out_file):
    """Write html line to stop float."""

    print_h_line = "<h3 class=%s></h3>\n" % ('"stop-float"')
    out_file.write(print_h_line)

def do_html_end_wrapped_mark(out_file):
    """Write end / wrapped mark info."""
    global wrapped_line
    global end_line

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

def do_write_css_to_file(out_file):
    """Write css data to file"""
    for line in css_text:
        out_file.write(line)

def get_config_path():
    """ Try to find where the config files are. Using env variable PATH """
    env_path = os.environ['PATH']
    env_parts = env_path.split(':')
    for dir in env_parts:
        if os.path.isfile(dir + '/trace-color.conf'):
            print 'Found the file ' + dir
            return dir + '/'
    return ''



#----------------------
#  Main starts
#----------------------
args = parser.parse_args()

trace_file_full_name = str(args.html_log_file_dir) + '/' + str(args.html_log_file_name) + '.html'
gwf_trace_file_full_name = str(args.html_log_file_dir) + '/' + 'GWF-' + str(args.html_log_file_name) + '.html'
loc_search_trace_file_full_name = str(args.html_log_file_dir) + '/' + 'LocSearch-' + str(args.html_log_file_name) + '.html'
box_calc_trace_file_full_name = str(args.html_log_file_dir) + '/' + 'BoxCalc-' + str(args.html_log_file_name) + '.html'

trace_file_name = str(args.html_log_file_name) + '.html'
gwf_trace_file_name = 'GWF-' + str(args.html_log_file_name) + '.html'
loc_search_trace_file_name = 'LocSearch-' + str(args.html_log_file_name) + '.html'
box_calc_trace_file_name = 'BoxCalc-' + str(args.html_log_file_name) + '.html'
print 'Astro log file = ' + args.log_file_name
print 'Output file    = ' + trace_file_full_name
print 'Output file GWF  = ' + gwf_trace_file_full_name
print 'Output file LocSearch  = ' + loc_search_trace_file_full_name
print 'Output file BoxCalc  = ' + box_calc_trace_file_full_name

log_file    = open(args.log_file_name)
output_file = open(trace_file_full_name, 'w')
gwf_output_file = open(gwf_trace_file_full_name, 'w')
loc_search_output_file = open(loc_search_trace_file_full_name, 'w')
box_calc_output_file = open(box_calc_trace_file_full_name, 'w')

config_path = get_config_path()
#----------------------
#  Get config from external files
#----------------------
#-Get config for color -------------
try:
    gwf_config_file    = open(config_path + 'gwf-color.conf')
    for conf_line in gwf_config_file:
        tmp_conf = conf_line.rstrip()
        parts = tmp_conf.split(';',2)
        add_row = GwfConf(parts[0],parts[1])
        gwf_conf_list.append(add_row)
    gwf_config_file.close()
except IOError:
    print "Error: can\'t find file or read data " + 'gwf-color.conf'
    raise

try:
    trace_config_file    = open(config_path + 'trace-class.conf')
    for conf_line in trace_config_file:
        tmp_conf = conf_line.rstrip()
        parts = tmp_conf.split(';',2)
        add_row = TraceConf(parts[0],parts[1])
        trace_class_list.append(add_row)
    trace_config_file.close()
except IOError:
    print "Error: can\'t find file or read data " + 'trace-color.conf'
    raise

try:
    loc_search_color_config_file    = open(config_path + 'loc-search-color.conf')
    for conf_line in loc_search_color_config_file:
        tmp_conf = conf_line.rstrip()
        parts = tmp_conf.split(';',2)
        add_row = LocationSearchConf(parts[0],parts[1])
        loc_search_color_conf_list.append(add_row)
    loc_search_color_config_file.close()
except IOError:
    print "Error: can\'t find file or read data " + 'loc-search-color.conf'
    raise

try:
    box_calc_color_config_file    = open(config_path + 'box-calc-color.conf')
    for conf_line in box_calc_color_config_file:
        tmp_conf = conf_line.rstrip()
        parts = tmp_conf.split(';',2)
        add_row = BoxCalcConf(parts[0],parts[1])
        box_calc_color_conf_list.append(add_row)
    box_calc_color_config_file.close()
except IOError:
    print "Error: can\'t find file or read data " + 'box-calc-color.conf'
    raise

#-Get ignore lists -------------
try:
    gwf_ignore_file    = open(config_path + 'gwf-ignore.conf')
    for ignore_line in gwf_ignore_file:
        add_row = GwfIgnore(ignore_line.rstrip())
        gwf_ignore_list.append(add_row)
    gwf_ignore_file.close()
except IOError:
    print "Error: can\'t find file or read data " + 'gwf-ignore.conf'
    raise

try:
    trace_ignore_file    = open(config_path + 'trace-ignore.conf')
    for ignore_line in trace_ignore_file:
        add_row = TraceIgnore(ignore_line.rstrip())
        trace_ignore_list.append(add_row)
    trace_ignore_file.close()
except IOError:
    print "Error: can\'t find file or read data " + 'trace-ignore.conf'
    raise

#-Get gwf select lists -------------
try:
    gwf_select_file    = open(config_path + 'gwf-select.conf')
    for gwf_select_line in gwf_select_file:
        add_row = LocationSearch(gwf_select_line.rstrip())
        gwf_select_conf_list.append(add_row)
    gwf_select_file.close()
except IOError:
    print "Error: can\'t find file or read data " + 'gwf-select.conf'
    raise

#-Get location search lists -------------
try:
    loc_search_file    = open(config_path + 'loc-search.conf')
    for loc_search_line in loc_search_file:
        add_row = LocationSearch(loc_search_line.rstrip())
        loc_search_conf_list.append(add_row)
    loc_search_file.close()
except IOError:
    print "Error: can\'t find file or read data " + 'loc-search.conf'
    raise

#-Get Box Calc lists -------------
try:
    box_calc_file    = open(config_path + 'box-calc.conf')
    for box_calc_line in box_calc_file:
        add_row = BoxCalc(box_calc_line.rstrip())
        box_calc_conf_list.append(add_row)
    box_calc_file.close()
except IOError:
    print "Error: can\'t find file or read data " + 'box-calc.conf'
    raise

#-Get css text -------------
try:
    css_text_file    = open(config_path + 'css.conf')
    for css_line in css_text_file:
        # add_row = BoxCalc(box_calc_line.rstrip())
        css_text.append(css_line)
    css_text_file.close()
except IOError:
    print "Error: can\'t find file or read data " + 'css.conf'
    raise

#------------------------------
# Rip the logs apart and find out some basic data about the log.
# The ripped log will later be used to generate a HTML page.
#------------------------------
line_id = 0
for line in log_file:
    if not limit_trace(line):
        do_set_end_mark(line_id, line)
        do_set_wrapped_mark(line_id, line)
        matchObj = re.match( r'[0-9]{2}-[0-9]{2}-[0-9]{2}', line, re.M|re.I)
        if matchObj:
            offset = line.find("Real=");
            if offset == -1:
                add_row = LogRow(line_id,line[0:17],' ' + line[(19):],get_row_type(line))
            else:
                add_row = LogRow(line_id,line[0:17],line[(offset + 21):],get_row_type(line))
            save_row_type = get_row_type(line)
            do_db_error(line_id, line)
            do_appl_error(line_id, line)
            do_call_trace(line_id, line)
            do_syspar_error(line_id, line)
            line_list.append(add_row)
            line_id = line_id + 1
        else:
            if not remove_pure_xml_row(line):
                add_row = LogRow(line_id,' ',line[0:],save_row_type)
                line_list.append(add_row)
                line_id = line_id + 1

log_file.close()
log_file    = open(args.log_file_name)

#------------------------------
# Rip the logs apart and find gwf data
# The ripped log will later be used to generate a separat HTML page for GWF data.
#------------------------------
line_id = 0
for line in log_file:
    matchObj = re.match( r'[0-9]{2}-[0-9]{2}-[0-9]{2}', line, re.M|re.I)
    if matchObj:
        offset = line.find("Real=");
        if is_gwf_trace(line):
            if not limit_gwf_trace(line):
                add_row = GWFRow(line_id,line[0:17],line[(offset + 21):],get_gwf_row_type(line))
                gwf_list.append(add_row)
                line_id = line_id + 1

log_file.close()
log_file    = open(args.log_file_name)

#------------------------------
# Rip the logs apart and find Location Search data
# The ripped log will later be used to generate a separat HTML page for Location Search data.
#------------------------------
line_id = 0
for line in log_file:
    matchObj = re.match( r'[0-9]{2}-[0-9]{2}-[0-9]{2}', line, re.M|re.I)
    if matchObj:
        if is_loc_search_trace(line):
            offset = line.find("Real=");
            add_row = LocSearchRow(line_id,line[0:17],line[(offset + 21):],get_loc_search_row_type(line))
            loc_search_list.append(add_row)
            line_id = line_id + 1

log_file.close()
log_file    = open(args.log_file_name)
#------------------------------
# Rip the logs apart and find Box Calc data
# The ripped log will later be used to generate a separat HTML page for Box Calc data.
#------------------------------
line_id = 0
for line in log_file:
    matchObj = re.match( r'[0-9]{2}-[0-9]{2}-[0-9]{2}', line, re.M|re.I)
    if matchObj:
        if is_box_calc_trace(line):
            offset = line.find("Real=");
            add_row = BoxCalcRow(line_id,line[0:17],line[(offset + 21):],get_box_calc_row_type(line))
            box_calc_list.append(add_row)
            line_id = line_id + 1

#---------------
# Result of file runtrough
#---------------
print "Number of DB Errors = %d" % DbError.error_count
print "Number of APPL-ERROR = %d" % ApplError.appl_count
print "Number of CallTrace = %d" % CallTrace.trace_count
print "Number of SysPar errors = %d" % SysParTrace.syspar_count
print "Total rows %d" % LogRow.tot_row
print "Total GWF rows %d" % GWFRow.tot_row
print "Total Location Search rows %d" % LocSearchRow.tot_row
print "Total Box Calc rows %d" % BoxCalcRow.tot_row
print "End mark %d" % end_line
print "Wrapped mark %d" % wrapped_line

#---------------
# Start making the HTML files
#------------------------------
#--- Goods Workflow
#---------------
if len(gwf_list) > 0:
    do_html_file_header(gwf_output_file)
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

        print_line = "<FONT COLOR=%s>%8.1d <a name=%s></a> <FONT COLOR=%s>%s <FONT COLOR=%s>%s" % ('"grey"',index, '"' + str(index) + '"', '"green"',gwf_list[index].time_stamp, get_gwf_row_color(gwf_list[index].row_type),print_text)
        gwf_output_file.write(print_line)

        if (index + 1) < list_number:
            if gwf_list[index+1].row_type == save_row_type:
                gwf_output_file.write("<br>\n")
            else:
                save_row_type = gwf_list[index + 1].row_type
                print_line = "</p> \n<p style=%s >\n" % ('"background-color:#F8F8F8"')
                gwf_output_file.write(print_line)
else:
    do_html_file_header(gwf_output_file)
    do_html_file_reference(gwf_output_file, "Main trace ", trace_file_name, 'm-file')

    do_html_file_end(gwf_output_file)
    gwf_output_file.close()

#------------------------------
#--- Location Search
#---------------
if len(loc_search_list) > 0:
    do_html_file_header(loc_search_output_file)
    do_html_file_reference(loc_search_output_file, "Main trace ", trace_file_name, 'm-file')

    print_h_line = "<p style=%s >\n" % ('"background-color:#F8F8F8"')
    loc_search_output_file.write(print_h_line)
    save_row_type = loc_search_list[0].row_type
    list_number = len(loc_search_list)

    for index in range(len(loc_search_list)):
        print_text = loc_search_list[index].row_text
        print_line = "<FONT COLOR=%s>%8.1d <a name=%s></a> <FONT COLOR=%s>%s <FONT COLOR=%s>%s" % ('"grey"',index, '"' + str(index) + '"', '"green"',loc_search_list[index].time_stamp, get_loc_search_row_color(loc_search_list[index].row_type),print_text)
        loc_search_output_file.write(print_line)

        if (index + 1) < list_number:
            if loc_search_list[index+1].row_type == save_row_type:
                loc_search_output_file.write("<br>\n")
            else:
                save_row_type = loc_search_list[index + 1].row_type
                print_line = "</p> \n<p style=%s >\n" % ('"background-color:#F8F8F8"')
                loc_search_output_file.write(print_line)
else:
    do_html_file_header(loc_search_output_file)
    do_html_file_reference(loc_search_output_file, "Main trace ", trace_file_name, 'm-file')

    do_html_file_end(loc_search_output_file)
    loc_search_output_file.close()

#------------------------------
#--- Box Calc
#---------------
if len(box_calc_list) > 0:
    do_html_file_header(box_calc_output_file)
    do_html_file_reference(box_calc_output_file, "Main trace ", trace_file_name, 'm-file')

    print_h_line = "<p style=%s >\n" % ('"background-color:#F8F8F8"')
    box_calc_output_file.write(print_h_line)
    save_row_type = box_calc_list[0].row_type
    list_number = len(box_calc_list)

    for index in range(len(box_calc_list)):
        print_text = box_calc_list[index].row_text
        print_line = "<FONT COLOR=%s>%8.1d <a name=%s></a> <FONT COLOR=%s>%s <FONT COLOR=%s>%s" % ('"grey"',index, '"' + str(index) + '"', '"green"',box_calc_list[index].time_stamp, get_box_calc_row_color(box_calc_list[index].row_type),print_text)
        box_calc_output_file.write(print_line)

        if (index + 1) < list_number:
            if box_calc_list[index+1].row_type == save_row_type:
                box_calc_output_file.write("<br>\n")
            else:
                save_row_type = box_calc_list[index + 1].row_type
                print_line = "</p> \n<p style=%s >\n" % ('"background-color:#F8F8F8"')
                box_calc_output_file.write(print_line)
else:
    do_html_file_header(box_calc_output_file)
    do_html_file_reference(box_calc_output_file, "Main trace ", trace_file_name, 'm-file')

    do_html_file_end(box_calc_output_file)
    box_calc_output_file.close()

#---------------
#--- Trace file
#---------------
do_html_file_header(output_file)
do_write_css_to_file(output_file)
do_html_file_reference(output_file, "GWF trace ", gwf_trace_file_name, 'gwf-file')
do_html_file_reference(output_file, "Location Search ", loc_search_trace_file_name, 'ls-file')
do_html_file_reference(output_file, "Box Calc ", box_calc_trace_file_name, 'box-file')
do_html_file_stop_float(output_file)
do_html_end_wrapped_mark(output_file)

do_db_error_table(output_file)
do_appl_error_table(output_file)
do_call_trace_table(output_file)
do_syspar_trace_table(output_file)
do_html_file_stop_float(output_file)

save_row_type = line_list[0].row_type
print_h_line = "<p class=%s >" % (get_row_class(line_list[0].row_type))
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
            print_line = "</p> \n<p class=%s >" % (get_row_class(line_list[index+1].row_type))
            output_file.write(print_line)

output_file.write("</p>")
do_html_file_end(output_file)

output_file.close()