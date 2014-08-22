#!/usr/bin/python
# coding: UTF-8

#from string import *
#from math import *
#from struct import *
#import os
import sys
import re

#import gerber_org as gerber
#import gerber_test as gerber
import gerber
import gcode
import gerber_shapely as gs
from matplotlib import pyplot
#Global Constant
MERGINE = 1e-4
INCH = 25.4 #mm
MIL = INCH/1000.0

#For CNC machine
SET_INI = 1
INI_X = 0
INI_Y = 0
INI_Z = 5.0
MOVE_HEIGHT = 1.0
XY_SPEED = 100
Z_SPEED = 60

DRILL_SPEED = 50	#Drill in-plane speed
DRILL_Z_SPEED = 50	#Drill down speed
DRILL_DEPTH = -1.2#Drill depth
CUT_DEPTH = -0.07	#pattern cutting depth
TOOL_D = 0.2		#Tool diameter
DRILL_D = 0.8		#Drill diameter
EDGE_TOOL_D = 1.0		#Edge Tool diameter
EDGE_DEPTH = -1.2 #edge depth
EDGE_SPEED = 80	#Edge cut speed
EDGE_Z_SPEED = 60	#Edge down speed
Z_STEP = -0.5
DRILL_TYPE = 1
#for convert
PATTERN_SHIFT = 1
LEFT_X = 5.0
LOWER_Y = 5.0
#For file
OUT_INCH_FLAG = 0
IN_INCH_FLAG = 1
OUT_UNIT = 1.0		#mm
IN_UNIT = 25.4		#inch	

GERBER_EXT = '*.gtl'
DRILL_EXT = '*.drl'
EDGE_EXT = '*.gbr'
GCODE_EXT = '*.ngc'
GDRILL_EXT = '*.ngc'
GEDGE_EXT = '*.ngc'

#
GERBER_DIR = ""
FRONT_FILE = ""
BACK_FILE = ""
DRILL_FILE = ""
EDGE_FILE = ""
MIRROR_FRONT = False
MIRROR_BACK = False
MIRROR_DRILL = False
MIRROR_EDGE = False
ROT_ANG = 0
OUT_DIR = ""
OUT_FRONT_FILE = ""
OUT_BACK_FILE = ""
OUT_DRILL_FILE = ""
OUT_EDGE_FILE = ""
OUT_ALL_FILE = "test_gerber.ngc"
CUT_ALL_FRONT = 0
CUT_ALL_BACK = 0
CUT_STEP_R_FRONT = 1.9
CUT_STEP_R_BACK = 1.9
CUT_MAX_FRONT = 20
CUT_MAX_BACK = 20
CUT_MARGIN_R = 1.1
CUT_MARGIN_R = 1.1
#functions
def main():
	if len(sys.argv) > 1 and sys.argv[1]:
		read_config(sys.argv[1])
	else:
		print "Usage : python pygerber2gcode_cui.py config_file"
		exit()
	center=(0,0,0)
	if OUT_INCH_FLAG == 1:
		OUT_UNIT = INCH
	else:
		OUT_UNIT = 1.0
	if IN_INCH_FLAG == 1:
		IN_UNIT = INCH
	else:
		IN_UNIT = 1.0

	if FRONT_FILE:
		front_gerber = gerber.Gerber(GERBER_DIR,FRONT_FILE,OUT_UNIT)
		if not CUT_ALL_FRONT:
			f_op = gs.Gerber_OP(front_gerber,TOOL_D)
			f_op.gerber2shapely()
			f_op.in_unit=IN_UNIT
			f_op.out_unit=OUT_UNIT
			f_op.mirror=MIRROR_FRONT
			f_op.rot_ang=float(ROT_ANG)
			f_op.merge_polygon()
			f_op.diff_polygon()
			f_op.get_minmax()
			center=f_op.center
		else:
			CUT_STEP = TOOL_D * CUT_STEP_R_FRONT
			tmp_elements = []
			tmp_xmax = 0.0
			tmp_ymax = 0.0
			tmp_xmin = 0.0
			tmp_ymin = 0.0
			for i in range(CUT_MAX_FRONT):
				f_op = gs.Gerber_OP(front_gerber,TOOL_D+i*CUT_STEP)
				f_op.gerber2shapely()
				f_op.in_unit=IN_UNIT
				f_op.out_unit=OUT_UNIT
				f_op.mirror=MIRROR_FRONT
				f_op.rot_ang=float(ROT_ANG)
				f_op.merge_polygon()
				f_op.diff_polygon_multi()
				f_op.get_minmax()
				f_op.affine()
				if i == 0:
					tmp_xmax = f_op.xmax+CUT_MARGIN_R*TOOL_D
					tmp_ymax = f_op.ymax+CUT_MARGIN_R*TOOL_D
					tmp_xmin = f_op.xmin-CUT_MARGIN_R*TOOL_D
					tmp_ymin = f_op.ymin-CUT_MARGIN_R*TOOL_D
					center=f_op.center
				f_op.limit_cut(tmp_xmax,tmp_ymax,tmp_xmin,tmp_ymin)
				print "Loop No. = ",i,", number of plygons = ",len(f_op.figs.elements)
				tmp_elements += f_op.figs.elements
				#f_op.figs.elements=[]
				#print "num",len(tmp_elements)
			f_op.figs.elements=tmp_elements
	xoff=0.0
	yoff=0.0
	if PATTERN_SHIFT:
		xoff=LEFT_X-f_op.xmin
		yoff=LOWER_Y-f_op.ymin
	if BACK_FILE:
		back_gerber = gerber.Gerber(GERBER_DIR,BACK_FILE,OUT_UNIT)
		if not CUT_ALL_BACK:
			b_op = gs.Gerber_OP(back_gerber,TOOL_D)
			b_op.in_unit=IN_UNIT
			b_op.out_unit=OUT_UNIT
			b_op.mirror=MIRROR_BACK
			b_op.rot_ang=float(ROT_ANG)
			b_op.gerber2shapely()
			b_op.merge_polygon()
			b_op.diff_polygon()
			b_op.mirror=MIRROR_BACK
			b_op.rot_ang=float(ROT_ANG)
			b_op.get_minmax()
			#center=b_op.center
		else:
			CUT_STEP = TOOL_D * CUT_STEP_R_BACK
			tmp_elements = []
			tmp_xmax = 0.0
			tmp_ymax = 0.0
			tmp_xmin = 0.0
			tmp_ymin = 0.0
			for i in range(CUT_MAX_BACK):
				b_op = gs.Gerber_OP(back_gerber,TOOL_D+i*CUT_STEP)
				b_op.gerber2shapely()
				b_op.in_unit=IN_UNIT
				b_op.out_unit=OUT_UNIT
				b_op.mirror=MIRROR_BACK
				b_op.rot_ang=float(ROT_ANG)
				b_op.merge_polygon()
				b_op.diff_polygon_multi()
				b_op.get_minmax()
				b_op.affine()
				if i == 0:
					tmp_xmax = b_op.xmax+CUT_MARGIN_R*TOOL_D
					tmp_ymax = b_op.ymax+CUT_MARGIN_R*TOOL_D
					tmp_xmin = b_op.xmin-CUT_MARGIN_R*TOOL_D
					tmp_ymin = b_op.ymin-CUT_MARGIN_R*TOOL_D
				b_op.limit_cut(tmp_xmax,tmp_ymax,tmp_xmin,tmp_ymin)
				print "Loop No. = ",i,", number of plygons = ",len(b_op.figs.elements)
				tmp_elements += b_op.figs.elements
				#f_op.figs.elements=[]
				print "num",len(tmp_elements)
			b_op.figs.elements=tmp_elements

	#print "back center =",center
	if DRILL_FILE:
		#print "drill"
		drill_gerber=gerber.Drill(GERBER_DIR,DRILL_FILE,OUT_UNIT)
		#drill_gerber.parse()
		d_op = gs.Gerber_OP(drill_gerber,DRILL_D)
		d_op.in_unit=1.0
		d_op.out_unit=OUT_UNIT
		d_op.drill2shapely()
		d_op.mirror=MIRROR_DRILL
		d_op.rot_ang=float(ROT_ANG)
		d_op.get_minmax()
		#center=d_op.center
	#print "drill center =",center
	if EDGE_FILE:
		edge_gerber = gerber.Gerber(GERBER_DIR,EDGE_FILE,OUT_UNIT)
		e_op = gs.Gerber_OP(edge_gerber,EDGE_TOOL_D)
		e_op.in_unit=IN_UNIT
		e_op.out_unit=OUT_UNIT
		e_op.edge2shapely()
		e_op.merge_line()
		e_op.mirror=MIRROR_EDGE
		e_op.rot_ang=float(ROT_ANG)
		e_op.get_minmax()
		#center=e_op.center
	#print "edge center =",center

	#out gcode
	a_gcd = gcode.Gcode()
	set_gcode(a_gcd)
	if FRONT_FILE:
		f_op.center = center
		f_op.xoff = xoff
		f_op.yoff = yoff
		f_op.affine()
		f_op.affine_trans(f_op.raw_figs)
		f_op.draw_out()
		f_op.fig_out()
		f_gcd = gcode.Gcode()
		set_gcode(f_gcd)
		f_gcd.add_polygon(CUT_DEPTH,f_op.out_figs.elements,XY_SPEED, Z_SPEED)
		f_gcd.out(OUT_DIR,OUT_FRONT_FILE)
		a_gcd.add_polygon(CUT_DEPTH,f_op.out_figs.elements,XY_SPEED, Z_SPEED)
		disp_fig(f_op.raw_figs, f_op.figs)
	if BACK_FILE:
		b_op.center = center
		b_op.xoff = xoff
		b_op.yoff = yoff
		b_op.affine()
		b_op.fig_out()
		b_gcd = gcode.Gcode()
		set_gcode(b_gcd)
		b_gcd.add_polygon(CUT_DEPTH,b_op.out_figs.elements,XY_SPEED, Z_SPEED)
		b_gcd.out(OUT_DIR,OUT_BACK_FILE)
		a_gcd.add_polygon(CUT_DEPTH,b_op.out_figs.elements,XY_SPEED, Z_SPEED)
	if DRILL_FILE:
		d_op.center = (center[0]*IN_UNIT/OUT_UNIT,center[1]*IN_UNIT/OUT_UNIT,0)
		#d_op.center = center
		d_op.xoff = xoff
		d_op.yoff = yoff
		d_op.affine()
		d_op.fig_out()
		d_gcd = gcode.Gcode()
		set_gcode(d_gcd)
		drill2gcode(d_gcd,d_op.out_figs.elements)
		d_gcd.out(OUT_DIR,OUT_DRILL_FILE)
		drill2gcode(a_gcd,d_op.out_figs.elements)
	if EDGE_FILE:
		e_op.center = center
		e_op.xoff = xoff
		e_op.yoff = yoff
		e_op.affine()
		e_op.fig_out()
		e_gcd = gcode.Gcode()
		set_gcode(e_gcd)
		edge2gcode(e_gcd,e_op.out_figs.elements)
		e_gcd.out(OUT_DIR,OUT_EDGE_FILE)
		edge2gcode(a_gcd,e_op.out_figs.elements)

	a_gcd.out(OUT_DIR,OUT_ALL_FILE)

def set_gcode(gcode_handler):
	gcode_handler.mcode_sw = MCODE_FLAG
	gcode_handler.unit = OUT_INCH_FLAG
	gcode_handler.ini_x = INI_X
	gcode_handler.ini_y = INI_Y
	gcode_handler.ini_z = INI_Z
	gcode_handler.move_hight = MOVE_HEIGHT

def read_config(config_file):
	global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT, EDGE_TOOL_D, EDGE_DEPTH, EDGE_SPEED, EDGE_Z_SPEED, Z_STEP, GERBER_COLOR, DRILL_COLOR, EDGE_COLOR , CONTOUR_COLOR, GERBER_EXT, DRILL_EXT, EDGE_EXT, GCODE_EXT, GDRILL_EXT, GEDGE_EXT, CUT_FLAG, CUT_OV,MCODE_FLAG
	#global DRILL_UNIT, EDGE_UNIT
	global GERBER_DIR,FRONT_FILE,BACK_FILE,DRILL_FILE,EDGE_FILE,MIRROR_FRONT,MIRROR_BACK,MIRROR_DRILL,MIRROR_EDGE,ROT_ANG
	global OUT_DIR,OUT_FRONT_FILE,OUT_BACK_FILE,OUT_DRILL_FILE,OUT_EDGE_FILE,OUT_ALL_FILE
	global CUT_ALL_FRONT, CUT_ALL_BACK, CUT_STEP_R_FRONT,CUT_STEP_R_BACK, CUT_MAX_FRONT, CUT_MAX_BACK,CUT_MARGIN_R,PATTERN_SHIFT,DRILL_TYPE

	try:
		f = open(config_file,'r')
	except IOError, (errno, strerror):
		print "Unable to open the file =" + config_file + "\n"
	else:
		while 1:
			config = f.readline()
			if not config:
				break
			cfg = re.search("([A-Z\_]+)[\d\s\ ]*\=[\ \"\t]*([^\ \"\n\r]+)\"*",config)
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
				if(cfg.group(1)=="DRILL_Z_SPEED"):
					DRILL_Z_SPEED = int(cfg.group(2))
				if(cfg.group(1)=="DRILL_DEPTH"):
					DRILL_DEPTH = float(cfg.group(2))
				if(cfg.group(1)=="CUT_DEPTH"):
					CUT_DEPTH = float(cfg.group(2))
				if(cfg.group(1)=="TOOL_D"):
					TOOL_D = float(cfg.group(2))
				if(cfg.group(1)=="DRILL_D"):
					DRILL_D = float(cfg.group(2))
				if(cfg.group(1)=="EDGE_TOOL_D"):
					EDGE_TOOL_D = float(cfg.group(2))
				if(cfg.group(1)=="EDGE_DEPTH"):
					EDGE_DEPTH = float(cfg.group(2))
				if(cfg.group(1)=="EDGE_SPEED"):
					EDGE_SPEED = int(cfg.group(2))
				if(cfg.group(1)=="EDGE_Z_SPEED"):
					EDGE_Z_SPEED = int(cfg.group(2))
				if(cfg.group(1)=="Z_STEP"):
					Z_STEP = float(cfg.group(2))
				if(cfg.group(1)=="GERBER_COLOR"):
					GERBER_COLOR = str(cfg.group(2))
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
				if(cfg.group(1)=="GERBER_DIR"):
					GERBER_DIR = str(cfg.group(2))
				if(cfg.group(1)=="FRONT_FILE"):
					FRONT_FILE = str(cfg.group(2))
				if(cfg.group(1)=="BACK_FILE"):
					BACK_FILE = str(cfg.group(2))
				if(cfg.group(1)=="DRILL_FILE"):
					DRILL_FILE = str(cfg.group(2))
				if(cfg.group(1)=="EDGE_FILE"):
					EDGE_FILE = str(cfg.group(2))
				if(cfg.group(1)=="MIRROR_FRONT"):
					MIRROR_FRONT = int(cfg.group(2))
				if(cfg.group(1)=="MIRROR_BACK"):
					MIRROR_BACK = int(cfg.group(2))
				if(cfg.group(1)=="MIRROR_DRILL"):
					MIRROR_DRILL = int(cfg.group(2))
				if(cfg.group(1)=="MIRROR_EDGE"):
					MIRROR_EDGE = int(cfg.group(2))
				if(cfg.group(1)=="ROT_ANG"):
					ROT_ANG = float(cfg.group(2))
				if(cfg.group(1)=="OUT_DIR"):
					OUT_DIR = str(cfg.group(2))
				if(cfg.group(1)=="OUT_FRONT_FILE"):
					OUT_FRONT_FILE = str(cfg.group(2))
				if(cfg.group(1)=="OUT_BACK_FILE"):
					OUT_BACK_FILE = str(cfg.group(2))
				if(cfg.group(1)=="OUT_DRILL_FILE"):
					OUT_DRILL_FILE = str(cfg.group(2))
				if(cfg.group(1)=="OUT_EDGE_FILE"):
					OUT_EDGE_FILE = str(cfg.group(2))
				if(cfg.group(1)=="OUT_ALL_FILE"):
					OUT_ALL_FILE = str(cfg.group(2))
				if(cfg.group(1)=="CUT_ALL_FRONT"):
					CUT_ALL_FRONT = int(cfg.group(2))
				if(cfg.group(1)=="CUT_ALL_BACK"):
					CUT_ALL_BACK = int(cfg.group(2))
				if(cfg.group(1)=="CUT_STEP_R"):
					CUT_STEP_R = float(cfg.group(2))
				if(cfg.group(1)=="CUT_STEP_R_FRONT"):
					CUT_STEP_R_FRONT = float(cfg.group(2))
				if(cfg.group(1)=="CUT_STEP_R_BACK"):
					CUT_STEP_R_BACK = float(cfg.group(2))
				if(cfg.group(1)=="CUT_MAX_FRONT"):
					CUT_MAX_FRONT = int(cfg.group(2))
				if(cfg.group(1)=="CUT_MAX_BACK"):
					CUT_MAX_BACK = int(cfg.group(2))
				if(cfg.group(1)=="PATTERN_SHIFT"):
					PATTERN_SHIFT = int(cfg.group(2))
				if(cfg.group(1)=="DRILL_TYPE"):
					DRILL_TYPE = int(cfg.group(2))
				if(cfg.group(1)=="MCODE_FLAG"):
					MCODE_FLAG = int(cfg.group(2))

		f.close()
def drill2gcode(gcode_header,elements):
	z_step_n = int(DRILL_DEPTH/Z_STEP) + 1
	z_step = DRILL_DEPTH/z_step_n
	for elmt in elements:
		if len(elmt.points) < 2:
			#print "point"
			gcode_header.add_drill(DRILL_DEPTH,elmt.points[0], DRILL_Z_SPEED)
		else:
			j = 1
			while j <= z_step_n:
				z_depth = j*z_step
				gcode_header.add_path(z_depth,elmt.points, DRILL_SPEED, DRILL_Z_SPEED)
				j += 1
def edge2gcode(gcode_header,elements):
	z_step_n = int(EDGE_DEPTH/Z_STEP) + 1
	z_step = EDGE_DEPTH/z_step_n
	j = 1
	while j <= z_step_n:
		z_depth = j*z_step
		gcode_header.add_polygon(z_depth,elements, EDGE_SPEED, EDGE_Z_SPEED)
		j += 1
def disp_fig(header_raw,header_result):
	fig = pyplot.figure(1)
	ax = fig.add_subplot(111)
	for polygon in header_raw.elements:
		#print polygon.element.geom_type
		plot_coords(ax, polygon.element.exterior,'#999999')
	for polygon in header_result.elements:
		if polygon.active:
			if polygon.element.geom_type == 'Polygon':
				plot_coords(ax, polygon.element.exterior,'#FF0000')
			elif polygon.element.geom_type == 'MultiPolygon':
				for poly in polygon.element:
					plot_coords(ax, poly.exterior,'#FF0000')

	ax.set_title('Result')
	ax.set_aspect(1)
	unit = "mm"
	if OUT_UNIT == 25.4:
		unit = "inch"

	pyplot.xlabel(unit)
	pyplot.ylabel(unit)
	pyplot.show()

def plot_coords(ax, ob,plot_color):
    x, y = ob.xy
    ax.plot(x, y, '-', color=plot_color, zorder=1)
if __name__ == "__main__":
	main()
