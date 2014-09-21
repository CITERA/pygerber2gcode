#!/usr/bin/env python

#import os
#import sys
#import re
import gerber
import gcode
#import math
import gerber_shapely as gs

#for Display
from matplotlib import pyplot

def main():

	in_dir = "./gerber_data"
	out_dir = "./"

	filename = "xbee_test_usb1_1-Front.gtl"
	gcode_filename = "test_gerber.ngc"
	tool_d = 0.1
	#tool_d = 0.000
	gbr = gerber.Gerber(in_dir,filename)
	gop = gs.Gerber_OP(gbr,tool_d)
	print "gerber to shapely"
	gop.gerber2shapely()
	print "merge polygon"
	gop.merge_polygon()
	gop.get_minmax(gop.tmp_figs)
	#exit()
	#gop.mirror=True
	#gop.rot_ang=90.0
	#gop.affine()
	#
	disp_fig(gop.raw_figs,gop.figs)
	gop.fig_out()
	gcd = gcode.Gcode()
	height = -0.1
	xy_speed = 100
	z_speed = 60
	gcd.add_polygon(height,gop.out_figs.elements,xy_speed, z_speed)
	gcd.out(out_dir,gcode_filename)
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
	#if OUT_UNIT == 25.4:
	#	unit = "inch"

	pyplot.xlabel(unit)
	pyplot.ylabel(unit)
	pyplot.show()

def plot_coords(ax, ob,plot_color):
    x, y = ob.xy
    ax.plot(x, y, '-', color=plot_color, zorder=1)
if __name__ == "__main__":
	main()
