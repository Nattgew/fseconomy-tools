#!/usr/bin/python
import smtplib, sys
import fseutils # My custom FSE functions

def isnew(newdearth,type):
	#This function prevents repeat notifications for the same shortage
	#A list of airports with shortages is stored in a text file
	if type=="jeta":
		file="lowjeta.txt"
	if type=="100ll":
		file="low100ll.txt"
	if type=="supp"
		file="lowsupp.txt"
	oldnews=[] #List of shortages already notified
	with open(file, 'r+') as f:
		for olddearth in f: #Loop over all shortages in the file
			for current in newdearth: #Loop over all current shortanges
				if current[0]==olddearth: #Shortage was already listed in the file
					oldnews.append(current)
					break
	with open(file, 'w') as f: #Overwrite the file with the new list of shortages
		for current in newdearth:
			f.write(current[0]+"\n")
	for oldie in oldnews: #Remove shortages already notified from the list
		newdearth.remove(oldie)
	return newdearth

warndays = 14 #Days of supplies to first send warning
warnjeta = 1000 #Gallons of Jet A to first send warning
warn100ll = 1000 #Gallons of 100LL to first send warning
#print("Sending request for commodities list...")
commo = fseutils.grouprequest(1,'query=commodities&search=key','Commodity','xml')
#print(commo)
lowjeta = []
low100ll = []
lowsupp = []
for fbo in commo: #Parse commodity info
	icao = fseutils.gebtn(item, "Icao")
	f100 = fseutils.gebtn(item, "Fuel100LL")
	fja = fseutils.gebtn(item, "FuelJetA")
	days = fseutils.gebtn(item, "SuppliedDays")
	if fja/2.65 < warnjeta+1:
		lowjeta.append((icao,round(fja/2.65)))
	if f100 < warn100ll+1:
		low100ll.append((icao,round(f100/2.65)))
	if days < warndays+1:
		lowsupp.append((icao,days))
#print(msg)
lowjeta=isnew(lowjeta,"jeta")
low100ll=isnew(low100ll,"100ll")
lowsupp=isnew(lowsupp,"supp")
msg=""
if len(lowsupp)>0:
	msg+="Airports with low supplies:\n"
	for airport in lowsupp: #Add airport and qty to message
		msg+=airport[0]+" - "+airport[1]+" days\n"
	msg+="\n"
if len(lowjeta)>0:
	msg+="Airports with low Jet A:\n"
	for airport in lowjeta: #Add airport and qty to message
		msg+=airport[0]+" - "+airport[1]+" gals\n"
	msg+="\n"
if len(low100ll)>0:
	msg+="Airports with low 100LL:\n"
	for airport in low100ll: #Add airport and qty to message
		msg+=airport[0]+" - "+airport[1]+" gals\n"
	msg+="\n"
#print(msg)
if msg!="":
	fseutils.sendemail("FSE FBO Shortages",msg)