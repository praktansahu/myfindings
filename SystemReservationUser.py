#!/usr/bin/python
import pymongo
import pprint
import argparse
import sys
import openpyxl
import logging
import datetime
from html import HTML
from bottle import *

client=pymongo.MongoClient() #mongodb object creations
db=client.System_Reservation
datadict={}
#for d in data:
 # pprint.pprint(d)
colname=["Host","Board","Board Type","Board Revision","debug board no","Group","IP-KVM","Console Server","FPGA CYCLADES port no","ARM CYCLADES port no","JTAG-ID","JTAG","User(US)","User(India)","Board status","Purpose"]  #column declaration
dispcolname=["Host","Board","Board Type","Board Revision","debug board no","Group","IP-KVM","Console Server","FPGA Cyclades Port No","ARM Cyclades Port No","JTAG-ID","JTAG","User(US)","User(India)","Board Status","Purpose"]

#logging.basicConfig(filename='/home/lab-user01/SystemReservationUser.log', level=logging.DEBUG)
logging.basicConfig(filename='/projects/mongodb/labxvm0132/logs/SystemReservationUser.log', level=logging.DEBUG)

sortorder = 1  #sort - where 1 is ascending and -1 is descending

@route("/SystemReservation")  # creating root of html file
def dispdata(sortname=""):
  """ retrieving the data as you given selection creteria
      input: selecion creteria
      """
  global tags
  tags = "<head> <title>  System Reservation User Sheet </title> </head> <h2> <font color='blue'><center>System Reservation User page</center></font> <h2>"
  tags=tags+"<form action=\"/SystemReservation\" method=\"post\"><table border=\"1\">"

  try:
    for i, cname in enumerate(dispcolname, 1):
      tags = tags + "<th>" + cname + "</th>"
    tableEntries()
    table = tags + "<table border=\"1\"><tr>"
    if sortname=="":
      insdict={}
      insdictex={}
      for cname in colname:
        if request.forms.get(cname):
          insdictex[cname] = request.forms.get(cname)
          insdict[cname] = {"$regex": "^" + request.forms.get(cname) + ".*"}
      sortname="Group"
    data=db.testsetup.find()
    for i,cname in enumerate(dispcolname,1):
      table = table + "<th width=\"78\" nowrap><a href=\"/SystemReservation/" + cname + "\">" + cname + "</a></th>"
    table = table + "</tr>"
    table,field_val= get_table_details(table,sortname,data)
    table =table+ "</table></form>"
    #tags=tags+" <input value=\"getdetails\" type=\"submit\" />      <button formaction=\"http://10.2.21.66:8081/SystemReservation/insert\">insert_details</button></form>"
    return table
  except Exception, e:
    debugMsg = creatDebugMessage(str(e))
    logging.degug(debugMsg)
    abort(400, str(e))


def get_table_details(table,sortname,data,updict={}):
  ''' Get the details of the db and sorting it
      This is applicable for both displaying in web page and also for getting the details of any field in db'''

  global sortorder
  field_val=None

  if sortorder == -1:
    sortorder = 1
  else:
    sortorder = -1

  for i, field_val in enumerate(data.sort(sortname, sortorder), 1):
    updict[i] = {}
    if field_val['Board Type'] in ['nextflash', 'tavanna','vc709']:
      if field_val["Group"] == "sw":
        table = table + "<tr style=\"background-color:#FFFF00\">"
      else:
        table = table + "<tr>"

      for cname in colname:
        try:
          if cname == "Host" or cname=="Board":
            updict[i][cname] = field_val[cname]
            if field_val['Group'] == "sw":
              table = table + "<td><input size=\"10\" name=\"" + field_val[cname] + "\" value=\"" + field_val[cname] + "\" type=\"text\"style=\"background-color:#FFFF00\" readonly/></td>"
            else:
              table = table + "<td><input size=\"10\" name=\"" + field_val[cname] + "\" value=\"" + field_val[cname] + "\" type=\"text\" readonly/></td>"
          elif cname in ["User(US)", "User(India)", "Board status", "Purpose"]:
            updict[i][cname] = field_val["Host"] + cname
            if field_val['Group'] == "sw":
              table = table + "<td><input size=\"10\" name=\"" + field_val["Host"] + cname + "\"value=\"" + field_val[cname] + "\" type=\"text\"style=\"background-color:#FFFF00\"/></td>"
            else:
              table = table + "<td><input size=\"10\" name=\"" + field_val["Host"] + cname + "\"value=\"" + field_val[cname] + "\" type=\"text\"/></td>"
          else:
            table = table + "<td>" + field_val[cname] + "</td>"
        except Exception, e:
          table=table+ "<td>   </td>"
          debugMsg = creatDebugMessage(str(e))
          logging.debug(debugMsg)

      table = table + "</tr>"
  return table,field_val


def creatDebugMessage(msg):
  debugMessages = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + msg
  return debugMessages


@route("/SystemReservation",method="POST")  #getting the details of html file and post it
def getdetails(sortname=""):
  """ get the data using Mongodb and diplay the data at http://10.2.21.66:8081/SystemReservation"""
  global updict,insdict,insdictex,tags
  tags=tableEntries()
  if sortname=="":
    updict={}
    insdict={}
    insdictex={}
    for cname in colname:
      if request.forms.get(cname)!="":
        insdictex[cname]=request.forms.get(cname)
        insdict[cname]={"$regex":"^"+request.forms.get(cname)+".*"}
    sortname="Group"
  table="<table border=\"1\"><tr>"
  table = table+ "<form action=\"/SystemReservation/updated\" method=\"post\">""<input value=\"update_details\" type=\"submit\" />"
  if len(insdict.keys())==0:
    data=db.testsetup.find()#.sort(sortname)
  else:
    data=db.testsetup.find(insdictex)#.sort(sortname)
    vex=None
    for vex in data:
      pass
    if vex==None:
      data=db.testsetup.find(insdict)#.sort(sortname)
    else:
      data=db.testsetup.find(insdictex)#.sort(sortname)
  for i, cname in enumerate(dispcolname, 1):
    table = table + "<th width=\"78\" nowrap><a href=\"/SystemReservation/" + cname + "\">" + cname + "</a></th>"
  table,field_val=get_table_details(table,sortname,data,updict)
  table = table+"</table></form>"
  table=table+"</table></form>"
  if field_val!=None:
    return table
  else:
    return "<h1> given details are not matched</h1>"

@route("/SystemReservation/<name>")
def sorting(name):
  '''Column based sorting mechanism'''
  name=colname[dispcolname.index(name)]
  return dispdata(sortname=name)

@route("/SystemReservation/updated",method='POST')
def updatedb():
  """update the database at at http://10.2.21.66:8081/SystemReservation """
  #pprint.pprint(updict)
  global updict
  tags="<form action=\"/SystemReservation\" method=\"get\">""<input value=\"home_page\" type=\"submit\" />"
  updated={}

  try:
    for field_val in updict.keys():
      if len(updict[field_val].keys())!=0:
        updated[updict[field_val]['Host']]={}
        Hostname=updict[field_val]['Host']
        del updict[field_val]['Host']
        for colname in updict[field_val].keys():
          if not request.forms.get(updict[field_val][colname]):updated[Hostname][colname] = ""
          else: updated[Hostname][colname] = request.forms.get(updict[field_val][colname])
    #pprint.pprint(updated)
    for Hostname in updated.keys():
      Brdname = updated[Hostname]['Board']

      # db.testsetup.update({'Host':Hostname},{"$set":updated[Hostname]})
      db.testsetup.update({'Host': Hostname, 'Board': Brdname}, {"$set": updated[Hostname]})
    return "<h1> successfully updated</h1>" + tags

  except Exception, e:
    debugMsg = creatDebugMessage(str(e))
    logging.debug(debugMsg)
    abort(400, str(e))


def tableEntries():
  """ creation input at html files"""
  global tags
  tags=tags+"<tr>"
  for cname in colname:
    tags=tags+"<td><input size=\"10\" name=\""+cname+"\" type=\"text\" /></td>"
    #r.td("<input name=\""+cname+"\" type=\"text\" />")
    #r.td(tags)
  tags=tags+"</tr></table>"
  tags=tags+" <input value=\"getdetails\" type=\"submit\" />"
  #tags=tags+ "<form action=\"/SystemReservation/updated\" method=\"post\">""<input value=\"update_details\" type=\"submit\" />"
  return tags


run(host="10.2.21.66",port=8081)
