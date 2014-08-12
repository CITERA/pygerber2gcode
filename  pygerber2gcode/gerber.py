#
#Gerber data manipulation
#
import os
import sys
import re
#from math import *
class Drill:
	#http://www.excellon.com/manuals/program.htm
	class Drill:
		def __init__(self, type, d, point1,point2=[]):
			self.type = type
			self.d = d
			self.point1 = point1
			self.point2 = point2
	def __init__(self, dir,filename,out_unit=1.0):
		self.dir = dir
		self.filename = filename
		#Set variables
		self.drill_types = {}
		self.drills = []
		self.drill_d = 0
		self.inch = 25.4
		self.mm = 1.0
		self.out_unit=out_unit
		self.drill_unit = self.mm/self.out_unit
		#Open file
		self.drill_lines = self.open_file()
		#Parse
		self.parse()
	def open_file(self):
		return open_file(self.dir, self.filename)
	def parse(self):
		print "Parse Drill data"
		#drill_d_unit = DRILL_UNIT
		for drill in self.drill_lines:
			if not drill:
				continue
			drill_data = re.search("T([\d]+)C([\d\.]+)",drill)
			drill_num = re.search("T([\d]+)[^C\d]*",drill)
			if(drill_data):
				self.drill_types[int(drill_data.group(1))] = drill_data.group(2)
			if(drill_num):
				#print self.drill_types[int(drill_num.group(1))]
				#print int(drill_num.group(1))
				if int(drill_num.group(1)) > 0:
					self.drill_d=float(self.drill_types[int(drill_num.group(1))])*self.drill_unit
			if (drill.find("G") != -1):
				self.parse_drill_g(drill)
			elif (drill.find("X") != -1 or drill.find("Y") != -1):
				self.parse_drill_xy(drill)
			if (drill.find("INCH") != -1):
				self.drill_unit = self.inch/self.out_unit
			if (drill.find("METRIC") != -1):
				self.drill_unit = self.mm/self.out_unit
			if (drill.find("M72") != -1):
				self.drill_unit = self.inch/self.out_unit
			if (drill.find("M71") != -1):
				self.drill_unit = self.mm/self.out_unit
	def parse_drill_g(self,drill):
		xy = re.search("X([\d\.-]+)Y([\d\.-]+)\D[\d]+X([\d\.-]+)Y([\d\.-]+)",drill)
		if(xy):
			x1=float(xy.group(1)) * self.drill_unit
			y1=float(xy.group(2)) * self.drill_unit
			x2=float(xy.group(3)) * self.drill_unit
			y2=float(xy.group(4)) * self.drill_unit
			self.drills.append(self.Drill(1,self.drill_d,(x1,y1),(x2,y2)))

	def parse_drill_xy(self,drill):
		xx = re.search("X([\d\.-]+)[^\d\.\-]*",drill)
		yy = re.search("Y([\d\.-]+)[^\d\.\-]*",drill)
		if(xx):
			x=float(xx.group(1)) * self.drill_unit
		if(yy):
			y=float(yy.group(1)) * self.drill_unit
		self.drills.append(self.Drill(0,self.drill_d,(x,y)))
class Gerber:
	class Aperture:
		def __init__(self, atype, mod):
			self.type = atype
			self.mod = mod
	class Path:
		def __init__(self, fig_type, w, points, polygon, active = 1):
			self.type = 0
			self.active = active
			self.fig_type = fig_type
			self.w = w
			self.polygon = polygon
			self.points = points
		def add_point(self,points):
			self.points.append(points)
	class Circle:
		def __init__(self, cx, cy, r, hole_w=0, hole_h=0, active = 1):
			self.type = 1
			self.cx = cx
			self.cy = cy
			self.r = r
			self.hole_w = hole_w
			self.hole_h = hole_h
			self.active = active
	class Rectangle:
		def __init__(self, x1 , y1, x2, y2, hole_w=0, hole_h=0, active = 1):
			self.type = 2
			self.x1 = x1
			self.y1 = y1
			self.x2 = x2
			self.y2 = y2
			self.hole_w = hole_w
			self.hole_h = hole_h
			self.active = active
	class Oval:
		def __init__(self, cx, cy, w, h, hole_w=0, hole_h=0, active = 1):
			self.type = 3
			self.cx = cx
			self.cy = cy
			self.w = w
			self.h = h
			self.hole_w = hole_w
			self.hole_h = hole_h
			self.active = active
	class Polygon:
		def __init__(self, r,sides,rot=0, hole_w=0, hole_h=0, active = 1):
			self.type = 4
			self.r = r
			self.sides = sides
			self.rot = rot
			self.hole_w = hole_w
			self.hole_h = hole_h
			self.active = active
	def __init__(self, dir,filename,out_unit=1.0):
		self.dir = dir
		self.filename = filename
		#Set variables
		#self.paths = []
		self.figures = []
		self.tmp_points = []
		self.apertures = {}
		self.pre_x = 0
		self.pre_y = 0
		self.inch = 25.4
		self.mm = 1.0
		self.abs = 0
		self.rel = 1
		self.out_unit = out_unit
		self.unit = self.inch/self.out_unit
		self.coor = self.abs
		self.pre_aperture = 0
		self.pre_dnum = 0
		self.current_aperture = self.pre_aperture
		self.polygon_sw = 0
		self.g54_sw = 0
		self.xi = 0
		self.xf = 0
		self.yi = 0
		self.yf = 0
		self.left = 0
		self.right = 1
		self.cut0 = self.left
		self.line_interpolation = 0
		self.arc_interpolation = 0
		self.arc_dir = 0
		self.arc_interpolation360 = 0
		#Open file
		self.gerber_lines = self.open_file()
		#Parse
		self.parse()
	def change_float(self,value,xory=0):
		i = int(self.xi)
		f = int(self.xf)
		if (xory):	#y
			i = int(self.yi)
			f = int(self.yf)
		if(self.cut0 == self.left):
			out_val = float(int(value))/(10**f)
			#if len(value) < 7:
			#out_val = str(value)[:-f]+ "." + str(value)[-f:]
			#tmp = float(str(value)[:-f]+ "." + str(value)[-f:])
			#if out_val != tmp:
				#print value,out_val,tmp,len(str(value))
		elif(self.cut0 == self.right):
			out_val = str(value)[0:i] + "." + str(value)[i:]
		#return float(out_val)
		return out_val
	def set_aperture(self, atype, mod):
		self.atype = atype
		self.mod = mod
	def get_aperture(self, aperture_line):
		dn = re.search("ADD([\d]+)([a-zA-Z]+)\,([X\d\.]+)*",aperture_line)
		if (dn):
			d_num = dn.group(1)
			aperture_type = dn.group(2)
			if(dn.group(3).find("X") != -1):
				mod = dn.group(3).split("X")
			else:
				mod = [dn.group(3)]
			#print "d_num =" + d_num
			#print "type =" + aperture_type
			#print "mod =", mod

			self.apertures[int(d_num)] = self.Aperture(aperture_type,mod)
		else:
			return
	def open_file(self):
		return open_file(self.dir, self.filename)

	def parse(self):
		print "Start Parse Gerber data"
		for line in self.gerber_lines:
			if not line:
				break
			#Find G
			if(line.find("G") == 0 or line.find("g") == 0):
				#print "G " + line
				self.parse_g(line)
			#Find %
			if(line.find("%") == 0):
				#print "% " + line
				self.parse_p(line)
			#Find M
			if(line.find("M") == 0):
				print "M comand is not supported:" + line
			if (line.find("X") == 0):
			#	print "X " + line
				self.parse_xy(line)
		if len(self.tmp_points) > 1:
			self.add_polygon(self.tmp_points)
			self.tmp_points = []
	def get_dnum(self,gerber):
		dnum = re.search("D([\d]+)\D",gerber)
		return dnum.group(1)
	def parse_g(self,gerber):
		#current_aperture = self.pre_aperture
		index_d = gerber.find("D")
		if index_d < 0:
			index_d = 3
		#index_ast = gerber.find("*")

		#G10
		if (gerber.find("10",1,index_d) !=-1):
			print "G10 is not supported:" + gerber
			self.line_interpolation = 1
		#G11
		elif (gerber.find("11",1,index_d) !=-1):
			print "G11 is not supported:" + gerber
			self.line_interpolation = 1
		#G12
		elif (gerber.find("12",1,index_d) !=-1):
			print "G12 is not supported:" + gerber
			self.line_interpolation = 1
		#G36 polygon start
		elif (gerber.find("36",1,index_d) !=-1):
			#print "G36 is not supported:" + gerber
			self.polygon_sw = 1
			self.tmp_points = []
		#G37 polygon end
		elif (gerber.find("37",1,index_d) !=-1):
			#print "G37 is not supported:" + gerber
			if len(self.tmp_points) > 1:
				self.add_polygon(self.tmp_points)
				self.tmp_points = []
			self.polygon_sw = 0
		#G54 Select tool
		elif (gerber.find("54",1,index_d) !=-1):
			#print "54 is not supported:" + gerber
			#print "tool ID=" + str(get_dnum(gerber))
			if len(self.tmp_points) > 1:
				self.add_polygon(self.tmp_points)
				self.tmp_points = []
			tmp_aperture = str(self.get_dnum(gerber))
			self.g54_sw = 1
			if(tmp_aperture):
				if (tmp_aperture != self.current_aperture):
					self.pre_aperture = self.current_aperture
					self.current_aperture = tmp_aperture
		#G70
		elif (gerber.find("70",1,index_d) !=-1):
			#print "70 is not supported:" + gerber
			#print "  Unit = INCH"
			self.unit = self.inch/self.out_unit
		#G71
		elif (gerber.find("71",1,index_d) !=-1):
			#print "71 is not supported:" + gerber
			#print "  Unit = MM"
			self.unit = self.mm/self.out_unit
		#G74
		elif (gerber.find("74",1,index_d) !=-1):
			print "G74 is not supported:" + gerber
			self.arc_interpolation360 = 0
		#G75
		elif (gerber.find("75",1,index_d) !=-1):
			print "G75 is not supported:" + gerber
			self.arc_interpolation360 = 1
		#G90
		elif (gerber.find("90",1,index_d) !=-1):
			#print "90 is not supported:" + gerber
			#print "   ABS"
			self.coor = self.abs
		#G91
		elif (gerber.find("91",1,index_d) !=-1):
			#print "91 is not supported:" + gerber
			#print "   relative"
			self.coor = self.rel
		#### 00
		#G01
		elif (gerber.find("01",1,index_d) !=-1):
			#print "G01 is not supported:" + gerber
			self.line_interpolation = 1
		#G02
		elif (gerber.find("02",1,index_d) !=-1):
			print "G02 is not supported:" + gerber
			self.arc_interpolation = 1
			self.arc_dir = 0
		#G03
		elif (gerber.find("03",1,index_d) !=-1):
			print "G03 is not supported:" + gerber
			self.arc_interpolation = 1
			self.arc_dir = 1
		#G04	Comment 
		elif (gerber.find("04",1,index_d) !=-1):
			print "Comment :" + gerber
			#nop
		#G00
		elif (gerber.find("00",1,index_d) !=-1):
			print "G00 is not supported:" + gerber
		#else:
			#g54_FLAG = 0
	def parse_p(self,gerber):
		#index_ast = gerber.find("*")
		index_d = 3
		#AS
		if (gerber.find("AS",1,index_d) !=-1):
			print "AS is not supported:" + gerber
		#FS (Format Statement)
		elif (gerber.find("FS",1,index_d) !=-1):
			#print "FS is not supported:" + gerber
			if(gerber.find("L",3,4) !=-1):
				#print "  L"
				self.cut0 = self.left
			elif(gerber.find("T",3,4) !=-1):
				#print "  T"
				self.cut0 = self.right
			if(gerber.find("A",4,5) !=-1):
				#print "  A"
				self.coor = self.abs
			elif(gerber.find("I",4,5) !=-1):
				#print "  I"
				self.coor = self.rel
			fsx = re.search("X([\d]+)\D",gerber)
			fsy = re.search("Y([\d]+)\D",gerber)
			if (fsx):
				x = fsx.group(1)
				self.xi = x[0]
				self.xf = x[1]
				#print "    X_int = " + self.xi
				#print "    X_float = " + self.xf
			if (fsy):
				y = fsy.group(1)
				self.yi = y[0]
				self.yf = y[1]
				#print "    Y_int = " + self.yi
				#print "    Y_float = " + self.yf
		#MI
		elif (gerber.find("MI",1,index_d) !=-1):
			print "MI is not supported:" + gerber
		#MO (Mode of units)
		elif (gerber.find("MO",1,index_d) !=-1):
			#print "MO is not supported:" + gerber
			if(gerber.find("IN",3,5) !=-1):
				print "  Unit = INCH"
				self.unit = self.inch/self.out_unit
			elif(gerber.find("MM",3,5) !=-1):
				print "  Unit = MM"
				self.unit = self.mm/self.out_unit
		#OF
		elif (gerber.find("OF",1,index_d) !=-1):
			print "OF is not supported:" + gerber
		#SF
		elif (gerber.find("SF",1,index_d) !=-1):
			#print "SF is not supported:" + gerber
			g54_FLAG = 1
		#IJ
		elif (gerber.find("IJ",1,index_d) !=-1):
			print "IJ is not supported:" + gerber
		#IN
		elif (gerber.find("IN",1,index_d) !=-1):
			print "IN is not supported:" + gerber
		#IO
		elif (gerber.find("IO",1,index_d) !=-1):
			print "IO is not supported:" + gerber
		#IP
		elif (gerber.find("IP",1,index_d) !=-1):
			print "IP is not supported:" + gerber
		#IR
		elif (gerber.find("IR",1,index_d) !=-1):
			print "IR is not supported:" + gerber
		#AD (Aperture Definition)
		elif (gerber.find("AD",1,index_d) !=-1):
			#print "AD is not supported:" + gerber
			self.get_aperture(gerber)
			#print "tool ID=" + str(get_dnum(gerber))
		#AM (Aperture Macro)
		elif (gerber.find("AM",1,index_d) !=-1):
			print "AM is not supported:" + gerber
		#KO
		elif (gerber.find("KO",1,index_d) !=-1):
			print "KO is not supported:" + gerber
		#LN
		elif (gerber.find("LN",1,index_d) !=-1):
			print "LN is not supported:" + gerber
		#LP
		elif (gerber.find("LP",1,index_d) !=-1):
			print "LP is not supported:" + gerber
		#SR
		elif (gerber.find("SR",1,index_d) !=-1):
			print "SR is not supported:" + gerber
		#IF (Include File)
		elif (gerber.find("IF",1,index_d) !=-1):
			print "IF is not supported:" + gerber
		#else:
			#nop
	def add_polygon(self,points):
		mod1 = float(self.apertures[int(self.current_aperture)].mod[0])*self.unit
		if len(self.apertures[int(self.current_aperture)].mod) > 1:
			mod2 = float(self.apertures[int(self.current_aperture)].mod[1])*self.unit
		if(self.apertures[int(self.current_aperture)].type == "C"):
			#Circle (type, w, points, active = 1)
			self.figures.append(self.Path(0,mod1, points, self.polygon_sw))
		elif(self.apertures[int(self.current_aperture)].type == "R"):
			#Rect
			self.figures.append(self.Path(1,mod2,points, self.polygon_sw))
		elif(self.apertures[int(self.current_aperture)].type == "O"):
			#Oval
			self.figures.append(self.Path(2,mod2,points, self.polygon_sw))
		elif(self.apertures[int(self.current_aperture)].type ==  "P"):
			#Polygon
			self.figures.append(self.Path(3,mod1,points, self.polygon_sw))
		self.pre_x = points[-1][0]
		self.pre_y = points[-1][1]

	def parse_xy(self, gerber):
		d=0
		xx = re.search("X([\d\-]+)\D",gerber)
		yy = re.search("Y([\d\-]+)\D",gerber)
		dd = re.search("D([\d]+)\D",gerber)
		mod = self.apertures[int(self.current_aperture)].mod
		mod1 = float(mod[0]) * self.unit
		mod2 = 0
		if len(mod) > 1:
			mod2 = float(mod[1])*self.unit
		if (xx):
			x = int(xx.group(1))
			x = float(self.change_float(x)) * self.unit
			if (x != self.pre_x):
				self.pre_x = x
		if (yy):
			y = int(yy.group(1))
			y = float(self.change_float(y,1)) * self.unit
			if (y != self.pre_y):
				self.pre_y = y
		if (dd):
			d = dd.group(1)
			#Flash
			if(d == "03" or d == "3"):
				if(self.apertures[int(self.current_aperture)].type == "C"):
					#Circle(cx, cy, r, hole_w=0, hole_h=0, active = 1):
					self.figures.append(self.Circle(x,y,mod1/2))
				elif(self.apertures[int(self.current_aperture)].type ==  "R"):
					#Rectangle:(x1 , y1, x2, y2, hole_w=0, hole_h=0, active = 1):
					#self.figures.append(self.Rectangle(x-mod1/2,y,x+mod1/2,y))
					self.figures.append(self.Rectangle(x-mod1/2,y-mod2/2,x+mod1/2,y+mod2/2))
				elif(self.apertures[int(self.current_aperture)].type == "O"):
					#Oval(cx, cy, w, h, hole_w=0, hole_h=0, active = 1):
					self.figures.append(self.Oval(x,y,mod1,mod2))
				elif(self.apertures[int(self.current_aperture)].type ==  "P"):
					#Polygon(d,sides,rot=0, hole_w=0, hole_h=0, active = 1)
					self.figures.append(self.Polygon(mod1/2,mod2))
				self.pre_x = x
				self.pre_y = y
			#move
			elif(d == "02" or d == "2"):
				self.pre_x = x
				self.pre_y = y	
				if len(self.tmp_points) > 1:
						self.add_polygon(self.tmp_points)
				self.tmp_points=[(x,y)]
			elif(d == "01" or d == "1"):
				self.tmp_points.append((x,y))
			self.pre_dnum = d
		#if (self.g54_sw):
			#print "parse data"
			#self.parse_data(x,y,d)

def open_file(dirname, filename):
	file_name = os.path.join(dirname, filename)
	try:
		f = open(file_name,'r')
	except IOError, (errno, strerror):
		print "Unable to open the file" + file_name + "\n"
		return []
	else:
		ret = f.read()
		return ret.split("\n")
