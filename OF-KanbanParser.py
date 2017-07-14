#!#!/usr/bin/which python
# Omnifocus Task Based Kanban Generator v1.0
#
# Author:
# Version:
#

# from __future__ import print_function
import csv
import datetime
import argparse
from webbrowser import open_new_tab
from time import strptime, mktime, strftime

__author__ = "Ben Mason"
__copyright__ = "Copyright 2017"
__version__ = "0.0.1"
__email__ = "locutus@the-collective.net"
__status__ = "Development"

FILENAME = "test.csv"
HTMLOUTPUTFILE = "kanban.html"
TASKURL = "omnifocus:///task/"
IGNORELIST = ["Hold / Future", "Dropped", "Hold", "Future / Hold", "Shopping Lists", "Education", "Electronics Projects", "Home Routine", "Template"]
COMPLETEFILTER=-7
DEFERFILTER=3


def initargs():

    """ initialize variables with command-line arguments """
    parser = argparse.ArgumentParser(description='input -f [file]')
    parser.add_argument('-e', '--enable', \
        help='Option with input', \
        default='')
    parser.add_argument('-t', '--true', \
        help='True false', \
        action='store_true')

    arg = parser.parse_args()

    return arg

# def openwebpage:
#
#     filename = 'file:///Users/username/Desktop/programming-historian/' + filename
#
#     open_new_tab(filename)


def parsetime(datestring):
    # Tuesday, April 25, 2017 at 22:48:42
    if datestring == "missing value":
        return None
    else:
        return strptime(datestring , "%A, %B %d, %Y at %H:%M:%S")


def parsetask(csvdata):

    task = {}
    # print csvdata
    if 'id' not in csvdata[0]:
        task['taskid'] = csvdata[0]
        task['tasktext'] = csvdata[1]

        if csvdata[2] == "false":
            task['inbox'] = False
        else:
            task['inbox'] = True

        if csvdata[3] == "false":
            task['flagged'] = False
        else:
            task['flagged'] = True

        task['contextcontainer'] = csvdata[4]
        task['context'] = csvdata[5]
        task['projectcontainer'] = csvdata[6]
        task['project'] = csvdata[7]
        task['deferdate'] = parsetime(csvdata[8])
        task['duedate'] = parsetime(csvdata[9])
        task['projectstatus'] = csvdata[10]

        if csvdata[11] == "false":
            task['projectblocked'] = False
        else:
            task['projectblocked'] = True

        task['projectid'] = csvdata[12]

        if csvdata[13] == "false":
            task['complete'] = False
        else:
            task['complete'] = True

        task['completedate'] = parsetime(csvdata[14])

# id	Task Name	In Inbox	Flagged	Context Container	Context	Project	Defer Date	Due Date	Prj Status	Prj Blocked	Prj id	Project Complete	Completion Date
    return task

def loadcsvfile(filename):

    tasklist = []
    try:
        with open(filename, 'rU') as filehandle:
            reader = csv.reader(filehandle, dialect='excel')
            try:
                for row in reader:
                    # Parse each row in file and append to list of tasks
                    taskdict = parsetask(row)
                    if taskdict != {}:
                        tasklist.append(parsetask(row))
            except csv.Error as theerror:
                print "file {0}, line {1}: {2}: {3}".format(filename, reader.line_num, \
                     theerror, row)
    except IOError as openerror:
        print "Coule not open {0}, returned error {1}".format(filename, openerror)

    return tasklist

def createmapping(taskdata):

    today = datetime.date.today()
    kanbanmapping = {}
    kanbanmapping['complete'] = []
    kanbanmapping['inbox'] = []

    def appendtasktomapping(task):

        kbtaskinfo = { 'taskid' : task['taskid'],
            'tasktext' : task['tasktext'],
            'deferdate' : task['deferdate'],
            'duedate' : task['duedate'],
            'flagged' : task['flagged'],
            'project' : task['project'],
        }

        return kbtaskinfo

    for task in taskdata:
        # print task
        # add to completed list
        if task['context'] in IGNORELIST:
            pass
        elif task['projectcontainer'] in IGNORELIST:
            pass
        elif task['projectstatus'] == "on hold" or task['projectstatus'] == 'dropped':
            pass
        elif task['complete'] == True:
            if datetime.date.fromtimestamp(mktime(task['completedate'])) - today > datetime.timedelta(days=int(COMPLETEFILTER)):
                kanbanmapping['complete'].append(appendtasktomapping(task))
        elif task['inbox'] == True:
                kanbanmapping['inbox'].append(appendtasktomapping(task))
        else:

            if task['deferdate'] == None:
                try:
                    kanbanmapping[task['context']].append(appendtasktomapping(task))
                except KeyError:
                    kanbanmapping[task['context']] = []
                    kanbanmapping[task['context']].append(appendtasktomapping(task))
            elif datetime.date.fromtimestamp(mktime(task['deferdate'])) - today < datetime.timedelta(days=int(DEFERFILTER)):
                try:
                    kanbanmapping[task['context']].append(appendtasktomapping(task))
                except KeyError:
                    kanbanmapping[task['context']] = []
                    kanbanmapping[task['context']].append(appendtasktomapping(task))


    return kanbanmapping

def createhtmlheader():

    browsertitle = "Task Kanban"
    pagetitle = "Task Kanban"

    htmldata = """<!DOCTYPE html>
    <html>
      <head>
        <title>{0}</title>
        <link href='styles.css' rel='stylesheet' type='text/css'>
        <link href='typicons.css' rel='stylesheet' type='text/css'>
        <script src='/script.js'></script>
        <link href='/favicon.png' rel='icon'>
      </head>
      <body>
        <a class='refresh' href='/refresh'>
          <span class='typcn typcn-refresh'></span>
        </a>
        <h1>{1}</h1>
            <div class='columns'>
            """.format(browsertitle, pagetitle)

    return htmldata

def createcontexthtml(context, contexttasks):

    htmloutput =["""<section class='width-1' id='context'>
<h2>
</h2><div class='parent'>
<h3 class='parent-title'>{0}</h3>""".format(context)]

    # htmloutput.append(htmlscratch)
    contexttasks.sort()
    for task in contexttasks:
        if context == "Complete":
            # completed
            htmlscratch = """<div class='done project' style='background-color:hsl(240,100%,80%)'>
    <h4>
    <a href='{0}{1}'>{2}</a>
    </h4>
    </div>
    """.format(TASKURL, task['taskid'], task['tasktext'])

        else:
            # active
            #'taskid' : task['taskid'],
            # 'tasktext' : task['tasktext'],
            # 'deferdate' : task['deferdate'],
            # 'duedate' : task['duedate'],
            # 'flagged' : task['flagged'],

            desc = ""
            desc = desc + "Project: " + task['project'] + "\n"
            if task['deferdate'] != None:
                desc = desc + "<br>Defer: " + strftime("%m/%d/%y", task['deferdate']) + "\n"
            if task['duedate'] != None:
                desc = desc + "<br>Due: " + strftime("%m/%d/%y", task['duedate']) + "\n"

            if task['flagged'] == True:
                color = "background-color:hsl(0,100%,80%)"
            else:
                color = "background-color:hsl(120,100%,80%)"

            htmlscratch = """<div class='active expanded project' style='{4}'>
    <h4>
    <a href='{0}{1}'>{2}</a>
    </h4>
    <div class='desc'>
    {3}
    </div>
    </div>""".format(TASKURL, task['taskid'], task['tasktext'], desc, color)

        htmloutput.append(htmlscratch)
        # End Loop
    # Add footer
    htmlscratch = """<div class='clear'></div>
            </div>
          </section>"""

    htmloutput.append(htmlscratch)
    return '\n'.join(htmloutput)


def createhtmlfooter():

    htmloutput = """  </body>
    </html>"""

    return htmloutput

def buildhtmlfile(kanbanmap):

    htmloutput = []

    htmloutput.append(createhtmlheader())

    kanbanmapkeys = kanbanmap.keys()
    kanbanmapkeys.sort()
    htmloutput.append(createcontexthtml('Inbox', kanbanmap['inbox']))
    for context in kanbanmapkeys:
        if context == 'inbox' or context == 'complete':
            pass
        else:
            htmloutput.append(createcontexthtml(context, kanbanmap[context]))
    htmloutput.append(createcontexthtml('Complete', kanbanmap['complete']))

    htmloutput.append(createhtmlfooter())

    return '\n'.join(htmloutput)

def writehtmlfile(htmldata):

    with open(HTMLOUTPUTFILE, 'w') as filehandle:
        for line in htmldata:
            filehandle.write(line)


def main():
    tasklist = loadcsvfile(FILENAME)
    # print tasklist
    kanbanmap = createmapping(tasklist)
    htmloutput = buildhtmlfile(kanbanmap)
    writehtmlfile(htmloutput)

    return kanbanmap


if __name__ == "__main__":
    args = initargs()
    kanbanmap = main()
    # print kanbanmap.keys()