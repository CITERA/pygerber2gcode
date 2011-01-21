#!/usr/bin/python
# coding: UTF-8

from string import *
from math import *
#from struct import *
import os
import sys
#import datetime
import locale
import re
from datetime import datetime
from time import mktime

#Global Constant
HUGE = 1e10
TINY = 1e-6
MERGINE = 1e-4
INCH = 25.4 #mm
MIL = INCH/1000
CONFIG_FILE = "./pyg2g.conf"
WINDOW_X = 800
WINDOW_Y = 600
CENTER_X=200.0
CENTER_Y=200.0

#For CNC machine
INI_X = 0
INI_Y = 0
INI_Z = 5.0
MOVE_HEIGHT = 1.0
XY_SPEED = 100
Z_SPEED = 60
DRILL_SPEED = 50	#Drill down speed
DRILL_DEPTH = -1.2#Drill depth
CUT_DEPTH = -0.07	#pattern cutting depth
TOOL_D = 0.2		#Tool diameter
DRILL_D = 0.8		#Drill diameter
EDGE_TOOL_D = 1.0		#Edge Tool diameter
EDGE_DEPTH = -1.2 #edge depth
EDGE_SPEED = 80	#Edge cut speed
EDGE_Z_SPEED = 60	#Edge down speed
Z_STEP = -0.5

#for convert
MCODE_FLAG = 0
MERGE_DRILL_DATA = 0
LEFT_X = 5.0
LOWER_Y = 5.0
#For file
OUT_INCH_FLAG = 0
IN_INCH_FLAG = 1
CAD_UNIT = MIL/10
GERBER_EXT = '*.gtl'
DRILL_EXT = '*.drl'
EDGE_EXT = '*.gbr'
GCODE_EXT = '*.ngc'
GDRILL_EXT = '*.ngc'
GEDGE_EXT = '*.ngc'

#View
GERBER_COLOR = 'BLACK'	#black
DRILL_COLOR = 'BLUE'
EDGE_COLOR = 'GREEN YELLOW'
CONTOUR_COLOR = 'MAGENTA'

#


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

gGERBER_FILE = ""
gDRILL_FILE = ""
gEDGE_FILE = ""

gGCODE_FILE = ""
gGDRILL_FILE = ""
gGEDGE_FILE = ""

#For Drawing 
gPATTERNS = []
gDRAWDRILL = []
gDRAWEDGE = []
gDRAWCONTOUR = []
gMAG = 1.0
gPRE_X = CENTER_X
gPRE_Y = CENTER_X
gMAG_MIN = 0.1
gMAG_MAX = 100.0
gDRAW_XSHIFT = 0.0
gDRAW_YSHIFT = 0.0
gDISP_GERBER = 1
gDISP_DRILL = 0
gDISP_EDGE = 0
gDISP_CONTOUR = 0

gCOLORS = [
'AQUAMARINE','BLACK','BLUE','BLUE VIOLET','BROWN',
'CADET BLUE','CORAL','CORNFLOWER BLUE','CYAN','DARK GREY',
'DARK GREEN', 'DARK OLIVE GREEN', 'DARK ORCHID', 'DARK SLATE BLUE', 'DARK SLATE GREY',
'DARK TURQUOISE', 'DIM GREY', 'FIREBRICK', 'FOREST GREEN', 'GOLD',
'GOLDENROD', 'GREY', 'GREEN', 'GREEN YELLOW', 'INDIAN RED',
'KHAKI', 'LIGHT BLUE', 'LIGHT GREY', 'LIGHT STEEL BLUE', 'LIME GREEN',
'MAGENTA', 'MAROON', 'MEDIUM AQUAMARINE', 'MEDIUM BLUE', 'MEDIUM FOREST GREEN',
'MEDIUM GOLDENROD', 'MEDIUM ORCHID', 'MEDIUM SEA GREEN', 'MEDIUM SLATE BLUE', 'MEDIUM SPRING GREEN',
'MEDIUM TURQUOISE', 'MEDIUM VIOLET RED', 'MIDNIGHT BLUE', 'NAVY', 'ORANGE',
'ORANGE RED', 'ORCHID', 'PALE GREEN', 'PINK', 'PLUM',
'PURPLE', 'RED', 'SALMON', 'SEA GREEN', 'SIENNA',
'SKY BLUE', 'SLATE BLUE', 'SPRING GREEN', 'STEEL BLUE', 'TAN',
'THISTLE ', 'TURQUOISE', 'VIOLET', 'VIOLET RED', 'WHEAT',
'WHITE', 'YELLOW', 'YELLOW GREEN'
]

#Set Class
class DRAWPOLY:
	def __init__(self, points, color ,delete):
		self.points = points
		self.color = color
		self.delete = delete

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
	in_file="test1_pcb.gtl"
	drill_file="test1_drill.drl"
	edge_file = "test1_edge.gbr"


	in_file="avr_test1.gtl"
	drill_file="avr_test1.drl"
	edge_file = "avr_test1_edge.gbr"

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
def gerber2draw():
	global gPOLYGONS, gDRILLS, gEDGES, gPATTERNS, CENTER_X, CENTER_Y, gDRAWDRILL, gDRAWEDGE
	for polygon in gPOLYGONS:
		if (polygon.delete):
			continue
		i = 0
		points = []
		while i < len(polygon.points)-1:
			#x = polygon.points[i] + CENTER_X
			#y = -polygon.points[i + 1] + CENTER_Y
			x = polygon.points[i]
			y = -polygon.points[i + 1]
			points.append([x,y])
			i += 2
		gPATTERNS.append(DRAWPOLY(points,"",0))
	for drill in gDRILLS:
		x = drill.x
		y = -drill.y
		d = drill.d
		gDRAWDRILL.append(DRILL(x,y,d,0))
	for polygon in gEDGES:
		i = 0
		points = []
		while i < len(polygon.points)-1:
			#x = polygon.points[i] + CENTER_X
			#y = -polygon.points[i + 1] + CENTER_Y
			x = polygon.points[i]
			y = -polygon.points[i + 1]
			points.append([x,y])
			i += 2
		gDRAWEDGE.append(DRAWPOLY(points,"",0))

def contour2draw():
	global gPOLYGONS, gDRAWCONTOUR
	for polygon in gPOLYGONS:
		if (polygon.delete):
			continue
		i = 0
		points = []
		while i < len(polygon.points)-1:
			#x = polygon.points[i] + CENTER_X
			#y = -polygon.points[i + 1] + CENTER_Y
			x = polygon.points[i]
			y = -polygon.points[i + 1]
			points.append([x,y])
			i += 2
		gDRAWCONTOUR.append(DRAWPOLY(points,"",0))

def set_unit():
	global IN_INCH_FLAG, OUT_INCH_FLAG, gUNIT, INCH
	if (IN_INCH_FLAG and not OUT_INCH_FLAG):
		gUNIT = INCH
	elif(not IN_INCH_FLAG and OUT_INCH_FLAG):
		gUNIT = 1.0/INCH
	else:
		gUNIT = 1.0

def save_config():
	global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT, EDGE_TOOL_D, EDGE_DEPTH, EDGE_SPEED, EDGE_Z_SPEED, MERGE_DRILL_DATA, Z_STEP, GERBER_COLOR, DRILL_COLOR, EDGE_COLOR , CONTOUR_COLOR, GERBER_EXT, DRILL_EXT, EDGE_EXT, GCODE_EXT, GDRILL_EXT, GEDGE_EXT

	config_data =""
	config_data += "INI_X=" + str(INI_X) + "\n"
	config_data += "INI_Y=" + str(INI_Y) + "\n"
	config_data += "INI_Z=" + str(INI_Z) + "\n"
	config_data += "MOVE_HEIGHT=" + str(MOVE_HEIGHT) + "\n"
	config_data += "IN_INCH_FLAG=" + str(IN_INCH_FLAG) + "\n"
	config_data += "OUT_INCH_FLAG=" + str(OUT_INCH_FLAG) + "\n"
	config_data += "MCODE_FLAG=" + str(MCODE_FLAG) + "\n"
	config_data += "XY_SPEED=" + str(XY_SPEED) + "\n"
	config_data += "Z_SPEED=" + str(Z_SPEED) + "\n"
	config_data += "LEFT_X=" + str(LEFT_X) + "\n"
	config_data += "LOWER_Y=" + str(LOWER_Y) + "\n"
	config_data += "DRILL_SPEED=" + str(DRILL_SPEED) + "\n"
	config_data += "DRILL_DEPTH=" + str(DRILL_DEPTH) + "\n"
	config_data += "CUT_DEPTH=" + str(CUT_DEPTH) + "\n"
	config_data += "TOOL_D=" + str(TOOL_D) + "\n"
	config_data += "DRILL_D=" + str(DRILL_D) + "\n"
	config_data += "CAD_UNIT=" + str(CAD_UNIT) + "\n"
	config_data += "EDGE_TOOL_D=" + str(EDGE_TOOL_D) + "\n"
	config_data += "EDGE_DEPTH=" + str(EDGE_DEPTH) + "\n"
	config_data += "EDGE_SPEED=" + str(EDGE_SPEED) + "\n"
	config_data += "EDGE_Z_SPEED=" + str(EDGE_Z_SPEED) + "\n"
	config_data += "MERGE_DRILL_DATA=" + str(MERGE_DRILL_DATA) + "\n"
	config_data += "Z_STEP=" + str(Z_STEP) + "\n"
	config_data += "GERBER_COLOR=" + str(GERBER_COLOR) + "\n"
	config_data += "DRILL_COLOR=" + str(DRILL_COLOR) + "\n"
	config_data += "EDGE_COLOR=" + str(EDGE_COLOR) + "\n"
	config_data += "CONTOUR_COLOR=" + str(CONTOUR_COLOR) + "\n"
	config_data += "GERBER_EXT=" + str(GERBER_EXT) + "\n"
	config_data += "DRILL_EXT=" + str(DRILL_EXT) + "\n"
	config_data += "EDGE_EXT=" + str(EDGE_EXT) + "\n"
	config_data += "GCODE_EXT=" + str(GCODE_EXT) + "\n"
	config_data += "GDRILL_EXT=" + str(GDRILL_EXT) + "\n"
	config_data += "GEDGE_EXT=" + str(GEDGE_EXT) + "\n"
	out = open(CONFIG_FILE, 'w')
	out.write(config_data)
	out.close()
def read_config():
	global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT, EDGE_TOOL_D, EDGE_DEPTH, EDGE_SPEED, EDGE_Z_SPEED, MERGE_DRILL_DATA, Z_STEP, GERBER_COLOR, DRILL_COLOR, EDGE_COLOR , CONTOUR_COLOR, GERBER_EXT, DRILL_EXT, EDGE_EXT, GCODE_EXT, GDRILL_EXT, GEDGE_EXT
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
				if(cfg.group(1)=="EDGE_TOOL_D"):
					EDGE_TOOL_D = float(cfg.group(2))
				if(cfg.group(1)=="EDGE_DEPTH"):
					EDGE_DEPTH = float(cfg.group(2))
				if(cfg.group(1)=="EDGE_SPEED"):
					EDGE_SPEED = int(cfg.group(2))
				if(cfg.group(1)=="EDGE_Z_SPEED"):
					EDGE_Z_SPEED = int(cfg.group(2))
				if(cfg.group(1)=="MERGE_DRILL_DATA"):
					MERGE_DRILL_DATA = int(cfg.group(2))
				if(cfg.group(1)=="Z_STEP"):
					Z_STEP = float(cfg.group(2))
				if(cfg.group(1)=="GERBER_COLOR"):
					GERBER_COLO = str(cfg.group(2))
				if(cfg.group(1)=="DRILL_COLOR"):
					DRILL_COLOR = str(cfg.group(2))
				if(cfg.group(1)=="EDGE_COLOR"):
					EDGE_COLOR = str(cfg.group(2))
				if(cfg.group(1)=="CONTOUR_COLOR"):
					CONTOUR_COLOR = str(cfg.group(2))
				if(cfg.group(1)=="GERBER_EXT"):
					GERBER_EXT = str(cfg.group(2))
				if(cfg.group(1)=="DRILL_EXT"):
					DRILL_EXT = str(cfg.group(2))
				if(cfg.group(1)=="EDGE_EXT"):
					EDGE_EXT = str(cfg.group(2))
				if(cfg.group(1)=="GCODE_EXT"):
					GCODE_EXT = str(cfg.group(2))
				if(cfg.group(1)=="GDRILL_EXT"):
					GDRILL_EXT = str(cfg.group(2))
				if(cfg.group(1)=="GEDGE_EXT"):
					GEDGE_EXT = str(cfg.group(2))
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
		for edge2 in gEDGES:
			if(edge2.delete or edge2 == edge1):
				continue
			tmp_points2 = edge2.points	
			dist1 = calc_dist(edge1.points[0],edge1.points[1],edge2.points[0], edge2.points[1])
			dist2 = calc_dist(edge1.points[0],edge1.points[1],edge2.points[len(edge2.points)-2], edge2.points[-1])
			dist3 = calc_dist(edge1.points[len(edge1.points)-2],edge1.points[-1],edge2.points[0], edge2.points[1])
			dist4 = calc_dist(edge1.points[len(edge1.points)-2],edge1.points[-1],edge2.points[len(edge2.points)-2], edge2.points[-1])
			#print "dist1=" + str(dist1) + ", dist2=" + str(dist2) + ", dist3=" + str(dist3) + ", dist4=" + str(dist4)
			if(dist2 < MERGINE):
				#join
				del tmp_points1[0:2]
				tmp_points1 = tmp_points2 + tmp_points1
				edge2.delete = 1
			elif(dist3 < MERGINE):
				#join
				del tmp_points2[0:2]
				tmp_points1 = tmp_points1 + tmp_points2
				edge2.delete = 1
			elif(dist1 < MERGINE):
				#join
				tmp_points2 = points_revers(tmp_points2)
				del tmp_points1[0:2]
				tmp_points1 = tmp_points2 + tmp_points1
				edge2.delete = 1
			elif(dist4 < MERGINE):
				#join
				tmp_points2 = points_revers(tmp_points2)
				del tmp_points2[0:2]
				tmp_points1 = tmp_points1 + tmp_points2
				edge2.delete = 1
			edge1.points=tmp_points1
			#print "len=" + str(len(edge1.points)) + ", edges=" + str(len(gEDGES))
			#print edge1.points
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
			if(edge.delete):
				continue
			points = edge.points
			if(len(points) % 2):
				error_dialog("Error:Number of points is illegal ",0)
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
		return ""

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
	#d = datetime.datetime.today()
	d = datetime.today()
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
	#check_duplication()
	#gerber2polygon()
	gerber2polygon4draw()

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
	#mod1 = float(gDCODE[int(gFIG_NUM)].mod1) * gUNIT + float(TOOL_D)
	#mod2 = float(gDCODE[int(gFIG_NUM)].mod2) * gUNIT + float(TOOL_D)
	mod1 = float(gDCODE[int(gFIG_NUM)].mod1) * gUNIT
	mod2 = float(gDCODE[int(gFIG_NUM)].mod2) * gUNIT
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
		if(gGCODES[i].gtype == 1 or gGCODES[i].gtype == 2):
			i += 1
			continue
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
			#if(gGCODES[j].gtype == 1 or gGCODES[j].gtype == 2 or ti != gGCODES[j].gtype):
				#j += 1
				#continue
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
			if(xj_min>=xi_max or xj_max<=xi_min):
					j += 1
					continue
			if(yj_min>=yi_max or yj_max<=yi_min):
					j += 1
					continue
			#if((xj_min > xi_min and xj_max > xi_max) or (xj_min < xi_min and xj_max < xi_max)):
					#j += 1
					#continue

			dxi=xi2-xi1
			dyi=yi2-yi1
			dxj=xj2-xj1
			dyj=yj2-yj1
			if(dxi!=0 and dxj!=0):
				ai=dyi/dxi
				bi=yi1-ai*xi1
				aj=dyj/dxj
				bj=yj1-aj*xj1
				if(aj==ai and bj==bi):
					if(xj_min>=xi_min and xj_max<=xi_max):
						#overlap
						gGCODES[j].gtype=5
					elif(xj_min<=xi_min and xj_max>=xi_max):
						#overlap
						gGCODES[i].gtype=5
			elif(dxi==0 and dxj==0 and xi1==xj1):
				if(yj_min>=yi_min and yj_max<=yi_max):
					#overlap
					gGCODES[j].gtype=5
				elif(yj_min<=yi_min and yj_max>=yi_max):
					#overlap
					gGCODES[i].gtype=5
							
			j += 1
		i +=1

def gerber2polygon4draw():
	global gGCODES, TOOL_D
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

def gerber2polygon():
	global gPOLYGONS,gGCODES, TOOL_D
	gPOLYGONS = []	#initialize
	for gcode in gGCODES:
		if(gcode.gtype == 5):
			continue
		x1=gcode.x1
		y1=gcode.y1
		x2=gcode.x2
		y2=gcode.y2
		mod1=gcode.mod1 + float(TOOL_D)
		mod2=gcode.mod2 + float(TOOL_D)
		if(gcode.gtype == 1):
			#polygon(circle_points(x1,y1,mod1/2,20))
			#polygon2(x1-mod1/2,x1+mod1/2,y1-mod1/2,y1+mod1/2,circle_points(x1,y1,mod1/2,20))
			gPOLYGONS.append(POLYGON(x1-mod1/2,x1+mod1/2,y1-mod1/2,y1+mod1/2,circle_points(x1,y1,mod1/2,20),0))
		elif(gcode.gtype == 2):
			points = [x1-mod1/2,y1-mod2/2,x1-mod1/2,y1+mod2/2,x1+mod1/2,y1+mod2/2,x1+mod1/2,y1-mod2/2,x1-mod1/2,y1-mod2/2]
			#polygon([x1-mod1/2,y1-mod2/2,x1-mod1/2,y1+mod2/2,x1+mod1/2,y1+mod2/2,x1+mod1/2,y1-mod2/2,x1-mod1/2,y1-mod2/2])
			#polygon2(x1-mod1/2,x1+mod1/2,y1-mod2/2,y1+mod2/2,points)
			gPOLYGONS.append(POLYGON(x1-mod1/2,x1+mod1/2,y1-mod2/2,y1+mod2/2,points,0))
		elif(gcode.gtype == 3):
			line2poly(x1,y1,x2,y2,mod1/2,1,8)
		elif(gcode.gtype == 4):
			line2poly(x1,y1,x2,y2,mod2/2,0,8)

def polygon2(x_min,x_max,y_min,y_max,points):
	global HUGE, gPOLYGONS, gXMIN, gYMIN
	gPOLYGONS.append(POLYGON(x_min,x_max,y_min,y_max,points,0))


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
	global gGCODE_DATA, MOVE_HEIGHT, INI_X, INI_Y, INI_Z, gDRILL_DATA, gEDGE_DATA, MCODE_FLAG
	end_data = ""
	end_data += "\n(Goto to Initial position)\n"
	#Goto initial Z position
	end_data += "G00Z" + str(MOVE_HEIGHT) + "\n"
	if MCODE_FLAG:
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
	check_duplication()
	gerber2polygon()
	print "Start merge polygons"
	for poly1 in gPOLYGONS:
		out_points=[]
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
	margin = 0.0001
	for line1 in gLINES:
		if(line1.inside or line1.delete):
			continue
		tmp_points = [line1.x1, line1.y1, line1.x2, line1.y2]
		#polygon(tmp_points)
		#polygon([line1.x1, line1.y1, line1.x2, line1.y2])
		#x_min = line1.x1
		#x_max = line1.x2
		#y_min = line1.y1
		#y_max = line1.y2
		#if(line1.x1 > line1.x2):
			#x_min = line1.x2
			#x_max = line1.x1
		#if(line1.y1 > line1.y2):
			#y_min = line1.y2
			#y_max = line1.y1
		#polygon2(x_min,x_max,y_min,y_max,[line1.x1, line1.y1, line1.x2, line1.y2])
		line1.delete = 1
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
		gPOLYGONS.append(POLYGON(line1.x1, line1.x2, line1.y1, line1.y2,tmp_points,0))
		#gPOLYGONS[-1].points=tmp_points
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
	global gLINES, gCCOUNT1, gCCOUNT2
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
	global gDRILLS,gDRILL_D, gUNIT
	xx = re.search("X([\d\.-]+)\D",drill)
	yy = re.search("Y([\d\.-]+)\D",drill)
	if(xx):
		x=float(xx.group(1)) * gUNIT
	if(yy):
		y=float(yy.group(1)) * gUNIT
	gDRILLS.append(DRILL(x,y,gDRILL_D,0))

def do_drill():
	global DRILL_SPEED, DRILL_DEPTH, gDRILLS, MOVE_HEIGHT, gDRILL_DATA, gGCODE_DATA, gTMP_DRILL_X, gTMP_DRILL_Y, gTMP_DRILL_Z, gTMP_X, gTMP_Y, gTMP_Z,MERGE_DRILL_DATA, gDRILL_D, DRILL_D, gXSHIFT, gYSHIFT
	drill_data = ""
	drill_mergin = 0.02
	calc_shift()
	if(MERGE_DRILL_DATA):
		gTMP_DRILL_X = gTMP_X
		gTMP_DRILL_Y = gTMP_Y
		gTMP_DRILL_Z = gTMP_Z
	for drill in gDRILLS:
		x = drill.x + gXSHIFT
		y = drill.y + gYSHIFT
		#print "drill.d=" + str(drill.d) + ", DRILL_D=" + str(DRILL_D)
		#move to hole position
		if(drill.d > DRILL_D + drill_mergin):
			cir_r = drill.d/2 - DRILL_D/2
			#drill_data += move_drill(drill.x-cir_r,drill.y)
			drill_data += drill_hole(x,y,cir_r)
		else:
			drill_data += move_drill(x,y)
			#Drill
			if(DRILL_SPEED):
				drill_data += "G01Z" + str(DRILL_DEPTH) + "F" + str(DRILL_SPEED) + "\n"
			else:
				drill_data += "G01Z" + str(DRILL_DEPTH) + "\n"
		#Goto moving Z position
		drill_data += "G00Z" + str(MOVE_HEIGHT) + "\n"
		gTMP_DRILL_Z = MOVE_HEIGHT
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
	if(y != float(gTMP_DRILL_Y)):
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
	z_step_n = int(float(DRILL_DEPTH)/float(Z_STEP)) + 1
	z_step = float(DRILL_DEPTH)/z_step_n
	#print "r=" + str(r)
	if(MOVE_HEIGHT != gTMP_DRILL_Z):
		gTMP_DRILL_Z = MOVE_HEIGHT
		out_data += "G00Z" + str(gTMP_DRILL_Z) + "\n"
	out_data += "G00X" + str(cx+r) + "Y" + str(cy) + "\n"
	out_data += "G17\n"	#Set XY plane
	points = circle_points(cx,cy,r,100)
	i = 1
	while i <= z_step_n:
		gTMP_DRILL_Z = i*z_step
		out_data += "G00Z" + str(gTMP_DRILL_Z) + "F" + str(DRILL_SPEED) + "\n"
		j = 0
		cricle_data = "G01"
		while j< len(points):
			px=points[j]
			py=points[j+1]
			if (px != gTMP_DRILL_X):
				gTMP_DRILL_X=px
				cricle_data +="X" + str(px)
				gcode_tmp_flag = 1
			if(py != gTMP_DRILL_Y):
				gTMP_DRILL_Y=py
				cricle_data +="Y" + str(py)
				gcode_tmp_flag=1
			if(gcode_tmp_flag):
				#Goto initial X-Y position
				cricle_data +="F" + str(XY_SPEED)
				out_data += cricle_data + "\n"
				cricle_data ="G01"
			gcode_tmp_flag=0
			j += 2
		i += 1

	gTMP_DRILL_X = cx+r
	gTMP_DRILL_Y = cy
	return out_data

def drill_hole_test(cx,cy,r):
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
		#out_data += "G03X" + str(cx+r) + "Y" + str(cy) + "I" + str(cx) + "J" + str(cy) + "F" + str(XY_SPEED) + "\n"
		#out_data += "G03X" + str(cx-r) + "Y" + str(cy) + "I" + str(cx) + "J" + str(cy) + "F" + str(XY_SPEED) + "\n"
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
