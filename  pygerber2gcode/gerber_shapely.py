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
		def __init__(self, element, active = 1,fig_type=0,r=0):
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
				#print gbr.w
				if gbr.fig_type == 0:	#Circle
					cap_s=1
				elif gbr.fig_type == 1:	#Rectangle
					cap_s=3
				else:
					cap_s=1
				if gbr.polygon:
					tmp_polygon = Polygon(gbr.points)
					#print "Polygon",len(gbr.points)
					self.raw_figs.add(self.Figs(tmp_polygon))
					if tmp_polygon.is_valid:
						#print "valid polygon"
						self.figs.add(self.Figs(tmp_polygon.buffer(float(gbr.w)/2.0+self.tool_r, cap_style=cap_s)))
					else:
						#print "invalid polygon"
						self.invalid_polygons.append(self.Polygon_shape(gbr.points,r=float(gbr.w)/2.0+self.tool_r,fig_type=gbr.fig_type))
						for ring in tmp_polygon.buffer(float(gbr.w)/2.0, cap_style=cap_s).interiors:
							self.raw_figs.add(self.Figs(Polygon(ring)))
				else:
					if LineString(gbr.points).is_simple:
						self.figs.add(self.Figs(LineString(gbr.points).buffer(float(gbr.w)/2.0+self.tool_r, cap_style=cap_s)))
						self.raw_figs.add(self.Figs(LineString(gbr.points).buffer(float(gbr.w)/2.0, cap_style=cap_s)))
					else:
						self.raw_figs.add(self.Figs(LineString(gbr.points).buffer(float(gbr.w)/4.0, cap_style=cap_s)))

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
				points = [(gbr.x1,gbr.y1),(gbr.x1,gbr.y2),(gbr.x2,gbr.y2),(gbr.x2,gbr.y1),(gbr.x1,gbr.y1)]
				self.raw_figs.add(self.Figs(Polygon(points)))
			elif(gbr.type == 3):
				#Oval
				if gbr.h <= gbr.w:
					tmp_r = gbr.h/2.0+self.tool_r
					shift_x = (gbr.w-gbr.h)/2.0
					self.figs.add(self.Figs(LineString([(gbr.cx-shift_x,gbr.cy),(gbr.cx+shift_x,gbr.cy)]).buffer(tmp_r)))
					self.raw_figs.add(self.Figs(LineString([(gbr.cx-shift_x,gbr.cy),(gbr.cx+shift_x,gbr.cy)]).buffer(gbr.h/2.0)))
				else:
					tmp_r = gbr.w/2.0+self.tool_r
					shift_y = (gbr.h-gbr.w)/2.0
					self.figs.add(self.Figs(LineString([(gbr.cx,gbr.cy-shift_y),(gbr.cx,gbr.cy+shift_y)]).buffer(tmp_r)))
					self.raw_figs.add(self.Figs(LineString([(gbr.cx,gbr.cy-shift_y),(gbr.cx,gbr.cy+shift_y)]).buffer(gbr.h/2.0)))
			elif(gbr.type == 4):
				#Polygon
				self.figs.add(self.Figs(Point(gbr.cx,gbr.cy).buffer(float(gbr.r)+self.tool_r,resolution=gbr.sides)))
				self.raw_figs.add(self.Figs(Point(gbr.cx,gbr.cy).buffer(float(gbr.r),resolution=gbr.sides)))
	def merge_polygon(self):
		polygons =[]
		for elmt in self.figs.elements:
			if elmt.active == 0:
				continue
			if elmt.element.is_empty:
				continue
			if elmt.element.geom_type == 'Polygon':
				if elmt.element.is_valid:
					polygons.append(elmt.element)
					elmt.active = 0
				#else:
					#print "invaild"
			elif elmt.element.geom_type == 'MultiPolygon':
				polygons.extend(elmt.element.geoms)
				elmt.active = 0

		tmp_polygon = cascaded_union(polygons)
		if tmp_polygon.geom_type == 'Polygon':
			self.tmp_figs.add(self.Figs(tmp_polygon))
		elif tmp_polygon.geom_type == 'MultiPolygon':
			for polygon in tmp_polygon:
				self.tmp_figs.add(self.Figs(polygon))

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

	def diff_polygon_multi(self):
		tmp_inv_poly = []
		for i in range(len(self.invalid_polygons)):
			polygon_ex = Polygon(self.invalid_polygons[i].element.buffer(self.invalid_polygons[i].r).exterior)
			for polygon in self.tmp_figs.elements:
				if self.invalid_polygons[i].element.intersects(polygon.element):
					polygon.active = 0
					polygon_ex = polygon_ex.union(polygon.element)
				elif polygon_ex.intersects(polygon.element):
					if not polygon_ex.contains(polygon.element):
						polygon.active = 0
						polygon_ex = polygon_ex.union(polygon.element)
			tmp_inv_poly.append(polygon_ex)
		inv_poly_flag = [0] * len(self.invalid_polygons)
		for j in range(len(self.invalid_polygons)):
			inv_poly_flag[j] = True
			for ring in self.invalid_polygons[j].element.buffer(self.invalid_polygons[j].r).interiors:
				ring_polygon = Polygon(ring)
				ring_flag = True
				for i in range(len(self.invalid_polygons)):
					if i==j:
						continue
					if tmp_inv_poly[j].contains(self.invalid_polygons[i].element):
						if ring_polygon.contains(tmp_inv_poly[i]):
							continue
						if tmp_inv_poly[i].intersects(ring_polygon):
							ring_polygon = ring_polygon.difference(tmp_inv_poly[i])
							inv_poly_flag[i] = False
				for polygon in self.tmp_figs.elements:
					if ring_polygon.intersects(polygon.element):
						if ring_polygon.contains(polygon.element):
							continue
						if ring_polygon.within(polygon.element):
							ring_flag = False
							continue
						tmp_polygon = ring_polygon.difference(polygon.element)
						if tmp_polygon.is_empty:
							continue
						ring_flag=True
						ring_polygon = tmp_polygon
						polygon.active = 0

				if ring_flag:
					self.figs.add(self.Figs(ring_polygon))
		for i in range(len(self.invalid_polygons)):
			if inv_poly_flag[i]:
				self.figs.add(self.Figs(tmp_inv_poly[i]))
		for fig in self.tmp_figs.elements:
			self.figs.add(fig)

	def diff_polygon(self):
		in_flag=[]
		print "inv_poly_num =",len(self.invalid_polygons)
		for invalid_polygon in self.invalid_polygons:
			polygon_ex = Polygon(invalid_polygon.element.buffer(invalid_polygon.r).exterior)
			for i in range(len(self.tmp_figs.elements)):
				in_flag.append(False)
				if polygon_ex.intersects(self.tmp_figs.elements[i].element):
					if polygon_ex.contains(self.tmp_figs.elements[i].element):
						in_flag[-1]=True
						continue
					if polygon_ex.within(self.tmp_figs.elements[i].element):
						self.tmp_figs.elements[i].active = 0
						continue
					polygon_ex=polygon_ex.union(self.tmp_figs.elements[i].element)
					self.tmp_figs.elements[i].active = 0
			self.figs.add(self.Figs(polygon_ex))	
			for ring in invalid_polygon.element.buffer(invalid_polygon.r).interiors:
				ring_polygon = Polygon(ring)
				ring_flag = True
				for i in range(len(self.tmp_figs.elements)):
					if ring_polygon.intersects(self.tmp_figs.elements[i].element):
						if ring_polygon.contains(self.tmp_figs.elements[i].element):
							in_flag[i] = False
							continue
						if ring_polygon.within(self.tmp_figs.elements[i].element):
							self.tmp_figs.elements[i].active = 0
							ring_flag = False
							continue
						#
						tmp_polygon = ring_polygon.difference(self.tmp_figs.elements[i].element)
						if tmp_polygon.is_empty:
							print "empty"
							continue
						ring_polygon = tmp_polygon
						self.tmp_figs.elements[i].active = 0
						ring_flag=True
				if ring_flag:
					self.figs.add(self.Figs(ring_polygon))
		for i in range(len(self.tmp_figs.elements)):
			if not in_flag[i]:
				self.figs.add(self.tmp_figs.elements[i])
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
	def get_minmax(self):
		self.xmin = self.huge
		self.ymin = self.huge
		self.xmax = -self.huge
		self.ymax = -self.huge
		for elmt in self.figs.elements:
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
					#print "multi polygon"
					for sub_elmt in elmt.element:
						self.draw_figs.add(self.Polygon(list(sub_elmt.exterior.coords)))
				elif elmt.element.geom_type == 'Polygon':
					self.draw_figs.add(self.Polygon(list(elmt.element.exterior.coords)))
				elif elmt.element.geom_type == 'Point':
					#print "Point"
					self.draw_figs.add(self.Polygon(list(elmt.element.coords)))

	def fig_out(self):
		for elmt in self.figs.elements:
			if elmt.element.is_empty:
				continue
			if elmt.active:
				#print elmt.element
				if elmt.element.geom_type == 'MultiLineString':
					for sub_elmt in elmt.element:
						self.out_figs.add(self.Polygon(sub_elmt.coords))
				elif elmt.element.geom_type == 'LineString':
					self.out_figs.add(self.Polygon(elmt.element.coords))
				elif elmt.element.geom_type == 'LinearRing':
					self.out_figs.add(self.Polygon(elmt.element.coords))
				elif elmt.element.geom_type == 'MultiPolygon':
					#print "multi polygon"
					for sub_elmt in elmt.element:
						self.out_figs.add(self.Polygon(list(sub_elmt.exterior.coords)))
				elif elmt.element.geom_type == 'Polygon':
					self.out_figs.add(self.Polygon(list(elmt.element.exterior.coords)))
				elif elmt.element.geom_type == 'Point':
					#print "Point"
					self.out_figs.add(self.Polygon(list(elmt.element.coords)))

