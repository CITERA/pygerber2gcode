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

#Global Constant
HUGE = 1e10
TINY = 1e-6
INCH = 25.4 #mm
MIL = INCH/1000
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
DRILL_D = 0		#Drill diameter
CAD_UNIT = MIL/10

#Global variable
gXMIN = HUGE
gYMIN = HUGE
gXSHIFT = 0
gYSHIFT = 0
gGCODE_DATA = ""
gDRILL_DATA = ""
gTMP_X = INI_X 
gTMP_Y = INI_Y
gTMP_Z = INI_Z
gTMP_DRILL_X = INI_X 
gTMP_DRILL_Y = INI_Y
gTMP_DRILL_Z = INI_Z
gGERBER_TMP_X = 0
gGERBER_TMP_Y = 0
gDCODE = [0]*100
g54_FLAG = 0
gFIG_NUM = 0
gDRILL_TYPE = [0]*100
gPOLYGONS = []
gLINES = []
gDRILLS = []
gGCODES = []

#window class
class MainWindow(wx.Frame):
	def __init__(self, parent, id, title):
		global IN_INCH_FLAG, OUT_INCH_FLAG, DRILL_DEPTH, CUT_DEPTH
		self.dirname=''
		wx.Frame.__init__(self, parent, id, title)

		# Setting up the menu.
		filemenu= wx.Menu()
		menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
		setupmenu =  wx.Menu()
		menuMachine = setupmenu.Append(wx.ID_SETUP,"&Machine setup"," Setup Machine")
		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
		menuBar.Append(setupmenu,"&Setup") # Adding the "filemenu" to the MenuBar
		self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

		panel = wx.Panel(self, -1)
		sizer = wx.GridBagSizer(0, 0)

		text1 = wx.StaticText(panel, -1, 'Gerber file')
		sizer.Add(text1, (0, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.gerber = wx.TextCtrl(panel, -1)
		sizer.Add(self.gerber, (0, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		button1 = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button1, (0, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		text2 = wx.StaticText(panel, -1, 'Drill file')
		sizer.Add(text2, (1, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.drill = wx.TextCtrl(panel, -1)
		sizer.Add(self.drill, (1, 1), (1, 3), wx.TOP | wx.EXPAND,  5)

		button2 = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button2, (1, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		radioList = ['mm', 'inch']
		rb1 = wx.RadioBox(panel, label="unit of Input file", choices=radioList, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		rb1.SetSelection(int(IN_INCH_FLAG))
		sizer.Add(rb1, (2, 0), (1, 5), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		line = wx.StaticLine(panel, -1 )
		sizer.Add(line, (4, 0), (1, 5), wx.TOP | wx.EXPAND, -15)

		text3 = wx.StaticText(panel, -1, 'G-code file')
		sizer.Add(text3, (5, 0), flag= wx.LEFT | wx.TOP, border=10)

		self.gcode = wx.TextCtrl(panel, -1)
		sizer.Add(self.gcode, (5, 1), (1, 3), wx.TOP | wx.EXPAND, 5)

		button3 = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button3, (5, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		text4 = wx.StaticText(panel, -1, 'G-code Drill file')
		sizer.Add(text4, (6, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.gdrill = wx.TextCtrl(panel, -1)
		sizer.Add(self.gdrill, (6, 1), (1, 3), wx.TOP | wx.EXPAND,  5)

		button4 = wx.Button(panel, -1, 'Browse...', size=(-1, 30))
		sizer.Add(button4, (6, 4), (1, 1), wx.TOP | wx.LEFT | wx.RIGHT , 5)

		rb2 = wx.RadioBox(panel, label="unit of Output file", choices=radioList, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		rb2.SetSelection(int(OUT_INCH_FLAG))
		sizer.Add(rb2, (7, 0), (1, 5), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)
		#button3 = wx.Button(panel, -1, 'Help', size=(-1, 30))
		#sizer.Add(button3, (7, 0), (1, 1),  wx.LEFT, 10)

		text5 = wx.StaticText(panel, -1, 'Cutting depth')
		sizer.Add(text5, (8, 0), flag=wx.TOP | wx.LEFT, border=10)

		self.tc5 = wx.TextCtrl(panel, -1)
		self.tc5.SetValue(str(CUT_DEPTH))
		sizer.Add(self.tc5, (8, 1), (1, 1), wx.TOP | wx.EXPAND,  5)


		text6 = wx.StaticText(panel, -1, 'Drill depth')
		sizer.Add(text6, (8, 2), flag=wx.TOP | wx.LEFT, border=10)

		self.tc6 = wx.TextCtrl(panel, -1)
		self.tc6.SetValue(str(DRILL_DEPTH))
		sizer.Add(self.tc6, (8, 3), (1, 1), wx.TOP | wx.EXPAND,  5)

		button5 = wx.Button(panel, -1, 'Convert', size=(-1, 30))
		sizer.Add(button5, (10, 3), (1, 1),  wx.LEFT, 10)

		button6 = wx.Button(panel, -1, 'Cancel', size=(-1, 30))
		sizer.Add(button6, (10, 4), (1, 1),  wx.LEFT | wx.BOTTOM | wx.RIGHT, 10)

		sizer.AddGrowableCol(2)
        
		panel.SetSizer(sizer)
		sizer.Fit(self)
		# Events.
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		self.Bind(wx.EVT_BUTTON, self.OnGerberOpen, button1)
		self.Bind(wx.EVT_BUTTON, self.OnDrillOpen, button2)
		self.Bind(wx.EVT_BUTTON, self.OnGcodeOpen, button3)
		self.Bind(wx.EVT_BUTTON, self.OnGDrillOpen, button4)
		self.Bind(wx.EVT_BUTTON, self.OnConvert, button5)
		self.Bind(wx.EVT_BUTTON, self.OnCancel, button6)	
		self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox1, rb1)
		self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox2, rb2)
		self.Bind(wx.EVT_MENU, self.OnSetup, id=wx.ID_SETUP)

		#self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		#self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

		self.Centre()
		self.Show(True)

	#Events
	def OnAbout(self,e):
		# Create a message dialog box
		dlg = wx.MessageDialog(self, " A sample editor \n in wxPython", "About Sample Editor", wx.OK)
		dlg.ShowModal() # Shows it
		dlg.Destroy() # finally destroy it when finished.

	def OnExit(self,e):
		self.Close(True)  # Close the frame.
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
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a input Gerber file", self.dirname, "", "*.*", wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.gerber.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnDrillOpen(self,e):
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a input Drill file", self.dirname, "", "*.*", wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.drill.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnGcodeOpen(self,e):
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a output G-code file", self.dirname, "", "*.*", wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.gcode.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnGDrillOpen(self,e):
		""" Open a file"""
		dlg = wx.FileDialog(self, "Choose a output G-code Drill file", self.dirname, "", "*.*", wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			self.gdrill.SetValue(os.path.join(self.dirname, self.filename))
		dlg.Destroy()

	def OnConvert(self,e):
		global DRILL_DEPTH, CUT_DEPTH
		if(self.gerber.GetValue()==""):
			dlg = wx.MessageDialog(self, "Gerger file Error" ,"Enter Gerber file", wx.OK)
			dlg.ShowModal() # Shows it
			dlg.Destroy() # finally destroy it when finished.
		elif(self.gcode.GetValue()==""):
			dlg = wx.MessageDialog(self,  "G code file Error" ,"Enter G code file", wx.OK)
			dlg.ShowModal() # Shows it
			dlg.Destroy() # finally destroy it when finished.
		else:
			read_config()
			CUT_DEPTH = self.tc5.GetValue()
			gcode_init()
			read_Gerber(self.gerber.GetValue())
			merge()
			if(self.drill.GetValue()!=""):
				DRILL_DEPTH =self.tc6.GetValue()
				read_Drill_file(self.drill.GetValue())
				do_drill(0)
			end(self.gcode.GetValue(),self.gdrill.GetValue())
			dlg = wx.MessageDialog(self, "Convert finished", "Convert is finished" , wx.OK)
			dlg.ShowModal() # Shows it
			dlg.Destroy() # finally destroy it when finished.

	def OnCancel(self,e):
		#Crear all values
		self.gerber.SetValue("")
		self.drill.SetValue("")
		self.gcode.SetValue("")
		self.gdrill.SetValue("")

	def OnSetup(self,e):
		setup = MachineSetup(None, -1, 'Machine Setup')
		setup.ShowModal()
		setup.Destroy()

class MachineSetup(wx.Dialog):
	def __init__(self, parent, id, title):
		global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT
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

		radioList = ['mm', 'inch']
		self.rb1 = wx.RadioBox(panel, label="unit of Input file", choices=radioList, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		self.rb1.SetSelection(int(IN_INCH_FLAG))
		sizer.Add(self.rb1, (14, 0), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		self.rb2 = wx.RadioBox(panel, label="unit of Output file", choices=radioList, majorDimension=3, style=wx.RA_SPECIFY_COLS)
		self.rb2.SetSelection(int(OUT_INCH_FLAG))
		sizer.Add(self.rb2, (14, 1), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

		self.cb1 = wx.CheckBox(panel, -1, 'Enable M code', (10, 10))
		self.cb1.SetValue(int(MCODE_FLAG))
		sizer.Add(self.cb1, (14, 2), (1, 1), wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT , 10)

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
		global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT
		INI_X = self.inix.GetValue()
		INI_Y = self.iniy.GetValue()
		INI_Z = self.iniz.GetValue()
		MOVE_HEIGHT = self.moveh.GetValue()
		IN_INCH_FLAG = self.rb1.GetSelection()
		OUT_INCH_FLAG = self.rb2.GetSelection()
		MCODE_FLAG = int(self.cb1.IsChecked())
		XY_SPEED = self.xyspeed.GetValue()
		Z_SPEED = self.zspeed.GetValue()
		LEFT_X = self.leftx.GetValue()
		LOWER_Y = self.lowy.GetValue()
		DRILL_SPEED = self.drillspeed.GetValue()
		DRILL_DEPTH = self.drilldep.GetValue()
		CUT_DEPTH = self.cutdep.GetValue()
		TOOL_D = self.toold.GetValue()
		DRILL_D = self.drilld.GetValue()
		CAD_UNIT = float(self.cadunit.GetValue())
		#show_all_values()
		self.Close(True)  # Close the frame.
	def OnClose(self,e):
		self.Close(True)  # Close the frame.
	def OnSave(self,e):
		global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT
		INI_X = self.inix.GetValue()
		INI_Y = self.iniy.GetValue()
		INI_Z = self.iniz.GetValue()
		MOVE_HEIGHT = self.moveh.GetValue()
		IN_INCH_FLAG = self.rb1.GetSelection()
		OUT_INCH_FLAG = self.rb2.GetSelection()
		MCODE_FLAG = int(self.cb1.IsChecked())
		XY_SPEED = self.xyspeed.GetValue()
		Z_SPEED = self.zspeed.GetValue()
		LEFT_X = self.leftx.GetValue()
		LOWER_Y = self.lowy.GetValue()
		DRILL_SPEED = self.drillspeed.GetValue()
		DRILL_DEPTH = self.drilldep.GetValue()
		CUT_DEPTH = self.cutdep.GetValue()
		TOOL_D = self.toold.GetValue()
		DRILL_D = self.drilld.GetValue()
		CAD_UNIT = float(self.cadunit.GetValue())
		save_config()
		self.Close(True)  # Close the frame.

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
	def __init__(self, x, y, r, delete):
		self.x = x
		self.y = y
		self.r = r
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
	#Read Config data
	read_config()
	#Window setup
	app = wx.App()
	MainWindow(None, -1, 'pyGerber2Gcode')
	app.MainLoop()

def save_config():
	global INI_X, INI_Y, INI_Z, MOVE_HEIGHT, OUT_INCH_FLAG, IN_INCH_FLAG, MCODE_FLAG, XY_SPEED, Z_SPEED, LEFT_X, LOWER_Y, DRILL_SPEED, DRILL_DEPTH, CUT_DEPTH, TOOL_D, DRILL_D, CAD_UNIT, CONFIG_FILE

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
	out = open(CONFIG_FILE, 'w')
	out.write(config_data)
	out.close()

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


def gcode_init():
	global gGCODE_DATA, INI_X, INI_Y, INI_Z, OUT_INCH_FLAG, MCODE_FLAG, gDRILL_DATA, IN_INCH_FLAG, OUT_INCH_FLAG
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
	print "in unit = "+str(IN_INCH_FLAG)
	print "out unit = "+str(OUT_INCH_FLAG)

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
		if (find(gerber, "X") != -1 or find(gerber, "Y") != -1):
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
	global gDCODE, gFIG_NUM,INCH, TOOL_D, CAD_UNIT, gGERBER_TMP_X, gGERBER_TMP_Y, gGCODES

	if (IN_INCH_FLAG and not OUT_INCH_FLAG):
		unit = INCH
	elif(not IN_INCH_FLAG and OUT_INCH_FLAG):
		unit = 1.0/INCH
	else:
		unit = 1
	#print "unit=" + str(unit)
	mod1 = float(gDCODE[int(gFIG_NUM)].mod1) * unit + float(TOOL_D)
	mod2 = float(gDCODE[int(gFIG_NUM)].mod2) * unit + float(TOOL_D)
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
		error_dialog("Error: polygon point",0)
		#print "Error: polygon point"
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
		error_dialog("Error:Too small angle at Circle",0)
		#print "Too small angle at Circle"
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
	global gGCODE_DATA, MOVE_HEIGHT, INI_X, INI_Y, INI_Z, gDRILL_DATA
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

def end(out_file_name,out_drill_file):
	global gGCODE_DATA, CUT_DEPTH, XY_SPEED, Z_SPEED, gDRILL_DATA
	calc_shift()
	polygon2gcode(CUT_DEPTH,XY_SPEED, Z_SPEED)
	gcode_end()
	#File open
	out = open(out_file_name, 'w')
	out.write(gGCODE_DATA)
	out.close()
	if(out_drill_file!=""):
		out = open(out_drill_file, 'w')
		out.write(gDRILL_DATA)
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
		error_dialog("Error:Number of points is illegal ",0)
		#print "Number of points is illegal "
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
		error_dialog("Error:Start and End angle are same",0)
		#print "Start and End angle are same"
	int(kaku)
	if(kaku <= 2):
		error_dialog("Error:Too small angle",0)
		#print "Too small angle"
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
	global DRILL_D, gDRILL_TYPE
	f = open(drill_file,'r')
	print "Read and Parse Drill data"
	while 1:
		drill = f.readline()
		if not drill:
			break
		drill_data = re.search("T([\d]+)C([\d\.]+)",drill)
		drill_num = re.search("T([\d]+)",drill)
		if(drill_data):
			gDRILL_TYPE[int(drill_data.group(1))] = drill_data.group(2)
		if(drill_num):
			DRILL_D=gDRILL_TYPE[int(drill_num.group(1))]
		if (find(drill, "X") != -1 or find(drill, "Y") != -1):
			parse_drill_xy(drill)
	f.close()

def parse_drill_xy(drill):
	global gDRILLS, DRILL_D, gDRILL_TYPE, gXSHIFT, gYSHIFT, INCH, IN_INCH_FLAG, OUT_INCH_FLAG
	calc_shift()
	if (IN_INCH_FLAG and not OUT_INCH_FLAG):
		unit = INCH
	elif(not IN_INCH_FLAG and OUT_INCH_FLAG):
		unit = 1.0/INCH
	else:
		unit = 1.0
	#print "unit=" + str(unit)
	#print "x_shift=" + str(gXSHIFT) + "y_shift=" + str(gYSHIFT)
	xx = re.search("X([\d\.-]+)\D",drill)
	yy = re.search("Y([\d\.-]+)\D",drill)
	if(xx):
		x=float(xx.group(1)) * unit + gXSHIFT
	if(yy):
		y=float(yy.group(1)) * unit + gYSHIFT
	gDRILLS.append(DRILL(x,y,DRILL_D,0))

def do_drill(drill_sw):
	global DRILL_SPEED, DRILL_DEPTH, gDRILLS, MOVE_HEIGHT, gDRILL_DATA, gGCODE_DATA, gTMP_DRILL_X, gTMP_DRILL_Y, gTMP_DRILL_Z, gTMP_X, gTMP_Y, gTMP_Z
	drill_data = ""
	if(drill_sw):
		gTMP_DRILL_X = gTMP_X
		gTMP_DRILL_Y = gTMP_Y
		gTMP_DRILL_Z = gTMP_Z
	for drill in gDRILLS:
		#move to hole position
		drill_data += move_drill(drill.x,drill.y)
		#Drill
		if(DRILL_SPEED):
			drill_data += "G01Z" + str(DRILL_DEPTH,) + "F" + str(DRILL_SPEED) + "\n"
		else:
			drill_data += "G01Z" + str(DRILL_DEPTH,) + "\n"

		#Goto moving Z position
		drill_data += "G00Z" + str(MOVE_HEIGHT) + "\n"

	gDRILL_DATA += drill_data
	if(drill_sw):
		gGCODE_DATA += drill_data
		gTMP_X = gTMP_DRILL_X 
		gTMP_Y = gTMP_DRILL_Y
		gTMP_Z = gTMP_DRILL_Z

def move_drill(x,y):
	global MOVE_HEIGHT, gTMP_DRILL_X, gTMP_DRILL_Y, gTMP_DRILL_Z
	out_data = "G00"
	#print out_data
	gcode_tmp_flag = 0
	if(x != gTMP_DRILL_X):
		gTMP_DRILL_X = x
		out_data += "X" + str(x)
		gcode_tmp_flag=1
	if(y != gTMP_DRILL_X):
		gTMP_DRILL_X = y
		out_data +="Y" + str(y)
		gcode_tmp_flag = 1
	if(MOVE_HEIGHT!=gTMP_DRILL_Z):
		gTMP_DRILL_Z = MOVE_HEIGHT
		#Goto moving Z position
		#out_data += "G00Z" + str(MOVE_HEIGHT) + "\n"
		return "G00Z" + str(MOVE_HEIGHT) + "\n"
	if(gcode_tmp_flag):
		#Goto initial X-Y position
		return out_data + "\n"
	else:
		return

def error_dialog(error_mgs,sw):
	print error_mgs
	if(sw):
		#raw_input("\n\nPress the enter key to exit.")
		sys.exit()

if __name__ == "__main__":
    main()



