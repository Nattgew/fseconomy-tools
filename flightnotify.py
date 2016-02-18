#!/usr/bin/python
import smtplib, sys
import fseutils # My custom FSE functions
#import dicts # My script for custom dictionaries
# import os, re, fileinput, csv, sqlite3
# import locale, time
from datetime import timedelta, date, datetime

def getname(): #Returns username stored in file
	with open('/mnt/data/XPLANE10/XSDK/myfbokey.txt', 'r') as f:
		nothing = f.readline()
		myname = f.readline()
	myname=myname.strip()
	return myname

def getemail(): #Gets email info stored in file
	with open('creds.txt', 'r') as f:
		srvr=f.readline().strip()
		addr=f.readline().strip()
		passw=f.readline().strip()
		addrto=f.readline().strip()
		return srvr,addrto,addr,passw

def reldist(icao,rad): #Find distances of other airports from given airport
	#print("Looking for airports near "+icao)
	loc_dict=fseutils.build_csv("latlon")
	clat,clon=loc_dict[icao]
	dists=[]
	for apt,coords in loc_dict.items():
		if apt!=icao:
			#print("Dist from "+str(clat)+" "+str(clon)+" to "+str(coords[0])+" "+str(coords[1]))
			dist=fseutils.cosinedist(clat,clon,coords[0],coords[1])
			dists.append((apt,dist))
	return sorted(dists, key=lambda dist: dist[1])

i=0 #Index of plane in list
today = date.today() - timedelta(1)
month=today.month
year=today.year
day=today.day
ns = {'sfn': 'http://server.fseconomy.net'} #namespace for XML stuff
plogs=[]
#print("Sending request for aircraft list...")
airplanes = fseutils.fserequest(1,'query=aircraft&search=key','Aircraft','xml')
#print(airplanes)
for plane in airplanes:
	thisac=fseutils.getbtns(plane, [("Registration", 0), ("MakeModel", 0), ("SerialNumber", 0)])
	plogs.append((thisac[0],[]))
	logs=fseutils.fserequest(1,'query=flightlogs&search=monthyear&serialnumber='+thisac[2]+'&month='+str(month)+'&year='+str(year),'FlightLog','xml')
	for flt in logs:
		fltime = flt.find('sfn:Time', ns).text
		thepilot=flt.find('sfn:Pilot', ns).text
		#2016/02/04 02:48:34
		fltdtime = datetime.strptime(fltime, '%Y/%m/%d %H:%M:%S')
		if fltdtime.day==day and fltdtime.month==month and thepilot!=getname():
			logtype=flt.find('sfn:Type', ns).text
			row=[logtype,thepilot]
			if logtype=="flight":
				row.append=fseutils.getbtns(flt, [("From", 0), ("To", 0), ("FlightTime", 0), ("Bonus", 2)])
			elif logtype=="refuel":
				row.append=fseutils.getbtns(flt, [(("FuelCost", 2)])
			plogs[i][1].extend(row)
	i++

srvr,addrto,addr,passw=getemail()
msg="Airplane rentals on "+str(month)+"/"+str(day)+":\n"
#print(msg)
if len(aog)>0:
	for plane in plogs:
		if plane[1]!=[]:
			msg+="\n"+plane[0]+":\n"
			for thislog in plane[1]:
				if thislog[0]=="flight":
					msg+=thislog[2]+"-"+thislog[3]+" "+thislog[4]+" "+str(thislog[5])+" "+thislog[1]+"\n"
				elif thislog[0]=="refuel":
					msg+="Refuel: "+thislog[2]+" "+thislog[1]+"\n"
	message="""\From: %s\nTo: %s\nSubject: FSE Aircraft Activity\n\n%s""" % (addr, addr, msg)
	try:
		#print("Sending mail from "+addr+" to "+addrto)
		server=smtplib.SMTP_SSL(srvr, 465)
		server.ehlo()
		server.login(addr,passw)
		server.sendmail(addr,addrto,message)
		server.close()
		#print("Successfully sent the mail:")
	except:
		e = sys.exc_info()[0]
		#print("Failed to send the mail with error:")
		#print(e)
else:
	msg+="\nNone"
#print()
#print(msg)
