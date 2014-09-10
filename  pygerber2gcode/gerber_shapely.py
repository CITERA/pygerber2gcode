from shapely.geometry import Point,LineString,LinearRing,Polygon,MultiPolygon,box
from shapely.geometry.polygon import orient
from shapely.ops import cascaded_union
from shapely.ops import linemerge
from shapely import affinity

class Gerber_OP:
	def __init__(self, gerber, tool_d=0):
		#self.tiny = 1e-6
		self.tiny_ang = 1e-2	#deg
		self.huge = 1e6
		self.xoff = 0.0
		self.yoff = 0.0
		self.xmin = 0
		self.ymin = 0
		self.xmax = 0
		self.ymax = 0
		self.mirror = False
		self.rot_ang = 0
		self.center = (0,0,0)
		self.figs = self.Figure()
		self.tmp_figs = self.Figure()
		self.out_figs = self.Figure()
		self.draw_figs = self.Figure()
		self.raw_figs = self.Figure()
		self.gerber = gerber
		self.in_unit = 25.4
		self.out_unit = 1.0
		self.invalid_polygons= []
		self.tool_d = tool_d
		self.tool_r = float(tool_d)/2.0
		self.circle_ang = 20
		self.drill_circle_ang = 20
		self.drill_asobi = tool_d/10.0
	class Polygon_shape:
		def __init__(self, points, active = 1,fig_type=0,r=0):
			self.element = Polygon(points)
			self.active = active
			self.fig_type = fig_type
			self.r = r
	class Figs:
		#def __init__(self, element, active = 1,fig_type=0,r=0):
		def __init__(self, element, active = 1):
			self.element = element
			self.active = active
	class Polygon:
		def __init__(self, points, active = 1):
			self.points = points
			self.active = active
	class Figure:
		def __init__(self):
			self.elements = []
		def add(self,element):
			self.elements.append(element)
	def drill2shapely(self):
		for drl in self.gerber.drills:
			if(drl.type > 1):
				continue
			if drl.type == 0:
				if drl.d > self.tool_d:
					#print "lager than drill d", drl.d,self.tool_d
					self.figs.add(self.Figs(Point(drl.point1).buffer(float(drl.d)/2.0-float(self.tool_d)/2.0+self.drill_asobi,resolution=self.drill_circle_ang)))
					self.raw_figs.add(self.Figs(Point(drl.point1).buffer(float(drl.d)/2.0,resolution=self.drill_circle_ang)))
				else:
					self.figs.add(self.Figs(Point(drl.point1)))
					self.raw_figs.add(self.Figs(Point(drl.point1).buffer(float(self.tool_d)/2.0,resolution=self.drill_circle_ang)))
			elif drl.type == 1:
				if drl.d > self.tool_d:
					#print "lager than drill d", drl.d,self.tool_d
					self.figs.add(self.Figs(LineString(drl.point1,drl.point2).buffer(float(drl.d)/2.0-float(self.tool_d)/2.0+self.drill_asobi,resolution=self.drill_circle_ang)))
					self.raw_figs.add(self.Figs(LineString(drl.point1,drl.point2).buffer(float(drl.d)/2.0,resolution=self.drill_circle_ang)))
				else:
					self.figs.add(self.Figs(LineString(drl.point1,drl.point2)))
					self.raw_figs.add(self.Figs(LineString(drl.point1,drl.point2).buffer(float(self.tool_d)/2.0,resolution=self.drill_circle_ang)))
	def edge2shapely(self):
		for gbr in self.gerber.figures:
			if(gbr.active < 1):
				continue
			if(gbr.type > 4):
				continue
			if(gbr.type == 0):	#Path or Polygon
				#print gbr.w
				if gbr.polygon:
					self.figs.add(self.Figs(Polygon(gbr.points)))
					self.raw_figs.add(self.Figs(Polygon(gbr.points)))
				else:
					if LineString(gbr.points).is_simple:
						self.figs.add(self.Figs(LineString(gbr.points)))
						self.raw_figs.add(self.Figs(LineString(gbr.points)))
			elif(gbr.type == 1):
				#Circle
				self.figs.add(self.Figs(Point(gbr.cx,gbr.cy).buffer(float(gbr.r)+self.tool_r,resolution=self.circle_ang)))
				self.raw_figs.add(self.Figs(Point(gbr.cx,gbr.cy).buffer(float(gbr.r),resolution=self.circle_ang)))
			elif(gbr.type == 2):
				#Rectangle
				points = [(gbr.x1-self.tool_r,gbr.y1-self.tool_r),(gbr.x1-self.tool_r,gbr.y2+self.tool_r),
					(gbr.x2+self.tool_r,gbr.y2+self.tool_r),(gbr.x2+self.tool_r,gbr.y1-self.tool_r),
					(gbr.x1-self.tool_r,gbr.y1-self.tool_r)]
				self.figs.add(self.Figs(Polygon(points)))
				points = [(gbr.x1,gbr.y1),(gbr.x1,gbr.y2),(gbr.x2,gbr.y2),(gbr.x2gbr.y1),(gbr.x1,gbr.y1)]
				self.raw_figs.add(self.Figs(Polygon(points)))
			elif(gbr.type == 3):
				#Oval
				if gbr.h <= gbr.w:
					tmp_r = gbr.h/2.0+self.tool_r
					shift_x = (gbr.w-gbr.h)/2.0
					self.figs.add(self.Figs(LineString([(gbr.cx-shift_x,gbr.cy),(gbr.cx+shift_x,gbr.cy)]).buffer(tmp_r)))
					tmp_r = gbr.h/2.0
					shift_x = (gbr.w-gbr.h)/2.0
					self.raw_figs.add(self.Figs(LineString([(gbr.cx-shift_x,gbr.cy),(gbr.cx+shift_x,gbr.cy)]).buffer(tmp_r)))
				else:
					tmp_r = gbr.w/2.0+self.tool_r
					shift_y = (gbr.h-gbr.w)/2.0
					self.figs.add(self.Figs(LineString([(gbr.cx,gbr.cy-shift_y),(gbr.cx,gbr.cy+shift_y)]).buffer(tmp_r)))
					tmp_r = gbr.w/2.0
					shift_y = (gbr.h-gbr.w)/2.0
					self.raw_figs.add(self.Figs(LineString([(gbr.cx,gbr.cy-shift_y),(gbr.cx,gbr.cy+shift_y)]).buffer(tmp_r)))
			elif(gbr.type == 4):
				#Polygon
				self.figs.add(self.Figs(Point(gbr.cx,gbr.cy).buffer(float(gbr.r)+self.tool_r,resolution=gbr.sides)))
				self.raw_figs.add(self.Figs(Point(gbr.cx,gbr.cy).buffer(float(gbr.r)+self.tool_r,resolution=gbr.sides)))

	def gerber2shapely(self):
		for gbr in self.gerber.figures:
			if(gbr.active < 1):
				continue
			if(gbr.type > 4):
				continue
			if(gbr.type == 0):	#Path or Polygon
				if gbr.fig_type == 0:	#Circle
					cap_s=1
				elif gbr.fig_type == 1:	#Rectangle
					cap_s=3
				else:
					cap_s=1
				if gbr.polygon:
					tmp_polygon = Polygon(gbr.points)
					self.tmp_figs.add(self.Figs(tmp_polygon.buffer(float(gbr.w)/2.0+self.tool_r, cap_style=cap_s)))
					raw_polygon = tmp_polygon.buffer(float(gbr.w)/2.0, cap_style=cap_s)
					self.raw_figs.add(self.Figs(raw_polygon))
					if raw_polygon.interiors:
						for interior in raw_polygon.interiors:
							self.raw_figs.add(self.Figs(Polygon(interior)))
				else:
					self.tmp_figs.add(self.Figs(LineString(gbr.points).buffer(float(gbr.w)/2.0+self.tool_r, cap_style=cap_s)))
					self.raw_figs.add(self.Figs(LineString(gbr.points).buffer(float(gbr.w)/2.0, cap_style=cap_s)))
			elif(gbr.type == 1):
				#Circle
				self.tmp_figs.add(self.Figs(Point(gbr.cx,gbr.cy).buffer(float(gbr.r)+self.tool_r,resolution=self.circle_ang)))
				self.raw_figs.add(self.Figs(Point(gbr.cx,gbr.cy).buffer(float(gbr.r),resolution=self.circle_ang)))
			elif(gbr.type == 2):
				#Rectangle
				points = [(gbr.x1-self.tool_r,gbr.y1-self.tool_r),(gbr.x1-self.tool_r,gbr.y2+self.tool_r),
					(gbr.x2+self.tool_r,gbr.y2+self.tool_r),(gbr.x2+self.tool_r,gbr.y1-self.tool_r),
					(gbr.x1-self.tool_r,gbr.y1-self.tool_r)]
				self.tmp_figs.add(self.Figs(Polygon(points)))
				points = [(gbr.x1,gbr.y1),(gbr.x1,gbr.y2),(gbr.x2,gbr.y2),(gbr.x2,gbr.y1),(gbr.x1,gbr.y1)]
				self.raw_figs.add(self.Figs(Polygon(points)))
			elif(gbr.type == 3):
				#Oval
				if gbr.h <= gbr.w:
					tmp_r = gbr.h/2.0+self.tool_r
					shift_x = (gbr.w-gbr.h)/2.0
					self.tmp_figs.add(self.Figs(LineString([(gbr.cx-shift_x,gbr.cy),(gbr.cx+shift_x,gbr.cy)]).buffer(tmp_r)))
					self.raw_figs.add(self.Figs(LineString([(gbr.cx-shift_x,gbr.cy),(gbr.cx+shift_x,gbr.cy)]).buffer(gbr.h/2.0)))
				else:
					tmp_r = gbr.w/2.0+self.tool_r
					shift_y = (gbr.h-gbr.w)/2.0
					self.tmp_figs.add(self.Figs(LineString([(gbr.cx,gbr.cy-shift_y),(gbr.cx,gbr.cy+shift_y)]).buffer(tmp_r)))
					self.raw_figs.add(self.Figs(LineString([(gbr.cx,gbr.cy-shift_y),(gbr.cx,gbr.cy+shift_y)]).buffer(gbr.w/2.0)))
			elif(gbr.type == 4):
				#Polygon
				self.tmp_figs.add(self.Figs(Point(gbr.cx,gbr.cy).buffer(float(gbr.r)+self.tool_r,resolution=gbr.sides)))
				self.raw_figs.add(self.Figs(Point(gbr.cx,gbr.cy).buffer(float(gbr.r),resolution=gbr.sides)))

	def merge_polygon(self):
		merge = []
		for elmt in self.tmp_figs.elements:
			if elmt.active == 0:
				continue
			if elmt.element.is_empty:
				continue
			if elmt.element.geom_type == 'Polygon':
				merge.append(elmt.element)
			elif elmt.element.geom_type == 'MultiPolygon':
				for polygon in elmt.element:
					merge.append(polygon)
		tmp = cascaded_union(merge)
		if tmp.geom_type=='MultiPolygon':
			for poly in tmp:
				if poly.is_valid:
 					self.figs.add(self.Figs(poly))
				#else:
				#	print "Invalid"
				if poly.interiors:
					for inter in poly.interiors:
					 self.figs.add(self.Figs(Polygon(inter)))
		elif tmp.geom_type=='Polygon':
			self.figs.add(self.Figs(tmp))
			if tmp.interiors:
				for inter in tmp.interiors:
				 self.figs.add(self.Figs(Polygon(inter)))

	def merge_line(self):
		lines=[]
		for elmt in self.figs.elements:
			if elmt.active == 0:
				continue
			if elmt.element.geom_type=='LineString':
				lines.append(elmt.element)
				elmt.active = 0
			elif elmt.element.geom_type=='MultiLineString':
				lines.extend(elmt.element)
				elmt.active = 0
		if len(lines) > 0:
			self.figs.add(self.Figs(linemerge(lines)))
		else:
			print "no lines merged"

	def count_active_figs(self):
		i=0
		for elmt in self.figs.elements:
			if elmt.element.is_empty:
				continue
			if elmt.active:
				i+=1
		return i

	def limit_cut(self,maxx,maxy,minx,miny):
		limit=box(minx, miny, maxx, maxy, ccw=True)
		for elmt in self.figs.elements:
			if elmt.element.is_empty:
				continue
			if elmt.active:
				elmt.element=limit.intersection(elmt.element)
	def affine(self):
		for elmt in self.figs.elements:
			if elmt.element.is_empty:
				continue
			if elmt.active:
				if self.mirror:
					elmt.element=affinity.scale(elmt.element, xfact=1, yfact=-1,origin=self.center)
				if abs(self.rot_ang) > self.tiny_ang:
					elmt.element=affinity.rotate(elmt.element, self.rot_ang,origin=self.center)
				if abs(self.xoff) > 0.0 or abs(self.yoff) > 0.0:
					elmt.element=affinity.translate(elmt.element, xoff=self.xoff, yoff=self.yoff)
	def affine_trans(self,header):
		for elmt in header.elements:
			if elmt.element.is_empty:
				continue
			if elmt.active:
				if self.mirror:
					elmt.element=affinity.scale(elmt.element, xfact=1, yfact=-1,origin=self.center)
				if abs(self.rot_ang) > self.tiny_ang:
					elmt.element=affinity.rotate(elmt.element, self.rot_ang,origin=self.center)
				if abs(self.xoff) > 0.0 or abs(self.yoff) > 0.0:
					elmt.element=affinity.translate(elmt.element, xoff=self.xoff, yoff=self.yoff)
	def get_minmax(self,handler):
		self.xmin = self.huge
		self.ymin = self.huge
		self.xmax = -self.huge
		self.ymax = -self.huge
		for elmt in handler.elements:
			if elmt.element.is_empty:
				continue
			if elmt.active:
				minx, miny, maxx, maxy=elmt.element.bounds
				if minx < self.xmin:
					self.xmin=minx
				if miny < self.ymin:
					self.ymin=miny
				if maxx > self.xmax:
					self.xmax=maxx
				if maxy > self.ymax:
					self.ymax=maxy

		self.center=((self.xmax+self.xmin)/2.0,(self.ymax+self.ymin)/2.0,0)

	def draw_out(self):
		for elmt in self.raw_figs.elements:
			if elmt.element.is_empty:
				continue
			if elmt.active:
				if elmt.element.geom_type == 'MultiLineString':
					for sub_elmt in elmt.element:
						self.draw_figs.add(self.Polygon(sub_elmt.coords))
				elif elmt.element.geom_type == 'LineString':
					self.draw_figs.add(self.Polygon(elmt.element.coords))
				elif elmt.element.geom_type == 'LinearRing':
					self.draw_figs.add(self.Polygon(elmt.element.coords))
				elif elmt.element.geom_type == 'MultiPolygon':
					for sub_elmt in elmt.element:
						self.draw_figs.add(self.Polygon(list(sub_elmt.exterior.coords)))

				elif elmt.element.geom_type == 'Polygon':
					self.draw_figs.add(self.Polygon(list(elmt.element.exterior.coords)))
				elif elmt.element.geom_type == 'Point':
					self.draw_figs.add(self.Polygon(list(elmt.element.coords)))

	def fig_out(self):
		for elmt in self.figs.elements:
			if elmt.element.is_empty:
				continue
			if elmt.active:
				if elmt.element.geom_type == 'MultiLineString':
					for sub_elmt in elmt.element:
						self.out_figs.add(self.Polygon(sub_elmt.coords))
				elif elmt.element.geom_type == 'LineString':
					self.out_figs.add(self.Polygon(elmt.element.coords))
				elif elmt.element.geom_type == 'LinearRing':
					self.out_figs.add(self.Polygon(elmt.element.coords))
				elif elmt.element.geom_type == 'MultiPolygon':
					for sub_elmt in elmt.element:
						self.out_figs.add(self.Polygon(list(sub_elmt.exterior.coords)))
				elif elmt.element.geom_type == 'Polygon':
					self.out_figs.add(self.Polygon(list(elmt.element.exterior.coords)))
				elif elmt.element.geom_type == 'Point':
					self.out_figs.add(self.Polygon(list(elmt.element.coords)))

