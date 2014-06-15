#!/usr/bin/env python
# coding: UTF-8

import wx
from string import *
from math import *
#from struct import *
import os
import sys
import datetime
import locale
import re
import time
#Global Constant
HUGE = 1e10
TINY = 1e-6
MERGINE = 1e-6
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
DRILL_DEPTH = -1.9#Drill depth
CUT_DEPTH = -0.07	#pattern cutting depth
TOOL_D = 0.2		#Tool diameter
DRILL_D = 0.8		#Drill diameter
EDGE_TOOL_D = 1.0		#Edge Tool diameter
EDGE_DEPTH = -1.9 #edge depth
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
CUT_FLAG = 0
CAD_UNIT = MIL/10
DRILL_UNIT = MIL/10
EDGE_UNIT = MIL/10
CUT_OV = 0.1
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

DIST_COLOR = 'ORANGE'
ZOOM_COLOR = 'VIOLET RED'
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
gLINES2 = []
gEDGES = []
gDRILLS = []
gDRILL_LINES = []
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
gDRAWDRILL_LINE = []
gDRAWEDGE = []
gDRAWCONTOUR = []
gMAG = 1.0
gPRE_X = CENTER_X
gPRE_Y = CENTER_X
gMAG_MIN = 0.1
gMAG_MAX = 1000.0
gDRAW_XSHIFT = 0.0
gDRAW_YSHIFT = 0.0
gDISP_GERBER = 0
gDISP_DRILL = 0
gDISP_EDGE = 0
gDISP_CONTOUR = 0

TEST_POINTS1 =[]
TEST_POINTS2 =[]
TEST_POINT_R = 0.01

PRE_IN_FLAG = -1
gPAINTWINDOW_X = 300
gPAINTWINDOW_Y = 300
gPAINTWINDOW_X_MAX = 20000
gPAINTWINDOW_Y_MAX = 20000
gPAINTWINDOW_X_MIN = 100
gPAINTWINDOW_Y_MIN = 100

gSCROLL_DX = 10
gSCROLL_DY = 10

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

gMouseLeftDown = [0]*3
gMouseRightDown = [0]*3
gPROGRESS = 0
gPROGRESS_MSG = "Start Conversions ..."
#Window
class MainFrame(wx.Frame):
	def __init__(self, parent, id, title):
		global WINDOW_X, WINDOW_Y, gDISP_GERBER, gDISP_DRILL, gDISP_EDGE, gDISP_CONTOUR, gDRAWCONTOUR
		wx.Frame.__init__(self, parent, id, title, size=(WINDOW_X, WINDOW_Y))
		self.Bind(wx.EVT_CLOSE, self.OnExit)
		# Setting up the menu.
		filemenu= wx.Menu()
		menuOpen = filemenu.Append(wx.ID_OPEN,"&Open/Save"," Open/Save files")
		menuReload = filemenu.Append(wx.ID_REFRESH,"&Reload"," Reload files")
		menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
		setupmenu =  wx.Menu()
		menuMachine = setupmenu.Append(wx.ID_SETUP,"&Machine setup"," Setup Machine")
		menuConv = setupmenu.Append(wx.ID_VIEW_LIST,"&Convert setup"," Convert setup")
		#menuConv2 = setupmenu.Append(wx.ID_VIEW_LIST,"&Convert setup2"," Convert setup")
		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
		menuBar.Append(setupmenu,"&Setup") # Adding the "filemenu" to the MenuBar
		self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

		#Event for Menu bar
		self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
		self.Bind(wx.EVT_MENU, self.OnReload, menuReload)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		self.Bind(wx.EVT_MENU, self.OnConvSet, menuConv)
		#self.Bind(wx.EVT_MENU, self.OnConvSet2, menuConv2)
		self.Bind(wx.EVT_MENU, self.OnSetup, menuMachine)


		panel = wx.Panel(self, -1)
		vbox = wx.BoxSizer(wx.VERTICAL)

		#Display set
		panel1 = wx.Panel(panel, -1)
		box1 = wx.StaticBox(panel1, -1, 'Display data')
		sizer1 = wx.StaticBoxSizer(box1, orient=wx.VERTICAL)
		grid1 = wx.GridSizer(2, 5, 0, 5)
		self.cb1 = wx.CheckBox(panel1, -1, 'Pattern data')
		self.cb1.SetValue(gDISP_GERBER)
		grid1.Add(self.cb1)
		self.cb2 = wx.CheckBox(panel1, -1, 'Drill data')
		self.cb2.SetValue(gDISP_DRILL)
		grid1.Add(self.cb2)
		self.cb3 = wx.CheckBox(panel1, -1, 'Edge data')
		self.cb3.SetValue(gDISP_EDGE)
		grid1.Add(self.cb3)

		self.cb4 = wx.CheckBox(panel1, -1, 'Contour data')
		self.cb4.SetValue(gDISP_CONTOUR)
		grid1.Add(self.cb4)

		sizer1.Add(grid1)
		panel1.SetSizer(sizer1)

		vbox.Add(panel1, 0, wx.BOTTOM | wx.TOP, 9)

		#Draw data
		self.panel2 = wx.Panel(panel, -1)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)

		self.paint = Paint(self.panel2)


		hbox1.Add(self.paint, 1, wx.EXPAND | wx.ALL, 2)
		self.panel2.SetSizer(hbox1)
		vbox.Add(self.panel2, 1,  wx.LEFT | wx.RIGHT | wx.EXPAND, 2)

		hbox5 = wx.BoxSizer(wx.HORIZONTAL)
		btn0 = wx.Button(panel, -1, 'Generate contour', size=(150, 30))
		hbox5.Add(btn0, 0)
		btn1 = wx.Button(panel, -1, 'Convert and Save', size=(150, 30))
		hbox5.Add(btn1, 0)
		btn2 = wx.Button(panel, -1, 'Close', size=(70, 30))
		hbox5.Add(btn2, 0, wx.LEFT | wx.BOTTOM , 5)
		vbox.Add(hbox5, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)

		panel.SetSizer(vbox)
		self.Centre()
		self.Show(True)

		#Event
		self.Bind(wx.EVT_CHECKBOX, self.OnGeber,self.cb1)
		self.Bind(wx.EVT_CHECKBOX, self.OnDrill,self.cb2)
		self.Bind(wx.EVT_CHECKBOX, self.OnEdge,self.cb3)
		self.Bind(wx.EVT_CHECKBOX, self.OnContour,self.cb4)
		self.Bind(wx.EVT_BUTTON, self.OnExit, btn2)
		self.Bind(wx.EVT_BUTTON, self.OnGenerate, btn0)
		self.Bind(wx.EVT_BUTTON, self.OnConvert, btn1)

		#Redraw
		self.Bind(wx.EVT_PAINT, self.paint.OnPaint)
	#functions
	def OnGeber(self,e):
		global gDISP_GERBER
		gDISP_GERBER = int(self.cb1.IsChecked())
		self.Refresh(1)
	def OnDrill(self,e):
		global gDISP_DRILL
		gDISP_DRILL = int(self.cb2.IsChecked())
		self.Refresh(1)
	def OnEdge(self,e):
		global gDISP_EDGE
		gDISP_EDGE = int(self.cb3.IsChecked())
		self.Refresh(1)
	def OnContour(self,e):
		global gDISP_CONTOUR, gDRAWCONTOUR
		if(len(gDRAWCONTOUR) > 0):
			gDISP_CONTOUR = int(self.cb4.IsChecked())
		else:
			gDISP_CONTOUR = 0
			self.cb4.SetValue(0)
		self.Refresh(1)
	def OnExit(self,e):
		sys.exit(0)
	def OnSetup(self,e):
		setup = MachineSetup(None, -1, 'Machine Setup')
		setup.ShowModal()
		setup.Destroy()
	def OnConvSet(self,e):
		#print "view"
		setup = ConvSetup(None, -1, 'Convert Setup')
		setup.ShowModal()
		setup.Destroy()
	def OnConvSet2(self,e):
		#print "view"
		setup = ConvSetup2(None, -1, 'Convert Setup')
		setup.ShowModal()
		setup.Destroy()
	def OnReload(self,e):
		global gPATTERNS, gDRAWDRILL,gDRAWDRILL_LINE, gDRAWEDGE, gDISP_GERBER, gDISP_DRILL, gDISP_EDGE, gPOLYGONS, gLINES, gEDGES, gDRILLS, gGCODES
		#initialize
		gPOLYGONS = []
		gLINES = []
		gEDGES = []
		gDRILLS = []
		gGCODES = []
		gPATTERNS = []
		gDRAWDRILL = []
		gDRAWDRILL_LINE = []
		gDRAWEDGE = []
		gDRAWCONTOUR = []
		self.Refresh(1)
		set_unit()
		#read_config()	
		gcode_init()
		if(gGERBER_FILE):
			read_Gerber(gGERBER_FILE)
		if(gDRILL_FILE):
			read_Drill_file(gDRILL_FILE)
		if(gEDGE_FILE):
			readEdgeFile(gEDGE_FILE)
		gerber2draw()

	def OnOpen(self,e):
		global gPATTERNS, gDRAWDRILL, gDRAWDRILL_LINE, gDRAWEDGE, gDISP_GERBER, gDISP_DRILL, gDISP_EDGE
		setup = OpenFiles(None, -1, 'Open/Save Files')
		setup.ShowModal()
		setup.Destroy()
		if(len(gPATTERNS) > 0):
			gDISP_GERBER = 1
			self.cb1.SetValue(gDISP_GERBER)
		#print len(gDRAWDRILL)
		#print len(gDRAWDRILL_LINE)
		if(len(gDRAWDRILL) > 0 or len(gDRAWDRILL_LINE) > 0):
			gDISP_DRILL = 1
			self.cb2.SetValue(gDISP_DRILL)
		if(len(gDRAWEDGE) >0 ):
			gDISP_EDGE = 1
			self.cb3.SetValue(gDISP_EDGE)
		self.Refresh(1)
	def OnGenerate(self,e):
		global gPOLYGONS, gDISP_CONTOUR
		if(len(gPOLYGONS) > 0):
			progress = wx.ProgressDialog("Progress",'Progress', maximum = 100, parent=self, style = wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
			progress.SetSize((300, 100))
			progress.Update(5, 'Remove duplication pattern ...')
			check_duplication()
			progress.Update(7, 'Convert gerber data to polygon data ...')
			gerber2polygon()
			progress.Update(8, 'Generate Contour line ...')
			merge()		#Merge pattern
			progress.Update(75, 'Merge Contour line ...')
			line_merge()
			progress.Update(95, 'Re-Merge Contour line ...')
			merge_polygons()
			contour2draw()
			gDISP_CONTOUR = 1
			self.cb4.SetValue(gDISP_CONTOUR)
			progress.Update(100, 'Finished ...')
			progress.Destroy()
			dlg = wx.MessageDialog(self, "Contour generation is finished", "Contour generation is finished" , wx.OK)
			dlg.ShowModal() # Shows it
			dlg.Destroy()
			self.Refresh(1)
	def OnConvert(self,e):
		global gPOLYGONS, gEDGES, gDRILLS, MERGE_DRILL_DATA, gGCODE_FILE, gGDRILL_FILE, gGEDGE_FILE	
		if(len(gDRILLS) > 0):
			do_drill()
		if(len(gEDGES) > 0):
			mergeEdge()
			edge2gcode()
		if(len(gPOLYGONS) > 0 or len(gDRILLS) > 0 or len(gEDGES) > 0):
			end(gGCODE_FILE, gGDRILL_FILE, gGEDGE_FILE)
			dlg = wx.MessageDialog(self, "Convert finished", "Convert is finished" , wx.OK)
			dlg.ShowModal() # Shows it
			dlg.Destroy() # finally destroy it when finished.
		self.Refresh(1)

class Paint(wx.ScrolledWindow):
	def __init__(self, parent):
		global gPAINTWINDOW_X, gPAINTWINDOW_Y, gSCROLL_DX, gSCROLL_DY
		wx.ScrolledWindow.__init__(self, parent,-1,style=wx.HSCROLL|wx.VSCROLL)
		self.SetBackgroundColour('WHITE')
		self.Bind(wx.EVT_PAINT, self.OnPaint)

		self.SetScrollbars(gSCROLL_DX, gSCROLL_DY, int(gPAINTWINDOW_X/gSCROLL_DX),int(gPAINTWINDOW_Y/gSCROLL_DY));
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
		self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.OnDrag)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
		self.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
		self.Bind(wx.EVT_MOTION , self.OnMouseMove) 



		self.Centre()
		self.Show(True)

	def OnKeyDown(self, event):
		keycode = event.GetKeyCode()
		print keycode
		#if keycode == wx.WXK_UP:

	#gerber
	def OnPaint(self, e):
		global gPOLYGONS, gPATTERNS, gMAG, gDRAW_XSHIFT, gDRAW_YSHIFT, gDRAWDRILL, gDRAWDRILL_LINE, gDRAWEDGE, gDRAWCONTOUR, gEDGES, gDRILLS, GERBER_COLOR, DRILL_COLOR, EDGE_COLOR, CONTOUR_COLOR, gDISP_GERBER, gDISP_DRILL, gDISP_EDGE, gDISP_CONTOUR, CENTER_X, CENTER_Y, gPAINTWINDOW_X, gPAINTWINDOW_Y, gSCROLL_DX, gSCROLL_DY, gPAINTWINDOW_X_MAX, gPAINTWINDOW_Y_MAX, gPAINTWINDOW_X_MIN, gPAINTWINDOW_Y_MIN
		dc = wx.PaintDC(self)
		paint_size = self.GetSize()
		#print paint_size
		CENTER_X =int(paint_size.x/2)+1
		CENTER_Y =int(paint_size.y/2)+1
		veiw_start = self.CalcUnscrolledPosition(0,0)
		#print "pos=" + str(veiw_start)
		#print 'Mag' + str(gMAG) + ", x shift=" + str(gDRAW_XSHIFT-veiw_start[0]) + ", y shift=" + str(gDRAW_YSHIFT-veiw_start[1])
		if(len(gPATTERNS) > 0 and gDISP_GERBER):
			#dc.SetPen(wx.Pen(GERBER_COLOR, 1, wx.SOLID))
			for polygon in gPATTERNS:
				points = []
				for point in polygon.points:
					x = point[0] * gMAG + gDRAW_XSHIFT-veiw_start[0]
					y = point[1] * gMAG + gDRAW_YSHIFT-veiw_start[1]
					points.append([x,y])
				dc.SetPen(wx.Pen(GERBER_COLOR, 1, wx.SOLID))
				#dc.DrawPolygon(points)
				dc.DrawLines(points)

		if(len(gDRAWDRILL) > 0 and gDISP_DRILL):
			for drill in gDRAWDRILL:
				x = drill.x * gMAG + gDRAW_XSHIFT-veiw_start[0]
				y = drill.y * gMAG + gDRAW_YSHIFT-veiw_start[1]
				r = drill.d * gMAG/2
				#print x
				#print y
				dc.SetPen(wx.Pen(DRILL_COLOR, 1, wx.DOT))
				dc.DrawCircle(x, y, r)
		#print "len:"
		#print len(gDRAWDRILL_LINE)
		if(len(gDRAWDRILL_LINE) > 0 and gDISP_DRILL):
			#print "drill line"
			for polygon in gDRAWDRILL_LINE:
				points = []
				for point in polygon.points:
					#print "point"
					#print point
					x = point[0] * gMAG + gDRAW_XSHIFT-veiw_start[0]
					y = point[1] * gMAG + gDRAW_YSHIFT-veiw_start[1]
					points.append([x,y])
				dc.SetPen(wx.Pen(DRILL_COLOR, 1, wx.DOT))
				#print points
				#dc.DrawPolygon(points)
				dc.DrawLines(points)
		if(len(gDRAWEDGE) > 0 and gDISP_EDGE):
			for edge in gDRAWEDGE:
				points = []
				for point in edge.points:
					x = point[0] * gMAG + gDRAW_XSHIFT-veiw_start[0]
					y = point[1] * gMAG + gDRAW_YSHIFT-veiw_start[1]
					points.append([x,y])
				dc.SetPen(wx.Pen(EDGE_COLOR, 1, wx.DOT_DASH))
				dc.DrawLines(points)
		if(len(gDRAWCONTOUR) > 0 and gDISP_CONTOUR):
			for edge in gDRAWCONTOUR:
				points = []
				for point in edge.points:
					x = point[0] * gMAG + gDRAW_XSHIFT-veiw_start[0]
					y = point[1] * gMAG + gDRAW_YSHIFT-veiw_start[1]
					points.append([x,y])
				dc.SetPen(wx.Pen(CONTOUR_COLOR, 1, wx.SOLID))
				#dc.DrawPolygon(points)
				dc.DrawLines(points)
	def OnMouseWheel(self, event):
		global gMAG, gMAG_MIN, gMAG_MAX, gDRAW_XSHIFT, gDRAW_YSHIFT, WINDOW_X, WINDOW_Y, CENTER_X, CENTER_Y, gPRE_X, gPRE_Y,gPAINTWINDOW_X, gPAINTWINDOW_Y, gSCROLL_DX, gSCROLL_DY, gPAINTWINDOW_X_MAX, gPAINTWINDOW_Y_MAX, gPAINTWINDOW_X_MIN, gPAINTWINDOW_Y_MIN 
		pos = event.GetPosition()
		w = event.GetWheelRotation()
		#mag_cont += copysign(1.0, w)
		pre_mag = gMAG
		gMAG += copysign(1.0, w)
		#gMAG += w/100.0
		#gMAG = 1
		gDRAW_XSHIFT = float(CENTER_X) - (gMAG*(float(pos.x)-gDRAW_XSHIFT))/pre_mag
		gDRAW_YSHIFT = float(CENTER_Y) - (gMAG*(float(pos.y)-gDRAW_YSHIFT))/pre_mag
		gPRE_X = float(pos.x)
		gPRE_Y = float(pos.y)
		if(gMAG < gMAG_MIN):
			gMAG = gMAG_MIN
			gDRAW_XSHIFT = CENTER_X
			gDRAW_YSHIFT = CENTER_Y
		if(gMAG > gMAG_MAX):
			gMAG = gMAG_MAX
			gDRAW_XSHIFT = float(CENTER_X) - (gMAG*(float(pos.x)-gDRAW_XSHIFT))/pre_mag
			gDRAW_YSHIFT = float(CENTER_Y) - (gMAG*(float(pos.y)-gDRAW_YSHIFT))/pre_mag
		#print 'Mag' + str(gMAG) + ", x shift=" + str(gDRAW_XSHIFT) + ", y shift=" + str(gDRAW_YSHIFT)
		#print 'OnMouseWheel' + str(pos) + ", w=" + str(gMAG)
		#self.OnPaint(event)
		paint_window_x = int(gMAG * gPAINTWINDOW_X)
		paint_window_y = int(gMAG * gPAINTWINDOW_Y)
		if(gPAINTWINDOW_X_MAX < paint_window_x):
			paint_window_x = gPAINTWINDOW_X_MAX
		elif(gPAINTWINDOW_X_MIN > paint_window_x):
			paint_window_x = gPAINTWINDOW_X_MIN
		if(gPAINTWINDOW_Y_MAX < paint_window_y):
			paint_window_y = gPAINTWINDOW_Y_MAX
		elif(gPAINTWINDOW_Y_MIN > gPAINTWINDOW_Y):
			paint_window_y = gPAINTWINDOW_Y_MIN
		#print "window x=" + str(paint_window_x) + ", window y=" + str(paint_window_y)
		self.SetScrollbars(gSCROLL_DX, gSCROLL_DY, int(paint_window_x/gSCROLL_DX),int(paint_window_y/gSCROLL_DY));
		self.Refresh(1)
	def OnDrag(self, event):
		pos = event.GetPosition()
		# "Drag: pos=" + str(pos)
	def OnMouseLeftDown(self, event):
		global gMouseLeftDown
		pos = event.GetPosition()
		gMouseLeftDown[0] = 1
		gMouseLeftDown[1] = pos.x
		gMouseLeftDown[2] = pos.y
		#print "Left Down: pos=" + str(pos)
	def OnMouseRightDown(self, event):
		global gMouseRightDown
		pos = event.GetPosition()
		gMouseRightDown[0] = 1
		gMouseRightDown[1] = pos.x
		gMouseRightDown[2] = pos.y
		#print "Right Down: pos=" + str(pos)
	def OnMouseLeftUp(self, event):
		global gMouseLeftDown, gMAG, gDRAW_XSHIFT, gDRAW_YSHIFT, CENTER_X, CENTER_Y
		pos = event.GetPosition()
		size = self.GetSize()
		if gMouseLeftDown[0]:
			gMouseLeftDown[0] = 0
			pre_mag = gMAG
			dx = pos.x - gMouseLeftDown[1]
			dy = pos.y - gMouseLeftDown[2]
			cx = pos.x - dx/2
			cy = pos.y - dy/2
			if(dx > 0):
				gMAG = float(size.x)/float(dx/pre_mag)
			elif(dx < 0):
				gMAG = -float(pre_mag)/float(dx)
			#print "gmag=" + str(gMAG)
			if(dy > 0):
				if(gMAG > float(size.y)/float(dy/pre_mag)):
					gMAG = float(size.y)/float(dy/pre_mag)
			
			gDRAW_XSHIFT = float(CENTER_X) - (gMAG*(float(cx)-gDRAW_XSHIFT))/pre_mag
			gDRAW_YSHIFT = float(CENTER_Y) - (gMAG*(float(cy)-gDRAW_YSHIFT))/pre_mag
			if(gMAG < gMAG_MIN):
				gMAG = gMAG_MIN
				gDRAW_XSHIFT = CENTER_X
				gDRAW_YSHIFT = CENTER_Y
			if(gMAG > gMAG_MAX):
				gMAG = gMAG_MAX
				gDRAW_XSHIFT = float(CENTER_X) - (gMAG*(float(cx)-gDRAW_XSHIFT))/pre_mag
				gDRAW_YSHIFT = float(CENTER_Y) - (gMAG*(float(cy)-gDRAW_YSHIFT))/pre_mag
			paint_window_x = int(gMAG * gPAINTWINDOW_X)
			paint_window_y = int(gMAG * gPAINTWINDOW_Y)
			if(gPAINTWINDOW_X_MAX < paint_window_x):
				paint_window_x = gPAINTWINDOW_X_MAX
			elif(gPAINTWINDOW_X_MIN > paint_window_x):
				paint_window_x = gPAINTWINDOW_X_MIN
			if(gPAINTWINDOW_Y_MAX < paint_window_y):
				paint_window_y = gPAINTWINDOW_Y_MAX
			elif(gPAINTWINDOW_Y_MIN > gPAINTWINDOW_Y):
				paint_window_y = gPAINTWINDOW_Y_MIN
			#print "window x=" + str(paint_window_x) + ", window y=" + str(paint_window_y)
			self.SetScrollbars(gSCROLL_DX, gSCROLL_DY, int(paint_window_x/gSCROLL_DX),int(paint_window_y/gSCROLL_DY));

			self.Refresh(1)
			#print "Left UP: pos=" + str(pos) + ", dx=" + str(dx) + ", dy=" + str(dy) + ", cx=" + str(cx) + ", cy=" + str(cy) + ", mag=" + str(gMAG)
	def OnMouseRightUp(self, event):
		global gMouseRightDown, gMAG
		pos = event.GetPosition()
		if gMouseRightDown[0]:
			gMouseRightDown[0] = 0
			dx = pos.x - gMouseRightDown[1]
			dy = pos.y - gMouseRightDown[2]
			dist = sqrt(dx*dx + dy*dy)/gMAG
			#print dist
			cdc = wx.ClientDC(self)
			#cdc.BeginDrawing()
			cdc.DrawText(str(dist),pos.x,pos.y)
			cdc.SetPen(wx.Pen(DIST_COLOR, 1, wx.SOLID))
			cdc.DrawLines(([gMouseRightDown[1],gMouseRightDown[2]],[pos.x,pos.y]))
	def OnMouseLeftDClick(self, event):	#Set center
		pos = event.GetPosition()
	def OnMouseRightDClick(self, event):
		pos = event.GetPosition()
	def OnMouseMove(self, event):
		global dc
		pos = event.GetPosition()
		cdc = wx.ClientDC(self)
		#x = 0
		#y = 0
		#dx = 0
		#dy = 0
		if gMouseRightDown[0]:
			self.Refresh(1)
			#cdc = wx.ClientDC(self)
			#cdc.BeginDrawing()
			cdc.SetPen(wx.Pen(DIST_COLOR, 1, wx.SOLID))
			cdc.DrawLines(([gMouseRightDown[1],gMouseRightDown[2]],[pos.x,pos.y]))
		if gMouseLeftDown[0]:
			self.Refresh(1)
			#cdc.Dispose() #NG
			#cdc.Clear()	#NG

			#cdc.SetBrush(wx.Brush(ZOOM_COLOR,wx.TRANSPARENT)) #NG
			#cdc.SetPen(wx.Pen(ZOOM_COLOR, 1, wx.TRANSPARENT)) #NG
			#cdc.DrawRectangle(x,y,dx,dy) #NG
			dx = pos.x - gMouseLeftDown[1]
			dy = pos.y - gMouseLeftDown[2]
			x = gMouseLeftDown[1]
			y = gMouseLeftDown[2]
			if(dx < 0):
				dx = -1 * dx
				x = pos.x
			if(dy < 0 ):
				dy = -1 * dy
				y = pos.y
			#cdc = wx.ClientDC(self)
			#cdc.BeginDrawing()
			cdc.SetBrush(wx.Brush(ZOOM_COLOR,wx.TRANSPARENT))
			cdc.SetPen(wx.Pen(ZOOM_COLOR, 1, wx.SOLID))
			cdc.DrawRectangle(x,y,dx,dy)

class OpenFiles(wx.Dialog):
	def __init__(self, parent, id, title):
		global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT, gGERBER_FILE, gDRILL_FILE, gEDGE_FILE, gGCODE_FILE, gGDRILL_FILE, gGEDGE_FILE
		wx.Dialog.__init__(self, parent, id, title, size=(250, 210))
		self.dirname=''

		panel = wx.Panel(self, -1)
		sizer = wx.GridBagSizer(0, 0)

		text1 = wx.StaticText(panel, -1, 'Gerber file')
		sizer.Add(text1, (0, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.gerber = wx.TextCtrl(panel, -1)
		self.gerber.SetValue(gGERBER_FILE)
		sizer.Add(self.gerber, (0, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		button1 = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button1, (0, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		text2 = wx.StaticText(panel, -1, 'Drill file')
		sizer.Add(text2, (1, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.drill = wx.TextCtrl(panel, -1)
		self.drill.SetValue(gDRILL_FILE)
		sizer.Add(self.drill, (1, 1), (1, 3), wx.TOP | wx.EXPAND,  5)

		button2 = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button2, (1, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		text0 = wx.StaticText(panel, -1, 'Edge file')
		sizer.Add(text0, (2, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.edge = wx.TextCtrl(panel, -1)
		self.edge.SetValue(gEDGE_FILE)
		sizer.Add(self.edge, (2, 1), (1, 3), wx.TOP | wx.EXPAND,  5)

		button_edge = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button_edge, (2, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		radioList = ['mm', 'inch']
		rb1 = wx.RadioBox(panel, label="unit of Input file", choices=radioList, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		rb1.SetSelection(int(IN_INCH_FLAG))
		sizer.Add(rb1, (3, 0), (1, 5), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		line = wx.StaticLine(panel, -1 )
		sizer.Add(line, (5, 0), (1, 5), wx.TOP | wx.EXPAND, -15)

		text3 = wx.StaticText(panel, -1, 'G-code file')
		sizer.Add(text3, (6, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.gcode = wx.TextCtrl(panel, -1)
		self.gcode.SetValue(gGCODE_FILE)
		sizer.Add(self.gcode, (6, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		button3 = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button3, (6, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		text4 = wx.StaticText(panel, -1, 'G-code Drill file')
		sizer.Add(text4, (7, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.gdrill = wx.TextCtrl(panel, -1)
		self.gdrill.SetValue(gGDRILL_FILE)
		sizer.Add(self.gdrill, (7, 1), (1, 3), wx.TOP | wx.EXPAND,  5)

		button4 = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button4, (7, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		text_gedge = wx.StaticText(panel, -1, 'G-code Edge file')
		sizer.Add(text_gedge, (8, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.gedge = wx.TextCtrl(panel, -1)
		self.gedge.SetValue(gGEDGE_FILE)
		sizer.Add(self.gedge, (8, 1), (1, 3), wx.TOP | wx.EXPAND,  5)

		button_gedge = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button_gedge, (8, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		rb2 = wx.RadioBox(panel, label="unit of Output file", choices=radioList, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		rb2.SetSelection(int(OUT_INCH_FLAG))
		sizer.Add(rb2, (9, 0), (1, 5), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		text5 = wx.StaticText(panel, -1, 'Cutting depth')
		sizer.Add(text5, (10, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.tc5 = wx.TextCtrl(panel, -1)
		self.tc5.SetValue(str(CUT_DEPTH))
		sizer.Add(self.tc5, (10, 1), (1, 1), wx.TOP | wx.EXPAND,  5)


		text6 = wx.StaticText(panel, -1, 'Drill depth')
		sizer.Add(text6, (10, 2), flag=wx.TOP | wx.LEFT, border=10)

		self.tc6 = wx.TextCtrl(panel, -1)
		self.tc6.SetValue(str(DRILL_DEPTH))
		sizer.Add(self.tc6, (10, 3), (1, 1), wx.TOP | wx.EXPAND,  5)

		button5 = wx.Button(panel, -1, 'OK', size=(-1, 30))
		sizer.Add(button5, (11, 3), (1, 1),  wx.LEFT, 10)

		button6 = wx.Button(panel, -1, 'Close', size=(-1, 30))
		sizer.Add(button6, (11, 4), (1, 1),  wx.LEFT | wx.BOTTOM | wx.RIGHT, 10)

		sizer.AddGrowableCol(2)

		panel.SetSizer(sizer)
		sizer.Fit(self)
		# Events.
		self.Bind(wx.EVT_BUTTON, self.OnGerberOpen, button1)
		self.Bind(wx.EVT_BUTTON, self.OnDrillOpen, button2)
		self.Bind(wx.EVT_BUTTON, self.OnEdgeOpen, button_edge)
		self.Bind(wx.EVT_BUTTON, self.OnGcodeOpen, button3)
		self.Bind(wx.EVT_BUTTON, self.OnGDrillOpen, button4)
		self.Bind(wx.EVT_BUTTON, self.OnGEdgeOpen, button_gedge)
		self.Bind(wx.EVT_BUTTON, self.OnOK, button5)
		self.Bind(wx.EVT_BUTTON, self.OnClose, button6)	
		self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox1, rb1)
		self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox2, rb2)


		self.Centre()
		self.Show(True)

	#Events
	def EvtRadioBox1(self, e):
		global IN_INCH_FLAG
		if(e.GetInt()==0): #milli
			IN_INCH_FLAG = 0
		elif(e.GetInt()==1): #Inch
			IN_INCH_FLAG = 1
	def EvtRadioBox2(self, e):
		global OUT_INCH_FLAG
		if(e.GetInt()==0): #milli
			OUT_INCH_FLAG = 0
		elif(e.GetInt()==1): #Inch
			OUT_INCH_FLAG = 1
	def OnGerberOpen(self,e):
		global GERBER_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a input Gerber file", self.dirname, "", GERBER_EXT, wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.gerber.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnDrillOpen(self,e):
		global DRILL_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a input Drill file", self.dirname, "", DRILL_EXT, wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.drill.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnEdgeOpen(self,e):
		global EDGE_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a input Edge file", self.dirname, "", EDGE_EXT, wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.edge.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnGcodeOpen(self,e):
		global GCODE_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a output G-code file", self.dirname, "", GCODE_EXT, wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.gcode.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnGDrillOpen(self,e):
		global GDRILL_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a output G-code Drill file", self.dirname, "", GDRILL_EXT, wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.gdrill.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnGEdgeOpen(self,e):
		global GEDGE_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a output G-code Edge file", self.dirname, "", GEDGE_EXT, wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.gedge.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()


	def OnOK(self,e):
		global DRILL_DEPTH, CUT_DEPTH, gGERBER_FILE, gDRILL_FILE, gEDGE_FILE, gGCODE_FILE, gGDRILL_FILE, gGEDGE_FILE, gPATTERNS, gDRAWDRILL,gDRAWDRILL_LINE, gDRAWEDGE, gDRAWCONTOUR
		#initialize
		gPATTERNS = []
		gDRAWDRILL = []
		gDRAWDRILL_LINE = []
		gDRAWEDGE = []
		gDRAWCONTOUR = []
		set_unit()
		read_config()	
		gcode_init()
		if(self.gerber.GetValue()):
			gGERBER_FILE = self.gerber.GetValue()
			read_Gerber(gGERBER_FILE)
		if(self.drill.GetValue()):
			gDRILL_FILE = self.drill.GetValue()
			read_Drill_file(gDRILL_FILE)
		if(self.edge.GetValue()):
			gEDGE_FILE = self.edge.GetValue()
			readEdgeFile(gEDGE_FILE)
		if(self.gerber.GetValue()):
			gGCODE_FILE = self.gcode.GetValue()
		if(self.drill.GetValue()):
			gGDRILL_FILE = self.gdrill.GetValue()
		if(self.edge.GetValue()):
			gGEDGE_FILE = self.gedge.GetValue()
		gerber2draw()
		CUT_DEPTH = self.tc5.GetValue()
		DRILL_DEPTH =self.tc6.GetValue()
		self.Close(True)  # Close the frame.

	def OnClose(self,e):
		self.Close(True)  # Close the frame.


class MachineSetup(wx.Dialog):
	def __init__(self, parent, id, title):
		global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT, EDGE_TOOL_D, EDGE_DEPTH, EDGE_SPEED, EDGE_Z_SPEED, MERGE_DRILL_DATA, Z_STEP
		wx.Dialog.__init__(self, parent, id, title, size=(250, 210))

		panel = wx.Panel(self, -1)
		sizer = wx.GridBagSizer(0, 0)

		text1 = wx.StaticText(panel, -1, 'Initial X posision')
		sizer.Add(text1, (0, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.inix = wx.TextCtrl(panel, -1)
		self.inix.SetValue(str(INI_X))
		sizer.Add(self.inix, (0, 1), (1, 3), wx.TOP | wx.EXPAND, 5)


		text2 = wx.StaticText(panel, -1, 'Initial Y posision')
		sizer.Add(text2, (1, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.iniy = wx.TextCtrl(panel, -1)
		self.iniy.SetValue(str(INI_Y))
		sizer.Add(self.iniy, (1, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text3 = wx.StaticText(panel, -1, 'Initial Z posision')
		sizer.Add(text3, (2, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.iniz = wx.TextCtrl(panel, -1)
		self.iniz.SetValue(str(INI_Z))
		sizer.Add(self.iniz, (2, 1), (1, 3), wx.TOP | wx.EXPAND, 5)


		text4 = wx.StaticText(panel, -1, 'Moving height')
		sizer.Add(text4, (3, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.moveh = wx.TextCtrl(panel, -1)
		self.moveh.SetValue(str(MOVE_HEIGHT))
		sizer.Add(self.moveh, (3, 1), (1, 3), wx.TOP | wx.EXPAND, 5)


		text5 = wx.StaticText(panel, -1, 'XY Speed')
		sizer.Add(text5, (4, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.xyspeed = wx.TextCtrl(panel, -1)
		self.xyspeed.SetValue(str(XY_SPEED))
		sizer.Add(self.xyspeed, (4, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text6 = wx.StaticText(panel, -1, 'Z speed')
		sizer.Add(text6, (5, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.zspeed = wx.TextCtrl(panel, -1)
		self.zspeed.SetValue(str(Z_SPEED))
		sizer.Add(self.zspeed, (5, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text7 = wx.StaticText(panel, -1, 'Cutting depth')
		sizer.Add(text7, (6, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.cutdep = wx.TextCtrl(panel, -1)
		self.cutdep.SetValue(str(CUT_DEPTH))
		sizer.Add(self.cutdep, (6, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text8 = wx.StaticText(panel, -1, 'Tool diameter')
		sizer.Add(text8, (7, 0), flag=wx.TOP | wx.LEFT, border=10)
		self.toold = wx.TextCtrl(panel, -1)
		self.toold.SetValue(str(TOOL_D))
		sizer.Add(self.toold, (7, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text9 = wx.StaticText(panel, -1, 'Drill depth')
		sizer.Add(text9, (8, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.drilldep = wx.TextCtrl(panel, -1)
		self.drilldep.SetValue(str(DRILL_DEPTH))
		sizer.Add(self.drilldep, (8, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text10 = wx.StaticText(panel, -1, 'Drill down speed')
		sizer.Add(text10, (9, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.drillspeed = wx.TextCtrl(panel, -1)
		self.drillspeed.SetValue(str(DRILL_SPEED))
		sizer.Add(self.drillspeed, (9, 1), (1, 3), wx.TOP | wx.EXPAND, 5)


		text11 = wx.StaticText(panel, -1, 'Drill diameter')
		sizer.Add(text11, (10, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.drilld = wx.TextCtrl(panel, -1)
		self.drilld.SetValue(str(DRILL_D))
		sizer.Add(self.drilld, (10, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text12 = wx.StaticText(panel, -1, 'Edge depth')
		sizer.Add(text12, (11, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edgedep = wx.TextCtrl(panel, -1)
		self.edgedep.SetValue(str(EDGE_DEPTH))
		sizer.Add(self.edgedep, (11, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text13 = wx.StaticText(panel, -1, 'Edge tool diameter')
		sizer.Add(text13, (12, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edged = wx.TextCtrl(panel, -1)
		self.edged.SetValue(str(EDGE_TOOL_D))
		sizer.Add(self.edged, (12, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text14 = wx.StaticText(panel, -1, 'Edge cutting speed')
		sizer.Add(text14, (13, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edgespeed = wx.TextCtrl(panel, -1)
		self.edgespeed.SetValue(str(EDGE_SPEED))
		sizer.Add(self.edgespeed, (13, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text15 = wx.StaticText(panel, -1, 'Edge Z speed')
		sizer.Add(text15, (14, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edgezspeed = wx.TextCtrl(panel, -1)
		self.edgezspeed.SetValue(str(EDGE_Z_SPEED))
		sizer.Add(self.edgezspeed, (14, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text16 = wx.StaticText(panel, -1, 'Z step')
		sizer.Add(text16, (15, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.zstep = wx.TextCtrl(panel, -1)
		self.zstep.SetValue(str(Z_STEP))
		sizer.Add(self.zstep, (15, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		button0 = wx.Button(panel, -1, 'Save to config file', size=(-1, 30))
		sizer.Add(button0, (17, 0), (1, 1),  wx.LEFT, 10)

		button1 = wx.Button(panel, -1, 'Temporally Apply', size=(-1, 30))
		sizer.Add(button1, (17, 1), (1, 1),  wx.LEFT, 10)

		button2 = wx.Button(panel, -1, 'Close', size=(-1, 30))
		sizer.Add(button2, (17, 2), (1, 1),  wx.LEFT | wx.BOTTOM | wx.RIGHT, 10)
		sizer.AddGrowableCol(2)

		panel.SetSizer(sizer)
		sizer.Fit(self)
		#Event
		self.Bind(wx.EVT_BUTTON, self.OnSave, button0)
		self.Bind(wx.EVT_BUTTON, self.OnApply, button1)
		self.Bind(wx.EVT_BUTTON, self.OnClose, button2)

	def OnApply(self,e):
		global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT, EDGE_TOOL_D, EDGE_DEPTH, EDGE_SPEED, EDGE_Z_SPEED, Z_STEP
		INI_X = float(self.inix.GetValue())
		INI_Y = float(self.iniy.GetValue())
		INI_Z = float(self.iniz.GetValue())
		MOVE_HEIGHT = float(self.moveh.GetValue())
		XY_SPEED = int(self.xyspeed.GetValue())
		Z_SPEED = int(self.zspeed.GetValue())
		DRILL_SPEED = int(self.drillspeed.GetValue())
		DRILL_DEPTH = float(self.drilldep.GetValue())
		CUT_DEPTH = float(self.cutdep.GetValue())
		TOOL_D = float(self.toold.GetValue())
		DRILL_D = float(self.drilld.GetValue())
		EDGE_TOOL_D = float(self.edged.GetValue())
		EDGE_DEPTH = float(self.edgedep.GetValue())
		EDGE_SPEED = int(self.edgespeed.GetValue())
		EDGE_Z_SPEED = int(self.edgezspeed.GetValue())
		Z_STEP = float(self.zstep.GetValue())
		#show_all_values()
		self.Close(True)  # Close the frame.
	def OnClose(self,e):
		self.Close(True)  # Close the frame.
	def OnSave(self,e):
		global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT, EDGE_TOOL_D, EDGE_DEPTH, EDGE_SPEED, EDGE_Z_SPEED, Z_STEP
		INI_X = float(self.inix.GetValue())
		INI_Y = float(self.iniy.GetValue())
		INI_Z = float(self.iniz.GetValue())
		MOVE_HEIGHT = float(self.moveh.GetValue())
		XY_SPEED = int(self.xyspeed.GetValue())
		Z_SPEED = int(self.zspeed.GetValue())
		DRILL_SPEED = int(self.drillspeed.GetValue())
		DRILL_DEPTH = float(self.drilldep.GetValue())
		CUT_DEPTH = float(self.cutdep.GetValue())
		TOOL_D = float(self.toold.GetValue())
		DRILL_D = float(self.drilld.GetValue())
		EDGE_TOOL_D = float(self.edged.GetValue())
		EDGE_DEPTH = float(self.edgedep.GetValue())
		EDGE_SPEED = int(self.edgespeed.GetValue())
		EDGE_Z_SPEED = int(self.edgezspeed.GetValue())
		Z_STEP = float(self.zstep.GetValue())
		save_config()
		self.Close(True)  # Close the frame.
class ConvSetup(wx.Dialog):
	def __init__(self, parent, id, title):
		global gCOLORS, GERBER_COLOR, DRILL_COLOR, EDGE_COLOR , CONTOUR_COLOR, GERBER_EXT, DRILL_EXT, EDGE_EXT, GCODE_EXT, GDRILL_EXT, GEDGE_EXT, OUT_INCH_FLAG, IN_INCH_FLAG,CAD_UNIT, DRILL_UNIT, EDGE_UNIT, CUT_FLAG, CUT_OV
		wx.Dialog.__init__(self, parent, id, title, size=(250, 210))

		panel = wx.Panel(self, -1)
		sizer = wx.GridBagSizer(0, 0)

		text1 = wx.StaticText(panel, -1, 'Gerber data color')
		sizer.Add(text1, (0, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.gerber_color = wx.ComboBox(panel, -1, choices=gCOLORS, style=wx.CB_READONLY)
		self.gerber_color.SetValue(str(GERBER_COLOR))
		sizer.Add(self.gerber_color, (0, 1), (1, 3), wx.TOP | wx.EXPAND, 5)


		text2 = wx.StaticText(panel, -1, 'Drill data color')
		sizer.Add(text2, (1, 0), flag=wx.TOP | wx.LEFT, border=10)
		self.drill_color = wx.ComboBox(panel, -1, choices=gCOLORS, style=wx.CB_READONLY)
		self.drill_color.SetValue(str(DRILL_COLOR))
		sizer.Add(self.drill_color, (1, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text3 = wx.StaticText(panel, -1, 'Edge data color')
		sizer.Add(text3, (2, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edge_color = wx.ComboBox(panel, -1, choices=gCOLORS, style=wx.CB_READONLY)
		self.edge_color.SetValue(str(EDGE_COLOR))
		sizer.Add(self.edge_color, (2, 1), (1, 3), wx.TOP | wx.EXPAND, 5)


		text4 = wx.StaticText(panel, -1, 'Contour data color')
		sizer.Add(text4, (3, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.contour_color = wx.ComboBox(panel, -1, choices=gCOLORS, style=wx.CB_READONLY)
		self.contour_color.SetValue(str(CONTOUR_COLOR))
		sizer.Add(self.contour_color, (3, 1), (1, 3), wx.TOP | wx.EXPAND, 5)


		text5 = wx.StaticText(panel, -1, 'Gerber file extension')
		sizer.Add(text5, (4, 0), flag=wx.TOP | wx.LEFT, border=10)
		self.gerber_ext = wx.TextCtrl(panel, -1)
		self.gerber_ext.SetValue(str(GERBER_EXT))
		sizer.Add(self.gerber_ext, (4, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text6 = wx.StaticText(panel, -1, 'Drill file extension')
		sizer.Add(text6, (5, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.drill_ext = wx.TextCtrl(panel, -1)
		self.drill_ext.SetValue(str(DRILL_EXT))
		sizer.Add(self.drill_ext, (5, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text7 = wx.StaticText(panel, -1, 'Edge file extension')
		sizer.Add(text7, (6, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edge_ext = wx.TextCtrl(panel, -1)
		self.edge_ext.SetValue(str(EDGE_EXT))
		sizer.Add(self.edge_ext, (6, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text8 = wx.StaticText(panel, -1, 'Gcode file extension')
		sizer.Add(text8, (7, 0), flag=wx.TOP | wx.LEFT, border=10)
		self.gcode_ext = wx.TextCtrl(panel, -1)
		self.gcode_ext.SetValue(str(GCODE_EXT))
		sizer.Add(self.gcode_ext, (7, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text9 = wx.StaticText(panel, -1, 'Gcode Drill file extension')
		sizer.Add(text9, (8, 0), flag=wx.TOP | wx.LEFT, border=10)
		self.gdrill_ext = wx.TextCtrl(panel, -1)
		self.gdrill_ext.SetValue(str(GDRILL_EXT))
		sizer.Add(self.gdrill_ext, (8, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text10 = wx.StaticText(panel, -1, 'Gcode Edge file extension')
		sizer.Add(text10, (9, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.gedge_ext = wx.TextCtrl(panel, -1)
		self.gedge_ext.SetValue(str(GEDGE_EXT))
		sizer.Add(self.gedge_ext, (9, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text12 = wx.StaticText(panel, -1, 'G code left X')
		sizer.Add(text12, (11, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.leftx = wx.TextCtrl(panel, -1)
		self.leftx.SetValue(str(LEFT_X))
		sizer.Add(self.leftx, (11, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text13 = wx.StaticText(panel, -1, 'G code lower Y')
		sizer.Add(text13, (12, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.lowy = wx.TextCtrl(panel, -1)
		self.lowy.SetValue(str(LOWER_Y))
		sizer.Add(self.lowy, (12, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text14 = wx.StaticText(panel, -1, 'CAD unit')
		sizer.Add(text14, (13, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.cadunit = wx.TextCtrl(panel, -1)
		self.cadunit.SetValue(str(CAD_UNIT))
		sizer.Add(self.cadunit, (13, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text15 = wx.StaticText(panel, -1, 'Drill unit')
		sizer.Add(text15, (14, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.drillunit = wx.TextCtrl(panel, -1)
		self.drillunit.SetValue(str(DRILL_UNIT))
		sizer.Add(self.drillunit, (14, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text16 = wx.StaticText(panel, -1, 'Edge unit')
		sizer.Add(text16, (15, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edgeunit = wx.TextCtrl(panel, -1)
		self.edgeunit.SetValue(str(EDGE_UNIT))
		sizer.Add(self.edgeunit, (15, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		radioList_cut = ['line only', 'all']
		self.rb_cut = wx.RadioBox(panel, label="Scrape ", choices=radioList_cut, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		self.rb_cut.SetSelection(int(CUT_FLAG))
		sizer.Add(self.rb_cut, (16, 0), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		text_cut = wx.StaticText(panel, -1, 'scrape overlap')
		sizer.Add(text_cut, (16, 1), flag= wx.LEFT | wx.TOP, border=10)
		self.cut_ov = wx.TextCtrl(panel, -1)
		self.cut_ov.SetValue(str(CUT_OV))
		sizer.Add(self.cut_ov, (16, 2), (1, 1), wx.TOP | wx.EXPAND, 5)

		radioList = ['mm', 'inch']
		self.rb1 = wx.RadioBox(panel, label="unit of Input file", choices=radioList, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		self.rb1.SetSelection(int(IN_INCH_FLAG))
		sizer.Add(self.rb1, (17, 0), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		self.rb2 = wx.RadioBox(panel, label="unit of Output file", choices=radioList, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		self.rb2.SetSelection(int(OUT_INCH_FLAG))
		sizer.Add(self.rb2, (17, 1), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		self.cb1 = wx.CheckBox(panel, -1, 'Enable M code', (10, 10))
		self.cb1.SetValue(int(MCODE_FLAG))
		sizer.Add(self.cb1, (17, 2), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		button0 = wx.Button(panel, -1, 'Save to config file', size=(-1, 30))
		sizer.Add(button0, (18, 0), (1, 1),  wx.LEFT, 10)

		button1 = wx.Button(panel, -1, 'Temporally Apply', size=(-1, 30))
		sizer.Add(button1, (18, 1), (1, 1),  wx.LEFT, 10)

		button2 = wx.Button(panel, -1, 'Close', size=(-1, 30))
		sizer.Add(button2, (18, 2), (1, 1),  wx.LEFT | wx.BOTTOM | wx.RIGHT, 10)
		sizer.AddGrowableCol(2)

		panel.SetSizer(sizer)
		sizer.Fit(self)
		#Event
		self.Bind(wx.EVT_BUTTON, self.OnSave, button0)
		self.Bind(wx.EVT_BUTTON, self.OnApply, button1)
		self.Bind(wx.EVT_BUTTON, self.OnClose, button2)

	def OnApply(self,e):
		global OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, LEFT_X, LOWER_Y, CAD_UNIT, GERBER_COLOR, DRILL_COLOR, EDGE_COLOR , CONTOUR_COLOR, GERBER_EXT, DRILL_EXT, EDGE_EXT, GCODE_EXT, GDRILL_EXT, GEDGE_EXT, DRILL_UNIT, EDGE_UNIT, CUT_FLAG, CUT_OV
		IN_INCH_FLAG = int(self.rb1.GetSelection())
		OUT_INCH_FLAG = int(self.rb2.GetSelection())
		MCODE_FLAG = int(self.cb1.IsChecked())
		LEFT_X = float(self.leftx.GetValue())
		LOWER_Y = float(self.lowy.GetValue())
		CAD_UNIT = float(self.cadunit.GetValue())
		GERBER_COLOR = str(self.gerber_color.GetValue())
		DRILL_COLOR = str(self.drill_color.GetValue())
		EDGE_COLOR = str(self.edge_color.GetValue())
		CONTOUR_COLOR = str(self.contour_color.GetValue())
		GERBER_EXT = str(self.gerber_ext.GetValue())
		DRILL_EXT = str(self.drill_ext.GetValue())
		EDGE_EXT = str(self.edge_ext.GetValue())
		GCODE_EXT = str(self.gcode_ext.GetValue())
		GDRILL_EXT = str(self.gdrill_ext.GetValue())
		GEDGE_EXT = str(self.gedge_ext.GetValue())
		DRILL_UNIT = float(self.drillunit.GetValue())
		EDGE_UNIT  = float(self.edgeunit.GetValue())
		CUT_FLAG = int(self.rb_cut.GetSelection())
		CUT_OV  = float(self.cut_ov.GetValue())
		#show_all_values()
		self.Close(True)  # Close the frame.
	def OnClose(self,e):
		self.Close(True)  # Close the frame.
	def OnSave(self,e):
		global OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, LEFT_X, LOWER_Y, CAD_UNIT, GERBER_COLOR, DRILL_COLOR, EDGE_COLOR , CONTOUR_COLOR, GERBER_EXT, DRILL_EXT, EDGE_EXT, GCODE_EXT, GDRILL_EXT, GEDGE_EXT, DRILL_UNIT, EDGE_UNIT, CUT_FLAG, CUT_OV
		IN_INCH_FLAG = int(self.rb1.GetSelection())
		OUT_INCH_FLAG = int(self.rb2.GetSelection())
		MCODE_FLAG = int(self.cb1.IsChecked())
		LEFT_X = float(self.leftx.GetValue())
		LOWER_Y = float(self.lowy.GetValue())
		CAD_UNIT = float(self.cadunit.GetValue())
		GERBER_COLOR = str(self.gerber_color.GetValue())
		DRILL_COLOR = str(self.drill_color.GetValue())
		EDGE_COLOR = str(self.edge_color.GetValue())
		CONTOUR_COLOR = str(self.contour_color.GetValue())
		GERBER_EXT = str(self.gerber_ext.GetValue())
		DRILL_EXT = str(self.drill_ext.GetValue())
		EDGE_EXT = str(self.edge_ext.GetValue())
		GCODE_EXT = str(self.gcode_ext.GetValue())
		GDRILL_EXT = str(self.gdrill_ext.GetValue())
		GEDGE_EXT = str(self.gedge_ext.GetValue())
		DRILL_UNIT = float(self.drillunit.GetValue())
		EDGE_UNIT  = float(self.edgeunit.GetValue())
		CUT_FLAG = int(self.rb_cut.GetSelection())
		CUT_OV  = float(self.cut_ov.GetValue())
		save_config()
		self.Close(True)  # Close the frame.

class ConvSetup2(wx.Dialog):
	def __init__(self, parent, id, title):
		global CONFIG_FILE
		self.cfg = wx.Config(CONFIG_FILE)
		if self.cfg.Exists('width'):
			w, h = self.cfg.ReadInt('width'), self.cfg.ReadInt('height')
		else:
			(w, h) = (250, 250)
		wx.Dialog.__init__(self, parent, id, title, size=(w, h))

		wx.StaticText(self, -1, 'Width:', (20, 20))
		wx.StaticText(self, -1, 'Height:', (20, 70))
		self.sc1 = wx.SpinCtrl(self, -1, str(w), (80, 15), (60, -1), min=200, max=500)
		self.sc2 = wx.SpinCtrl(self, -1, str(h), (80, 65), (60, -1), min=200, max=500)
		wx.Button(self, 1, 'Save', (20, 120))

		self.Bind(wx.EVT_BUTTON, self.OnSave, id=1)
		#self.statusbar = self.CreateStatusBar()
		self.Centre()
		self.Show(True)

	def OnSave(self, event):
		self.cfg.WriteInt("width", self.sc1.GetValue())
		self.cfg.WriteInt("height", self.sc2.GetValue())
		self.statusbar.SetStatusText('Configuration saved, %s ' % wx.Now())


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
class LINE2:
	def __init__(self, p1, p2, inside, delete):
		self.p1 = p1
		self.p2 = p2
		self.inside = inside
		self.delete = delete

class POINT:
	def __init__(self, x, y, inside, delete):
		self.x = x
		self.y = y
		self.inside = inside
		self.delete = delete

class DRILL:
	def __init__(self, x, y, d, delete):
		self.x = x
		self.y = y
		self.d = d
		self.delete = delete

class DRILL_LINE:
	def __init__(self, x1, y1, x2, y2, d, delete):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
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
	app = wx.App()
	MainFrame(None, -1, 'pyGerber2Gcode')
	app.MainLoop()

def gerber2draw():
	global gPOLYGONS, gDRILLS, gDRILL_LINES, gEDGES, gPATTERNS, CENTER_X, CENTER_Y, gDRAWDRILL, gDRAWEDGE
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
	for drill_l in gDRILL_LINES:
		x1 = drill_l.x1
		y1 = -drill_l.y1
		x2 = drill_l.x2
		y2 = -drill_l.y2
		d = drill_l.d
		dpoints = draw_drill_line(x1,y1,x2,y2,d)
		i = 0
		points = []
		while i < len(dpoints)-1:
			#x = polygon.points[i] + CENTER_X
			#y = -polygon.points[i + 1] + CENTER_Y
			x = dpoints[i]
			y = dpoints[i + 1]
			points.append([x,y])
			i += 2
		#print points
		gDRAWDRILL_LINE.append(DRAWPOLY(points,"",0))
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
	global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT, EDGE_TOOL_D, EDGE_DEPTH, EDGE_SPEED, EDGE_Z_SPEED, MERGE_DRILL_DATA, Z_STEP, GERBER_COLOR, DRILL_COLOR, EDGE_COLOR , CONTOUR_COLOR, GERBER_EXT, DRILL_EXT, EDGE_EXT, GCODE_EXT, GDRILL_EXT, GEDGE_EXT, DRILL_UNIT, EDGE_UNIT, CUT_FLAG, CUT_OV 

	config_data =""
	config_data += "INI_X=" + str(INI_X) + "\n"
	config_data += "INI_Y=" + str(INI_Y) + "\n"
	config_data += "INI_Z=" + str(INI_Z) + "\n"
	config_data += "MOVE_HEIGHT=" + str(MOVE_HEIGHT) + "\n"
	config_data += "IN_INCH_FLAG=" + str(IN_INCH_FLAG) + "\n"
	config_data += "OUT_INCH_FLAG=" + str(OUT_INCH_FLAG) + "\n"
	config_data += "CUT_FLAG=" + str(CUT_FLAG) + "\n"
	config_data += "CUT_OV=" + str(CUT_OV ) + "\n"
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
	config_data += "DRILL_UNIT=" + str(DRILL_UNIT) + "\n"
	config_data += "EDGE_UNIT=" + str(EDGE_UNIT) + "\n"
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
	global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT, EDGE_TOOL_D, EDGE_DEPTH, EDGE_SPEED, EDGE_Z_SPEED, MERGE_DRILL_DATA, Z_STEP, GERBER_COLOR, DRILL_COLOR, EDGE_COLOR , CONTOUR_COLOR, GERBER_EXT, DRILL_EXT, EDGE_EXT, GCODE_EXT, GDRILL_EXT, GEDGE_EXT, DRILL_UNIT, EDGE_UNIT, CUT_FLAG, CUT_OV
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
				if(cfg.group(1)=="CUT_FLAG"):
					CUT_FLAG = int(cfg.group(2))
				if(cfg.group(1)=="CUT_OV"):
					CUT_OV = float(cfg.group(2))
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
				if(cfg.group(1)=="DRILL_UNIT"):
					DRILL_UNIT = float(cfg.group(2))
				if(cfg.group(1)=="EDGE_UNIT"):
					EDGE_UNIT = float(cfg.group(2))
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
	global gTMP_EDGE_X, gTMP_EDGE_Y, gTMP_EDGE_Z, gEDGE_DATA, gEDGES, EDGE_UNIT, OUT_INCH_FLAG, IN_INCH_FLAG
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
				x = float(xx.group(1)) * EDGE_UNIT
				#if (x != gTMP_EDGE_X):
					#gTMP_EDGE_X = x
			if (yy):
				y = float(yy.group(1)) * EDGE_UNIT
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
		if (find(gerber, "D") == 0):
			parse_d(gerber)
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
def parse_d(gerber):
	global g54_FLAG, gFIG_NUM
	#print gerber
	index_d=find(gerber, "D")
	index_ast=find(gerber, "*")
	g54_FLAG = 1
	gFIG_NUM=gerber[index_d+1:index_ast]
	#print gFIG_NUM
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
	global gGCODES,TINY
	print "Check overlapping lines ..."
	i = 0

	while i< len(gGCODES)-1:
		if(gGCODES[i].gtype == 0):
			i += 1
			continue
		m_x1_flag=0
		m_y1_flag=0
		#xi1=gGCODES[i].x1
		#yi1=gGCODES[i].y1
		#xi2=gGCODES[i].x2
		#yi2=gGCODES[i].y2
		ti=gGCODES[i].gtype
		xi_min=gGCODES[i].x1
		xi_max=gGCODES[i].x2
		yi_min=gGCODES[i].y1
		yi_max=gGCODES[i].y2
		if(gGCODES[i].x1>gGCODES[i].x2):
			xi_min=gGCODES[i].x2
			xi_max=gGCODES[i].x1
			m_x1_flag=1
		if(gGCODES[i].y1>gGCODES[i].y2):
			yi_min=gGCODES[i].y2
			yi_max=gGCODES[i].y1
			m_y1_flag=1
		j = i + 1
		while j< len(gGCODES):
			if(gGCODES[j].gtype == 0):
				j += 1
				continue
			if(gGCODES[i].gtype == 0):
				#j += 1
				break
			m_x2_flag=0
			m_y2_flag=0
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
				m_x2_flag=1
			if(yj1>yj2):
				yj_min=yj2
				yj_max=yj1
				m_y2_flag=1
			#if(xj_min>=xi_max or xj_max<=xi_min):
					#continue
			#if((xj_min>=xi_min and xj_max>=xi_max) or (xj_min<=xi_min and xj_max<=xi_max)):
					#continue
			
			if(ti == tj):	#same type
				if(ti == 3 or ti == 4):
					dxi=gGCODES[i].x2-gGCODES[i].x1
					dyi=gGCODES[i].y2-gGCODES[i].y1
					dxj=xj2-xj1
					dyj=yj2-yj1
					if(abs(dxi) >= TINY):
						ai=dyi/dxi
						bi=gGCODES[i].y1-ai*gGCODES[i].x1
						if(abs(dxj) >= TINY):
							aj=dyj/dxj
							bj=yj1-aj*xj1
							if(abs(aj-ai) < TINY and abs(bj-bi) < TINY):
								#print "a=" + str(ai)
								if(xj_min>=xi_min):
									#print "a"
									if(xj_max<=xi_max):
										#print "aa"
										#overlap
										if(gGCODES[i].mod1 >= gGCODES[j].mod1):
											gGCODES[j].gtype=0
									elif(xi_max >= xj_min):	# xj_max > xi_max
										if(gGCODES[i].mod1 == gGCODES[j].mod1):
											#print "ab i=" +str(i) + ", j=" + str(j)
											gGCODES[j].gtype=0
											#gGCODES[i].x1 = xi_min
											#gGCODES[i].y1 = gGCODES[i].y1
											if(m_x1_flag):	#if xi_min = gGCODES[i].x2
												gGCODES[i].x1 = xi_min
												gGCODES[i].y1 = gGCODES[i].y2
											gGCODES[i].x2 = xj_max
											gGCODES[i].y2 = yj2
											xi_max = xj_max
											if(m_x2_flag):	#if xj_max = xj1
												gGCODES[i].y2 = yj1
								elif(xj_min<=xi_min):
									#print "b"
									if(xj_max>=xi_max):
										#print "ba"
										#overlap
										if(gGCODES[i].mod1 <= gGCODES[j].mod1):
											gGCODES[i].gtype=0
									elif(xj_max >= xi_min):	# xj_max < xi_max
										if(gGCODES[i].mod1 == gGCODES[j].mod1):
											#print "bb i=" +str(i) + ", j=" + str(j)
											gGCODES[j].gtype=0
											#print "x1=" +str(gGCODES[i].x1) +", y1=" +str(gGCODES[i].y1) +", x2=" +str(gGCODES[i].x2) +", y2=" +str(gGCODES[i].y2)
											#gGCODES[i].x2 = xi_max
											#gGCODES[i].y2 = gGCODES[i].y2
											if(m_x1_flag):	#if xi_max = gGCODES[i].x1
												gGCODES[i].x2 = xi_max
												gGCODES[i].y2 = gGCODES[i].y1
											gGCODES[i].x1 = xj_min
											gGCODES[i].y1 = gGCODES[j].y1
											xi_min = xj_min
											if(m_x2_flag):	#if xi_min = xj2
												gGCODES[i].y1 = gGCODES[j].y2
											#print "x1=" +str(gGCODES[i].x1) +", y1=" +str(gGCODES[i].y1) +", x2=" +str(gGCODES[i].x2) +", y2=" +str(gGCODES[i].y2)

					else:	#dxi==0
						if(dxj==0 and gGCODES[i].x1==xj1):
							if(yj_min>=yi_min):
								if(yj_max<=yi_max):
									if(gGCODES[i].mod1 >= gGCODES[j].mod1):
										#overlap
										gGCODES[j].gtype=0
								elif(yi_max > yj_min):
									if(gGCODES[i].mod1 == gGCODES[j].mod1):
										gGCODES[j].gtype=0
										#gGCODES[i].x1 = gGCODES[i].x1
										gGCODES[i].y1 = yi_min
										if(m_y1_flag):	#yi_min = gGCODES[i].y2
											gGCODES[i].x1 = gGCODES[i].x2
											#gGCODES[i].y1 = yi_min
										gGCODES[i].x2 = gGCODES[j].x2
										gGCODES[i].y2 = yj_max
										if(m_y2_flag):
											gGCODES[i].x2 = gGCODES[j].x1
							elif(yj_min<=yi_min):
								if(yj_max>=yi_max):
									if(gGCODES[i].mod1 <= gGCODES[j].mod1):
										#overlap
										gGCODES[i].gtype=0
								elif(yj_max > yi_min):
									if(gGCODES[i].mod1 == gGCODES[j].mod1):
										#gGCODES[i].x2 = GCODES[i].x2
										gGCODES[i].y2 = yi_max
										if(m_y1_flag):
											gGCODES[i].x2 = gGCODES[i].x1
											#gGCODES[i].y2 = yi_max
										gGCODES[i].x1 = GCODES[j].x1
										gGCODES[i].y1 = yj_min
										if(m_y2_flag):
											gGCODES[i].x1 = GCODES[j].x2
											#gGCODES[i].y1 = yj_min
			else:	#ti != tj
				if(ti == 2):
					if(tj == 3 or tj == 4):
						#print "rect ti"
						if(gGCODES[j].x1 == gGCODES[j].x2 and gGCODES[i].x1 == gGCODES[j].x1):	#Vertical
							#print "ti check x"
							if(gGCODES[i].mod1 == gGCODES[j].mod1):
								#print "ti check x mod1"
								#line = [gGCODES[i].x1,gGCODES[i].y1-gGCODES[i].mod2/2,gGCODES[i].x1,gGCODES[i].y1+gGCODES[i].mod2/2]
								x1=gGCODES[i].x1
								y1=gGCODES[i].y1-gGCODES[i].mod2/2
								x2=gGCODES[i].x1
								y2=gGCODES[i].y1+gGCODES[i].mod2/2
								xa=gGCODES[j].x1
								ya=gGCODES[j].y1
								xb=gGCODES[j].x2
								yb=gGCODES[j].y2
								ovflag = check_overlap(x1,y1,x2,y2,xa,ya,xb,yb,1)
								if(ovflag):	#Vertical 1-4	
									if(ovflag == 1):
										gGCODES[j].gtype=0
									if(ovflag == 3):
										gGCODES[i].gtype=0
									#print "ti overlap =" + str(ovflag)
									#print line_joint(x1,y1,x2,y2,xa,ya,xb,yb,ovflag)
									tx1,ty1,tx2,ty2=line_joint(x1,y1,x2,y2,xa,ya,xb,yb,ovflag)
									if(tj == 4):	#Rect
										#print "Rect-Rect"
										gGCODES[j].gtype = 0
										gGCODES[i].gtype = 4
										gGCODES[i].x1 = tx1
										gGCODES[i].y1 = ty1
										gGCODES[i].x2 = tx2
										gGCODES[i].y2 = ty2
									elif(tj == 3):
										#print "rect-cir"
										gGCODES[j].gtype = 0
										gGCODES[i].gtype = 5
										gGCODES[i].mod1 =gGCODES[j].mod1
										gGCODES[i].x1 = tx1
										gGCODES[i].y1 = ty1
										gGCODES[i].x2 = tx2
										gGCODES[i].y2 = ty2
										if(ovflag == 4):
											gGCODES[i].x1 = tx2
											gGCODES[i].y1 = ty2
											gGCODES[i].x2 = tx1
											gGCODES[i].y2 = ty1
						if(gGCODES[j].y1 == gGCODES[j].y2 and gGCODES[i].y1 == gGCODES[j].y1):	#Horizontal
							#print "ti check y"
							if(gGCODES[i].mod2 == gGCODES[j].mod1):
								#print "ti check y mod1"
								#line = [gGCODES[i].x1-gGCODES[i].mod1/2,gGCODES[i].y1,gGCODES[i].x1+gGCODES[i].mod1/2,gGCODES[i].y1]
								x1=gGCODES[i].x1-gGCODES[i].mod1/2
								y1=gGCODES[i].y1
								x2=gGCODES[i].x1+gGCODES[i].mod1/2
								y2=gGCODES[i].y1
								xa=gGCODES[j].x1
								ya=gGCODES[j].y1
								xb=gGCODES[j].x2
								yb=gGCODES[j].y2
								ovflag = check_overlap(x1,y1,x2,y2,xa,ya,xb,yb,0)
								if(ovflag):	#Horizontal 5-8
									if(ovflag == 5):
										gGCODES[j].gtype=0
									if(ovflag == 7):
										gGCODES[i].gtype=0	
									#print "ti overlap =" + str(ovflag)
									tx1,ty1,tx2,ty2=line_joint(x1,y1,x2,y2,xa,ya,xb,yb,ovflag)
									
									if(tj == 4):	#Rect
										#print "Rect-Rect"
										gGCODES[j].gtype = 0
										gGCODES[i].gtype = 4
										gGCODES[i].x1 = tx1
										gGCODES[i].y1 = ty1
										gGCODES[i].x2 = tx2
										gGCODES[i].y2 = ty2
									elif(tj == 3):
										#print "rect-cir"
										gGCODES[j].gtype = 0
										gGCODES[i].gtype = 5
										gGCODES[i].mod1 =gGCODES[j].mod1
										gGCODES[i].x1 = tx1
										gGCODES[i].y1 = ty1
										gGCODES[i].x2 = tx2
										gGCODES[i].y2 = ty2
										if(ovflag == 8):
											gGCODES[i].x1 = tx2
											gGCODES[i].y1 = ty2
											gGCODES[i].x2 = tx1
											gGCODES[i].y2 = ty1
				if(tj == 2):
					if(ti == 3 or ti == 4):
						#print "rect tj"
						if(gGCODES[i].x1 == gGCODES[i].x2 and gGCODES[i].x1 == gGCODES[j].x1):	#Vertical
							#print "ti check x"
							if(gGCODES[i].mod1 == gGCODES[j].mod1):
								#print "ti check x mod1"
								#line = [gGCODES[i].x1,gGCODES[i].y1-gGCODES[i].mod2/2,gGCODES[i].x1,gGCODES[i].y1+gGCODES[i].mod2/2]
								x1=gGCODES[j].x1
								y1=gGCODES[j].y1-gGCODES[j].mod2/2
								x2=gGCODES[j].x1
								y2=gGCODES[j].y1+gGCODES[j].mod2/2
								xa=gGCODES[i].x1
								ya=gGCODES[i].y1
								xb=gGCODES[i].x2
								yb=gGCODES[i].y2
								ovflag = check_overlap(x1,y1,x2,y2,xa,ya,xb,yb,1)
								if(ovflag):	#Vertical 1-4	
									if(ovflag == 1):
										gGCODES[j].gtype=0
									if(ovflag == 3):
										gGCODES[i].gtype=0
									#print "tj overlap =" + str(ovflag)
									#print line_joint(x1,y1,x2,y2,xa,ya,xb,yb,ovflag)
									tx1,ty1,tx2,ty2=line_joint(x1,y1,x2,y2,xa,ya,xb,yb,ovflag)
									if(tj == 4):	#Rect
										#print "Rect-Rect"
										gGCODES[j].gtype = 0
										gGCODES[i].gtype = 4
										gGCODES[i].x1 = tx1
										gGCODES[i].y1 = ty1
										gGCODES[i].x2 = tx2
										gGCODES[i].y2 = ty2
									elif(tj == 3):
										#print "rect-cir"
										gGCODES[j].gtype = 0
										gGCODES[i].gtype = 5
										gGCODES[i].mod1 =gGCODES[j].mod1
										gGCODES[i].x1 = tx1
										gGCODES[i].y1 = ty1
										gGCODES[i].x2 = tx2
										gGCODES[i].y2 = ty2
										if(ovflag == 4):
											gGCODES[i].x1 = tx2
											gGCODES[i].y1 = ty2
											gGCODES[i].x2 = tx1
											gGCODES[i].y2 = ty1
						if(gGCODES[i].y1 == gGCODES[i].y2 and gGCODES[i].y1 == gGCODES[j].y1):	#Horizontal
							#print "ti check y"
							if(gGCODES[i].mod1 == gGCODES[j].mod2):
								#print "ti check y mod1"
								#line = [gGCODES[i].x1-gGCODES[i].mod1/2,gGCODES[i].y1,gGCODES[i].x1+gGCODES[i].mod1/2,gGCODES[i].y1]
								x1=gGCODES[j].x1-gGCODES[j].mod1/2
								y1=gGCODES[j].y1
								x2=gGCODES[j].x1+gGCODES[j].mod1/2
								y2=gGCODES[j].y1
								xa=gGCODES[i].x1
								ya=gGCODES[i].y1
								xb=gGCODES[i].x2
								yb=gGCODES[i].y2
								ovflag = check_overlap(x1,y1,x2,y2,xa,ya,xb,yb,0)
								if(ovflag):	#Horizontal 5-8
									if(ovflag == 5):
										gGCODES[j].gtype=0
									if(ovflag == 7):
										gGCODES[i].gtype=0	
									#print "tj overlap =" + str(ovflag)
									tx1,ty1,tx2,ty2=line_joint(x1,y1,x2,y2,xa,ya,xb,yb,ovflag)
									
									if(tj == 4):	#Rect
										#print "Rect-Rect"
										gGCODES[j].gtype = 0
										gGCODES[i].gtype = 4
										gGCODES[i].x1 = tx1
										gGCODES[i].y1 = ty1
										gGCODES[i].x2 = tx2
										gGCODES[i].y2 = ty2
									elif(tj == 3):
										#print "rect-cir"
										gGCODES[j].gtype = 0
										gGCODES[i].gtype = 5
										gGCODES[i].mod1 =gGCODES[j].mod1
										gGCODES[i].x1 = tx1
										gGCODES[i].y1 = ty1
										gGCODES[i].x2 = tx2
										gGCODES[i].y2 = ty2
										if(ovflag == 8):
											gGCODES[i].x1 = tx2
											gGCODES[i].y1 = ty2
											gGCODES[i].x2 = tx1
											gGCODES[i].y2 = ty1
			j += 1
		#print "total x1=" +str(gGCODES[i].x1) +", y1=" +str(gGCODES[i].y1) +", x2=" +str(gGCODES[i].x2) +", y2=" +str(gGCODES[i].y2)
		i +=1
def line_joint(x1,y1,x2,y2,xa,ya,xb,yb,ovflag):
	if(ovflag == 2):	#Vertical 2
		ox1=x1
		oy1=y1
		oy2=yb
		ox2=x2
		if(y1>y2):
			oy1=y2
		if(ya>yb):
			oy2=ya
	elif(ovflag == 4):	#Vertical 4
		ox1=x1
		ox2=x2
		oy1=ya
		oy2=y2
		if(y1>y2):
			oy2=y1
		if(ya>yb):
			oy1=yb
	elif(ovflag == 6):	#Horizontal
		ox1=x1
		ox2=xb
		oy1=y1
		oy2=y2
		if(x1>x2):
			ox1=x2
		if(xa>xb):
			ox2=xa
	elif(ovflag == 8):	#Horizontal
		ox1=xa
		ox2=x2
		oy1=y1
		oy2=y2
		if(x1>x2):
			ox2=x1
		if(xa>xb):
			ox1=xb
	else:
		return (0,0,0,0)
	return (ox1,oy1,ox2,oy2)
def check_overlap(x1,y1,x2,y2,xa,ya,xb,yb,sw):
	if(sw):	#Vertical
		if(y2 < y1):	#x2 < x1
			tmpy = y1
			y1 = y2
			y2 = tmpy
		if(yb < ya):	#xb < xa
			tmpy = ya
			ya = yb
			yb = tmpy
		if(y1 <= ya and y2 >= ya):
			if(y2 >= yb):
				# line 2 is in line1
				return 1
			elif(y2 < yb):
				return 2
		elif(y1 <= yb and y2 >= yb):
			return 4
		elif(y1 > ya and y2 < yb):
			return 3
		else:
			return 0
	else:	#Horizontal
		if(x2 < x1):	#x2 < x1
			tmpx = x1
			x1 = x2
			x2 = tmpx
		if(xb < xa):	#xb < xa
			tmpx = xa
			xa = xb
			xb = tmpx
		if(x1 <= xa and x2 >= xa):
			if(x2 >= xb):
				# line 2 is in line1
				return 5
			elif(x2 < xb):
				return 6
		elif(x1 <= xb and x2 >= xb):
			return 8
		elif(x1 > xa and x2 < xb):
			return 7
		else:
			return 0
def gerber2polygon4draw():
	global gGCODES, TOOL_D
	for gcode in gGCODES:
		if(gcode.gtype == 5):
			continue
		#print gcode
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
		if(gcode.gtype == 0):
			continue
		x1=gcode.x1
		y1=gcode.y1
		x2=gcode.x2
		y2=gcode.y2
		mod1=gcode.mod1 + float(TOOL_D)
		mod2=gcode.mod2 + float(TOOL_D)
		if(gcode.gtype == 1):
			#polygon(circle_points(x1,y1,mod1/2,20))
			gPOLYGONS.append(POLYGON(x1-mod1/2,x1+mod1/2,y1-mod1/2,y1+mod1/2,circle_points(x1,y1,mod1/2,20),0))
		elif(gcode.gtype == 2):
			points = [x1-mod1/2,y1-mod2/2,x1-mod1/2,y1+mod2/2,x1+mod1/2,y1+mod2/2,x1+mod1/2,y1-mod2/2,x1-mod1/2,y1-mod2/2]
			#polygon([x1-mod1/2,y1-mod2/2,x1-mod1/2,y1+mod2/2,x1+mod1/2,y1+mod2/2,x1+mod1/2,y1-mod2/2,x1-mod1/2,y1-mod2/2])
			gPOLYGONS.append(POLYGON(x1-mod1/2,x1+mod1/2,y1-mod2/2,y1+mod2/2,points,0))
		elif(gcode.gtype == 3):
			line2poly(x1,y1,x2,y2,mod1/2,1,8)
		elif(gcode.gtype == 4):
			line2poly(x1,y1,x2,y2,mod2/2,0,8)
		elif(gcode.gtype == 5):
			line2poly(x1,y1,x2,y2,mod1/2,2,8)

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
	if(atype==1):
		points = points + arc_points(x1,y1,r,ang+3*deg90,ang+deg90,ang_n)
		points = points + arc_points(x2,y2,r,ang+deg90,ang-deg90,ang_n)
		points = points + [xa2,ya2]
	elif(atype==2):
		points = points + [xa2,ya2,xa1,ya1]
		points = points + arc_points(x2,y2,r,ang+deg90,ang-deg90,ang_n)
		points = points + [xa2,ya2]
	else:
		points=(xa1,ya1,xb1,yb1,xb2,yb2,xa2,ya2,xa1,ya1)
	polygon(points)

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

def polygon2line(points,sw):
	global gLINES,gLINES2
	i = 0
	while i< len(points)-2:
		if(sw):
			gLINES2.append(LINE(points[i],points[i+1],points[i+2],points[i+3],0,0))
		else:
			gLINES.append(LINE(points[i],points[i+1],points[i+2],points[i+3],0,0))
		i += 2

def merge():
	global gPOLYGONS, gLINES,PRE_IN_FLAG,gLINES2
	#check_duplication()
	#gerber2polygon()
	print "Start merge polygons"
	for poly1 in gPOLYGONS:
		PRE_IN_FLAG = -1
		out_points=[]
		if(poly1.delete):
			continue
		x_max=poly1.x_max
		x_min=poly1.x_min
		y_max=poly1.y_max
		y_min=poly1.y_min
		start_line_id=len(gLINES)
		polygon2line(poly1.points,0)
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
			start_line_id2=len(gLINES2)
			polygon2line(poly2.points,1)
			end_line_id2=len(gLINES2)
			k = start_line_id
			while k < end_line_id:
				CrossAndIn(k,poly2.points)
				k += 1
			end_line_id = len(gLINES)

	for poly3 in gPOLYGONS:
		#del all polygons
		poly3.delete = 1

	#line_merge()
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
	#merge_polygons()


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

def IsLineParallel(line1,line2):
	global TINY
	dx1 = line1.x2-line1.x1
	dy1 = line1.y2-line1.y1
	dx2 = line2.x2-line2.x1
	dy2 = line2.y2-line2.y1
	if(abs(dx1) < TINY):
		if(abs(dx2) < TINY):
			return 1
		else:
			return 0
	else:
		if(abs(dx2) < TINY):
			return 0
		else:
			a1 = (dy1)/(dx1)
			a2 = (dy2)/(dx2)
			if(abs(a1-a2) < TINY):
				return 1
			else:
				return 0
def IsLineOverlap(x1,y1,x2,y2,xa,ya,xb,yb):
	global TINY
	#print "check overlap"
	dx1 = x2-x1
	dy1 = y2-y1
	dx2 = xb-xa
	dy2 = yb-ya
	if(abs(dx1)  < TINY):
		if(abs(dx2) < TINY):	#Vertical
			if(abs(x1-xa) < TINY):
				if(dy1 > 0):	#+
					if(y1 <= ya and y2 >= ya):
						return 1
					if(y1 <= yb and y2 >= yb):
						return 2
				elif(dy1 < 0):	#-
					if(y2 <= ya and y1 >= ya):
						return 3
					if(y2 <= yb and y1 >= yb):
						return 4
				return 0
			else:
				return 0
		else:
			return 0
	else:
		if(abs(dx2) < TINY):
			return 0
		else:
			a1 = (dy1)/(dx1)
			b1 = y1-a1*x1
			a2 = (dy2)/(dx2)
			b2 = ya-a2*xa
			if(abs(a1-a2) < TINY):
				#print "same angle " + str(a1 )+ ", b1=" + str(b1)+ ", b2=" + str(b2) + ", b2-b1=" + str(abs(b2-b1)) +", y1=" +str(y1) + ", ya=" + str(ya)
				if(abs(b2-b1) < TINY):	#Horizontal
					#print "same b " + str(b1)
					if(dx1 > 0):	#+
						if(x1 <= xa and x2 >= xa):
							return 5
						if(x1 <= xb and x2 >= xb):
							return 6	#
					elif(dx1 < 0):	#-
						if(x2 <= xa and x1 >= xa):
							return 7 #
						if(x2 <= xb and x1 >= xb):
							return 8
				else:
					return 0
			else:
				return 0
	return 0
def IsLineOverlap2(line1,line2):
	global TINY
	dx1 = line1.x2-line1.x1
	dy1 = line1.y2-line1.y1
	dx2 = line2.x2-line2.x1
	dy2 = line2.y2-line2.y1
	if(abs(dx1)  < TINY):
		if(abs(dx2) < TINY):
			if(abs(line1.x1-line2.x1) < TINY):
				if(dy1 > 0):	#+
					if(line1.y1 <= line2.y1 and line1.y2 >= line2.y1):
						return 1
					if(line1.y1 <= line2.y2 and line1.y2 >= line2.y2):
						return 1
				elif(dy1 < 0):	#-
					if(line1.y2 <= line2.y1 and line1.y1 >= line2.y1):
						return 1
					if(line1.y2 <= line2.y2 and line1.y1 >= line2.y2):
						return 1
				return 0
			else:
				return 0
		else:
			return 0
	else:
		if(abs(dx2) < TINY):
			return 0
		else:
			a1 = (dy1)/(dx1)
			a2 = (dy2)/(dx2)
			if(abs(a1-a2) < TINY):
				if(dy1 > 0):	#+
					if(line1.y1 <= line2.y1 and line1.y2 >= line2.y1):
						return 1
					if(line1.y1 <= line2.y2 and line1.y2 >= line2.y2):
						return 1
				elif(dy1 < 0):	#-
					if(line1.y2 <= line2.y1 and line1.y1 >= line2.y1):
						return 1
					if(line1.y2 <= line2.y2 and line1.y1 >= line2.y2):
						return 1
				return 0
			else:
				return 0
def GetLineDist(line1,line2):
	global TINY
	dx = line1.x2-line1.x1
	dy = line1.y2-line1.y1
	a = dx * dx + dy * dy
	if(a < TINY):
		dist1 = calc_dist(line1.x1,line1.y1,line2.x1,line2.y1)
		dist2 = calc_dist(line1.x1,line1.y1,line2.x2,line2.y2)
	else:
		b1 = dx * (line1.x1-line2.x1) + dy * (line1.y1-line2.y1)
		b2 = dx * (line1.x1-line2.x2) + dy * (line1.y1-line2.y2)
		t1 =  - (b1 / a)
		t2 =  - (b2 / a)
		if(t1 < 0.0):
			t1 = 0.0
		if(t1 > 1.0):
			t1 = 1.0
		if(t2 < 0.0):
			t2 = 0.0
		if(t2 > 1.0):
			t2 = 1.0
		x1 = t1 * dx + line1.x1
		y1 = t1 * dy + line1.y1
		x2 = t2 * dx + line1.x2
		y2 = t2 * dy + line1.y2
		dist1 = calc_dist(x1,y1,line2.x1,line2.y1)
		dist2 = calc_dist(x2,y2,line2.x2,line2.y2)

		if(abs(dist1-dist2) < TINY):
			return dist1
		else:
			if(dist1 >= dist2):
				return dist1
			else:
				return dist2
def CrossAndIn(line_id,spoints):
	global gLINES, gCCOUNT1, gCCOUNT2,TEST_POINTS1,TEST_POINTS2
	#check in or out
	#print line_id
	if(gLINES[line_id].inside):
		return
	xa = gLINES[line_id].x1
	ya = gLINES[line_id].y1
	xb = gLINES[line_id].x2
	yb = gLINES[line_id].y2
	cross_count1 = 0
	cross_count2 = 0
	cross_points = []
	cross_nums = []
	cross_num = 0
	cross_flag = 0
	tmp_flag = 0
	return_flag = 0
	ovflag = 0
	si = 0
	while si< len(spoints)-2:
		xp1=spoints[si]
		yp1=spoints[si+1]
		xp2=spoints[si+2]
		yp2=spoints[si+3]
		if(IsLineOverlap(xa,ya,xb,yb,xp1,yp1,xp2,yp2)):
			ovflag = 1
		(cross_flag,cross_x,cross_y)=find_cross_point(xa,ya,xb,yb,xp1,yp1,xp2,yp2)
		cross_num+=cross_flag
		if(cross_flag):
			#print "cross"
			cross_points.extend([cross_x,cross_y])
			cross_nums.append(si)
			#ovflag = IsLineOverlap(xa,ya,xb,yb,xp1,yp1,xp2,yp2)
			#print ovflag
		#reset flags
		flagX1 = 0
		flagX2 = 0
		flagY1 = 0
		flagY2 = 0
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
		#TEST_POINTS1.append([xa,ya])
		#if(line_id > 9):
			#TEST_POINTS1.append([xa,ya])
		if(line_id == 1):
			TEST_POINTS1.append([xa,ya])
			TEST_POINTS1.append([xp1,yp1])
	else:
		in_flag1 = 0
		if(line_id == 1):
			TEST_POINTS1.append([xa,ya])
			TEST_POINTS1.append([xp1,yp1])
	if(cross_count2):#
		in_flag2 = 1
		if(line_id == 1):
			TEST_POINTS2.append([xb,yb])
			TEST_POINTS2.append([xp2,yp2])
		#if(line_id <= 9):
			#TEST_POINTS1.append([xb,yb])
		#if(line_id > 9):
			#TEST_POINTS2.append([xb,yb])
	else:
		in_flag2 = 0
		if(line_id == 1):
			TEST_POINTS2.append([xb,yb])
			TEST_POINTS2.append([xp2,yp2])
	PRE_IN_FLAG = in_flag2
	#print "line=" +str(line_id) + ", Cross point num =" + str(cross_num)
	#if(line_id == 16):
		#print "Cross point num =" + str(cross_num)
		#TEST_POINTS2.append([cross_points[0],cross_points[1]])
	#if(cross_num > 0):
		#ovflag = IsLineOverlap(xa,ya,xb,yb,xp1,yp1,xp2,yp2)
		#if(ovflag):
			#print "overlap " + str(line_id) + ", cross_num " + str(cross_num) + ", ovflag" + str(ovflag)

	if(cross_num>1):
		cross_points = sort_points_by_dist(xa,ya,cross_points)
		#print calc_dist(gLINES[line_id].x1,gLINES[line_id].y1,cross_points[0],cross_points[1])
		if(calc_dist(gLINES[line_id].x1,gLINES[line_id].y1,cross_points[0],cross_points[1])<=0.0):
			if(in_flag1 != in_flag2):
				gLINES[line_id].inside = 1
			else:
				gLINES[line_id].inside = in_flag1
			tmp_flag = in_flag1
			tmp_x=gLINES[line_id].x1
			tmp_y=gLINES[line_id].y1
		else:
			gLINES[line_id].x2 = cross_points[0]
			gLINES[line_id].y2 = cross_points[1]
			gLINES[line_id].inside = in_flag1
			tmp_x=cross_points[0]
			tmp_y=cross_points[1]
		if(in_flag1):
			tmp_flag=0
		else:
			tmp_flag=1
		i = 2
		while i < len(cross_points)-2:
			gLINES.append(LINE(tmp_x,tmp_y,cross_points[i],cross_points[i+1],tmp_flag,0))
			if(in_flag1):
				tmp_flag = 0
			else:
				tmp_flag = 1
			tmp_x=cross_points[i]
			tmp_y=cross_points[i+1]
			i += 2
		#end while
		if(calc_dist(cross_points[len(cross_points)-2],cross_points[len(cross_points)-1],xb,yb)>0.0):
			gLINES.append(LINE(cross_points[len(cross_points)-2],cross_points[len(cross_points)-1],xb,yb,in_flag2,0))
	
	elif(cross_num==1):
		if(in_flag1 == in_flag2):
			#in in
			gLINES[line_id].inside=in_flag1
			#print "in-in or Out-OUT:flag="+str(in_flag1)+ ", id=" +str(line_id)
		else:
			#in out
			if(ovflag <=0):
				gLINES[line_id].x2 = cross_points[0]
				gLINES[line_id].y2 = cross_points[1]
				gLINES[line_id].inside = in_flag1
				gLINES.append(LINE(cross_points[0],cross_points[1],xb,yb,in_flag2,0))
			else:
				#overlap
				gLINES[line_id].x2 = cross_points[0]
				gLINES[line_id].y2 = cross_points[1]
				gLINES[line_id].inside = 0
				gLINES.append(LINE(cross_points[0],cross_points[1],xb,yb,0,0))
				#print line_id
				#if(in_flag2 == 1):
					#print line_id
					#gLINES.append(LINE(cross_points[0],cross_points[1]+0.1,xb,yb+0.1,in_flag1,0))
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

def CrossAndIn_test(line_id,spoints):
	global gLINES, gCCOUNT1, gCCOUNT2,TEST_POINTS1,TEST_POINTS2,PRE_IN_FLAG
	#check in or out
	#print line_id
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
		xp1=spoints[si]
		yp1=spoints[si+1]
		xp2=spoints[si+2]
		yp2=spoints[si+3]
		(cross_flag,cross_x,cross_y)=find_cross_point(xa,ya,xb,yb,xp1,yp1,xp2,yp2)
		cross_num+=cross_flag
		if(cross_flag):
			cross_points.extend([cross_x,cross_y])
			cross_nums.append(si)
		if(PRE_IN_FLAG == -1):
			#reset flags
			flagX1 = 0
			flagX2 = 0
			flagY1 = 0
			flagY2 = 0
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
			if(cross_count1):#
				in_flag1 = 1
				#TEST_POINTS1.append([xa,ya])
			else:
				in_flag1 = 0
		else:
			in_flag1 = PRE_IN_FLAG
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



	if(cross_count2):#
		in_flag2 = 1
		if(line_id <= 8):
			TEST_POINTS1.append([xb,yb])
		if(line_id > 8):
			TEST_POINTS2.append([xb,yb])
	else:
		in_flag2 = 0
	PRE_IN_FLAG = in_flag2

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
			#print "in-in or Out-OUT:flag="+str(in_flag1)+ ", id=" +str(line_id)
		else:
			#in out
			gLINES[line_id].x2 = cross_points[0]
			gLINES[line_id].y2 = cross_points[1]
			gLINES[line_id].inside = in_flag1
			gLINES.append(LINE(cross_points[0],cross_points[1],xb,yb,in_flag2,0))
			if(in_flag2 == 1):
				#print line_id
				gLINES.append(LINE(cross_points[0],cross_points[1]+0.1,xb,yb+0.1,in_flag1,0))
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
def disp_test_points():
	global TEST_POINTS1,TEST_POINTS2,gPOLYGONS
	#print "disp in point"
	for point in TEST_POINTS1:
		points = circle_points(point[0],point[1],0.01,20)
		gPOLYGONS.append(POLYGON(0, 0, 0, 0,points,0))	
	for point in TEST_POINTS2:
		points = circle_points(point[0],point[1],0.03,20)
		gPOLYGONS.append(POLYGON(0, 0, 0, 0,points,0))	
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
	global gDRILL_D, gDRILL_TYPE, DRILL_UNIT,gUNIT,INCH
	f = open(drill_file,'r')
	print "Read and Parse Drill data"
	drill_d_unit = DRILL_UNIT
	while 1:
		drill = f.readline()
		if not drill:
			break
		drill_data = re.search("T([\d]+)C([\d\.]+)",drill)
		drill_num = re.search("T([\d]+)\s",drill)
		if(drill_data):
			gDRILL_TYPE[int(drill_data.group(1))] = drill_data.group(2)
		if(drill_num):
			#print drill_d_unit
			gDRILL_D=float(gDRILL_TYPE[int(drill_num.group(1))]) * drill_d_unit
			#gDRILL_D=float(gDRILL_TYPE[int(drill_num.group(1))]) * gUNIT
		if (find(drill, "G") != -1):
			parse_drill_g(drill)
		elif (find(drill, "X") != -1 or find(drill, "Y") != -1):
			parse_drill_xy(drill)
		if (find(drill, "INCH") != -1):
			drill_d_unit = INCH
			#print "Drill Diameter = INCH"
		if (find(drill, "M72") != -1):
			#print "Drill unit = INCH"
			DRILL_UNIT = INCH
	f.close()
def parse_drill_g(drill):
	global gDRILL_LINES, gDRILL_D, DRILL_UNIT
	#print "Drill G";
	#xx = re.search("X([\d\.-]+)\D",drill)
	#yy = re.search("Y([\d\.-]+)\D",drill)
	xy = re.search("X([\d\.-]+)Y([\d\.-]+)\D[\d]+X([\d\.-]+)Y([\d\.-]+)",drill)
	#if(xx):
	#	x=float(xx.group(1)) * DRILL_UNIT
	#if(yy):
	#	y=float(yy.group(1)) * DRILL_UNIT
	if(xy):
		x1=float(xy.group(1)) * DRILL_UNIT
		y1=float(xy.group(2)) * DRILL_UNIT
		x2=float(xy.group(3)) * DRILL_UNIT
		y2=float(xy.group(4)) * DRILL_UNIT
		#print "x1=" + str(x1) + "y1=" + str(y1) + "x2=" + str(x2) + "y2=" + str(y2)
		gDRILL_LINES.append(DRILL_LINE(x1,y1,x2,y2,gDRILL_D,0))

def parse_drill_xy(drill):
	global gDRILLS,gDRILL_D, DRILL_UNIT
	xx = re.search("X([\d\.-]+)\D",drill)
	yy = re.search("Y([\d\.-]+)\D",drill)
	if(xx):
		x=float(xx.group(1)) * DRILL_UNIT
	if(yy):
		y=float(yy.group(1)) * DRILL_UNIT
	gDRILLS.append(DRILL(x,y,gDRILL_D,0))

def do_drill():
	global DRILL_SPEED, DRILL_DEPTH, gDRILLS, gDRILL_LINES, MOVE_HEIGHT, gDRILL_DATA, gGCODE_DATA, gTMP_DRILL_X, gTMP_DRILL_Y, gTMP_DRILL_Z, gTMP_X, gTMP_Y, gTMP_Z,MERGE_DRILL_DATA, gDRILL_D, DRILL_D, gXSHIFT, gYSHIFT
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
	#print "len gDRILL_LINES=" +str(len(gDRILL_LINES))
	for drill_l in gDRILL_LINES:
		x1 = drill_l.x1 + gXSHIFT
		y1 = drill_l.y1 + gYSHIFT
		x2 = drill_l.x2 + gXSHIFT
		y2 = drill_l.y2 + gYSHIFT

		drill_data += drill_line(x1,y1,x2,y2,drill_l.d)
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
def draw_drill_line(x1,y1,x2,y2,d):
	global DRILL_D
	drill_mergin = 0.02
	ang_n = 100
	points = []
	deg90 = pi/2.0
	if(d > DRILL_D + drill_mergin):
		r = d/2 - DRILL_D/2
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
		points = points + arc_points(x1,y1,r,ang+3*deg90,ang+deg90,ang_n)
		points = points + arc_points(x2,y2,r,ang+deg90,ang-deg90,ang_n)
		points = points + [xa2,ya2]
	else:
		points = [x1,y1,x2,y2]
	return points

def drill_line(x1,y1,x2,y2,d):
	global MOVE_HEIGHT, gTMP_DRILL_X, gTMP_DRILL_Y, gTMP_DRILL_Z, DRILL_SPEED, DRILL_DEPTH, Z_STEP, XY_SPEED, DRILL_D ,gDRAWDRILL_LINE
	out_data = ""
	gcode_tmp_flag = 0
	z_step_n = int(float(DRILL_DEPTH)/float(Z_STEP)) + 1
	z_step = float(DRILL_DEPTH)/z_step_n
	if(MOVE_HEIGHT != gTMP_DRILL_Z):
		gTMP_DRILL_Z = MOVE_HEIGHT
		out_data += "G00Z" + str(gTMP_DRILL_Z) + "\n"
	points = []
	ang_n = 100
	drill_mergin = 0.02
	deg90=pi/2.0
	if(d > DRILL_D + drill_mergin):
		r = d/2 - DRILL_D/2
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
		points = points + arc_points(x1,y1,r,ang+3*deg90,ang+deg90,ang_n)
		points = points + arc_points(x2,y2,r,ang+deg90,ang-deg90,ang_n)
		points = points + [xa2,ya2]
		tmp_x = xa2
		tmp_y = ya2
	else:
		points = [x1,y1,x2,y2]
		tmp_x = x2
		tmp_y = y2
	#gDRAWDRILL_LINE.append(DRAWPOLY(points,"",0))
	out_data += "G00X" + str(tmp_x) + "Y" + str(tmp_y) + "\n"
	#print z_step_n
	#print len(points)
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

	gTMP_DRILL_X = tmp_x
	gTMP_DRILL_Y = tmp_y
	return out_data

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
