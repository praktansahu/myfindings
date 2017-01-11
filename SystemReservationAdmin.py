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
from bson.objectid import ObjectId


client=pymongo.MongoClient() #mongodb object creations
db=client.System_Reservation

datadict={}
colname=["Host","Host ip","Board","Board ip","Board Type","Board Revision","debug board no","Group","IP-KVM","Console Server","FPGA CYCLADES port no","ARM CYCLADES port no","JTAG-ID","JTAG","User(US)","User(India)","Board status","psw_ip","pnum","Purpose","OS"]  #column declaration
dispcolname=["Host","Host Ip","Board","Board Ip","Board Type","Board Revision","Debug Board No","Group","IP-KVM","Console Server","FPGA Cyclades Port No","ARM Cyclades Port No","JTAG-ID","JTAG","User(US)","User(India)","Board Status","RPC IP","RPC Pnum","Purpose","Os"]

logging.basicConfig(filename='/projects/mongodb/labxvm0132/logs/SystemReservationAdmin.log', level=logging.DEBUG)

sortorder = 1

@route("/SystemReservation")  # creating root of html file
def dispdata(sortname=""):
  """ retrieving the data as you given selection creteria
      input: selecion creteria
      """
  global tags
  tags = "<head> <title>  System Reservation Admin Sheet </title> </head> <h2> <font color='blue'><center>System Reservation Admin page</center></font> <h2>"
  tags=tags+"<form action=\"/SystemReservation\" method=\"post\"><table border=\"1\">"

  try:
    for i, cname in enumerate(dispcolname, 1):
        tags = tags + "<th>" + cname + "</th>"
    tableEntries()
    table = tags + "<table border=\"1\" bordercolor=#076D2A><tr>"
    if sortname=="":
      insdict={}
      insdictex={}
      for cname in colname:
        if request.forms.get(cname):
          insdictex[cname] = request.forms.get(cname)
          insdict[cname] = {"$regex": "^" + request.forms.get(cname) + ".*"}
      sortname="Group"

    #L.L. Get all rows from MongoDB with "System_Reservation" database and "testsetup" collection" 
    data=db.testsetup.find()

    for i,cname in enumerate(dispcolname,1):
      table = table + "<th width=\"78\" nowrap><a href=\"/SystemReservation/" + cname + "\">" + cname + "</a></th>"
    table = table + "</tr>"
    table,v=get_table_details(table,sortname,data)

    table = table + "</table></form>"

    return table
  except Exception, e:
    debugMsg = creatDebugMessage(str(e))
    logging.degug(debugMsg)
    abort(400, str(e))


def get_table_details(table,sortname,data,updict={}):
  global sortorder, row_id, origin_brdname
  v=None

  if sortorder == -1:
    sortorder = 1
  else:
    sortorder = -1

  for i, v in enumerate(data.sort(sortname, sortorder), 1):

    #L.L. Keep the original board name, then to check if the new board name 
    row_id = v['_id']   
    print "_id value =======> ", row_id
    origin_brdname = v['Board']

    updict[i] = {}
    if v['Group'] == "sw":
      table = table + "<tr style=\"backgruond-color:#FFFF00\">"
    else:  
      table = table + "<tr>"

    for cname in colname:
      try:
        if cname == "Host": 
          updict[i][cname] = v[cname]

          if v['Group'] == "sw":
            table = table + "<td><input size=\"10\" name=\"" + v[cname] + "\" value=\"" + v[cname] + "\" type=\"text\"style=\"background-color:#FFFF00\"/></td>"
          else:
            table = table + "<td><input size=\"10\" name=\"" + v[cname] + "\" value=\"" + v[cname] + "\" type=\"text\"/></td>"
        else:
          updict[i][cname] = v["Host"] + cname  
     
          if v['Group'] == "sw":
            table = table + "<td><input size=\"10\" name=\"" + v["Host"] + cname + "\"value=\"" + v[cname] + "\" type=\"text\"style=\"background-color:#FFFF00\"/></td>"
          else:
            table = table + "<td><input size=\"10\" name=\"" + v["Host"] + cname + "\"value=\"" + v[cname] + "\" type=\"text\"/></td>"

      except:
        table=table+"<td>    </td>"

      '''
      except Exception, e:
        table=table+"<td>    </td>"
        debugMsg = creatDebugMessage(str(e))
        logging.debug(debugMsg)
        abort(400, str(e))
      '''
    
    updict[i]['_id'] = v['_id']  #L.L.
    table = table + "</tr>"

  return table,v


def creatDebugMessage(msg):
  debugMessages = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + msg
  return debugMessages


@route("/SystemReservation",method="POST")  #getting the details of html file and post it
def getdetails():
  """ get the data using Mongodb and diplay the data at http://10.2.21.66:8090/SystemReservation"""
  
  global updict,insdict,insdictex,tags,sortname
  
  data = getalldata()
  table="<table border=\"1\"><tr>"

  #only enable the 'update' button if there is only one row displayed
  if data.count() == 1:
    table = table+ "<form action=\"/SystemReservation/updated\" method=\"post\">""<input value=\"update_details\" type=\"submit\" />" 

  for i, cname in enumerate(dispcolname, 1):
    table = table + "<th width=\"78\" nowrap><a href=\"/SystemReservation/" + cname + "\">" + cname + "</a></th>"
  table,v = get_table_details(table,sortname,data,updict)

  table = table + "</table></form>"
  if v!=None:
    return table
  else:
    return "<h1> given details are not matched</h1>"


@route("/SystemReservation/<name>")
def sorting(name):
  name=colname[dispcolname.index(name)]
  return dispdata(sortname=name)


@route("/SystemReservation/deleterows",method='POST')
def deletdb():
  global row_id

  tags="<form action=\"/SystemReservation\" method=\"get\">""<input value=\"home_page\" type=\"submit\" />"
 
  db.testsetup.remove({'_id':row_id})

  return "<h1> successfully deleted one row</h1>"+tags


@route("/SystemReservation/updated",method='POST')
def updatedb():
  """update the database at at http://10.2.21.66:8090/SystemReservation """
  global updict, row_id

  #print "request.forms.get('Board' ==========>", request.forms.get('Board')

  hostname = request.forms.get('Host')
  #print "hostname value ==============>", hostname

  #print "\nPrint out updict data =====>\n"
  #pprint.pprint(updict)  #L.L. data does not look correct

  tags="<form action=\"/SystemReservation\" method=\"get\">""<input value=\"home_page\" type=\"submit\" />"
  updated={}
  isempty = 1
  for v in updict.keys():
    if len(updict[v].keys())!=0:
      updated[updict[v]['Host']]={}
      Hostname=updict[v]['Host']

      #del updict[v]['Host']   #L.L.
      if updict[v]['_id'] != "":
        del updict[v]['_id']     #L.L.
      for colname in updict[v].keys():
        if not request.forms.get(updict[v][colname]):
          updated[Hostname][colname] = ""
        else: 
          updated[Hostname][colname] = request.forms.get(updict[v][colname])
          isempty = 0    
  
  
  #print "isempty value =======>", isempty
  #print "row_id value =====> ", row_id
  #print "\nPrint out updated{} data =====>\n"
  #pprint.pprint(updated)   #L.L. the data in updated{} is corrext, but should use '_id' as a key

  #L.L. check if the Board name existed or not

  testBoard = updated[Hostname]['Board'] 
  #print "testBoard ========> ", testBoard
  #print "********************"
  data = db.testsetup.find({"Board":testBoard})

  if testBoard != "":  #L.L. sometime remove the Board name from the Host
    for checkBrd in data:
      if origin_brdname != testBoard:
        print "Found existing board name: ", testBoard
        return "<h1> The board name is existed!!!</h1>" +tags

  for Hostname in updated.keys():

    Brdname = updated[Hostname]['Board']
    print "Brdname from updated{} dictionary \n"

    #db.testsetup.update({'Host':Hostname},{"$set":updated[Hostname]})
    db.testsetup.update({'_id':row_id},{"$set":updated[Hostname]})

  #L.L. remove the empty row
  if isempty == 1:
    db.testsetup.remove({'_id':row_id})
     
  return "<h1> successfully updated</h1>"+tags


def getalldata():
  global updict, insdict, insdictex, tags, sortname
  
  tags=tableEntries()
  
  updict={}
  insdict={}
  insdictex={}
  for cname in colname:
    if request.forms.get(cname)!="":
      insdictex[cname]=request.forms.get(cname)
      #L.L. added case insensitive search
      insdict[cname]={"$regex":"^"+request.forms.get(cname)+".*", "$options":"i"}

  if len(insdict.keys())==0:
    data=db.testsetup.find()
  else:
    data=db.testsetup.find(insdictex)
    vex=None
    for vex in data:
      pass
    if vex==None:
      data=db.testsetup.find(insdict)
    else:
      data=db.testsetup.find(insdictex)

  sortname = "Group"
  return data


def displayOneRow(table,data):

  dispDict = {}
  for document in data:
    dispDict = document #L.L. since we only have one row, we can do this

  table = table + "<tr>"
  
  for cname in colname:
    print "data value for ", cname, "is =======>", dispDict[cname] 
    table = table + "<td><input size=\"10\" name=\"" + dispDict[cname] + "\" value=\"" + dispDict[cname] + "\" type=\"text\"/></td>"
     
  table = table + "</tr></table></form>"
  
  return table


@route("/SystemReservation/getDeleteRow",method='POST')
def getdeleterow():
  global updict,insdict,insdictex,tags, sortname
  
  data = getalldata()
  table="<table border=\"1\"><tr>"

  for i, cname in enumerate(dispcolname, 1):
    table = table + "<th width=\"78\" nowrap><a href=\"/SystemReservation/" + cname + "\">" + cname + "</a></th>"

  if data.count() == 1:
    table = displayOneRow(table,data)

    table = table+ "<form action=\"/SystemReservation/deleterows\" method=\"post\">""<input value=\"Delete the row\"  style=\"background-color:red\" align=\"right\" type=\"submit\" />" 

    table = table + "</tr></table></form>"

    return table
  else:                    #L.L. this includes data.count() not equals 1 
    table,v = get_table_details(table,sortname,data,updict)
    table = table + "</table></form>"
    if v!=None:
      return table
    else:
      return "<h1> given details are not matched</h1>"


@route("/SystemReservation/insert",method='POST')
def insertData():
  
  """save the entered data into Mongo db"""
  tags=dispdata()
 
  hostname = request.forms.get('Host')
  print "hostname value ==============>", hostname

  boardname=request.forms.get('Board')
  v=None
  data=db.testsetup.find({"Board":boardname})

  if boardname != "":
    for v in data:
      pass
      #print(v)
      print "Found existing board name: ", boardname 
      return  tags+"<h1> The board name is already existing</h1>"  

  
  insdict={}
  #L.L. check if all fields are empty
  isempty= 1
  for cname in colname:
    insdict[cname]=request.forms.get(cname)
    if insdict[cname] != "":
       isempty = 0

  insdict['_id'] = ObjectId()

  #L.L. do not insert the empty row
  if isempty == 0:
    db.testsetup.insert(insdict)
    return tags+"<h1> Successfully Inserted</h1>"
  else:
    return tags+"<h1> No data to insert</h1>"

    
def tableEntries():
  """ creation input at html files"""
  global tags
  tags=tags+"<tr>"
  for cname in colname:
    tags=tags+"<td><input size=\"10\" name=\""+cname+"\" type=\"text\" /></td>"
  
  tags=tags+"</tr></table>"

  tags=tags+" <input value=\"getdetails\" type=\"submit\" />    <button formaction=\"http://10.2.21.66:8090/SystemReservation/insert\">insert_details</button>  <button formaction=\"http://10.2.21.66:8090/SystemReservation/getDeleteRow\" style=\"background-color:red\" >Get Delete Row</button> </form>"

  return tags


run(host="10.2.21.66",port=8090)
