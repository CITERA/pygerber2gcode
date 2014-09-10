#!/usr/bin/python
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

import gerber
import gcode
import gerber_shapely as gs
#Global Constant
HUGE = 1e10
TINY = 1e-6
MERGINE = 1e-6
INCH = 25.4 #mm
#MIL = INCH/1000
CONFIG_FILE = "./pyg2g.conf"
WINDOW_X = 1024
WINDOW_Y = 768
CENTER_X=200.0
CENTER_Y=200.0

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
DRILL_ENDMILL = 1
#for convert
MCODE_FLAG = 0
MERGE_DRILL_DATA = 0
PATTERN_SHIFT = 1
LEFT_X = 5.0
LOWER_Y = 5.0
#For file
OUT_INCH_FLAG = 0
IN_INCH_FLAG = 1
OUT_UNIT = 1.0		#mm
IN_UNIT = 25.4		#inch	
GERBER_EXT = '*.gtl'
BACK_EXT = '*.gbl'
DRILL_EXT = '*.drl'
EDGE_EXT = '*.gbr'

GCODE_EXT = '*.ngc'
GBACK_EXT = '*.ngc'
GDRILL_EXT = '*.ngc'
GEDGE_EXT = '*.ngc'

#View
GERBER_COLOR = 'BLACK'	#black
BACK_COLOR = 'GREEN'
DRILL_COLOR = 'BLUE'
EDGE_COLOR = 'GREEN YELLOW'
CONTOUR_COLOR = 'MAGENTA'
CONTOUR_BACK_COLOR = 'MAGENTA'
DIST_COLOR = 'ORANGE'
ZOOM_COLOR = 'VIOLET RED'
#
GERBER_DIR = ""
FRONT_FILE = ""
BACK_FILE = ""
DRILL_FILE = ""
EDGE_FILE = ""
MIRROR_FRONT = 0
MIRROR_BACK = 0
MIRROR_DRILL = 0
MIRROR_EDGE = 0
ROT_ANG = 0
OUT_DIR = ""
OUT_FRONT_FILE = ""
OUT_BACK_FILE = ""
OUT_DRILL_FILE = ""
OUT_EDGE_FILE = ""
OUT_ALL_FILE = "test_gerber.ngc"
CUT_ALL_FRONT = 0
CUT_ALL_BACK = 0
#CUT_OV = 0.1
CUT_STEP_R_FRONT = 1.9
CUT_STEP_R_BACK = 1.9
CUT_MAX_FRONT = 20
CUT_MAX_BACK = 20
CUT_MARGIN_R = 1.1
#Global variable
gFRONT_HEADER = ""
gBACK_HEADER = ""
gDRILL_HEADER = ""
gEDGE_HEADER = ""

#For Drawing 
gPATTERNS = []
gBACK_PATTERNS = []
gDRAWDRILL = []
gDRAWDRILL_LINE = []
gDRAWEDGE = []
gDRAWCONTOUR = []
gDRAWCONTOUR_BACK = []
gMAG = 1.0
gPRE_X = CENTER_X
gPRE_Y = CENTER_X
gMAG_MIN = 0.1
gMAG_MAX = 1000.0
gDRAW_XSHIFT = 0.0
gDRAW_YSHIFT = 0.0
gDISP_FRONT = 0
gDISP_BACK = 0
gDISP_DRILL = 0
gDISP_EDGE = 0
gDISP_CONTOUR_FRONT = 0
gDISP_CONTOUR_BACK = 0

gFIG_XMAX = WINDOW_X
gFIG_YMAX = WINDOW_Y
gFIG_XMIN = 0
gFIG_YMIN = 0
gFIG_CX = 0
gFIG_CY = 0
PRE_IN_FLAG = -1
TMP_POLY_POINTS = []
gPOLY_FLAG = 0
gGPOLYGONS = []

PRE_IN_FLAG = -1
gPAINTWINDOW_X = 300
gPAINTWINDOW_Y = 300
gPAINTWINDOW_X_MAX = 20000
gPAINTWINDOW_Y_MAX = 20000
gPAINTWINDOW_X_MIN = 100
gPAINTWINDOW_Y_MIN = 100

gSCROLL_DX = 10
gSCROLL_DY = 10
gPRE_SCROLL_X = 0
gPRE_SCROLL_Y = 0

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

class RedirectText(object):
	def __init__(self,aWxTextCtrl):
		self.out=aWxTextCtrl
	def write(self, string):
		wx.CallAfter(self.out.WriteText, string)
#Window
class MainFrame(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title, size=(WINDOW_X, WINDOW_Y))

		# Setting up the menu.
		filemenu= wx.Menu()
		menuOpen = filemenu.Append(wx.ID_OPEN,"&Open/Save","Gerber Open/G-code Save files")
		menuReload = filemenu.Append(wx.ID_REFRESH,"&Reload Data","Reload files")
		menuLoadConf = filemenu.Append(wx.ID_FILE,"&Load Configure","Open configure file")
		menuSaveConf = filemenu.Append(wx.ID_SAVE,"&Save Configure","Save configure file")
		menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
		setupmenu =  wx.Menu()
		menuMachine = setupmenu.Append(wx.ID_SETUP,"&Machine setup"," Setup Machine")
		menuConv = setupmenu.Append(wx.ID_VIEW_LIST,"&Convert setup"," Convert setup")

		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
		menuBar.Append(setupmenu,"&Setup") # Adding the "filemenu" to the MenuBar
		self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

		self.statusbar = self.CreateStatusBar()
		self.SetStatusText("mouse position")

		#Event for Menu bar
		self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
		self.Bind(wx.EVT_MENU, self.OnReload, menuReload)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		self.Bind(wx.EVT_MENU, self.OnConvSet, menuConv)
		self.Bind(wx.EVT_MENU, self.OnSetup, menuMachine)
		self.Bind(wx.EVT_MENU, self.OnLoadConf, menuLoadConf)
		self.Bind(wx.EVT_MENU, self.OnSaveConf, menuSaveConf)
		panel = wx.Panel(self, -1)
		vbox = wx.BoxSizer(wx.VERTICAL)

		#Display set
		panel1 = wx.Panel(panel, -1)
		hbox0 = wx.BoxSizer(wx.HORIZONTAL)

		box1 = wx.StaticBox(panel1, -1, 'Display data')
		#sizer1 = wx.StaticBoxSizer(box1, orient=wx.VERTICAL)
		sizer1 = wx.StaticBoxSizer(box1, orient=wx.HORIZONTAL)
		grid1 = wx.GridSizer(2, 6, 0, 6)
		self.cb0 = wx.CheckBox(panel1, -1, 'Front data')
		self.cb0.SetValue(gDISP_FRONT)
		grid1.Add(self.cb0)

		self.cb1 = wx.CheckBox(panel1, -1, 'Back data')
		self.cb1.SetValue(gDISP_BACK)
		grid1.Add(self.cb1)
		self.cb2 = wx.CheckBox(panel1, -1, 'Drill data')
		self.cb2.SetValue(gDISP_DRILL)
		grid1.Add(self.cb2)
		self.cb3 = wx.CheckBox(panel1, -1, 'Edge data')
		self.cb3.SetValue(gDISP_EDGE)
		grid1.Add(self.cb3)

		self.cb4 = wx.CheckBox(panel1, -1, 'Front Contour')
		self.cb4.SetValue(gDISP_CONTOUR_FRONT)
		grid1.Add(self.cb4)

		self.cb5 = wx.CheckBox(panel1, -1, 'Back Contour')
		self.cb5.SetValue(gDISP_CONTOUR_BACK)
		grid1.Add(self.cb5)
		sizer1.Add(grid1)
		hbox0.Add(sizer1)

		fit_btn = wx.Button(panel1, -1, 'Fit to window', size=(100, 30))
		hbox0.Add(fit_btn)
		center_btn = wx.Button(panel1, -1, 'Goto Center', size=(100, 30))
		hbox0.Add(center_btn)

		#panel1.SetSizer(sizer1)
		panel1.SetSizer(hbox0)

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
		btn1 = wx.Button(panel, -1, 'Convert to G-code and Save G-code', size=(300, 30))
		hbox5.Add(btn1, 0)
		btn2 = wx.Button(panel, -1, 'Close', size=(70, 30))
		hbox5.Add(btn2, 0, wx.LEFT | wx.BOTTOM , 5)
		vbox.Add(hbox5, 0, wx.ALIGN_RIGHT | wx.RIGHT, 10)

		#msg_box = wx.BoxSizer(wx.HORIZONTAL)
		#msg = wx.TextCtrl(panel, wx.ID_ANY,style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
		msg = wx.TextCtrl(panel, wx.ID_ANY,size=(1000,50),style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
		#msg_box.Add(msg, flag=wx.GROW)
		#vbox.Add(msg_box, 0, wx.ALIGN_LEFT | wx.RIGHT, 10)
		#vbox.Add(msg_box)
		vbox.Add(msg, flag=wx.GROW)
		panel.SetSizer(vbox)

		self.Centre()
		self.Show(True)
		# redirect text here
		redir=RedirectText(msg)
		sys.stdout=redir
		#Redraw
		#self.Bind(wx.EVT_PAINT, self.paint.OnPaint)
		#wx.EVT_PAINT(self,self.paint.OnPaint)
		#Event
		self.Bind(wx.EVT_CHECKBOX, self.OnFront,self.cb0)
		self.Bind(wx.EVT_CHECKBOX, self.OnBack,self.cb1)
		self.Bind(wx.EVT_CHECKBOX, self.OnDrill,self.cb2)
		self.Bind(wx.EVT_CHECKBOX, self.OnEdge,self.cb3)
		self.Bind(wx.EVT_CHECKBOX, self.OnFrontContour,self.cb4)
		self.Bind(wx.EVT_CHECKBOX, self.OnBackContour,self.cb5)
		self.Bind(wx.EVT_BUTTON, self.OnExit, btn2)
		self.Bind(wx.EVT_BUTTON, self.OnGenerate, btn0)
		self.Bind(wx.EVT_BUTTON, self.OnConvert, btn1)
		self.Bind(wx.EVT_BUTTON, self.OnFit,fit_btn)
		self.Bind(wx.EVT_BUTTON, self.OnCenter,center_btn)
		self.Bind(wx.EVT_CLOSE,self.OnExit)
	#functions
	def OnLoadConf(self,e):
		global CONFIG_FILE
		dlg = wx.FileDialog(self, "Choose a input Configure file", "./",CONFIG_FILE, "*.conf", wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			CONFIG_FILE=os.path.join(self.dirname, self.filename)
		dlg.Destroy()
		read_config(CONFIG_FILE)
		set_unit()
	def OnSaveConf(self,e):
		global CONFIG_FILE
		dlg = wx.FileDialog(self, "Choose a Configure file for save", "./", CONFIG_FILE,"*.conf", wx.FD_SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			CONFIG_FILE=os.path.join(self.dirname, self.filename)
		dlg.Destroy()
		save_config()
	def OnFit(self,e):
		global gMAG,gDRAW_XSHIFT,gDRAW_YSHIFT
		#size = self.GetSize()
		#size = self.panel2.GetSize()
		size = self.paint.GetSize()
		#print size
		gMAG=size.x/abs(gFIG_XMAX-gFIG_XMIN)
		if gMAG > size.y/abs(gFIG_YMAX-gFIG_YMIN):
			gMAG = size.y/abs(gFIG_YMAX-gFIG_YMIN)
		gDRAW_XSHIFT = -gFIG_CX*gMAG
		gDRAW_YSHIFT = gFIG_CY*gMAG

		self.Refresh(True)
	def OnCenter(self,e):
		global gDRAW_XSHIFT,gDRAW_YSHIFT
		gDRAW_XSHIFT = 0
		gDRAW_YSHIFT = 0
		self.Refresh(True)
	def OnFront(self,e):
		global gDISP_FRONT
		gDISP_FRONT = int(self.cb0.IsChecked())
		self.Refresh(1)
	def OnBack(self,e):
		global gDISP_BACK
		gDISP_BACK = int(self.cb1.IsChecked())
		self.Refresh(1)
	def OnDrill(self,e):
		global gDISP_DRILL
		gDISP_DRILL = int(self.cb2.IsChecked())
		self.Refresh(1)
	def OnEdge(self,e):
		global gDISP_EDGE
		gDISP_EDGE = int(self.cb3.IsChecked())
		self.Refresh(1)
	def OnFrontContour(self,e):
		global gDISP_CONTOUR_FRONT
		#global gDRAWCONTOUR
		if(len(gDRAWCONTOUR) > 0):
			gDISP_CONTOUR_FRONT = int(self.cb4.IsChecked())
		else:
			gDISP_CONTOUR_FRONT = 0
			self.cb4.SetValue(0)
		self.Refresh(1)
	def OnBackContour(self,e):
		global gDISP_CONTOUR_BACK
		#global gDRAWCONTOUR_BACK
		if(len(gDRAWCONTOUR_BACK) > 0):
			gDISP_CONTOUR_BACK = int(self.cb5.IsChecked())
		else:
			gDISP_CONTOUR_BACK = 0
			self.cb5.SetValue(0)
		self.Refresh(1)
	def OnExit(self,e):
		#self.Close(True)  # Close the frame.
		sys.exit()
	def OnSetup(self,e):
		setup = MachineSetup(None, -1, 'Machine Setup')
		setup.ShowModal()
		setup.Destroy()
	def OnConvSet(self,e):
		#print "view"
		setup = ConvSetup(None, -1, 'Convert Setup')
		setup.ShowModal()
		setup.Destroy()

	def OnReload(self,e):
		global gPATTERNS,gBACK_PATTERNS, gDRAWDRILL,gDRAWDRILL_LINE, gDRAWEDGE, gPOLYGONS, gDRAWCONTOUR
		#global gDISP_FRONT, gDISP_DRILL, gDISP_EDGE
		#global gFRONT_HEADER,gBACK_HEADER,gDRILL_HEADER,gEDGE_HEADER
		global gMAG,gDRAW_XSHIFT, gDRAW_YSHIFT
		global gFIG_XMAX,gFIG_YMAX,gFIG_XMIN,gFIG_YMIN,gFIG_CX,gFIG_CY
		#initialize
		gPOLYGONS = []
		gPATTERNS = []
		gBACK_PATTERNS = []
		gDRAWDRILL = []
		gDRAWDRILL_LINE = []
		gDRAWEDGE = []
		gDRAWCONTOUR = []
		set_unit()
		self.Refresh(1)
		size = self.paint.GetSize()
		if(FRONT_FILE):
			front_gerber = gerber.Gerber(GERBER_DIR,FRONT_FILE,OUT_UNIT)
			tmp_front = gs.Gerber_OP(front_gerber,TOOL_D)
			tmp_front.gerber2shapely()
			tmp_front.get_minmax(tmp_front.tmp_figs)
			tmp_front.draw_out()
			gFIG_XMAX = tmp_front.xmax
			gFIG_YMAX = tmp_front.ymax
			gFIG_XMIN = tmp_front.xmin
			gFIG_YMIN = tmp_front.ymin
			gFIG_CX = (gFIG_XMAX+gFIG_XMIN)/2.0
			gFIG_CY = (gFIG_YMAX+gFIG_YMIN)/2.0
			front_draw(tmp_front.draw_figs)
			gMAG=size.x/abs(gFIG_XMAX-gFIG_XMIN)
			if gMAG > size.y/abs(gFIG_YMAX-gFIG_YMIN):
				gMAG = size.y/abs(gFIG_YMAX-gFIG_YMIN)
			gDRAW_XSHIFT = -gFIG_CX*gMAG
			gDRAW_YSHIFT = gFIG_CY*gMAG

		if(BACK_FILE):
			back_gerber = gerber.Gerber(GERBER_DIR,BACK_FILE,OUT_UNIT)
			tmp_back = gs.Gerber_OP(back_gerber,TOOL_D/IN_UNIT)
			tmp_back.in_unit=IN_UNIT
			tmp_back.out_unit=OUT_UNIT
			tmp_back.gerber2shapely()
			tmp_back.draw_out()
			back_draw(tmp_back.draw_figs)
		if(DRILL_FILE):
			drill_gerber=gerber.Drill(GERBER_DIR,DRILL_FILE,OUT_UNIT)
			tmp_drill = gs.Gerber_OP(drill_gerber,DRILL_D)
			tmp_drill.in_unit=IN_UNIT
			tmp_drill.out_unit=OUT_UNIT
			tmp_drill.drill2shapely()
			tmp_drill.draw_out()
			drill_draw(tmp_drill.draw_figs)
		if(EDGE_FILE):
			edge_gerber = gerber.Gerber(GERBER_DIR,EDGE_FILE,OUT_UNIT)
			tmp_edge = gs.Gerber_OP(edge_gerber,EDGE_TOOL_D)
			tmp_edge.in_unit=IN_UNIT
			tmp_edge.out_unit=OUT_UNIT
			tmp_edge.edge2shapely()
			tmp_edge.draw_out()
			edge_draw(tmp_edge.draw_figs)

	def OnOpen(self,e):
		#global gPATTERNS,gBACK_PATTERNS, gDRAWDRILL, gDRAWDRILL_LINE, gDRAWEDGE
		global gDISP_FRONT,gDISP_BACK, gDISP_DRILL, gDISP_EDGE
		setup = OpenFiles(None, -1, 'Gerber Open/G-code Save files')
		setup.ShowModal()
		setup.Destroy()
		set_unit()
		if(len(gPATTERNS) > 0):
			gDISP_FRONT = 1
			self.cb0.SetValue(gDISP_FRONT)
		if(len(gBACK_PATTERNS) > 0):
			gDISP_BACK = 1
			self.cb1.SetValue(gDISP_BACK)

		if(len(gDRAWDRILL) > 0 or len(gDRAWDRILL_LINE) > 0):
			gDISP_DRILL = 1
			self.cb2.SetValue(gDISP_DRILL)
		if(len(gDRAWEDGE) >0 ):
			gDISP_EDGE = 1
			self.cb3.SetValue(gDISP_EDGE)
		self.Refresh(1)
	def OnGenerate(self,e):
		#global gPOLYGONS
		global gDISP_CONTOUR_FRONT,gDISP_CONTOUR_BACK
		global gFRONT_HEADER,gBACK_HEADER,gDRILL_HEADER,gEDGE_HEADER
		global gMAG,gDRAW_XSHIFT, gDRAW_YSHIFT
		global gFIG_XMAX,gFIG_YMAX,gFIG_XMIN,gFIG_YMIN,gFIG_CX,gFIG_CY
		global CUT_MAX_FRONT,CUT_MAX_BACK
		size = self.paint.GetSize()

		if FRONT_FILE:
			front_gerber = gerber.Gerber(GERBER_DIR,FRONT_FILE,OUT_UNIT)
			if not CUT_ALL_FRONT:
				CUT_MAX_FRONT = 1
			CUT_STEP = float(TOOL_D) * float(CUT_STEP_R_FRONT)
			tmp_elements = []
			tmp_xmax = 0.0
			tmp_ymax = 0.0
			tmp_xmin = 0.0
			tmp_ymin = 0.0
			progress = wx.ProgressDialog("Front Progress",'Front Progress', maximum = 100, parent=self, style = wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
			progress.SetSize((300, 100))
			for i in range(int(CUT_MAX_FRONT)):
				pp=((i+1)*100)/int(CUT_MAX_FRONT)
				gFRONT_HEADER = gs.Gerber_OP(front_gerber,TOOL_D+i*CUT_STEP)
				gFRONT_HEADER.gerber2shapely()
				gFRONT_HEADER.in_unit=IN_UNIT
				gFRONT_HEADER.out_unit=OUT_UNIT
				gFRONT_HEADER.mirror=MIRROR_FRONT
				gFRONT_HEADER.rot_ang=float(ROT_ANG)
				gFRONT_HEADER.merge_polygon()
				gFRONT_HEADER.get_minmax(gFRONT_HEADER.figs)
				#gFRONT_HEADER.affine()
				if i == 0:
					tmp_xmax = gFRONT_HEADER.xmax+CUT_MARGIN_R*TOOL_D
					tmp_ymax = gFRONT_HEADER.ymax+CUT_MARGIN_R*TOOL_D
					tmp_xmin = gFRONT_HEADER.xmin-CUT_MARGIN_R*TOOL_D
					tmp_ymin = gFRONT_HEADER.ymin-CUT_MARGIN_R*TOOL_D
					center=gFRONT_HEADER.center
				gFRONT_HEADER.limit_cut(tmp_xmax,tmp_ymax,tmp_xmin,tmp_ymin)
				tmp_poly_num=gFRONT_HEADER.count_active_figs()
				progress.Update(pp, 'Loop No. '+ str(i+1)+"/"+str(CUT_MAX_FRONT)+", Number of Polygons"+str(tmp_poly_num))
				tmp_elements += gFRONT_HEADER.figs.elements
				if tmp_poly_num < 2:
					progress.Update(100, 'No new polygons')
					break
			gFRONT_HEADER.figs.elements=tmp_elements
		progress.Destroy()
		xoff=0.0
		yoff=0.0
		if PATTERN_SHIFT:
			xoff=LEFT_X-gFRONT_HEADER.xmin
			yoff=LOWER_Y-gFRONT_HEADER.ymin
		if BACK_FILE:
			back_gerber = gerber.Gerber(GERBER_DIR,BACK_FILE,OUT_UNIT)
			if not CUT_ALL_BACK:
				CUT_MAX_BACK = 1
			CUT_STEP = float(TOOL_D) * float(CUT_STEP_R_BACK)
			tmp_elements = []
			tmp_xmax = 0.0
			tmp_ymax = 0.0
			tmp_xmin = 0.0
			tmp_ymin = 0.0
			progress = wx.ProgressDialog("Back Progress",'Back Progress', maximum = 100, parent=self, style = wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
			progress.SetSize((300, 100))
			for i in range(CUT_MAX_BACK):
				pp=((i+1)*100)/int(CUT_MAX_BACK)
				gBACK_HEADER = gs.Gerber_OP(back_gerber,TOOL_D+i*CUT_STEP)
				gBACK_HEADER.gerber2shapely()
				gBACK_HEADER.in_unit=IN_UNIT
				gBACK_HEADER.out_unit=OUT_UNIT
				gBACK_HEADER.mirror=MIRROR_BACK
				gBACK_HEADER.rot_ang=float(ROT_ANG)
				gBACK_HEADER.merge_polygon()
				gBACK_HEADER.get_minmax(gBACK_HEADER.figs)
				#gBACK_HEADER.affine()
				if i == 0:
					tmp_xmax = gBACK_HEADER.xmax+CUT_MARGIN_R*TOOL_D
					tmp_ymax = gBACK_HEADER.ymax+CUT_MARGIN_R*TOOL_D
					tmp_xmin = gBACK_HEADER.xmin-CUT_MARGIN_R*TOOL_D
					tmp_ymin = gBACK_HEADER.ymin-CUT_MARGIN_R*TOOL_D
				gBACK_HEADER.limit_cut(tmp_xmax,tmp_ymax,tmp_xmin,tmp_ymin)
				if len(gBACK_HEADER.figs.elements) < 1:
					break
				tmp_poly_num=gBACK_HEADER.count_active_figs()
				#tmp_poly_num=len(gBACK_HEADER.figs.elements)
				progress.Update(pp, 'Loop No. '+ str(i+1)+"/"+str(CUT_MAX_BACK)+", Number of Polygons"+str(tmp_poly_num))
				tmp_elements += gBACK_HEADER.figs.elements
				if tmp_poly_num < 2:
					progress.Update(100, 'No new polygons')
					break
			gBACK_HEADER.figs.elements=tmp_elements
		progress.Destroy()
		#print "back center =",center
		if DRILL_FILE:
			#print "drill"
			drill_gerber=gerber.Drill(GERBER_DIR,DRILL_FILE,OUT_UNIT)
			drill_gerber.parse()
			gDRILL_HEADER = gs.Gerber_OP(drill_gerber,DRILL_D)
			gDRILL_HEADER.in_unit=1.0
			gDRILL_HEADER.out_unit=OUT_UNIT
			gDRILL_HEADER.drill2shapely()
			gDRILL_HEADER.mirror=MIRROR_DRILL
			gDRILL_HEADER.rot_ang=float(ROT_ANG)
			gDRILL_HEADER.get_minmax(gDRILL_HEADER.figs)
			#center=gDRILL_HEADER.center

		if EDGE_FILE:
			edge_gerber = gerber.Gerber(GERBER_DIR,EDGE_FILE,OUT_UNIT)
			gEDGE_HEADER = gs.Gerber_OP(edge_gerber,EDGE_TOOL_D)
			gEDGE_HEADER.in_unit=IN_UNIT
			gEDGE_HEADER.out_unit=OUT_UNIT
			gEDGE_HEADER.edge2shapely()
			gEDGE_HEADER.merge_line()
			gEDGE_HEADER.mirror=MIRROR_EDGE
			gEDGE_HEADER.rot_ang=float(ROT_ANG)
			gEDGE_HEADER.get_minmax(gEDGE_HEADER.figs)
			#center=gEDGE_HEADER.center
		#print "rot ang",ROT_ANG
		###########out gcode
		if FRONT_FILE:
			gFRONT_HEADER.center = center
			gFRONT_HEADER.xoff = xoff
			gFRONT_HEADER.yoff = yoff
			gFRONT_HEADER.affine()
			gFRONT_HEADER.fig_out()
			gFRONT_HEADER.affine_trans(gFRONT_HEADER.raw_figs)
			gFRONT_HEADER.get_minmax(gFRONT_HEADER.figs)
			gFRONT_HEADER.draw_out()
			front_draw(gFRONT_HEADER.draw_figs)
			contour2draw_front(gFRONT_HEADER.out_figs)
			gFIG_XMAX = gFRONT_HEADER.xmax
			gFIG_YMAX = gFRONT_HEADER.ymax
			gFIG_XMIN = gFRONT_HEADER.xmin
			gFIG_YMIN = gFRONT_HEADER.ymin
			gFIG_CX = (gFIG_XMAX+gFIG_XMIN)/2.0
			gFIG_CY = (gFIG_YMAX+gFIG_YMIN)/2.0
			gMAG=size.x/abs(gFIG_XMAX-gFIG_XMIN)
			if gMAG > size.y/abs(gFIG_YMAX-gFIG_YMIN):
				gMAG = size.y/abs(gFIG_YMAX-gFIG_YMIN)
			gDRAW_XSHIFT = -gFIG_CX*gMAG
			gDRAW_YSHIFT = gFIG_CY*gMAG

			gDISP_CONTOUR_FRONT = 1
			self.cb4.SetValue(gDISP_CONTOUR_FRONT)
		if BACK_FILE:
			gBACK_HEADER.center = center
			gBACK_HEADER.xoff = xoff
			gBACK_HEADER.yoff = yoff
			gBACK_HEADER.affine()
			gBACK_HEADER.fig_out()
			gBACK_HEADER.affine_trans(gBACK_HEADER.raw_figs)
			gBACK_HEADER.draw_out()
			back_draw(gBACK_HEADER.draw_figs)
			contour2draw_back(gBACK_HEADER.out_figs)
			gDISP_CONTOUR_BACK = 1
			self.cb5.SetValue(gDISP_CONTOUR_BACK)
		if DRILL_FILE:
			gDRILL_HEADER.center = (center[0]*IN_UNIT/OUT_UNIT,center[1]*IN_UNIT/OUT_UNIT,0)
			#gDRILL_HEADER.center = center
			gDRILL_HEADER.xoff = xoff
			gDRILL_HEADER.yoff = yoff
			gDRILL_HEADER.affine()
			gDRILL_HEADER.fig_out()
			gDRILL_HEADER.affine_trans(gDRILL_HEADER.raw_figs)
			gDRILL_HEADER.draw_out()
			drill_draw(gDRILL_HEADER.draw_figs)
		if EDGE_FILE:
			gEDGE_HEADER.center = center
			gEDGE_HEADER.xoff = xoff
			gEDGE_HEADER.yoff = yoff
			gEDGE_HEADER.affine()
			gEDGE_HEADER.fig_out()
			gEDGE_HEADER.affine_trans(gEDGE_HEADER.raw_figs)
			gEDGE_HEADER.draw_out()
			edge_draw(gEDGE_HEADER.draw_figs)

		dlg = wx.MessageDialog(self, "Contour generation is finished", "Contour generation is finished" , wx.OK)
		dlg.ShowModal() # Shows it
		dlg.Destroy()
		#self.Refresh(1)
		#e.Skip()
	def OnConvert(self,e):
		a_gcd = gcode.Gcode()
		set_gcode(a_gcd)
		if FRONT_FILE:
			f_gcd = gcode.Gcode()
			set_gcode(f_gcd)
			f_gcd.add_polygon(CUT_DEPTH,gFRONT_HEADER.out_figs.elements,XY_SPEED, Z_SPEED)
			f_gcd.out(OUT_DIR,OUT_FRONT_FILE)
			a_gcd.add_polygon(CUT_DEPTH,gFRONT_HEADER.out_figs.elements,XY_SPEED, Z_SPEED)
		if BACK_FILE:
			b_gcd = gcode.Gcode()
			set_gcode(b_gcd)
			b_gcd.add_polygon(CUT_DEPTH,gBACK_HEADER.out_figs.elements,XY_SPEED, Z_SPEED)
			b_gcd.out(OUT_DIR,OUT_BACK_FILE)
			a_gcd.add_polygon(CUT_DEPTH,gBACK_HEADER.out_figs.elements,XY_SPEED, Z_SPEED)
		if DRILL_FILE:
			d_gcd = gcode.Gcode()
			set_gcode(d_gcd)
			drill2gcode(d_gcd,gDRILL_HEADER.out_figs.elements)
			d_gcd.out(OUT_DIR,OUT_DRILL_FILE)
			drill2gcode(a_gcd,gDRILL_HEADER.out_figs.elements)
		if EDGE_FILE:
			e_gcd = gcode.Gcode()
			set_gcode(e_gcd)
			edge2gcode(e_gcd,gEDGE_HEADER.out_figs.elements)
			e_gcd.out(OUT_DIR,OUT_EDGE_FILE)
			edge2gcode(a_gcd,gEDGE_HEADER.out_figs.elements)

		a_gcd.out(OUT_DIR,OUT_ALL_FILE)
		dlg = wx.MessageDialog(self, "Convert finished", "Convert is finished" , wx.OK)
		dlg.ShowModal() # Shows it
		dlg.Destroy() # finally destroy it when finished.
		self.Refresh(1)

class Paint(wx.ScrolledWindow):
	def __init__(self, parent):
		#global gPAINTWINDOW_X, gPAINTWINDOW_Y, gSCROLL_DX, gSCROLL_DY
		wx.ScrolledWindow.__init__(self, parent,-1,style=wx.HSCROLL|wx.VSCROLL)
		#self.scroll = wx.ScrolledWindow.__init__(self, parent,-1,style=wx.HSCROLL|wx.VSCROLL)
		#parent = Panel
		self.mainW = parent.GetParent().GetParent()
		self.SetBackgroundColour('WHITE')
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.parentW = parent
		#print self.GetSize(),parent.GetSize()
		
		self.SetScrollbars(gSCROLL_DX, gSCROLL_DY, int(gPAINTWINDOW_X/gSCROLL_DX),int(gPAINTWINDOW_Y/gSCROLL_DY))
		self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

		#self.Bind(wx.EVT_PAINT, self.OnPaint)
		wx.EVT_SIZE(self, self.OnSize)
		#self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
		self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.OnDrag)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
		self.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
		self.Bind(wx.EVT_MOTION , self.OnMouseMove) 
		#self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseLeftDClick)
		#self.Bind(wx.EVT_RIGHT_DCLICK , self.OnMouseRightDClick) 

		#wx.EVT_SCROLL(self,self.OnScroll)
		#self.Bind(wx.EVT_COMMAND_SCROLL,self.OnScroll)
		self.Bind(wx.EVT_SCROLLWIN,self.OnScroll)
		self.OnSize(None)
	def OnSize(self, e):
		Size  = self.ClientSize
		self._Buffer = wx.EmptyBitmap(*Size)
		self.UpdateDrawing()

	def OnScroll(self, e):
		global gDRAW_XSHIFT,gDRAW_YSHIFT,gPRE_SCROLL_X ,gPRE_SCROLL_Y
		#print e.CalcScrollInc()
		#print gDRAW_XSHIFT,gDRAW_YSHIFT
		#print self.CalcScrolledPosition(e.GetPosition(),gDRAW_YSHIFT)
		#print self.CalcUnscrolledPosition(gDRAW_XSHIFT,gDRAW_YSHIFT)
		#print e.GetOrientation()
		#print "scroll"
		#print locals()
		#try:
		#	pre_x = pre_x
		#except UnboundLocalError:
		#	pre_x = 0

		if e.GetOrientation() == wx.HORIZONTAL:
			#x = e.GetPosition():gMAG
			#gDRAW_XSHIFT = CENTER_Y - e.GetPosition()*gMAG
			#gDRAW_XSHIFT = - gMAG*(e.GetPosition()-gDRAW_XSHIFT-CENTER_X)
			gDRAW_XSHIFT += (gPRE_SCROLL_X - e.GetPosition())*1
			#print pre_x - e.GetPosition(),pre_x,e.GetPosition()
			gPRE_SCROLL_X = e.GetPosition()
			#print pre_x 
		elif e.GetOrientation() == wx.VERTICAL:
			gDRAW_YSHIFT += (gPRE_SCROLL_Y - e.GetPosition())*1
			gPRE_SCROLL_Y = e.GetPosition()
		#print e.GetPosition()
		#print e.GetOrientation()
		#print x,y
		#self.Refresh(True)
		#self.SetScrollbars(gSCROLL_DX, gSCROLL_DY, int(paint_window_x/gSCROLL_DX),int(paint_window_y/gSCROLL_DY))
		#print self.GetPosition()
		#print self.GetOrientation()
		#self.Refresh(True)
		self.UpdateDrawing()
	#gerber
	def UpdateDrawing(self):
		dc = wx.MemoryDC()
		dc.SelectObject(self._Buffer)
		#self.Draw(dc)
		del dc # need to get rid of the MemoryDC before Update() is called.
		self.Refresh()
		self.Update()
	def OnPaint(self, e):
		global CENTER_X, CENTER_Y
		#USE_BUFFERED_DC:
		dc = wx.BufferedPaintDC(self, self._Buffer)
		#dc = wx.PaintDC(self)
		dc.SetBackground(wx.Brush("White"))
		dc.Clear() 
		paint_size = self.GetSize()
		#print paint_size,self.parentW.GetSize()
		#print paint_size
		CENTER_X =int(paint_size.x/2)+1
		CENTER_Y =int(paint_size.y/2)+1
		veiw_start = [-CENTER_X,-CENTER_Y]
		org_x = gDRAW_XSHIFT-veiw_start[0]
		org_y = gDRAW_YSHIFT-veiw_start[1]
		#Draw axis
		dc.DrawLines( ([org_x,org_y], [org_x+10,org_y]) )	#X axis
		dc.DrawLines( ([org_x,org_y], [org_x,org_y-10]) )	#Y axis
		if(len(gPATTERNS) > 0 and gDISP_FRONT):
			for polygon in gPATTERNS:
				points = []
				for point in polygon.points:
					x = point[0] * gMAG + gDRAW_XSHIFT-veiw_start[0]
					y = -point[1] * gMAG + gDRAW_YSHIFT-veiw_start[1]
					points.append([x,y])
				dc.SetPen(wx.Pen(GERBER_COLOR, 1, wx.SOLID))
				dc.DrawLines(points)
		if(len(gBACK_PATTERNS) > 0 and gDISP_BACK):
			for polygon in gBACK_PATTERNS:
				points = []
				for point in polygon.points:
					x = point[0] * gMAG + gDRAW_XSHIFT-veiw_start[0]
					y = -point[1] * gMAG + gDRAW_YSHIFT-veiw_start[1]
					points.append([x,y])
				dc.SetPen(wx.Pen(BACK_COLOR, 1, wx.SOLID))

				dc.DrawLines(points)
		if(len(gDRAWDRILL) > 0 and gDISP_DRILL):
			#print "Drill",len(gDRAWDRILL)
			for drill in gDRAWDRILL:
				x = drill.x * gMAG + gDRAW_XSHIFT-veiw_start[0]
				y = -drill.y * gMAG + gDRAW_YSHIFT-veiw_start[1]
				r = drill.d * gMAG/2
				dc.SetPen(wx.Pen(DRILL_COLOR, 1, wx.DOT))
				dc.DrawCircle(x, y, r)
		if(len(gDRAWDRILL_LINE) > 0 and gDISP_DRILL):
			for polygon in gDRAWDRILL_LINE:
				points = []
				for point in polygon.points:
					x = point[0] * gMAG + gDRAW_XSHIFT-veiw_start[0]
					y = -point[1] * gMAG + gDRAW_YSHIFT-veiw_start[1]
					points.append([x,y])
				dc.SetPen(wx.Pen(DRILL_COLOR, 1, wx.DOT))
				dc.DrawLines(points)
		if(len(gDRAWEDGE) > 0 and gDISP_EDGE):
			for edge in gDRAWEDGE:
				points = []
				for point in edge.points:
					x = point[0] * gMAG + gDRAW_XSHIFT-veiw_start[0]
					y = -point[1] * gMAG + gDRAW_YSHIFT-veiw_start[1]
					points.append([x,y])
				dc.SetPen(wx.Pen(EDGE_COLOR, 1, wx.DOT_DASH))
				dc.DrawLines(points)
		if(len(gDRAWCONTOUR) > 0 and gDISP_CONTOUR_FRONT):
			for edge in gDRAWCONTOUR:
				points = []
				for point in edge.points:
					x = point[0] * gMAG + gDRAW_XSHIFT-veiw_start[0]
					y = -point[1] * gMAG + gDRAW_YSHIFT-veiw_start[1]
					points.append([x,y])
				dc.SetPen(wx.Pen(CONTOUR_COLOR, 1, wx.SOLID))

				dc.DrawLines(points)
		if(len(gDRAWCONTOUR_BACK) > 0 and gDISP_CONTOUR_BACK):
			for edge in gDRAWCONTOUR_BACK:
				points = []
				for point in edge.points:
					x = point[0] * gMAG + gDRAW_XSHIFT-veiw_start[0]
					y = -point[1] * gMAG + gDRAW_YSHIFT-veiw_start[1]
					points.append([x,y])
				dc.SetPen(wx.Pen(CONTOUR_BACK_COLOR, 1, wx.SOLID))
				dc.DrawLines(points)

	def OnKeyDown(self, event):
		keycode = event.GetKeyCode()
		print keycode
		#if keycode == wx.WXK_UP:
	def OnMouseWheel(self, event):
		global gMAG,gDRAW_XSHIFT, gDRAW_YSHIFT, gPRE_X, gPRE_Y
		pos = event.GetPosition()
		w = event.GetWheelRotation()
		pre_mag = gMAG
		#gMAG += copysign(0.1, w)
		gMAG = gMAG * (1 + copysign(0.1, w))

		gPRE_X = float(pos.x)
		gPRE_Y = float(pos.y)
		if(gMAG < gMAG_MIN):
			gMAG = gMAG_MIN
			gDRAW_XSHIFT = 0
			gDRAW_YSHIFT = 0
		if(gMAG > gMAG_MAX):
			gMAG = gMAG_MAX

		#gDRAW_XSHIFT += float(CENTER_X) - float(pos.x)
		#gDRAW_YSHIFT += float(CENTER_Y) - float(pos.y)
		gDRAW_XSHIFT = -(gMAG/pre_mag)*(float(pos.x)-gDRAW_XSHIFT-CENTER_X)
		gDRAW_YSHIFT = -(gMAG/pre_mag)*(float(pos.y)-gDRAW_YSHIFT-CENTER_Y)

		paint_window_x = int(gMAG * gPAINTWINDOW_X)
		paint_window_y = int(gMAG * gPAINTWINDOW_Y)

		self.SetScrollbars(gSCROLL_DX, gSCROLL_DY, int(paint_window_x/gSCROLL_DX),int(paint_window_y/gSCROLL_DY))
		self.EnableScrolling(True,True)
		#self.Refresh(True)
		self.UpdateDrawing()
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
		#global gMouseLeftDown, gMAG, gDRAW_XSHIFT, gDRAW_YSHIFT, CENTER_X, CENTER_Y
		global gMAG, gDRAW_XSHIFT, gDRAW_YSHIFT,gMouseLeftDown
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
				#gMAG = -float(pre_mag)/float(dx)
				#gMAG = abs(float(dx))/float(size.x)
				#gMAG -= float(pre_mag)/3
				gMAG = pre_mag*0.5

			if(dy > 0):
				if(gMAG > float(size.y)/float(dy/pre_mag)):
					gMAG = float(size.y)/float(dy/pre_mag)
			elif(dx < 0):
				gMAG = gMAG*0.5

			if(gMAG > gMAG_MAX):
				gMAG = gMAG_MAX		
			gDRAW_XSHIFT = -(gMAG/pre_mag)*(float(cx)-gDRAW_XSHIFT-CENTER_X)
			gDRAW_YSHIFT = -(gMAG/pre_mag)*(float(cy)-gDRAW_YSHIFT-CENTER_Y)

			if(gMAG < gMAG_MIN):
				gMAG = gMAG_MIN
				gDRAW_XSHIFT = 0
				gDRAW_YSHIFT = 0
			#print pre_mag,gMAG,gDRAW_XSHIFT,gDRAW_YSHIFT
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
			self.SetScrollbars(gSCROLL_DX, gSCROLL_DY, int(paint_window_x/gSCROLL_DX),int(paint_window_y/gSCROLL_DY))
			#self.Refresh(True)
			self.UpdateDrawing()
	def OnMouseRightUp(self, event):
		#global gMouseRightDown, gMAG
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
		global gDRAW_XSHIFT,gDRAW_YSHIFT
		pos = event.GetPosition()
		gDRAW_XSHIFT += CENTER_X - pos.x
		gDRAW_YSHIFT += CENTER_Y - pos.y
	def OnMouseRightDClick(self, event):
		global gDRAW_XSHIFT,gDRAW_YSHIFT
		#pos = event.GetPosition()
		gDRAW_XSHIFT = 0
		gDRAW_YSHIFT = 0
	def OnMouseMove(self, event):
		global dc
		pos = event.GetPosition()
		cdc = wx.ClientDC(self)

		if gMouseRightDown[0]:
			#self.Refresh(1)
			self.UpdateDrawing()
			cdc.SetPen(wx.Pen(DIST_COLOR, 1, wx.SOLID))
			cdc.DrawLines(([gMouseRightDown[1],gMouseRightDown[2]],[pos.x,pos.y]))
		if gMouseLeftDown[0]:
			#self.Refresh(1)
			self.UpdateDrawing()
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
			cdc.SetBrush(wx.Brush(ZOOM_COLOR,wx.TRANSPARENT))
			cdc.SetPen(wx.Pen(ZOOM_COLOR, 1, wx.SOLID))
			cdc.DrawRectangle(x,y,dx,dy)
		#print pos.x,gDRAW_XSHIFT,CENTER_X,gMAG
		mouse_x = (pos.x-gDRAW_XSHIFT-CENTER_X)/gMAG
		mouse_y = -(pos.y-gDRAW_YSHIFT-CENTER_Y)/gMAG
		self.mainW.statusbar.SetStatusText('x:'+str(mouse_x)+", y:"+str(mouse_y))
class OpenFiles(wx.Dialog):
	def __init__(self, parent, id, title):
		wx.Dialog.__init__(self, parent, id, title, size=(250, 210))
		self.dirname=''

		panel = wx.Panel(self, -1)
		sizer = wx.GridBagSizer(0, 0)

		text1 = wx.StaticText(panel, -1, 'Front Gerber file')
		sizer.Add(text1, (0, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.gerber = wx.TextCtrl(panel, -1)
		self.gerber.SetValue(FRONT_FILE)
		sizer.Add(self.gerber, (0, 1), (1, 4), wx.TOP | wx.EXPAND, 5)

		button1 = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button1, (0, 5), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)


		back_txt = wx.StaticText(panel, -1, 'Back Gerber file')
		sizer.Add(back_txt, (1, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.back = wx.TextCtrl(panel, -1)
		self.back.SetValue(BACK_FILE)
		sizer.Add(self.back, (1, 1), (1, 4), wx.TOP | wx.EXPAND, 5)

		back_button = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(back_button, (1, 5), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		text2 = wx.StaticText(panel, -1, 'Drill data file')
		sizer.Add(text2, (2, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.drill = wx.TextCtrl(panel, -1)
		self.drill.SetValue(DRILL_FILE)
		sizer.Add(self.drill, (2, 1), (1, 4), wx.TOP | wx.EXPAND,  5)

		button2 = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button2, (2, 5), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		text0 = wx.StaticText(panel, -1, 'Edge data file')
		sizer.Add(text0, (3, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.edge = wx.TextCtrl(panel, -1)
		self.edge.SetValue(EDGE_FILE)
		sizer.Add(self.edge, (3, 1), (1, 4), wx.TOP | wx.EXPAND,  5)

		button_edge = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button_edge, (3, 5), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		radioList = ['mm', 'inch']
		rb1 = wx.RadioBox(panel, label="unit of Input file", choices=radioList, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		rb1.SetSelection(int(IN_INCH_FLAG))
		sizer.Add(rb1, (4, 0), (1, 6), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		line = wx.StaticLine(panel, -1 )
		sizer.Add(line, (6, 0), (1, 6), wx.TOP | wx.EXPAND, -15)

		text3 = wx.StaticText(panel, -1, 'Front G-code file')
		sizer.Add(text3, (7, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.gcode = wx.TextCtrl(panel, -1)
		self.gcode.SetValue(OUT_FRONT_FILE)
		sizer.Add(self.gcode, (7, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		button3 = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button3, (7, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		self.mirror_front = wx.CheckBox(panel, -1, 'Mirror', (10, 10))
		self.mirror_front.SetValue(int(MIRROR_FRONT))
		sizer.Add(self.mirror_front, (7, 5), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		self.scribe_front = wx.CheckBox(panel, -1, 'Multi-Scrape:', (10, 10))
		self.scribe_front.SetValue(int(CUT_ALL_FRONT))
		sizer.Add(self.scribe_front, (8, 0), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		cut_step_front_txt = wx.StaticText(panel, -1, 'Scrape Step/Tool Diameter')
		sizer.Add(cut_step_front_txt, (8, 1), flag=wx.TOP | wx.LEFT, border=10)
		self.cut_step_front = wx.TextCtrl(panel, -1)
		self.cut_step_front.SetValue(str(CUT_STEP_R_FRONT))
		sizer.Add(self.cut_step_front, (8, 2), (1, 1), wx.TOP | wx.EXPAND,  5)

		cut_max_front_txt = wx.StaticText(panel, -1, 'Scrape Loop Max')
		sizer.Add(cut_max_front_txt, (8, 3), flag=wx.TOP | wx.LEFT, border=10)
		self.cut_max_front = wx.TextCtrl(panel, -1)
		self.cut_max_front.SetValue(str(CUT_MAX_FRONT))
		sizer.Add(self.cut_max_front, (8, 4), (1, 1), wx.TOP | wx.EXPAND,  5)

		back_g_txt = wx.StaticText(panel, -1, 'Back G-code file')
		sizer.Add(back_g_txt, (9, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.back_g = wx.TextCtrl(panel, -1)
		self.back_g.SetValue(OUT_BACK_FILE)
		sizer.Add(self.back_g, (9, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		back_g_button = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(back_g_button, (9, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		self.mirror_back = wx.CheckBox(panel, -1, 'Mirror', (10, 10))
		self.mirror_back.SetValue(int(MIRROR_BACK))
		sizer.Add(self.mirror_back, (9, 5), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		self.scribe_back = wx.CheckBox(panel, -1, 'Multi-Scrape:', (10, 10))
		self.scribe_back.SetValue(int(CUT_ALL_BACK))
		sizer.Add(self.scribe_back, (10, 0), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		cut_step_back_txt = wx.StaticText(panel, -1, 'Scrape Step/Tool Diameter')
		sizer.Add(cut_step_back_txt, (10, 1), flag=wx.TOP | wx.LEFT, border=10)
		self.cut_step_back = wx.TextCtrl(panel, -1)
		self.cut_step_back.SetValue(str(CUT_STEP_R_BACK))
		sizer.Add(self.cut_step_back, (10, 2), (1, 1), wx.TOP | wx.EXPAND,  5)

		cut_max_back_txt = wx.StaticText(panel, -1, 'Scrape Loop Max')
		sizer.Add(cut_max_back_txt, (10, 3), flag=wx.TOP | wx.LEFT, border=10)
		self.cut_max_back = wx.TextCtrl(panel, -1)
		self.cut_max_back.SetValue(str(CUT_MAX_BACK))
		sizer.Add(self.cut_max_back, (10, 4), (1, 1), wx.TOP | wx.EXPAND,  5)

		text4 = wx.StaticText(panel, -1, 'G-code Drill file')
		sizer.Add(text4, (11, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.gdrill = wx.TextCtrl(panel, -1)
		self.gdrill.SetValue(OUT_DRILL_FILE)
		sizer.Add(self.gdrill, (11, 1), (1, 3), wx.TOP | wx.EXPAND,  5)

		button4 = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button4, (11, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		self.mirror_drill = wx.CheckBox(panel, -1, 'Mirror', (10, 10))
		self.mirror_drill.SetValue(int(MIRROR_DRILL))
		sizer.Add(self.mirror_drill, (11, 5), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)


		text_gedge = wx.StaticText(panel, -1, 'G-code Edge file')
		sizer.Add(text_gedge, (12, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.gedge = wx.TextCtrl(panel, -1)
		self.gedge.SetValue(OUT_EDGE_FILE)
		sizer.Add(self.gedge, (12, 1), (1, 3), wx.TOP | wx.EXPAND,  5)

		button_gedge = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button_gedge, (12, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		self.mirror_edge = wx.CheckBox(panel, -1, 'Mirror', (10, 10))
		self.mirror_edge.SetValue(int(MIRROR_EDGE))
		sizer.Add(self.mirror_edge, (12, 5), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)


		text_gall = wx.StaticText(panel, -1, 'All G-code file')
		sizer.Add(text_gall, (13, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.gall = wx.TextCtrl(panel, -1)
		self.gall.SetValue(OUT_ALL_FILE)
		sizer.Add(self.gall, (13, 1), (1, 3), wx.TOP | wx.EXPAND,  5)

		button_gall = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button_gall, (13, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		rb2 = wx.RadioBox(panel, label="unit of Output file", choices=radioList, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		rb2.SetSelection(int(OUT_INCH_FLAG))
		sizer.Add(rb2, (14, 0), (1, 3), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		rot_ang_txt = wx.StaticText(panel, -1, 'Rotation angle (deg)')
		sizer.Add(rot_ang_txt, (14, 3), flag=wx.TOP | wx.LEFT, border=10)

		self.rot_ang = wx.TextCtrl(panel, -1)
		self.rot_ang.SetValue(str(ROT_ANG))
		sizer.Add(self.rot_ang, (14, 4), (1, 1), wx.TOP | wx.EXPAND,  5)
		
		text5 = wx.StaticText(panel, -1, 'Cutting depth')
		sizer.Add(text5, (15, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.tc5 = wx.TextCtrl(panel, -1)
		self.tc5.SetValue(str(CUT_DEPTH))
		sizer.Add(self.tc5, (15, 1), (1, 1), wx.TOP | wx.EXPAND,  5)


		text6 = wx.StaticText(panel, -1, 'Drill depth')
		sizer.Add(text6, (15, 2), flag=wx.TOP | wx.LEFT, border=10)

		self.tc6 = wx.TextCtrl(panel, -1)
		self.tc6.SetValue(str(DRILL_DEPTH))
		sizer.Add(self.tc6, (15, 3), (1, 1), wx.TOP | wx.EXPAND,  5)

		edge_dep_txt = wx.StaticText(panel, -1, 'Edge depth')
		sizer.Add(edge_dep_txt, (15, 4), flag=wx.TOP | wx.LEFT, border=10)

		self.edge_dep = wx.TextCtrl(panel, -1)
		self.edge_dep.SetValue(str(EDGE_DEPTH))
		sizer.Add(self.edge_dep, (15, 5), (1, 1), wx.TOP | wx.EXPAND,  5)

		button5 = wx.Button(panel, -1, 'OK', size=(-1, 30))
		sizer.Add(button5, (17, 3), (1, 1),  wx.LEFT, 10)

		button6 = wx.Button(panel, -1, 'Close', size=(-1, 30))
		sizer.Add(button6, (17, 4), (1, 1),  wx.LEFT | wx.BOTTOM | wx.RIGHT, 10)

		sizer.AddGrowableCol(2)

		panel.SetSizer(sizer)
		sizer.Fit(self)
		# Events.
		self.Bind(wx.EVT_BUTTON, self.OnGerberOpen, button1)
		self.Bind(wx.EVT_BUTTON, self.OnBackOpen, back_button)
		self.Bind(wx.EVT_BUTTON, self.OnDrillOpen, button2)
		self.Bind(wx.EVT_BUTTON, self.OnEdgeOpen, button_edge)
		self.Bind(wx.EVT_BUTTON, self.OnGcodeOpen, button3)
		self.Bind(wx.EVT_BUTTON, self.OnGBackOpen, back_g_button)
		self.Bind(wx.EVT_BUTTON, self.OnGDrillOpen, button4)
		self.Bind(wx.EVT_BUTTON, self.OnGEdgeOpen, button_gedge)
		self.Bind(wx.EVT_BUTTON, self.OnGAllOpen, button_gall)
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
		#global GERBER_EXT
		""" Open a front pattern file"""
		dlg = wx.FileDialog(self, "Choose a input Gerber file", self.dirname, "", GERBER_EXT, wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.gerber.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnBackOpen(self,e):
		#global GERBER_EXT
		""" Open a Back pattern file"""
		dlg = wx.FileDialog(self, "Choose a input Gerber file", self.dirname, "", BACK_EXT, wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.back.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()
	def OnDrillOpen(self,e):
		#global DRILL_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a input Drill file", self.dirname, "", DRILL_EXT, wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.drill.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnEdgeOpen(self,e):
		#global EDGE_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a input Edge file", self.dirname, "", EDGE_EXT, wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.edge.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnGcodeOpen(self,e):
		#global GCODE_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a output G-code Front file", self.dirname, "", GCODE_EXT, wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.gcode.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnGBackOpen(self,e):
		#global GCODE_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a output G-code Back file", self.dirname, "", GBACK_EXT, wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.back_g.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnGDrillOpen(self,e):
		#global GDRILL_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a output G-code Drill file", self.dirname, "", GDRILL_EXT, wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.gdrill.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnGEdgeOpen(self,e):
		#global GEDGE_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a output G-code Edge file", self.dirname, "", GEDGE_EXT, wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.gedge.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnGAllOpen(self,e):
		#global GEDGE_EXT
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a output All G-code file", self.dirname, "", GCODE_EXT, wx.SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.gall.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnOK(self,e):
		global DRILL_DEPTH, EDGE_DEPTH, CUT_DEPTH
		global gPATTERNS,gBACK_PATTERNS, gDRAWDRILL,gDRAWDRILL_LINE, gDRAWEDGE, gDRAWCONTOUR,gDRAWCONTOUR_BACK
		global FRONT_FILE,BACK_FILE,DRILL_FILE,EDGE_FILE, OUT_FRONT_FILE,OUT_BACK_FILE ,OUT_DRILL_FILE, OUT_EDGE_FILE,OUT_ALL_FILE
		global MIRROR_FRONT, MIRROR_BACK, MIRROR_DRILL, MIRROR_EDGE, ROT_ANG
		#global gFRONT, gBACK
		#global gFRONT_HEADER,gBACK_HEADER,gDRILL_HEADER,gEDGE_HEADER
		global CUT_STEP_R_FRONT,CUT_STEP_R_BACK,CUT_MAX_FRONT,CUT_MAX_BACK,CUT_ALL_FRONT,CUT_ALL_BACK
		global gFIG_XMAX,gFIG_YMAX,gFIG_XMIN,gFIG_YMIN,gFIG_CX,gFIG_CY
		global gMAG,gDRAW_XSHIFT, gDRAW_YSHIFT
		#initialize
		gPATTERNS = []
		gBACK_PATTERNS = []
		gDRAWDRILL = []
		gDRAWDRILL_LINE = []
		gDRAWEDGE = []
		gDRAWCONTOUR = []
		gDRAWCONTOUR_BACK = []
		size = self.GetSize()
		#print size
		if(self.gerber.GetValue()):
			FRONT_FILE = self.gerber.GetValue()
			front_gerber = gerber.Gerber(GERBER_DIR,FRONT_FILE,OUT_UNIT)
			tmp_front = gs.Gerber_OP(front_gerber,TOOL_D)
			tmp_front.gerber2shapely()
			tmp_front.get_minmax(tmp_front.tmp_figs)
			tmp_front.draw_out()
			gFIG_XMAX = tmp_front.xmax
			gFIG_YMAX = tmp_front.ymax
			gFIG_XMIN = tmp_front.xmin
			gFIG_YMIN = tmp_front.ymin
			gFIG_CX = (gFIG_XMAX+gFIG_XMIN)/2.0
			gFIG_CY = (gFIG_YMAX+gFIG_YMIN)/2.0
			front_draw(tmp_front.draw_figs)
			gMAG=size.x/abs(gFIG_XMAX-gFIG_XMIN)
			if gMAG > size.y/abs(gFIG_YMAX-gFIG_YMIN):
				gMAG = size.y/abs(gFIG_YMAX-gFIG_YMIN)
			gDRAW_XSHIFT = -gFIG_CX*gMAG
			gDRAW_YSHIFT = gFIG_CY*gMAG

		if(self.back.GetValue()):
			BACK_FILE = self.back.GetValue()
			back_gerber = gerber.Gerber(GERBER_DIR,BACK_FILE,OUT_UNIT)
			tmp_back = gs.Gerber_OP(back_gerber,TOOL_D/IN_UNIT)
			tmp_back.in_unit=IN_UNIT
			tmp_back.out_unit=OUT_UNIT
			tmp_back.gerber2shapely()
			tmp_back.draw_out()
			back_draw(tmp_back.draw_figs)
		if(self.drill.GetValue()):
			DRILL_FILE = self.drill.GetValue()
			drill_gerber=gerber.Drill(GERBER_DIR,DRILL_FILE,OUT_UNIT)
			#drill_gerber.parse()
			tmp_drill = gs.Gerber_OP(drill_gerber,DRILL_D)
			tmp_drill.in_unit=IN_UNIT
			tmp_drill.out_unit=OUT_UNIT
			tmp_drill.drill2shapely()
			tmp_drill.draw_out()
			drill_draw(tmp_drill.draw_figs)
		if(self.edge.GetValue()):
			EDGE_FILE = self.edge.GetValue()
			edge_gerber = gerber.Gerber(GERBER_DIR,EDGE_FILE,OUT_UNIT)
			tmp_edge = gs.Gerber_OP(edge_gerber,EDGE_TOOL_D)
			tmp_edge.in_unit=IN_UNIT
			tmp_edge.out_unit=OUT_UNIT
			tmp_edge.edge2shapely()
			tmp_edge.draw_out()
			edge_draw(tmp_edge.draw_figs)

		if(self.gcode.GetValue()):
			OUT_FRONT_FILE = self.gcode.GetValue()
		if(self.back_g.GetValue()):
			OUT_BACK_FILE = self.back_g.GetValue()
		if(self.gdrill.GetValue()):
			OUT_DRILL_FILE = self.gdrill.GetValue()
		if(self.gedge.GetValue()):
			OUT_EDGE_FILE = self.gedge.GetValue()
		if(self.gall.GetValue()):
			OUT_ALL_FILE = self.gall.GetValue()
		if(self.rot_ang.GetValue()):
			ROT_ANG = float(self.rot_ang.GetValue())
		if(self.cut_step_front.GetValue()):
			CUT_STEP_R_FRONT = float(self.cut_step_front.GetValue())
		if(self.cut_step_back.GetValue()):
			CUT_STEP_R_BACK = float(self.cut_step_back.GetValue())
		if(self.cut_max_front.GetValue()):
			CUT_MAX_FRONT = int(self.cut_max_front.GetValue())
		if(self.cut_max_back.GetValue()):
			CUT_MAX_BACK = int(self.cut_max_back.GetValue())

		CUT_DEPTH = self.tc5.GetValue()
		DRILL_DEPTH =self.tc6.GetValue()
		EDGE_DEPTH =self.edge_dep.GetValue()
		MIRROR_FRONT = int(self.mirror_front.IsChecked())
		MIRROR_BACK = int(self.mirror_back.IsChecked())
		MIRROR_DRILL = int(self.mirror_drill.IsChecked())
		MIRROR_EDGE = int(self.mirror_edge.IsChecked())
		CUT_ALL_FRONT = int(self.scribe_front.IsChecked())
		CUT_ALL_BACK = int(self.scribe_back.IsChecked())
		self.Close(True)  # Close the frame.

	def OnClose(self,e):
		self.Close(True)  # Close the frame.


class MachineSetup(wx.Dialog):
	def __init__(self, parent, id, title):

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

		text10 = wx.StaticText(panel, -1, 'Drill XY speed')
		sizer.Add(text10, (9, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.drillspeed = wx.TextCtrl(panel, -1)
		self.drillspeed.SetValue(str(DRILL_SPEED))
		sizer.Add(self.drillspeed, (9, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		drill_z_txt = wx.StaticText(panel, -1, 'Drill down speed')
		sizer.Add(drill_z_txt, (10, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.drillzspeed = wx.TextCtrl(panel, -1)
		self.drillzspeed.SetValue(str(DRILL_Z_SPEED))
		sizer.Add(self.drillzspeed, (10, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text11 = wx.StaticText(panel, -1, 'Drill diameter')
		sizer.Add(text11, (11, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.drilld = wx.TextCtrl(panel, -1)
		self.drilld.SetValue(str(DRILL_D))
		sizer.Add(self.drilld, (11, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text12 = wx.StaticText(panel, -1, 'Edge depth')
		sizer.Add(text12, (12, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edgedep = wx.TextCtrl(panel, -1)
		self.edgedep.SetValue(str(EDGE_DEPTH))
		sizer.Add(self.edgedep, (12, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text13 = wx.StaticText(panel, -1, 'Edge tool diameter')
		sizer.Add(text13, (13, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edged = wx.TextCtrl(panel, -1)
		self.edged.SetValue(str(EDGE_TOOL_D))
		sizer.Add(self.edged, (13, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text14 = wx.StaticText(panel, -1, 'Edge cutting speed')
		sizer.Add(text14, (14, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edgespeed = wx.TextCtrl(panel, -1)
		self.edgespeed.SetValue(str(EDGE_SPEED))
		sizer.Add(self.edgespeed, (14, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text15 = wx.StaticText(panel, -1, 'Edge Z speed')
		sizer.Add(text15, (15, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edgezspeed = wx.TextCtrl(panel, -1)
		self.edgezspeed.SetValue(str(EDGE_Z_SPEED))
		sizer.Add(self.edgezspeed, (15, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text16 = wx.StaticText(panel, -1, 'Z step')
		sizer.Add(text16, (16, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.zstep = wx.TextCtrl(panel, -1)
		self.zstep.SetValue(str(Z_STEP))
		sizer.Add(self.zstep, (16, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

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
		global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, XY_SPEED, Z_SPEED, DRILL_SPEED,DRILL_Z_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, EDGE_TOOL_D, EDGE_DEPTH, EDGE_SPEED, EDGE_Z_SPEED, Z_STEP
		#global LEFT_X, LOWER_Y
		INI_X = float(self.inix.GetValue())
		INI_Y = float(self.iniy.GetValue())
		INI_Z = float(self.iniz.GetValue())
		MOVE_HEIGHT = float(self.moveh.GetValue())
		XY_SPEED = int(self.xyspeed.GetValue())
		Z_SPEED = int(self.zspeed.GetValue())
		DRILL_SPEED = int(self.drillspeed.GetValue())
		DRILL_Z_SPEED = int(self.drillzspeed.GetValue())
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
		global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, XY_SPEED, Z_SPEED, DRILL_SPEED,DRILL_Z_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, EDGE_TOOL_D, EDGE_DEPTH, EDGE_SPEED, EDGE_Z_SPEED, Z_STEP
		#global LEFT_X, LOWER_Y
		INI_X = float(self.inix.GetValue())
		INI_Y = float(self.iniy.GetValue())
		INI_Z = float(self.iniz.GetValue())
		MOVE_HEIGHT = float(self.moveh.GetValue())
		XY_SPEED = int(self.xyspeed.GetValue())
		Z_SPEED = int(self.zspeed.GetValue())
		DRILL_SPEED = int(self.drillspeed.GetValue())
		DRILL_Z_SPEED = int(self.drillzspeed.GetValue())
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
		wx.Dialog.__init__(self, parent, id, title, size=(250, 210))

		panel = wx.Panel(self, -1)
		sizer = wx.GridBagSizer(0, 0)

		text1 = wx.StaticText(panel, -1, 'Front data color')
		sizer.Add(text1, (0, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.gerber_color = wx.ComboBox(panel, -1, choices=gCOLORS, style=wx.CB_READONLY)
		self.gerber_color.SetValue(str(GERBER_COLOR))
		sizer.Add(self.gerber_color, (0, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		back_color_txt = wx.StaticText(panel, -1, 'Back data color')
		sizer.Add(back_color_txt, (1, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.back_color = wx.ComboBox(panel, -1, choices=gCOLORS, style=wx.CB_READONLY)
		self.back_color.SetValue(str(BACK_COLOR))
		sizer.Add(self.back_color, (1, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text2 = wx.StaticText(panel, -1, 'Drill data color')
		sizer.Add(text2, (2, 0), flag=wx.TOP | wx.LEFT, border=10)
		self.drill_color = wx.ComboBox(panel, -1, choices=gCOLORS, style=wx.CB_READONLY)
		self.drill_color.SetValue(str(DRILL_COLOR))
		sizer.Add(self.drill_color, (2, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text3 = wx.StaticText(panel, -1, 'Edge data color')
		sizer.Add(text3, (3, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edge_color = wx.ComboBox(panel, -1, choices=gCOLORS, style=wx.CB_READONLY)
		self.edge_color.SetValue(str(EDGE_COLOR))
		sizer.Add(self.edge_color, (3, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text4 = wx.StaticText(panel, -1, 'Front Contour color')
		sizer.Add(text4, (4, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.contour_color = wx.ComboBox(panel, -1, choices=gCOLORS, style=wx.CB_READONLY)
		self.contour_color.SetValue(str(CONTOUR_COLOR))
		sizer.Add(self.contour_color, (4, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		back_contour_text = wx.StaticText(panel, -1, 'Back Contour color')
		sizer.Add(back_contour_text, (5, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.back_contour_color = wx.ComboBox(panel, -1, choices=gCOLORS, style=wx.CB_READONLY)
		self.back_contour_color.SetValue(str(CONTOUR_BACK_COLOR))
		sizer.Add(self.back_contour_color, (5, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text5 = wx.StaticText(panel, -1, 'Front file extension')
		sizer.Add(text5, (6, 0), flag=wx.TOP | wx.LEFT, border=10)
		self.gerber_ext = wx.TextCtrl(panel, -1)
		self.gerber_ext.SetValue(str(GERBER_EXT))
		sizer.Add(self.gerber_ext, (6, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		back_ex_txt = wx.StaticText(panel, -1, 'Back file extension')
		sizer.Add(back_ex_txt, (7, 0), flag=wx.TOP | wx.LEFT, border=10)
		self.back_ext = wx.TextCtrl(panel, -1)
		self.back_ext.SetValue(str(BACK_EXT))
		sizer.Add(self.back_ext, (7, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text6 = wx.StaticText(panel, -1, 'Drill file extension')
		sizer.Add(text6, (8, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.drill_ext = wx.TextCtrl(panel, -1)
		self.drill_ext.SetValue(str(DRILL_EXT))
		sizer.Add(self.drill_ext, (8, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text7 = wx.StaticText(panel, -1, 'Edge file extension')
		sizer.Add(text7, (9, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.edge_ext = wx.TextCtrl(panel, -1)
		self.edge_ext.SetValue(str(EDGE_EXT))
		sizer.Add(self.edge_ext, (9, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text8 = wx.StaticText(panel, -1, 'Gcode fornt file extension')
		sizer.Add(text8, (10, 0), flag=wx.TOP | wx.LEFT, border=10)
		self.gcode_ext = wx.TextCtrl(panel, -1)
		self.gcode_ext.SetValue(str(GCODE_EXT))
		sizer.Add(self.gcode_ext, (10, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		back_g_txt = wx.StaticText(panel, -1, 'Gcode back file extension')
		sizer.Add(back_g_txt, (11, 0), flag=wx.TOP | wx.LEFT, border=10)
		self.back_g_ext = wx.TextCtrl(panel, -1)
		self.back_g_ext.SetValue(str(GBACK_EXT))
		sizer.Add(self.back_g_ext, (11, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text9 = wx.StaticText(panel, -1, 'Gcode Drill file extension')
		sizer.Add(text9, (12, 0), flag=wx.TOP | wx.LEFT, border=10)
		self.gdrill_ext = wx.TextCtrl(panel, -1)
		self.gdrill_ext.SetValue(str(GDRILL_EXT))
		sizer.Add(self.gdrill_ext, (12, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text10 = wx.StaticText(panel, -1, 'Gcode Edge file extension')
		sizer.Add(text10, (13, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.gedge_ext = wx.TextCtrl(panel, -1)
		self.gedge_ext.SetValue(str(GEDGE_EXT))
		sizer.Add(self.gedge_ext, (13, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text12 = wx.StaticText(panel, -1, 'G code left X')
		sizer.Add(text12, (14, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.leftx = wx.TextCtrl(panel, -1)
		self.leftx.SetValue(str(LEFT_X))
		sizer.Add(self.leftx, (14, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		text13 = wx.StaticText(panel, -1, 'G code lower Y')
		sizer.Add(text13, (15, 0), flag= wx.LEFT | wx.TOP, border=10)
		self.lowy = wx.TextCtrl(panel, -1)
		self.lowy.SetValue(str(LOWER_Y))
		sizer.Add(self.lowy, (15, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		radioList_cut = ['line only', 'all']
		self.rb_cut = wx.RadioBox(panel, label="Scrape Front", choices=radioList_cut, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		self.rb_cut.SetSelection(int(CUT_ALL_FRONT))
		sizer.Add(self.rb_cut, (16, 0), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)
		self.rb_cut_back = wx.RadioBox(panel, label="Scrape Back", choices=radioList_cut, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		self.rb_cut_back.SetSelection(int(CUT_ALL_BACK))
		sizer.Add(self.rb_cut_back, (16, 1), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		self.ptn_shift = wx.CheckBox(panel, -1, 'Pattern Shift', (10, 10))
		self.ptn_shift.SetValue(int(PATTERN_SHIFT))
		sizer.Add(self.ptn_shift, (16, 2), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)
		#text_cut = wx.StaticText(panel, -1, 'Scrape Exteria margin Ratio')
		#sizer.Add(text_cut, (17, 0), flag= wx.LEFT | wx.TOP, border=10)
		#self.cut_margin = wx.TextCtrl(panel, -1)
		#self.cut_margin.SetValue(str(CUT_MARGIN_R))
		#sizer.Add(self.ccut_margin, (17, 1), (1, 1), wx.TOP | wx.EXPAND, 5)

		radioList = ['mm', 'inch']
		self.rb1 = wx.RadioBox(panel, label="unit of Input file", choices=radioList, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		self.rb1.SetSelection(int(IN_INCH_FLAG))
		sizer.Add(self.rb1, (18, 0), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		self.rb2 = wx.RadioBox(panel, label="unit of Output file", choices=radioList, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		self.rb2.SetSelection(int(OUT_INCH_FLAG))
		sizer.Add(self.rb2, (18, 1), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		self.cb1 = wx.CheckBox(panel, -1, 'Enable M code', (10, 10))
		self.cb1.SetValue(int(MCODE_FLAG))
		sizer.Add(self.cb1, (18, 2), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		button0 = wx.Button(panel, -1, 'Save to config file', size=(-1, 30))
		sizer.Add(button0, (20, 0), (1, 1),  wx.LEFT, 10)

		button1 = wx.Button(panel, -1, 'Temporally Apply', size=(-1, 30))
		sizer.Add(button1, (20, 1), (1, 1),  wx.LEFT, 10)

		button2 = wx.Button(panel, -1, 'Close', size=(-1, 30))
		sizer.Add(button2, (20, 2), (1, 1),  wx.LEFT | wx.BOTTOM | wx.RIGHT, 10)
		sizer.AddGrowableCol(2)

		panel.SetSizer(sizer)
		sizer.Fit(self)
		#Event
		self.Bind(wx.EVT_BUTTON, self.OnSave, button0)
		self.Bind(wx.EVT_BUTTON, self.OnApply, button1)
		self.Bind(wx.EVT_BUTTON, self.OnClose, button2)

	def OnApply(self,e):
		global IN_INCH_FLAG,OUT_INCH_FLAG, MCODE_FLAG,LEFT_X,LOWER_Y
		global GERBER_COLOR,BACK_COLOR, DRILL_COLOR, EDGE_COLOR , CONTOUR_COLOR,CONTOUR_BACK_COLOR
		global GERBER_EXT, BACK_EXT,DRILL_EXT, EDGE_EXT, GCODE_EXT,GBACK_EXT, GDRILL_EXT, GEDGE_EXT
		global CUT_ALL_FRONT,CUT_ALL_BACK,CUT_MARGIN_R,PATTERN_SHIFT

		IN_INCH_FLAG = int(self.rb1.GetSelection())
		OUT_INCH_FLAG = int(self.rb2.GetSelection())
		MCODE_FLAG = int(self.cb1.IsChecked())
		LEFT_X = float(self.leftx.GetValue())
		LOWER_Y = float(self.lowy.GetValue())
		#
		GERBER_COLOR = str(self.gerber_color.GetValue())
		BACK_COLOR = str(self.back_color.GetValue())
		DRILL_COLOR = str(self.drill_color.GetValue())
		EDGE_COLOR = str(self.edge_color.GetValue())
		CONTOUR_COLOR = str(self.contour_color.GetValue())
		CONTOUR_BACK_COLOR = str(self.back_contour_color.GetValue())
		#
		GERBER_EXT = str(self.gerber_ext.GetValue())
		BACK_EXT = str(self.back_ext.GetValue())
		DRILL_EXT = str(self.drill_ext.GetValue())
		EDGE_EXT = str(self.edge_ext.GetValue())
		GCODE_EXT = str(self.gcode_ext.GetValue())
		GBACK_EXT = str(self.back_g_ext.GetValue())
		GDRILL_EXT = str(self.gdrill_ext.GetValue())
		GEDGE_EXT = str(self.gedge_ext.GetValue())
		#
		CUT_ALL_FRONT = int(self.rb_cut.GetSelection())
		CUT_ALL_BACK = int(self.rb_cut_back.GetSelection())
		#CUT_MARGIN_R = float(self.cut_margin.GetValue())
		PATTERN_SHIFT = int(self.ptn_shift.IsChecked())

		#show_all_values()
		self.Close(True)  # Close the frame.
	def OnClose(self,e):
		self.Close(True)  # Close the frame.
	def OnSave(self,e):
		global IN_INCH_FLAG,OUT_INCH_FLAG, MCODE_FLAG,LEFT_X,LOWER_Y
		global GERBER_COLOR,BACK_COLOR, DRILL_COLOR, EDGE_COLOR , CONTOUR_COLOR,CONTOUR_BACK_COLOR
		global GERBER_EXT, BACK_EXT,DRILL_EXT, EDGE_EXT, GCODE_EXT,GBACK_EXT, GDRILL_EXT, GEDGE_EXT
		global CUT_ALL_FRONT,CUT_ALL_BACK,CUT_MARGIN_R,PATTERN_SHIFT

		IN_INCH_FLAG = int(self.rb1.GetSelection())
		OUT_INCH_FLAG = int(self.rb2.GetSelection())
		MCODE_FLAG = int(self.cb1.IsChecked())
		LEFT_X = float(self.leftx.GetValue())
		LOWER_Y = float(self.lowy.GetValue())
		#
		GERBER_COLOR = str(self.gerber_color.GetValue())
		BACK_COLOR = str(self.back_color.GetValue())
		DRILL_COLOR = str(self.drill_color.GetValue())
		EDGE_COLOR = str(self.edge_color.GetValue())
		CONTOUR_COLOR = str(self.contour_color.GetValue())
		CONTOUR_BACK_COLOR = str(self.back_contour_color.GetValue())
		#
		GERBER_EXT = str(self.gerber_ext.GetValue())
		BACK_EXT = str(self.back_ext.GetValue())
		DRILL_EXT = str(self.drill_ext.GetValue())
		EDGE_EXT = str(self.edge_ext.GetValue())
		GCODE_EXT = str(self.gcode_ext.GetValue())
		GBACK_EXT = str(self.back_g_ext.GetValue())
		GDRILL_EXT = str(self.gdrill_ext.GetValue())
		GEDGE_EXT = str(self.gedge_ext.GetValue())
		#
		CUT_ALL_FRONT = int(self.rb_cut.GetSelection())
		CUT_ALL_BACK = int(self.rb_cut_back.GetSelection())
		#CUT_MARGIN_R = float(self.cut_margin.GetValue())
		PATTERN_SHIFT = int(self.rb_cut.GetSelection())
		save_config()
		self.Close(True)  # Close the frame.


#Set Class
class DRAWPOLY:
	def __init__(self, points, color ,delete):
		self.points = points
		self.color = color
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

#functions
def main():
	if len(sys.argv) > 1 and sys.argv[1]:
		read_config(sys.argv[1])
	else:
		read_config(CONFIG_FILE)
	set_unit()
	#app = wx.App()
	#app = wx.App(redirect=True)
	app = wx.App(redirect=False)
	MainFrame(None, -1, 'pyGerber2Gcode')
	app.MainLoop()
def set_unit():
	global IN_UNIT,OUT_UNIT
	if OUT_INCH_FLAG == 1:
		OUT_UNIT = INCH
	else:
		OUT_UNIT = 1.0
	if IN_INCH_FLAG == 1:
		IN_UNIT = INCH
	else:
		IN_UNIT = 1.0

def front_draw(header):
	global gPATTERNS
	gPATTERNS = []
	for polygon in header.elements:
		gPATTERNS.append(DRAWPOLY(polygon.points,"",0))
def back_draw(header):
	global gBACK_PATTERNS
	gBACK_PATTERNS = []
	for polygon in header.elements:
		gBACK_PATTERNS.append(DRAWPOLY(polygon.points,"",0))
def edge_draw(header):
	global gDRAWEDGE
	gDRAWEDGE = []
	for polygon in header.elements:
		gDRAWEDGE.append(DRAWPOLY(polygon.points,"",0))
def drill_draw(header):
	global gDRAWDRILL_LINE,gDRAWDRILL
	gDRAWDRILL_LINE = []
	gDRAWDRILL = []
	for polygon in header.elements:
		if len(polygon.points) > 1:
			gDRAWDRILL_LINE.append(DRAWPOLY(polygon.points,"",0))
		else:
			gDRAWDRILL.append(DRILL(polygon.points[0][0],polygon.points[0][1],DRILL_D,0))

def set_gcode(gcode_handler):
	gcode_handler.mcode_sw = MCODE_FLAG
	gcode_handler.unit = OUT_INCH_FLAG
	gcode_handler.ini_x = INI_X
	gcode_handler.ini_y = INI_Y
	gcode_handler.ini_z = INI_Z
	gcode_handler.move_hight = MOVE_HEIGHT

def contour2draw_front(header):
	global gDRAWCONTOUR
	for polygon in header.elements:
		gDRAWCONTOUR.append(DRAWPOLY(polygon.points,"",0))
def contour2draw_back(header):
	global gDRAWCONTOUR_BACK
	for polygon in header.elements:
		gDRAWCONTOUR_BACK.append(DRAWPOLY(polygon.points,"",0))

def save_config():
	config_data ="#Data files\n"
	config_data += "GERBER_DIR = \"" + str(GERBER_DIR) + "\"\n"
	config_data += "FRONT_FILE = \"" + str(FRONT_FILE) + "\"\n"
	config_data += "BACK_FILE = \"" + str(BACK_FILE) + "\"\n"
	config_data += "DRILL_FILE = \"" + str(DRILL_FILE) + "\"\n"
	config_data += "EDGE_FILE = \"" + str(EDGE_FILE) + "\"\n"
	config_data += "OUT_DIR = \"" + str(OUT_DIR) + "\"\n"
	config_data += "OUT_FRONT_FILE = \"" + str(OUT_FRONT_FILE) + "\"\n"
	config_data += "OUT_BACK_FILE = \"" + str(OUT_BACK_FILE) + "\"\n"
	config_data += "OUT_DRILL_FILE = \"" + str(OUT_DRILL_FILE) + "\"\n"
	config_data += "OUT_EDGE_FILE = \"" + str(OUT_EDGE_FILE) + "\"\n"
	config_data += "OUT_ALL_FILE = \"" + str(OUT_ALL_FILE) + "\"\n"
	#
	config_data += "MIRROR_FRONT = " + str(MIRROR_FRONT) + "\n"
	config_data += "MIRROR_BACK = " + str(MIRROR_BACK) + "\n"
	config_data += "MIRROR_DRILL = " + str(MIRROR_DRILL) + "\n"
	config_data += "MIRROR_EDGE = " + str(MIRROR_EDGE) + "\n"
	config_data += "ROT_ANG = " + str(ROT_ANG) + "\n"
	config_data += "CUT_ALL_FRONT = " + str(CUT_ALL_FRONT) + "\n"
	config_data += "CUT_ALL_BACK = " + str(CUT_ALL_BACK) + "\n"
	config_data += "CUT_STEP_R_FRONT = " + str(CUT_STEP_R_FRONT) + "\n"
	config_data += "CUT_STEP_R_BACK = " + str(CUT_STEP_R_BACK) + "\n"
	config_data += "CUT_MAX_FRONT = " + str(CUT_MAX_FRONT) + "\n"
	config_data += "CUT_MAX_BACK = " + str(CUT_MAX_BACK) + "\n"
	config_data += "CUT_MARGIN_R = " + str(CUT_MARGIN_R) + "\n"

	##############
	config_data +="\n#Convert Setting\n"
	config_data += "IN_INCH_FLAG = " + str(IN_INCH_FLAG) + "\n"
	config_data += "OUT_INCH_FLAG = " + str(OUT_INCH_FLAG) + "\n"
	config_data += "MCODE_FLAG = " + str(MCODE_FLAG) + "\n"
	config_data += "GERBER_COLOR = \"" + str(GERBER_COLOR) + "\"\n"
	config_data += "BACK_COLOR = \"" + str(BACK_COLOR) + "\"\n"
	config_data += "DRILL_COLOR = \"" + str(DRILL_COLOR) + "\"\n"
	config_data += "EDGE_COLOR = \"" + str(EDGE_COLOR) + "\"\n"
	config_data += "CONTOUR_COLOR = \"" + str(CONTOUR_COLOR) + "\"\n"
	config_data += "CONTOUR_BACK_COLOR = \"" + str(CONTOUR_BACK_COLOR) + "\"\n"
	config_data += "GERBER_EXT = \"" + str(GERBER_EXT) + "\"\n"
	config_data += "BACK_EXT = \"" + str(BACK_EXT) + "\"\n"
	config_data += "DRILL_EXT = \"" + str(DRILL_EXT) + "\"\n"
	config_data += "EDGE_EXT = \"" + str(EDGE_EXT) + "\"\n"
	config_data += "GCODE_EXT = \"" + str(GCODE_EXT) + "\"\n"
	config_data += "GBACK_EXT = \"" + str(GBACK_EXT) + "\"\n"
	config_data += "GDRILL_EXT = \"" + str(GDRILL_EXT) + "\"\n"
	config_data += "GEDGE_EXT = \"" + str(GEDGE_EXT) + "\"\n"
	#config_data += "CUT_ALL_FRONT = " + str(CUT_ALL_FRONT) + "\n"
	#config_data += "CUT_ALL_BACK = " + str(CUT_ALL_BACK) + "\n"
	#Optional
	config_data += "PATTERN_SHIFT = " + str(PATTERN_SHIFT) + "\n"
	#######################
	config_data +="\n#Machine Setting\n"
	config_data += "INI_X = " + str(INI_X) + "\n"
	config_data += "INI_Y = " + str(INI_Y) + "\n"
	config_data += "INI_Z = " + str(INI_Z) + "\n"
	config_data += "MOVE_HEIGHT = " + str(MOVE_HEIGHT) + "\n"
	config_data += "XY_SPEED = " + str(XY_SPEED) + "\n"
	config_data += "Z_SPEED = " + str(Z_SPEED) + "\n"
	config_data += "LEFT_X = " + str(LEFT_X) + "\n"
	config_data += "LOWER_Y = " + str(LOWER_Y) + "\n"
	config_data += "DRILL_SPEED = " + str(DRILL_SPEED) + "\n"
	config_data += "DRILL_Z_SPEED = " + str(DRILL_Z_SPEED) + "\n"
	config_data += "DRILL_DEPTH = " + str(DRILL_DEPTH) + "\n"
	config_data += "CUT_DEPTH = " + str(CUT_DEPTH) + "\n"
	config_data += "TOOL_D = " + str(TOOL_D) + "\n"
	config_data += "DRILL_D = " + str(DRILL_D) + "\n"
	config_data += "EDGE_TOOL_D = " + str(EDGE_TOOL_D) + "\n"
	config_data += "EDGE_DEPTH = " + str(EDGE_DEPTH) + "\n"
	config_data += "EDGE_SPEED = " + str(EDGE_SPEED) + "\n"
	config_data += "EDGE_Z_SPEED = " + str(EDGE_Z_SPEED) + "\n"
	config_data += "Z_STEP=" + str(Z_STEP) + "\n"

	out = open(CONFIG_FILE, 'w')
	out.write(config_data)
	out.close()
def read_config(config_file):
	global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_Z_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, EDGE_TOOL_D, EDGE_DEPTH, EDGE_SPEED, EDGE_Z_SPEED, Z_STEP, GERBER_EXT, DRILL_EXT, EDGE_EXT, GCODE_EXT, GDRILL_EXT, GEDGE_EXT,DRILL_ENDMILL
	global GERBER_COLOR, DRILL_COLOR, EDGE_COLOR , CONTOUR_COLOR,CONTOUR_BACK_COLOR
	global GERBER_DIR,FRONT_FILE,BACK_FILE,DRILL_FILE,EDGE_FILE,MIRROR_FRONT,MIRROR_BACK,MIRROR_DRILL,MIRROR_EDGE,ROT_ANG
	global OUT_DIR,OUT_FRONT_FILE,OUT_BACK_FILE,OUT_DRILL_FILE,OUT_EDGE_FILE,OUT_ALL_FILE
	global CUT_ALL_FRONT, CUT_ALL_BACK, CUT_STEP_R_FRONT,CUT_STEP_R_BACK,CUT_MAX_FRONT, CUT_MAX_BACK,PATTERN_SHIFT
	#print "Read config file"
	try:
		f = open(config_file,'r')
	except IOError, (errno, strerror):
		print "Unable to open the file =" + config_file + "\n"
	else:
		while 1:
			config = f.readline()
			if not config:
				break
			cfg = re.search("([A-Z\_]+)[\d\s\ ]*\=[\ \"]*([^\ \"\n\r]+)\"*",config)
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
				if(cfg.group(1)=="CONTOUR_BACK_COLOR"):
					CONTOUR_BACK_COLOR = str(cfg.group(2))
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
				if(cfg.group(1)=="DRILL_ENDMILL"):
					DRILL_ENDMILL = int(cfg.group(2))

		f.close()

def drill2gcode(gcode_header,elements):
	z_step_n = int(float(DRILL_DEPTH)/float(Z_STEP)) + 1
	z_step = float(DRILL_DEPTH)/z_step_n
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
	z_step_n = int(float(EDGE_DEPTH)/float(Z_STEP)) + 1
	z_step = float(EDGE_DEPTH)/z_step_n
	j = 1
	while j <= z_step_n:
		z_depth = j*z_step
		gcode_header.add_polygon(z_depth,elements, EDGE_SPEED, EDGE_Z_SPEED)
		j += 1
if __name__ == "__main__":
	main()
