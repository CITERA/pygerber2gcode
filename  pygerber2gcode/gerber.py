#
#Gerber data manipulation
#
import os
import sys
import re
import math
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
		self.pre_x = 0
		self.pre_y = 0
		self.left = 0
		self.right = 1
		self.cut0 = self.left
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
			if (drill.find("FMAT") != -1):
				print "FMAT",drill
			if (drill.find("INCH") != -1):
				self.drill_unit = self.inch/self.out_unit
				if(drill.find("LZ") !=-1):
					#print "  L"
					self.cut0 = self.left
				elif(drill.find("TZ") !=-1):
					#print "  T"
					self.cut0 = self.right
			if (drill.find("METRIC") != -1):
				self.drill_unit = self.mm/self.out_unit
			if (drill.find("M72") != -1):
				self.drill_unit = self.inch/self.out_unit
			if (drill.find("M71") != -1):
				self.drill_unit = self.mm/self.out_unit

			drill_data = re.search("T([\d]+)C([\d\.]+)",drill)
			drill_num = re.search("T([\d]+)[^C\d]*",drill)
			if(drill_data):
				self.drill_types[int(drill_data.group(1))] = drill_data.group(2)
			if(drill_num):
				#print self.drill_types[int(drill_num.group(1))]
				#print int(drill_num.group(1))
				if int(drill_num.group(1)) > 0:
					self.drill_d=float(self.drill_types[int(drill_num.group(1))])*self.drill_unit
			xx = re.search("X([\d\.-]+)[^\d\.\-]*",drill)
			yy = re.search("Y([\d\.-]+)[^\d\.\-]*",drill)
			dd = re.search("D([\d]+)\D",drill)
			gg = re.search("G([\d]+)\D",drill)
			xy = re.search("X([\d\.-]+)Y([\d\.-]+)G([\d]+)X([\d\.-]+)Y([\d\.-]+)",drill)

			if (gg):
				self.parse_drill_g(gg.group(1),drill)

			if (not xy) and (not gg):
				x = self.pre_x
				y = self.pre_y
				if(xx):
					x=float(xx.group(1)) * self.drill_unit
					self.pre_x = x
				if(yy):
					y=float(yy.group(1)) * self.drill_unit
					self.pre_y = y
				if (xx) or (yy):
					self.drills.append(self.Drill(0,self.drill_d,(x,y)))


	def parse_drill_g(self,g_num,drill):
		g_num=int(g_num)

		#G
		if (g_num ==90):
			print "Absolute Mode"
		if (g_num ==5):
			print "Drill Mode"
		if (g_num ==85):
			print "slot"
			xy = re.search("X([\d\.-]+)Y([\d\.-]+)\D[\d]+X([\d\.-]+)Y([\d\.-]+)",drill)
			if(xy):
				x1=float(xy.group(1)) * self.drill_unit
				y1=float(xy.group(2)) * self.drill_unit
				x2=float(xy.group(3)) * self.drill_unit
				y2=float(xy.group(4)) * self.drill_unit
				self.drills.append(self.Drill(1,self.drill_d,(x1,y1),(x2,y2)))
		if (g_num ==0):
			print "G00:Route Mode is not supported:" + drill
		if (g_num ==1):
			print "G01:Linear (Straight Line) Mode is not supported:" + drill
		if (g_num ==2):
			print "G02:Circular CW Mode is not supported:" + drill
		if (g_num ==3):
			print "G03:Circular CCW Mode is not supported:" + drill
		if (g_num ==4):
			print "G04:X# Variable Dwell is not supported:" + drill
		if (g_num ==7):
			print "G07:Override current tool feed or speed is not supported:" + drill
		if (g_num ==32):
			print "G32:Routed Circle Canned Cycle is not supported:" + drill
		if (g_num ==33):
			print "G33:Routed Circle Canned Cycle is not supported:" + drill
		if (g_num ==34):
			print "G34:Select Vision Tool is not supported:" + drill
		if (g_num >=35):
			print "G35 and above are not supported:" + drill

	def parse_drill_g_old(self,drill):
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
		self.ii = 0
		self.jj = 0
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
		elif(self.cut0 == self.right):
			out_val = str(value)[0:i] + "." + str(value)[i:]
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
			#print line
			xx = re.search("X([\d\-]+)\D",line)
			yy = re.search("Y([\d\-]+)\D",line)
			dd = re.search("D([\d]+)\D",line)
			gg = re.search("G([\d]+)\D",line)
			ii = re.search("I([\d\-]+)\D",line)
			jj = re.search("J([\d\-]+)\D",line)
			x=self.pre_x
			y=self.pre_y

			#Find G
			if(gg):
				self.parse_g(gg.group(1))
			if (xx):
				x = xx.group(1)
				x = float(self.change_float(x)) * self.unit
				#self.pre_x = x
			if (yy):
				y = yy.group(1)
				y = float(self.change_float(y,1)) * self.unit
				#self.pre_y = y
			if (ii):
				i = ii.group(1)
				i = float(self.change_float(i)) * self.unit
				self.ii = i
			if (jj):
				j = jj.group(1)
				j = float(self.change_float(j,1)) * self.unit
				self.jj = j
			#Find D
			if (dd):
				d = dd.group(1)
				self.parse_d(d,x,y)
			else:
				#print int(self.pre_dnum)
				self.parse_d(self.pre_dnum,x,y)
			self.pre_x = x
			self.pre_y = y
			#Find %
			if(line.find("%") == 0):
				#print "% " + line
				self.parse_p(line)
			#Find M
			if(line.find("M") == 0):
				print "M comand is not supported:" + line
		if len(self.tmp_points) > 1:
			self.add_polygon(self.tmp_points)
			self.tmp_points = []
	def get_dnum(self,gerber):
		dnum = re.search("D([\d]+)\D",gerber)
		return dnum.group(1)

	def parse_g(self,g_num):
		g_num=int(g_num)
		self.arc_interpolation = 0
		#G10
		if (g_num ==10):
			print "G10 is not supported:"
			self.line_interpolation = 1
		#G11
		elif (g_num ==11):
			print "G11 is not supported:"
			self.line_interpolation = 1
		#G12
		elif (g_num ==12):
			print "G12 is not supported:"
			self.line_interpolation = 1
		#G36 polygon start
		elif (g_num ==36):
			#print "G36 is not supported:" + gerber
			self.polygon_sw = 1
			self.tmp_points = []
		#G37 polygon end
		elif (g_num ==37):
			#print "G37 is not supported:" + gerber
			if len(self.tmp_points) > 1:
				self.add_polygon(self.tmp_points)
				self.tmp_points = []
			self.polygon_sw = 0
		#G54 Select tool
		elif (g_num ==54):
			#print "54 is not supported:" + gerber
			#print "tool ID=" + str(get_dnum(gerber))
			#if len(self.tmp_points) > 1:
			#	self.add_polygon(self.tmp_points)
			#	self.tmp_points = []
			self.g54_sw = 1
			#tmp_aperture = str(self.get_dnum(gerber))
			#if(tmp_aperture):
			#	if (tmp_aperture != self.current_aperture):
			#		self.pre_aperture = self.current_aperture
			#		self.current_aperture = tmp_aperture
		#G70
		elif (g_num ==70):
			#print "70 is not supported:"
			#print "  Unit = INCH"
			self.unit = self.inch/self.out_unit
		#G71
		elif (g_num ==71):
			#print "71 is not supported:"
			#print "  Unit = MM"
			self.unit = self.mm/self.out_unit
		#G74
		elif (g_num ==74):
			#print "G74 is not supported:"
			self.arc_interpolation360 = 0
		#G75
		elif (g_num ==75):
			#print "G75 is not supported:"
			self.arc_interpolation360 = 1
		#G90
		elif (g_num ==90):
			#print "90 is not supported:"
			#print "   ABS"
			self.coor = self.abs
		#G91
		elif (g_num ==91):
			print "G91 (Incremental Mode) is not supported:"
			#print "91 is not supported:"
			#print "   relative"
			self.coor = self.rel
		#### 00
		#G01
		elif (g_num ==1):
			#print "G01 is not supported:"
			self.line_interpolation = 1
		#G02
		elif (g_num ==2):
			#print "G02 is not supported:"
			self.arc_interpolation = 1
			self.arc_dir = 0	#CW
		#G03
		elif (g_num ==3):
			#print "G03 is not supported:"
			self.arc_interpolation = 1
			self.arc_dir = 1	#CCW
		#G04	Comment 
		#elif (g_num ==04):
		#	print "Comment :" + gerber
			#nop
		#G00
		elif (g_num ==0):
			print "G00 is not supported:"
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
				print "  Incremental Mode is not supported:"
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
			self.g54_sw = 1
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
		#if int(self.current_aperture) in self.apertures:
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
		#self.pre_x = points[-1][0]
		#self.pre_y = points[-1][1]

	def parse_d(self,d,x,y):
		#self.arc_interpolation
		#self.arc_interpolation360
		#self.arc_dir
		if int(self.current_aperture) in self.apertures:
			#print gerber,self.current_aperture
			mod = self.apertures[int(self.current_aperture)].mod
			mod1 = float(mod[0]) * self.unit
			mod2 = 0
			if len(mod) > 1:
				mod2 = float(mod[1])*self.unit
		#Flash
		if(int(d) == 3):
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
			self.tmp_points = []
		#move
		elif(int(d) == 2):
			if len(self.tmp_points) > 1:
					self.add_polygon(self.tmp_points)
			self.tmp_points=[(x,y)]	#
		elif(int(d) == 1):	#Draw
			if (self.arc_interpolation):
				#print self.pre_x,x,self.pre_y,y
				r = math.sqrt(self.ii*self.ii+self.jj*self.jj)
				if (self.arc_interpolation360 and (self.pre_x == x and self.pre_y == y)):
					#circle
					#r = math.sqrt(self.ii*self.ii+self.jj*self.jj)
					self.figures.append(self.Circle(self.pre_x+self.ii,self.pre_y+self.jj,r))
					return
				#arc_points(c,r,sp,ep,ccw,kaku)
				#self.add_polygon(arc_points((self.pre_x+self.ii,self.pre_y+self.jj),r,(self.pre_x,self.pre_y),(x,y),self.arc_dir,20))
				self.tmp_points.extend(arc_points((self.pre_x+self.ii,self.pre_y+self.jj),r,(self.pre_x,self.pre_y),(x,y),self.arc_dir,20))
			else:
				self.tmp_points.append((x,y))
		else:	#Tool change
			if len(self.tmp_points) > 1:
				self.add_polygon(self.tmp_points)
				self.tmp_points = []
			self.g54_sw = 1
			if (d != self.current_aperture):
				self.pre_aperture = self.current_aperture
				self.current_aperture = d
		self.pre_dnum = d
def arc_points(c,r,sp,ep,ccw,kaku):
	points=[]
	start_angle = math.atan2(sp[1]-c[1],sp[0]-c[0])
	end_angle = math.atan2(ep[1]-c[1],ep[0]-c[0])
	if ccw:
		if start_angle < end_angle:
			ang_step=(end_angle-start_angle)/(kaku-1)
		else:
			ang_step=(end_angle+2*math.pi-start_angle)/(kaku-1)
	else:
		if start_angle < end_angle:
			ang_step=(end_angle-start_angle+2*math.pi)/(kaku-1)
		else:
			ang_step=(end_angle-start_angle)/(kaku-1)
	i = 0
	while i < kaku:
		arc_x=c[0]+r*math.cos(start_angle+ang_step*float(i))
		arc_y=c[1]+r*math.sin(start_angle+ang_step*float(i))
		points.append((arc_x,arc_y))
		i += 1
	return points
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
