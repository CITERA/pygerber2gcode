#!/usr/bin/python
# coding: UTF-8

from string import *
from math import *
#from struct import *
import os
import sys
import datetime
import locale
import re

#Global Constant
HUGE = 1e10
TINY = 1e-6
MERGINE = 1e-6
INCH = 25.4 #mm
MIL = INCH/1000
CAD_UNIT = MIL/10
CONFIG_FILE = "./pyg2g.conf"
#Set
INI_X = 0
INI_Y = 0
INI_Z = 5.0
MOVE_HEIGHT = 1.0
OUT_INCH_FLAG = 0
IN_INCH_FLAG = 1
MCODE_FLAG = 0
XY_SPEED = 100
Z_SPEED = 60
LEFT_X = 5.0
LOWER_Y = 5.0
DRILL_SPEED = 50	#Drill down speed
DRILL_DEPTH = -1.2#Drill depth
CUT_DEPTH = -0.07	#pattern cutting depth
TOOL_D = 0.2		#Tool diameter
DRILL_D = 0.8		#Drill diameter
EDGE_TOOL_D = 1.0		#Edge Tool diameter
EDGE_DEPTH = -1.2 #edge depth
EDGE_SPEED = 80	#Edge cut speed
EDGE_Z_SPEED = 60	#Edge down speed
MERGE_DRILL_DATA = 0
Z_STEP = -0.5
#Global variable
gXMIN = HUGE
gYMIN = HUGE
gXSHIFT = 0
gYSHIFT = 0
gGCODE_DATA = ""
gDRILL_DATA = ""
gEDGE_DATA = ""
gTMP_X = INI_X 
gTMP_Y = INI_Y
gTMP_Z = INI_Z
gTMP_DRILL_X = INI_X 
gTMP_DRILL_Y = INI_Y
gTMP_DRILL_Z = INI_Z
gTMP_EDGE_X = INI_X 
gTMP_EDGE_Y = INI_Y
gTMP_EDGE_Z = INI_Z
gGERBER_TMP_X = 0
gGERBER_TMP_Y = 0
gDCODE = [0]*100
g54_FLAG = 0
gFIG_NUM = 0
gDRILL_TYPE = [0]*100
gDRILL_D = 0
gPOLYGONS = []
gLINES = []
gEDGES = []
gDRILLS = []
gGCODES = []
gUNIT = 1

#Set Class
class POLYGON:
	def __init__(self, x_min, x_max, y_min, y_max, points, delete):
		self.x_min = x_min
		self.x_max = x_max
		self.y_min = y_min
		self.y_max = y_max
		self.points = points
		self.delete = delete

class LINE:
	def __init__(self, x1, y1, x2, y2, inside, delete):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.inside = inside
		self.delete = delete

class DRILL:
	def __init__(self, x, y, d, delete):
		self.x = x
		self.y = y
		self.d = d
		self.delete = delete

class D_DATA:
	def __init__(self, atype, mod1, mod2):
		self.atype = atype
		self.mod1 = mod1
		self.mod2 = mod2

class GCODE:
	def __init__(self, x1, y1, x2, y2, gtype, mod1, mod2):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.gtype = gtype
		self.mod1 = mod1
		self.mod2 = mod2

#functions
def main():
	#in_file="colpitts1-Front0.gtl" #with filling zone
	in_file="colpitts1-Front_1.gtl" #1lines and 1 rect
	#in_file="colpitts1-Front_2.gtl" #2 line and 1 rect
	#in_file="colpitts1-Front_3.gtl" #3 lines and 2 rects
	#in_file="colpitts1-Front_4.gtl"
	#in_file="colpitts1-Front_5.gtl"
	#in_file="colpitts1-Front_6.gtl"
	#in_file="colpitts1-Front_7.gtl"	#for zone error
	#in_file="colpitts1-Front_8.gtl"	#for zone error
	#in_file="uav1_1-Front.gtl"
	#in_file="avr_test1.gtl"
	#drill_file="uav1_1.drl"
	drill_file="avr_test1.drl"
	edge_file = "avr_test1_edge.gbr"
	#drill_sw = 0	#for check
	out_file = "test_gcode.ngc"
	out_drill_file = "test_drill.ngc"
	out_edge_file = "test_edge.ngc"
	#process start
	set_unit()
	gcode_init()
	read_Gerber(in_file)
	merge()
	read_Drill_file(drill_file)
	do_drill()
	readEdgeFile(edge_file)
	mergeEdge()
	edge2gcode()
	end(out_file,out_drill_file,out_edge_file)

def set_unit():
	global IN_INCH_FLAG, OUT_INCH_FLAG, gUNIT, INCH
	if (IN_INCH_FLAG and not OUT_INCH_FLAG):
		gUNIT = INCH
	elif(not IN_INCH_FLAG and OUT_INCH_FLAG):
		gUNIT = 1.0/INCH
	else:
		gUNIT = 1.0

def read_config():
	global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT, CONFIG_FILE
	try:
		f = open(CONFIG_FILE,'r')
	except IOError, (errno, strerror):
		error_dialog("Unable to open the file" + CONFIG_FILE + "\n",1)
	else:
		while 1:
			config = f.readline()
			if not config:
				break
			cfg = re.search("([A-Z\_]+)\s*\=\s*([\-\d\.]+)",config)
			if (cfg):
				if(cfg.group(1)=="INI_X"):
					INI_X = float(cfg.group(2))
				if(cfg.group(1)=="INI_Y"):
					INI_Y = float(cfg.group(2))
				if(cfg.group(1)=="INI_Z"):
					INI_Z = float(cfg.group(2))
				if(cfg.group(1)=="MOVE_HEIGHT"):
					MOVE_HEIGHT = float(cfg.group(2))
				if(cfg.group(1)=="OUT_INCH_FLAG"):
					OUT_INCH_FLAG = int(cfg.group(2))
				if(cfg.group(1)=="IN_INCH_FLAG"):
					IN_INCH_FLAG = int(cfg.group(2))
				if(cfg.group(1)=="MCODE_FLAG"):
					MCODE_FLAG = int(cfg.group(2))
				if(cfg.group(1)=="XY_SPEED"):
					XY_SPEED = int(cfg.group(2))
				if(cfg.group(1)=="Z_SPEED"):
					Z_SPEED = int(cfg.group(2))
				if(cfg.group(1)=="LEFT_X"):
					LEFT_X = float(cfg.group(2))
				if(cfg.group(1)=="LOWER_Y"):
					LOWER_Y = float(cfg.group(2))
				if(cfg.group(1)=="DRILL_SPEED"):
					DRILL_SPEED = int(cfg.group(2))
				if(cfg.group(1)=="DRILL_DEPTH"):
					DRILL_DEPTH = float(cfg.group(2))
				if(cfg.group(1)=="CUT_DEPTH"):
					CUT_DEPTH = float(cfg.group(2))
				if(cfg.group(1)=="TOOL_D"):
					TOOL_D = float(cfg.group(2))
				if(cfg.group(1)=="DRILL_D"):
					DRILL_D = float(cfg.group(2))
				if(cfg.group(1)=="CAD_UNIT"):
					CAD_UNIT = float(cfg.group(2))

		f.close()

def readEdgeFile(edge_file):
	global gTMP_EDGE_X, gTMP_EDGE_Y, gTMP_EDGE_Z, gEDGE_DATA, gEDGES, CAD_UNIT, OUT_INCH_FLAG, IN_INCH_FLAG
	try:
		f = open(edge_file,'r')
	except IOError, (errno, strerror):
		error_dialog("Unable to open the file" + edge_file + "\n",1)
	else:
		pre_x = gTMP_EDGE_X
		pre_y = gTMP_EDGE_Y
		while 1:
			edge = f.readline()
			if not edge:
				break
			xx = re.search("X([\d\.\-]+)\D",edge)
			yy = re.search("Y([\d\-]+)\D",edge)
			dd = re.search("D([\d]+)\D",edge)
			if (xx):
				x = float(xx.group(1)) * CAD_UNIT
				#if (x != gTMP_EDGE_X):
					#gTMP_EDGE_X = x
			if (yy):
				y = float(yy.group(1)) * CAD_UNIT
				#if (y != gTMP_Y):
					#gTMP_EDGE_Y = y
			if (dd):
				if(dd.group(1) == "1" or dd.group(1) == "01"):
					gEDGES.append(POLYGON(0, 0, 0, 0, [pre_x,pre_y,x,y], 0))
					#gEDGES.append(LINE(pre_x,pre_y,x,y,0,0))
				elif(dd.group(1) == "2" or dd.group(1) == "02"):
					pre_x = x
					pre_y = y
		f.close()
def mergeEdge():
	global gTMP_EDGE_X, gTMP_EDGE_Y, gTMP_EDGE_Z, gEDGE_DATA, gEDGES, MERGINE
	for edge1 in gEDGES:
		if(edge1.delete):
			continue
		tmp_points1 = edge1.points
		xi1 = edge1.points[0]
		yi1 = edge1.points[1]
		xi2 = edge1.points[len(edge1.points)-2]
		yi2 = edge1.points[-1]
		for edge2 in gEDGES:
			if(edge2.delete or edge2 == edge1):
				continue
			tmp_points2 = edge2.points
			xj1 = edge2.points[0]
			yj1 = edge2.points[1]
			xj2 = edge2.points[len(edge2.points)-2]
			yj2 = edge2.points[-1]
			if(xi1 == xj2 and yi1 == yj2):
				#join
				del tmp_points1[0:2]
				tmp_points1 = tmp_points2 + tmp_points1
			elif(xi2 == xj1 and yi2 == yj1):
				#join
				del tmp_points2[0:2]
				tmp_points1 = tmp_points1 + tmp_points2
			elif(xi1 == xj1 and yi1 == yj1):
				#join
				tmp_points2 = points_revers(tmp_points2)
				del tmp_points1[0:2]
				tmp_points1 = tmp_points2 + tmp_points1
			elif(xi2 == xj2 and yi2 == yj2):
				#join
				tmp_points2 = points_revers(tmp_points2)
				del tmp_points2[0:2]
				tmp_points1 = tmp_points1 + tmp_points2

			edge2.delete = 1
			edge1.points=tmp_points1
def edge2gcode():
	global gEDGE_DATA, gXSHIFT, gYSHIFT, gTMP_EDGE_X, gTMP_EDGE_Y, gTMP_EDGE_Z, gEDGES, EDGE_TOOL_D, EDGE_DEPTH, EDGE_SPEED, EDGE_Z_SPEED, Z_STEP
	out_data = "G01"
	gcode_tmp_flag = 0
	z_step_n = int(EDGE_DEPTH/Z_STEP) + 1
	z_step = EDGE_DEPTH/z_step_n
	j = 1
	while j <= z_step_n:
		z_depth = j*z_step
		for edge in gEDGES:
			points = edge.points
			if(len(points) % 2):
				error_dialog("Error:Number of points is illegal ",0)
				#print "Number of points is illegal "
			#print "x=" + str(gTMP_EDGE_X) + ", y=" + str(gTMP_EDGE_Y)
			#print "x=" + str(float(points[0])+float(gXSHIFT)) + ", y=" + str(float(points[1])+float(gYSHIFT))
			#move to Start position
			gEDGE_DATA += move_edge(float(points[0])+float(gXSHIFT),float(points[1])+float(gYSHIFT))
			#move to cuting heght
			if(z_depth != gTMP_EDGE_Z):
				gTMP_EDGE_Z=z_depth
				gEDGE_DATA += "G01Z" + str(z_depth) + "F" + str(EDGE_Z_SPEED) + "\n"
			i = 0
			while i< len(points):
				px=float(points[i])+gXSHIFT
				py=float(points[i+1])+gYSHIFT
				if (px != gTMP_EDGE_X):
					gTMP_EDGE_X=px
					out_data +="X" + str(px)
					gcode_tmp_flag = 1
				if(py != gTMP_EDGE_Y):
					gTMP_EDGE_Y=py
					out_data +="Y" + str(py)
					gcode_tmp_flag=1
				if(gcode_tmp_flag):
					#Goto initial X-Y position
					out_data +="F" + str(EDGE_SPEED)
					gEDGE_DATA += out_data + "\n"
					out_data ="G01"
				gcode_tmp_flag=0
				i += 2
		j += 1
def move_edge(x,y):
	global MOVE_HEIGHT, gTMP_EDGE_X, gTMP_EDGE_Y, gTMP_EDGE_Z
	xy_data = "G00"
	out_data = ""
	#print out_data
	gcode_tmp_flag = 0
	if(x != gTMP_EDGE_X):
		gTMP_EDGE_X = x
		xy_data += "X" + str(x)
		gcode_tmp_flag=1
	if(y != gTMP_EDGE_Y):
		gTMP_EDGE_Y = y
		xy_data += "Y" + str(y)
		gcode_tmp_flag = 1
	if(MOVE_HEIGHT!=gTMP_EDGE_Z):
		gTMP_EDGE_Z = MOVE_HEIGHT
		#Goto moving Z position
		out_data = "G00Z" + str(MOVE_HEIGHT) + "\n"
	if(gcode_tmp_flag):
		#Goto initial X-Y position
		return out_data + xy_data + "\n"
	else:
		return

def points_revers(points):
	return_points = []
	i = len(points)-1
	while i>0:
		return_points = return_points + [points[i-1],points[i]]
		i -=2	

	return return_points

def gcode_init():
	global gGCODE_DATA, INI_X, INI_Y, INI_Z, OUT_INCH_FLAG, MCODE_FLAG, gDRILL_DATA, gEDGE_DATA
	gGCODE_DATA += "(Generated by " + sys.argv[0] +" )\n"
	gGCODE_DATA += "( " + get_date() +" )\n"
	gGCODE_DATA += "(Initialize)\n"
	gGCODE_DATA += "G90G54G92X" + str(INI_X) + "Y" + str(INI_Y) + "Z" + str(INI_Z) + "\n"
	if OUT_INCH_FLAG:
		gGCODE_DATA += "(Set to inch unit)\n"
		gGCODE_DATA += "G20\n"

	gGCODE_DATA += "\n" + "(Start form here)\n"
	if MCODE_FLAG:
		gGCODE_DATA += "(Spindl and Coolant ON)\n"
		gGCODE_DATA += "M03\n"
		gGCODE_DATA += "M08\n"

	gDRILL_DATA = gGCODE_DATA
	gEDGE_DATA = gGCODE_DATA

def get_date():
	d = datetime.datetime.today()
	return d.strftime("%Y-%m-%d %H:%M:%S")

def read_Gerber(filename):
	global IN_INCH_FLAG
	f = open(filename,'r')
	print "Parse Gerber data"
	while 1:
		gerber = f.readline()
		if not gerber:
			break
		#print gerber
		if (find(gerber, "%MOIN") != -1):
			IN_INCH_FLAG = 1

		if (find(gerber, "%ADD") != -1):
			parse_add(gerber)
		#if(find(gerber, "%AM") != -1):
			#do nothing
		if (find(gerber, "G") != -1):
			parse_g(gerber)
		#if (find(gerber, "X") != -1 or find(gerber, "Y") != -1):
		if (find(gerber, "X") == 0):
			parse_xy(gerber)
	f.close()
	check_duplication()
	gcode2polygon()

def parse_add(gerber):
	global gDCODE,D_DATA
	dn = re.search("ADD([\d]+)([a-zA-Z]+)\,([\d\.]+)[a-zA-Z]+([\d\.]+)\W*",gerber)
	dm = re.search("ADD([\d]+)([a-zA-Z]+)\,([\d\.]+)\W*",gerber)
	mod2 = 0
	if (dn):
		d_num = dn.group(1)
		aperture_type = dn.group(2)
		mod1 = dn.group(3)
		mod2 = dn.group(4)
	elif (dm):
		d_num = dm.group(1)
		aperture_type = dm.group(2)
		mod1 = dm.group(3)
	else:
		return

	gDCODE[int(d_num)] = D_DATA(aperture_type,mod1,mod2)

def parse_g(gerber):
	global gTMP_X, gTMP_Y, gTMP_Z, g54_FLAG, gFIG_NUM
	index_d=find(gerber, "D")
	index_ast=find(gerber, "*")
	if (find(gerber, "54",1,index_d) !=-1):
		g54_FLAG = 1
	else:
		g54_FLAG = 0

	gFIG_NUM=gerber[index_d+1:index_ast]

def parse_xy(gerber):
	global gTMP_X, gTMP_Y, gTMP_Z, g54_FLAG, gFIG_NUM
	d=0
	xx = re.search("X([\d\.\-]+)\D",gerber)
	yy = re.search("Y([\d\-]+)\D",gerber)
	dd = re.search("D([\d]+)\D",gerber)
	if (xx):
		x = xx.group(1)
		if (x != gTMP_X):
			gTMP_X = x

	if (yy):
		y = yy.group(1)
		if (y != gTMP_Y):
			gTMP_Y = y
	if (dd):
		d = dd.group(1)

	if (g54_FLAG):
		parse_data(x,y,d)

def parse_data(x,y,d):
	global gDCODE, gFIG_NUM,INCH, TOOL_D, CAD_UNIT, gGERBER_TMP_X, gGERBER_TMP_Y, gGCODES, gUNIT
	mod1 = float(gDCODE[int(gFIG_NUM)].mod1) * gUNIT + float(TOOL_D)
	mod2 = float(gDCODE[int(gFIG_NUM)].mod2) * gUNIT + float(TOOL_D)
	x = float(x) * CAD_UNIT
	y = float(y) * CAD_UNIT
	if(d == "03" or d == "3"):
		#Flash
		if( gDCODE[int(gFIG_NUM)].atype == "C"):
			#Circle
			#polygon(circle_points(x,y,mod1/2,20))
			gGCODES.append(GCODE(x,y,0,0,1,mod1,0))
		elif(gDCODE[int(gFIG_NUM)].atype ==  "R"):
			#Rect
			#points = [x-mod1/2,y-mod2/2,x-mod1/2,y+mod2/2,x+mod1/2,y+mod2/2,x+mod1/2,y-mod2/2,x-mod1/2,y-mod2/2]
			#polygon(points)
			gGCODES.append(GCODE(x,y,0,0,2,mod1,mod2))
	elif(d == "02" or d == "2"):
		#move  w light off
		gGERBER_TMP_X = x
		gGERBER_TMP_Y = y
	elif(d == "01" or d == "1"):
		#move w Light on
		if(gDCODE[int(gFIG_NUM)].atype == "C"):
			#line2poly(gGERBER_TMP_X,gGERBER_TMP_Y,x,y,mod1/2,1,8)
			gGCODES.append(GCODE(gGERBER_TMP_X,gGERBER_TMP_Y,x,y,3,mod1,mod2))
		elif(gDCODE[int(gFIG_NUM)].atype == "R"):
			#Rect
			#line2poly(gGERBER_TMP_X,gGERBER_TMP_Y,x,y,mod2/2,0,8)
			gGCODES.append(GCODE(gGERBER_TMP_X,gGERBER_TMP_Y,x,y,4,mod1,mod2))
		gGERBER_TMP_X = x
		gGERBER_TMP_Y = y

def check_duplication():
	global gGCODES
	print "Check overlapping lines ..."
	i = 0
	while i< len(gGCODES)-1:
		xi1=gGCODES[i].x1
		yi1=gGCODES[i].y1
		xi2=gGCODES[i].x2
		yi2=gGCODES[i].y2
		ti=gGCODES[i].gtype
		xi_min=xi1
		xi_max=xi2
		yi_min=yi1
		yi_max=yi2
		if(xi1>xi2):
			xi_min=xi2
			xi_max=xi1
		if(yi1>yi2):
			yi_min=yi2
			yi_max=yi1
		j = i + 1
		while j< len(gGCODES):
			xj1=gGCODES[j].x1
			yj1=gGCODES[j].y1
			xj2=gGCODES[j].x2
			yj2=gGCODES[j].y2
			tj=gGCODES[j].gtype
			xj_min=xj1
			xj_max=xj2
			yj_min=yj1
			yj_max=yj2
			if(xj1>xj2):
				xj_min=xj2
				xj_max=xj1
			if(yj1>yj2):
				yj_min=yj2
				yj_max=yj1
			#if(xj_min>=xi_max or xj_max<=xi_min):
					#continue
			#if((xj_min>=xi_min and xj_max>=xi_max) or (xj_min<=xi_min and xj_max<=xi_max)):
					#continue
			
			if(ti == tj):	#same type
				dxi=xi2-xi1
				dyi=yi2-yi1
				dxj=xj2-xj1
				dyj=yj2-yj1
				if(dxi!=0):
					ai=dyi/dxi
					bi=yi1-ai*xi1
					if(dxj!=0):
						aj=dyj/dxj
						bj=yj1-aj*xj1
						if(aj==ai and bj==bi):
							if(xj_min>=xi_min and xj_max<=xi_max):
								#overlap
								gGCODES[j].gtype=5
							elif(xj_min<=xi_min and xj_max>=xi_max):
								#overlap
								gGCODES[i].gtype=5
				else:	#dxi==0
					if(dxj==0 and xi1==xj1):
						if(yj_min>=yi_min and yj_max<=yi_max):
							#overlap
							gGCODES[j].gtype=5
						elif(yj_min<=yi_min and yj_max>=yi_max):
							#overlap
							gGCODES[i].gtype=5
							
			j += 1
		i +=1

def check_duplication_old():
	global gGCODES
	i = 0
	while i< len(gGCODES)-1:
		xi1=gGCODES[i].x1
		yi1=gGCODES[i].y1
		xi2=gGCODES[i].x2
		yi2=gGCODES[i].y2
		ti=gGCODES[i].gtype
		j = i + 1
		while j< len(gGCODES):
			xj1=gGCODES[j].x1
			yj1=gGCODES[j].y1
			xj2=gGCODES[j].x2
			yj2=gGCODES[j].y2
			tj=gGCODES[j].gtype
			if((xi1 == xj1 and yi1 == yj1 and xi2 == xj2 and yi2 == yj2) or (xi1 == xj2 and yi1 == yj2 and xi2 == xj1 and yi2 == yj1)):
				#same line
				if(ti == tj):
					#same line, same type
					gGCODES[j].gtype=5
			j += 1
		i +=1

def gcode2polygon():
	global gGCODES
	for gcode in gGCODES:
		if(gcode.gtype == 5):
			continue
		x1=gcode.x1
		y1=gcode.y1
		x2=gcode.x2
		y2=gcode.y2
		mod1=gcode.mod1
		mod2=gcode.mod2
		if(gcode.gtype == 1):
			polygon(circle_points(x1,y1,mod1/2,20))
		elif(gcode.gtype == 2):
			points = [x1-mod1/2,y1-mod2/2,x1-mod1/2,y1+mod2/2,x1+mod1/2,y1+mod2/2,x1+mod1/2,y1-mod2/2,x1-mod1/2,y1-mod2/2]
			polygon(points)
		elif(gcode.gtype == 3):
			line2poly(x1,y1,x2,y2,mod1/2,1,8)
		elif(gcode.gtype == 4):
			line2poly(x1,y1,x2,y2,mod2/2,0,8)


def polygon(points):
	global HUGE, gPOLYGONS, gXMIN, gYMIN
	x_max=-HUGE
	x_min=HUGE
	y_max=-HUGE
	y_min=HUGE
	if(len(points)<=2):
		print "Error: polygon point"
		return
	i = 0
	while i< len(points):
		if(points[i] > x_max):
			x_max=points[i]
		if(points[i] < x_min):
			x_min=points[i]
		if(points[i+1] > y_max):
			y_max=points[i+1]
		if(points[i+1] < y_min):
			y_min=points[i+1]
		i += 2

	gPOLYGONS.append(POLYGON(x_min,x_max,y_min,y_max,points,0))

	if(gXMIN>x_min):
		gXMIN = x_min
	if(gYMIN>y_min):
		gYMIN=y_min

def circle_points(cx,cy,r,points_num):
	points=[]
	if(points_num <= 2):
		print "Too small angle at Circle"
		return
	i = points_num
	while i > 0:
		cir_x=cx+r*cos(2.0*pi*float(i)/float(points_num))
		cir_x=cx+r*cos(2.0*pi*float(i)/float(points_num))
		cir_y=cy+r*sin(2.0*pi*float(i)/float(points_num))
		points.extend([cir_x,cir_y])
		i -= 1
	cir_x=cx+r*cos(0.0)
	cir_y=cy+r*sin(0.0)
	points.extend([cir_x,cir_y])
	return points

def gcode_end():
	global gGCODE_DATA, MOVE_HEIGHT, INI_X, INI_Y, INI_Z, gDRILL_DATA, gEDGE_DATA
	end_data = ""
	end_data += "\n(Goto to Initial position)\n"
	#Goto initial Z position
	end_data += "G00Z" + str(MOVE_HEIGHT) + "\n"
	#STOP Coolant
	end_data += "M09\n"
	#STOP spindl
	end_data += "M05\n"	
	#Goto initial X-Y position
	end_data += "G00X" + str(INI_X) + "Y" + str(INI_Y) + "\n"
	#Goto initial Z position
	end_data += "G00Z" + str(INI_Z) + "\n"
	#Program END
	end_data += "M30\n"
	end_data += "%\n"
	gGCODE_DATA += end_data
	gDRILL_DATA += end_data
	gEDGE_DATA += end_data

def end(out_file_name,out_drill_file,out_edge_file):
	global gGCODE_DATA, CUT_DEPTH, XY_SPEED, Z_SPEED, gDRILL_DATA, gEDGE_DATA
	#calc_shift()
	polygon2gcode(CUT_DEPTH,XY_SPEED, Z_SPEED)
	gcode_end()
	#File open
	out = open(out_file_name, 'w')
	out.write(gGCODE_DATA)
	out.close()
	out = open(out_drill_file, 'w')
	out.write(gDRILL_DATA)
	out.close()
	out = open(out_edge_file, 'w')
	out.write(gEDGE_DATA)
	out.close()

def polygon2gcode(height,xy_speed,z_speed):
	global gPOLYGONS
	print "Convert to G-code"
	for poly in gPOLYGONS:
		if (poly.delete):
			continue
		path(height,xy_speed,z_speed,poly.points)

def path(height,xy_speed,z_speed,points):
	global gGCODE_DATA, gXSHIFT, gYSHIFT, gTMP_X, gTMP_Y, gTMP_Z
	out_data = "G01"
	gcode_tmp_flag = 0
	if(len(points) % 2):
		print "Number of points is illegal "
	#move to Start position
	move(points[0]+float(gXSHIFT),points[1]+float(gYSHIFT))
	#move to cuting heght
	if(height != gTMP_Z):
		gTMP_Z=height
		gGCODE_DATA += "G01Z" + str(height) + "F" + str(z_speed) + "\n"
	i = 0
	while i< len(points):
		px=points[i]+gXSHIFT
		py=points[i+1]+gYSHIFT
		if (px != gTMP_X):
			gTMP_X=px
			out_data +="X" + str(px)
			gcode_tmp_flag = 1
		if(py != gTMP_Y):
			gTMP_Y=py
			out_data +="Y" + str(py)
			gcode_tmp_flag=1
		if(gcode_tmp_flag):
			#Goto initial X-Y position
			out_data +="F" + str(xy_speed)
			gGCODE_DATA += out_data + "\n"
			out_data ="G01"
		gcode_tmp_flag=0
		i += 2

def move(x,y):
	global gGCODE_DATA, MOVE_HEIGHT, gTMP_X, gTMP_Y, gTMP_Z
	out_data = "G00"
	gcode_tmp_flag = 0
	if(x != gTMP_X):
		gTMP_X = x
		out_data += "X" + str(x)
		gcode_tmp_flag=1
	if(y != gTMP_Y):
		gTMP_Y = y
		out_data +="Y" + str(y)
		gcode_tmp_flag = 1
	if(MOVE_HEIGHT!=gTMP_Z):
		gTMP_Z = MOVE_HEIGHT
		#Goto moving Z position
		gGCODE_DATA += "G00Z" + str(MOVE_HEIGHT) + "\n"
	if(gcode_tmp_flag):
		#Goto X-Y position
		gGCODE_DATA += out_data + "\n"

def line2poly(x1,y1,x2,y2,r,atype,ang_n):
	points = []
	deg90=pi/2.0
	dx = x2-x1
	dy = y2-y1
	ang=atan2(dy,dx)
	xa1=x1+r*cos(ang+deg90)
	ya1=y1+r*sin(ang+deg90)
	xa2=x1-r*cos(ang+deg90)
	ya2=y1-r*sin(ang+deg90)
	xb1=x2+r*cos(ang+deg90)
	yb1=y2+r*sin(ang+deg90)
	xb2=x2-r*cos(ang+deg90)
	yb2=y2-r*sin(ang+deg90)
	if(atype):
		points = points + arc_points(x1,y1,r,ang+3*deg90,ang+deg90,ang_n)
		points = points + arc_points(x2,y2,r,ang+deg90,ang-deg90,ang_n)
		points = points + [xa2,ya2]
	else:
		points=(xa1,ya1,xb1,yb1,xb2,yb2,xa2,ya2,xa1,ya1)
	polygon(points)

def arc_points(cx,cy,r,s_angle,e_angle,kaku):
	points=[]
	if(s_angle == e_angle):
		print "Start and End angle are same"
	int(kaku)
	if(kaku <= 2):
		print "Too small angle"
	ang_step=(e_angle-s_angle)/(kaku-1)
	i = 0
	while i < kaku:
		arc_x=cx+r*cos(s_angle+ang_step*float(i))
		arc_y=cy+r*sin(s_angle+ang_step*float(i))
		points.extend([arc_x,arc_y])
		i += 1

	return points

def calc_shift():
	global gXSHIFT, gYSHIFT, gXMIN, gYMIN, LEFT_X, LOWER_Y
	gXSHIFT = LEFT_X - gXMIN
	gYSHIFT = LOWER_Y - gYMIN
	#print "x_shift=" + str(gXSHIFT) + "y_shift=" + str(gYSHIFT)

def polygon2line(points):
	global gLINES
	i = 0
	while i< len(points)-2:
		gLINES.append(LINE(points[i],points[i+1],points[i+2],points[i+3],0,0))
		i += 2

def merge():
	global gPOLYGONS, gLINES
	print "Start merge polygons"
	for poly1 in gPOLYGONS:
		out_points=[]
		merged=0
		if(poly1.delete):
			continue
		x_max=poly1.x_max
		x_min=poly1.x_min
		y_max=poly1.y_max
		y_min=poly1.y_min
		start_line_id=len(gLINES)
		polygon2line(poly1.points)
		end_line_id=len(gLINES)
		for poly2 in gPOLYGONS:
			if(poly2.delete):
				continue
			if(poly1 == poly2):
				continue
			xa_max=poly2.x_max
			xa_min=poly2.x_min
			ya_max=poly2.y_max
			ya_min=poly2.y_min
			if(x_max < xa_min or x_min > xa_max):
				continue
			if(y_max < ya_min or y_min > ya_max):
				continue
			k = start_line_id
			while k < end_line_id:
				CrossAndIn(k,poly2.points)
				k += 1
			end_line_id = len(gLINES)

	for poly3 in gPOLYGONS:
		#del all polygons
		poly3.delete = 1

	line_merge()
	print "End merge polygons"

def line_merge():
	global gPOLYGONS, gLINES
	print "   Start merge lines"
	#tmp_points = []
	margin = 0.0001
	for line1 in gLINES:
		if(line1.inside or line1.delete):
			continue
		tmp_points = [line1.x1, line1.y1, line1.x2, line1.y2]
		polygon(tmp_points)
		line1.delete = 1
		#tmp_points = gPOLYGONS[-1].points
		for line2  in gLINES:
			if(line2.inside or line2.delete):
				continue
			if(len(tmp_points) > 3):
				dist1 = calc_dist(tmp_points[0],tmp_points[1],line2.x2, line2.y2)
				dist2 = calc_dist(tmp_points[len(tmp_points)-2],tmp_points[len(tmp_points)-1], line2.x1, line2.y1)
				if(dist2 < margin):
					tmp_points = tmp_points + [line2.x2, line2.y2]
					line2.delete = 1
				elif(dist1 < margin):
					tmp_points = [line2.x1, line2.y1] + tmp_points
					line2.delete = 1

		gPOLYGONS[-1].points=tmp_points
	merge_polygons()

def merge_polygons():
	global gPOLYGONS
	print "      Start merge lines 2"
	#tmp_points1 = []
	#tmp_points2 = []
	margin = 0.00001
	for poly1 in gPOLYGONS:
		if(poly1.delete):
			continue
		tmp_points1 = poly1.points
		for poly2 in gPOLYGONS:
			if(poly2.delete or poly1==poly2):
				continue
			tmp_points2 = poly2.points
			dist1 = calc_dist(tmp_points1[0],tmp_points1[1],tmp_points2[len(tmp_points2)-2],tmp_points2[-1])
			dist2 = calc_dist(tmp_points1[len(tmp_points1)-2],tmp_points1[-1],tmp_points2[0],tmp_points2[1])
			if(dist2 < margin):
				del tmp_points2[0:2]
				tmp_points1 = tmp_points1 + tmp_points2
				poly2.delete = 1
			elif(dist1 < margin and dist2 > margin):
				tmp_points2.pop()
				tmp_points2.pop()
				tmp_points1 = tmp_points2 + tmp_points1
				poly2.delete = 1
			#elif(dist1 < margin and dist2 < margin):
				#print "error dist1=" + str(dist1) + ", dist2=" + str(dist2)
				#print "xi=" + str(tmp_points1[0]) + "xj=" +  str(tmp_points2[len(tmp_points2)-2]) + "yi=" + str(tmp_points1[1]) + "yj=" +  str(tmp_points2[-1])			
				#poly2.delete = 1

		poly1.points = tmp_points1

def CrossAndIn(line_id,spoints):
	global gLINES
	#check in or out
	xa = gLINES[line_id].x1
	ya = gLINES[line_id].y1
	xb = gLINES[line_id].x2
	yb = gLINES[line_id].y2
	if(gLINES[line_id].inside):
		return
	cross_count1 = 0
	cross_count2 = 0
	cross_points = []
	cross_nums = []
	cross_num = 0
	cross_flag = 0
	tmp_flag = 0
	return_flag = 0
	si = 0
	while si< len(spoints)-2:
		#reset flags
		flagX1 = 0
		flagX2 = 0
		flagY1 = 0
		flagY2 = 0
		xp1=spoints[si]
		yp1=spoints[si+1]
		xp2=spoints[si+2]
		yp2=spoints[si+3]
		(cross_flag,cross_x,cross_y)=find_cross_point(xa,ya,xb,yb,xp1,yp1,xp2,yp2)
		cross_num+=cross_flag
		if(cross_flag):
			cross_points.extend([cross_x,cross_y])
			cross_nums.append(si)
		#Is Point A IN?
		if(xa <= xp1):
			flagX1 = 1
		if(xa <= xp2):
			flagX2 = 1
		if(ya <= yp1):
			flagY1 = 1
		if(ya <= yp2):
			flagY2 = 1

		if(flagY1 != flagY2):
			#Cross?
			if(flagX1 == flagX2):
				if(flagX1):
					#Cross
					if(flagY1):#
						cross_count1 -=1
					else:
						cross_count1 += 1
			elif(yp2 != yp1):#
				if(xa <= (xp1+(xp2-xp1)*(ya-yp1)/(yp2-yp1))):#
					if(flagY1):#
						cross_count1 -= 1
					else:
						cross_count1 += 1
		#Is Point B IN?
		#reset flags
		flagX1 = 0
		flagX2 = 0
		flagY1 = 0
		flagY2 = 0
		#start check
		if(xb <= xp1):
			flagX1 = 1
		if(xb <= xp2):
			flagX2 = 1
		if(yb <= yp1):
			flagY1 = 1
		if(yb <= yp2):
			flagY2 = 1

		if(flagY1 != flagY2):
			#Cross?
			if(flagX1 == flagX2):
				if(flagX1):
					#Cross
					if(flagY1):#
						cross_count2 -= 1
					else:
						cross_count2 += 1
			elif(yp2 != yp1):#
				if(xb <= (xp1+(xp2-xp1)*(yb-yp1)/(yp2-yp1))):#
					if(flagY1):#
						cross_count2 -= 1
					else:
						cross_count2 += 1

		si += 2
	#end while

	if(cross_count1):#
		in_flag1 = 1
	else:
		in_flag1 = 0

	if(cross_count2):#
		in_flag2 = 1
	else:
		in_flag2 = 0

	if(cross_num>1):
		cross_points = sort_points_by_dist(xa,ya,cross_points)
		gLINES[line_id].x2 = cross_points[0]
		gLINES[line_id].y2 = cross_points[1]
		gLINES[line_id].inside = in_flag1
		if(in_flag1):
			tmp_flag=0
		else:
			tmp_flag=1

		tmp_x=cross_points[0]
		tmp_y=cross_points[1]
		i = 0
		while i < len(cross_points):
			gLINES.append(LINE(tmp_x,tmp_y,cross_points[i],cross_points[i+1],tmp_flag,0))
			if(in_flag1):
				tmp_flag = 0
			else:
				tmp_flag = 1
			tmp_x=cross_points[i]
			tmp_y=cross_points[i+1]
			i += 2
		#end while
		gLINES.append(LINE(cross_points[len(cross_points)-2],cross_points[len(cross_points)-1],xb,yb,in_flag2,0))
	
	elif(cross_num==1):
		if(in_flag1 == in_flag2):
			#in in
			gLINES[line_id].inside=in_flag1
		else:
			#in out
			gLINES[line_id].x2 = cross_points[0]
			gLINES[line_id].y2 = cross_points[1]
			gLINES[line_id].inside = in_flag1
			gLINES.append(LINE(cross_points[0],cross_points[1],xb,yb,in_flag2,0))
	else:
		if(in_flag1 != in_flag2):
			gLINES[line_id].inside = in_flag1
		else:
			gLINES[line_id].inside = in_flag1

	if(cross_num > 0):
		return 1
	elif(in_flag1 or in_flag2):
		return 1
	else:
		return 0

def sort_points_by_dist(x,y,points):
	return_points=[]
	return_pos=[]
	pre_dist=calc_dist(x,y,points[0],points[1])
	i = 0
	while i < len(points):
		if(pre_dist > calc_dist(x,y,points[i],points[i+1])):
			tmp_x = points[i]
			tmp_y = points[i+1]
			points[i] = points[i-2]
			points[i+1] = points[i-1]
			points[i-2] = tmp_x
			points[i-1] = tmp_y
		i += 2
	return points

def calc_dist(x1,y1,x2,y2):
	return sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))

def find_cross_point(x1,y1,x2,y2,xa,ya,xb,yb):
	flag = 0
	margin = 0.00001
	x_max = x2
	x_min = x1
	y_max = y2
	y_min = y1
	xa_max = xb
	xa_min = xa
	ya_max = yb
	ya_min = ya
	if(x1 > x2):
		x_max = x1
		x_min = x2
	if(y1 > y2):
		y_max=y1
		y_min=y2
	if(xa > xb):
		xa_max=xa
		xa_min=xb
	if(ya >  yb):
		ya_max = ya
		ya_min = yb
	if(x1 ==  x2):
		if(xa == xb):
			return (0,0,0)
		else:
			aa=(yb-ya)/(xb-xa)
			ba=ya-aa*xa
			x=x1
			y=aa*x+ba
	else:
		a1=(y2-y1)/(x2-x1)
		b1=y1-a1*x1
		if(xa == xb):
			x=xa
			y=a1*x+b1
		else:
			aa=(yb-ya)/(xb-xa)
			ba=ya-aa*xa
			if(a1 == aa):
				return (0,0,0)
			else:
				x=(ba-b1)/(a1-aa)
				y=a1*x+b1
	if(x_min-margin <= x and x_max+margin >= x):
		if(xa_min-margin <= x and xa_max+margin>=x):
			if(y_min-margin <= y and y_max+margin >= y):
				if(ya_min-margin <= y and ya_max+margin >= y):
					return (1,x,y)
	return (0,0,0)

#Drill 
def read_Drill_file(drill_file):
	global gDRILL_D, gDRILL_TYPE, gUNIT
	f = open(drill_file,'r')
	print "Read and Parse Drill data"
	while 1:
		drill = f.readline()
		if not drill:
			break
		drill_data = re.search("T([\d]+)C([\d\.]+)",drill)
		drill_num = re.search("T([\d]+)\s",drill)
		if(drill_data):
			gDRILL_TYPE[int(drill_data.group(1))] = drill_data.group(2)
		if(drill_num):
			gDRILL_D=float(gDRILL_TYPE[int(drill_num.group(1))]) * gUNIT
		if (find(drill, "X") != -1 or find(drill, "Y") != -1):
			parse_drill_xy(drill)
	f.close()

def parse_drill_xy(drill):
	global gDRILLS,gDRILL_D, gXSHIFT, gYSHIFT, INCH, IN_INCH_FLAG, OUT_INCH_FLAG, gUNIT
	calc_shift()
	xx = re.search("X([\d\.-]+)\D",drill)
	yy = re.search("Y([\d\.-]+)\D",drill)
	if(xx):
		x=float(xx.group(1)) * gUNIT + gXSHIFT
	if(yy):
		y=float(yy.group(1)) * gUNIT + gYSHIFT
	gDRILLS.append(DRILL(x,y,gDRILL_D,0))

def do_drill():
	global DRILL_SPEED, DRILL_DEPTH, gDRILLS, MOVE_HEIGHT, gDRILL_DATA, gGCODE_DATA, gTMP_DRILL_X, gTMP_DRILL_Y, gTMP_DRILL_Z, gTMP_X, gTMP_Y, gTMP_Z,MERGE_DRILL_DATA, gDRILL_D, DRILL_D
	drill_data = ""
	drill_mergin = 1
	if(MERGE_DRILL_DATA):
		gTMP_DRILL_X = gTMP_X
		gTMP_DRILL_Y = gTMP_Y
		gTMP_DRILL_Z = gTMP_Z
	for drill in gDRILLS:
		#print "drill.d=" + str(drill.d) + ", DRILL_D=" + str(DRILL_D)
		#move to hole position
		if(drill.d > DRILL_D + drill_mergin):
			cir_r = drill.d/2 - DRILL_D/2
			#drill_data += move_drill(drill.x-cir_r,drill.y)
			drill_data += drill_hole(drill.x,drill.y,cir_r)
		else:
			drill_data += move_drill(drill.x,drill.y)
			#Drill
			if(DRILL_SPEED):
				drill_data += "G01Z" + str(DRILL_DEPTH,) + "F" + str(DRILL_SPEED) + "\n"
			else:
				drill_data += "G01Z" + str(DRILL_DEPTH,) + "\n"

	#Goto moving Z position
	drill_data += "G00Z" + str(MOVE_HEIGHT) + "\n"

	gDRILL_DATA += drill_data
	if(MERGE_DRILL_DATA):
		gGCODE_DATA += drill_data
		gTMP_X = gTMP_DRILL_X 
		gTMP_Y = gTMP_DRILL_Y
		gTMP_Z = gTMP_DRILL_Z

def move_drill(x,y):
	global MOVE_HEIGHT, gTMP_DRILL_X, gTMP_DRILL_Y, gTMP_DRILL_Z
	xy_data = "G00"
	out_data = ""
	#print out_data
	gcode_tmp_flag = 0
	if(x != gTMP_DRILL_X):
		gTMP_DRILL_X = x
		xy_data += "X" + str(x)
		gcode_tmp_flag=1
	if(y != gTMP_DRILL_Y):
		gTMP_DRILL_Y = y
		xy_data += "Y" + str(y)
		gcode_tmp_flag = 1
	if(MOVE_HEIGHT!=gTMP_DRILL_Z):
		gTMP_DRILL_Z = MOVE_HEIGHT
		#Goto moving Z position
		out_data = "G00Z" + str(MOVE_HEIGHT) + "\n"
	if(gcode_tmp_flag):
		#Goto initial X-Y position
		return out_data + xy_data + "\n"
	else:
		return ""

def drill_hole(cx,cy,r):
	global MOVE_HEIGHT, gTMP_DRILL_X, gTMP_DRILL_Y, gTMP_DRILL_Z, DRILL_SPEED, DRILL_DEPTH, Z_STEP, XY_SPEED
	out_data = ""
	gcode_tmp_flag = 0
	z_step_n = int(DRILL_DEPTH/Z_STEP) + 1
	z_step = DRILL_DEPTH/z_step_n
	#print "r=" + str(r)
	if(MOVE_HEIGHT != gTMP_DRILL_Z):
		gTMP_DRILL_Z = MOVE_HEIGHT
		out_data += "G00Z" + str(gTMP_DRILL_Z) + "\n"
	out_data += "G00X" + str(cx-r) + "Y" + str(cy) + "\n"
	out_data += "G17\n"	#Set XY plane
	i = 1
	while i <= z_step_n:
		gTMP_DRILL_Z = i*z_step
		out_data += "G00Z" + str(gTMP_DRILL_Z) + "F" + str(DRILL_SPEED) + "\n"
		#Circle
		out_data += "G02X" + str(cx+r) + "Y" + str(cy) + "R" + str(r) + "F" + str(XY_SPEED) + "\n"
		out_data += "G02X" + str(cx-r) + "Y" + str(cy) + "R" + str(r) + "F" + str(XY_SPEED) + "\n"
		i += 1

	gTMP_DRILL_X = cx+r
	gTMP_DRILL_Y = cy
	return out_data

def error_dialog(error_mgs,sw):
	print error_mgs
	if(sw):
		#raw_input("\n\nPress the enter key to exit.")
		sys.exit()

if __name__ == "__main__":
    main()



