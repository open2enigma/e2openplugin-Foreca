# -*- coding: UTF-8 -*-

from __future__ import absolute_import
from __future__ import print_function

from . import _
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.ConfigList import ConfigList
from Components.FileList import FileList
from Components.GUIComponent import GUIComponent
from Components.Label import Label
from Components.Language import language
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Components.PluginComponent import plugins
from Components.Sources.StaticText import StaticText
from Components.config import (
	config,
	ConfigSelection,
	ConfigInteger,
	ConfigYesNo,
	ConfigEnableDisable,
	getConfigListEntry,
	KEY_LEFT,
	KEY_RIGHT,
	KEY_0,
	ConfigText,
)
from enigma import (
	eListboxPythonMultiContent,
	ePicLoad,
	eTimer,
	getDesktop,
	gFont,
	RT_VALIGN_CENTER,
)
from locale import setlocale, LC_COLLATE, strxfrm
from os import makedirs, unlink, remove, listdir
from os.path import exists, join
from re import sub, DOTALL, compile, findall
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from skin import parseFont, parseColor
from sys import version_info
from time import localtime, mktime, strftime
from Tools.Directories import resolveFilename, SCOPE_CONFIG, SCOPE_PLUGINS, fileExists
from Tools.LoadPixmap import LoadPixmap
from twisted.internet._sslverify import ClientTLSOptions
from twisted.internet.ssl import ClientContextFactory
import ssl

PY3 = version_info[0] == 3
if PY3:
	from urllib.request import urlopen, Request, pathname2url
else:
	from urllib import pathname2url
	from urllib2 import urlopen, Request
try:
	from urllib.parse import urlparse
except ImportError:
	from urlparse import urlparse

try:
	_create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
	pass
else:
	ssl._create_default_https_context = _create_unverified_https_context
VERSION = "3.3.5"
#
#  $Id$
#
# -------------------------------------------------------
#
#              Foreca Weather Forecast E2
#
#   This Plugin retrieves the actual weather forecast
#   for the next 10 days from the Foreca website.
#
#        We wish all users wonderful weather!
#
#
#                    04.10.2017
#
#     Source of information: http://www.foreca.nz
#
#             Design and idea by
#                  @Bauernbub
#            enigma2 mod by mogli123
#
# -------------------------------------------------------
#
#  Provided with no warranties of any sort.
#
# -------------------------------------------------------
#
# History:
# 2.6 Various minor changes
# 2.7 Wrap around mode enabled in screen-lists
# 2.8 Calculate next date based on displayed date when left/right key is pushed
#	  after prior date jump using 0 - 9 keys was performed
# 2.9 Fix: Show correct date and time in weather videos
#     Main screen navigation modified to comply with standard usage:
#	  scroll page up/down by left/right key
#	  select previous/next day by left/right arrow key of numeric key group
# 2.9.1 Latvian cities and localization added. Thanks to muca
# 2.9.2 Iranian cities updated and localization added. Thanks to Persian Prince
#	Hungarian and Slovakian cities added. Thanks to torpe
# 2.9.3 Detail line in main screen condensed to show more text in SD screen
#	Grading of temperature colors reworked
#	Some code cosmetics
#	Translation code simplified: Setting the os LANGUAGE variable isn't needed anymore
#	Typos in German localization fixed
# 2.9.4 Many world-wide cities added. Thanks to AnodA
#	Hungarian and Slovakian localization added. Thanks to torpe
# 2.9.5 Fixed: Cities containing "_" didn't work as favorites. Thanks to kashmir
# 2.9.6 Size of temperature item slightly extended to match with skins using italic font
#	Grading of temperature colors reworked
# 2.9.7 Use specified "Frame size in full view" value when showing "5 day forecast" chart
#	Info screen reworked
#	False temperature colors fixed
#	Up/down keys now scroll by page in main screen (without highlighting selection)
# 3.0.0 Option added to select measurement units. Thanks to muca
#	Option added to select time format.
#	Setup menu reworked.
#	Main screen navigation modified: Select previous/next day by left/right key
#	Many Italian cities added and Italian localization updated. Thanks to mat8861
#	Czech, Greek, French, Latvian, Dutch, Polish, Russian localization updated. Thanks to muca
# 3.0.1 Fix broken transliteration
#	Disable selection in main screen.
# 3.0.2 Weather maps of Czech Republic, Greece, Hungary, Latvia, Poland, Russia, Slovakia added
#	Temperature Satellite video added
#	Control key assignment in slide show reworked to comply with Media Player standard
#	Some Italian cities added
#	Thumbnail folders compacted
#	Unused code removed, redundant code purged
#	Localization updated
# 3.0.3 List of German states and list of European countries sorted
#	Code cosmetics
#	Localization updated
# 3.0.4 Language determination improved
# 3.0.5 Setup of collating sequence reworked
# 3.0.6 Weather data in Russian version obtained from foreca.com instead of foreca.ru due
#	  to structural discrepancy of Russian web site
#	Code cosmetics
# 3.0.7 Turkish cities updated. Thanks to atsiz77
#	Debug state noted in log file
# 3.0.8 Fixed for Foreca's pages changes
# 3.0.9 Path for weather map regions updated after change of Wetterkontor's pages. Thanks to Bag58.
#	Add missing spinner icon
# 3.1.0 Plugin splitted into a loader and UI part, as Foreca needs quite a while to load. Hence
#	  actual load postponed until the user requests for it.
#	Finnish localization added. Thanks to kjuntara
#	Ukrainian localization added. Thanks to Irkoff
# 3.1.1 ForecaPreview skineable
# 3.1.2 Next screens skineable
# 3.1.3 Added font size for slideshow into setting
# 3.1.4 rem /www.metoffice.gov.uk due non existing infrared on this pages more
# 3.1.7 fix url foreca com
# 3.1.8 fix problem with national chars in favorite names
# 3.1.9 renamed parsed variables, added humidity into list - for display in default screen must be:
#	changed line:  		self.itemHeight = 90   ... change to new height, if is needed
#	and rearanged lines:	self.valText1 = 365,5,600,28
#				self.valText2 = 365,33,600,28
#				self.valText3 = 365,59,600,28
#				self.valText4 = 365,87,600,28
#	similar in user skin - there text4Pos="x,y,w,h" must be added
# 3.2.0	fixed satellite maps, removed infrared - page not exist more, sanity check if nothing is downloaded
# 3.2.3-r3 change URL to .net and .ru
# 3.2.7 change URL to .hr, Py3-bugfix for videos and several code cleanups
# 3.2.8 'startservice.cfg', 'fav1.cfg' and 'fav2.cfg' are obsolete and now part of etc/enigma2/settings and therefore can be deleted
# 3.2.9 change URL to .biz (THX to jup @OpenA.TV) and some code improvements
# 3.3.0 accelerated start-up of plugin (threaded url-access & processing) and replaced 'urllib(2).urlopen & .Request' by 'requests.get & .exceptions'
# 3.3.1 AGENTS-list bugfixed
# 3.3.2 corrected url for satellite views and recoded access to Eumetsat
#
# To do:
#	Add 10 day forecast on green key press
#	City search at Foreca website on yellow key press. This will eliminate complete city DB.
#	Option to add unlimited cities to a favorite list and to manage this favorite list (add & delete city, sort list).
#	Show home city (first entry of favorite list) on OK key press.
#	Skip to next/previous favorite city on left/right arrow key.
#	Show weather videos and maps on blue key
#	Show setup menu on Menu key
#
# 3.3.3 change URL to .nz
#
# 3.3.4 change URL to and many code improvements
#  RECODE FROM LULULLA TO 20241222
# To do:
#   Add choice list for pressure and other menu
#   check all url and fetch..
#   CACHE_PATH moved
#   FAlog moved
#   secure remove image from folde CACHE_PATH
#   Remove profile ICC from bad image


class WebClientContextFactory(ClientContextFactory):
	def __init__(self, url=None):
		domain = urlparse(url).netloc
		self.hostname = domain

	def getContext(self, hostname=None, port=None):
		ctx = ClientContextFactory.getContext(self)
		if self.hostname and ClientTLSOptions is not None:  # workaround for TLS SNI
			ClientTLSOptions(self.hostname, ctx)
		return ctx


pluginPrintname = "[Foreca Ver. %s]" % VERSION
config.plugins.foreca.home = ConfigText(default="Netherlands/Amsterdam", fixed_size=False)
config.plugins.foreca.fav1 = ConfigText(default="United_Kingdom/London", fixed_size=False)
config.plugins.foreca.fav2 = ConfigText(default="Italy/Rome", fixed_size=False)
config.plugins.foreca.resize = ConfigSelection(default="0", choices=[("0", _("simple")), ("1", _("better"))])
config.plugins.foreca.bgcolor = ConfigSelection(default="#00000000", choices=[("#00000000", _("black")), ("#009eb9ff", _("blue")), ("#00ff5a51", _("red")), ("#00ffe875", _("yellow")), ("#0038FF48", _("green"))])
config.plugins.foreca.textcolor = ConfigSelection(default="#0038FF48", choices=[("#00000000", _("black")), ("#009eb9ff", _("blue")), ("#00ff5a51", _("red")), ("#00ffe875", _("yellow")), ("#0038FF48", _("green"))])
config.plugins.foreca.framesize = ConfigInteger(default=5, limits=(5, 99))
config.plugins.foreca.fontsize = ConfigInteger(default=20, limits=(20, 30))
config.plugins.foreca.slidetime = ConfigInteger(default=1, limits=(1, 60))
config.plugins.foreca.infoline = ConfigYesNo(default=True)
config.plugins.foreca.loop = ConfigYesNo(default=False)
config.plugins.foreca.citylabels = ConfigEnableDisable(default=True)
config.plugins.foreca.units = ConfigSelection(default="metrickmh", choices=[("metric", _("Metric (C, m/s)")), ("metrickmh", _("Metric (C, km/h)")), ("imperial", _("Imperial (C, mph)")), ("us", _("US (F, mph)"))])
config.plugins.foreca.time = ConfigSelection(default="24h", choices=[("12h", _("12 h")), ("24h", _("24 h"))])
config.plugins.foreca.debug = ConfigEnableDisable(default=False)

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6'}
BASEURL = "http://www.foreca.nz/"
MODULE_NAME = __name__.split(".")[-1]
USR_PATH = resolveFilename(SCOPE_CONFIG) + "Foreca"
PICON_PATH = resolveFilename(SCOPE_PLUGINS) + "Extensions/Foreca/picon/"
THUMB_PATH = resolveFilename(SCOPE_PLUGINS) + "Extensions/Foreca/thumb/"


# Make Path for Slideshow
CACHE_PATH = "/var/volatile/tmp/Foreca/"
if exists(CACHE_PATH) is False:
	try:
		# makedirs(CACHE_PATH, 755)
		makedirs(CACHE_PATH, mode=0o755, exist_ok=True)
	except Exception:
		pass


def FAlog(info, wert=""):
	if config.plugins.foreca.debug.value:
		try:
			with open('/var/volatile/tmp/foreca.log', 'a') as f:
				f.write('{} {} {}\r\n'.format(strftime('%H:%M:%S'), info, wert))
		except IOError:
			print('[Foreca] Logging-Error')
	else:
		print('[Foreca] {} {}'.format(str(info), str(wert)))


# Make Path for user settings
if not exists(USR_PATH):
	try:
		makedirs(USR_PATH, mode=0o755, exist_ok=True)
	except Exception as e:
		print("Error creating directory: %s", e)


# Get screen size
size_w = getDesktop(0).size().width()
size_h = getDesktop(0).size().height()

HD = True
if size_w < 1280:
	HD = False

# Get diacritics to handle
FILTERin = []
FILTERout = []
FILTERidx = 0

MAPPING = {"zh": "en"}
LANGUAGE = language.getActiveLanguage()[:2]  # "en_US" -> "en"
if LANGUAGE in MAPPING:
	LANGUAGE = MAPPING.get(LANGUAGE, "en")
try:
	setlocale(LC_COLLATE, language.getLanguage())
except Exception:
	FAlog("Collating sequence undeterminable; default used")

if fileExists(USR_PATH + "/Filter.cfg"):
	file = open(USR_PATH + "/Filter.cfg", "r")
	for line in file:
		regel = str(line)
		if regel[:2] == LANGUAGE and regel[4] == "Y":
			FILTERidx += 1
			FILTERin.append(regel[7:15].strip())
			FILTERout.append(regel[17:].strip())
	file.close

# ---------------------- Skin Functions ----------------------------------------------------


def download_image(url, devicepath):
	try:
		req = Request(url, headers=HEADERS)
		resp = urlopen(req, timeout=10)
		with open(devicepath, 'wb') as f:
			f.write(resp.read())
		FAlog("SatBild: Image saved to %s" % devicepath)
		print("SatBild: Image saved to %s" % devicepath)
		return True
	except Exception as e:
		FAlog("SatBild Error: Failed to download image", str(e))
		print("SatBild Error: Failed to download image", str(e))
		raise e


def remove_icc_profile(devicepath):
	try:
		from PIL import Image
		import warnings
		warnings.filterwarnings("ignore", "(?s).*iCCP.*", category=UserWarning)
		img = Image.open(devicepath)
		img.save(devicepath, icc_profile=None)
	except Exception as e:
		print("Error: Failed to remove ICC profile", str(e))
		raise e


def getScale():
	return AVSwitch().getFramebufferScale()


# ------------------------------------------------------------------------------------------
# ----------------------------------  MainMenuList   ---------------------------------------
# ------------------------------------------------------------------------------------------


class MainMenuList(MenuList):

	def __init__(self):
		MenuList.__init__(self, [], False, eListboxPythonMultiContent)
		GUIComponent.__init__(self)

		# default values:
		self.font0 = gFont("Regular", 20)
		self.font1 = gFont("Regular", 24)
		self.font2 = gFont("Regular", 18)
		self.font3 = gFont("Regular", 22)
		self.itemHeight = 120
		self.valTime = 10, 34, 60, 24
		self.valPict = 70, 10, 70, 70
		self.valPictScale = 0
		self.valTemp = 145, 15, 80, 24
		self.valTempUnits = 145, 45, 80, 24
		self.valWindPict = 230, 36, 28, 28
		self.valWindPictScale = 0
		self.valWind = 265, 15, 95, 24
		self.valWindUnits = 265, 45, 95, 24
		self.valText1 = 365, 5, 600, 28
		self.valText2 = 365, 33, 600, 28
		self.valText3 = 365, 59, 600, 28
		self.valText4 = 365, 87, 600, 28
		self.listCompleted = []
		self.callback = None
		self.idx = 0
		self.thumb = ""
		self.pos = 20
		FAlog("MainMenuList...")

# --------------------------- get skin attribs ---------------------------------------------
	def applySkin(self, desktop, parent):
		def warningWrongSkinParameter(string, wanted, given):
			print("[ForecaPreview] wrong '%s' skin parameters. Must be %d arguments (%d given)" % (string, wanted, given))

		def font0(value):
			self.font0 = parseFont(value, ((1, 1), (1, 1)))

		def font1(value):
			self.font1 = parseFont(value, ((1, 1), (1, 1)))

		def font2(value):
			self.font2 = parseFont(value, ((1, 1), (1, 1)))

		def font3(value):
			self.font3 = parseFont(value, ((1, 1), (1, 1)))

		def itemHeight(value):
			self.itemHeight = int(value)

		def setTime(value):
			self.valTime = list(map(int, value.split(",")))
			lx = len(self.valTime)
			if lx != 4:
				warningWrongSkinParameter(attrib, 4, lx)

		def setPict(value):
			self.valPict = list(map(int, value.split(",")))
			lx = len(self.valPict)
			if lx != 4:
				warningWrongSkinParameter(attrib, 4, lx)

		def setPictScale(value):
			self.valPictScale = int(value)

		def setTemp(value):
			self.valTemp = list(map(int, value.split(",")))
			lx = len(self.valTemp)
			if lx != 4:
				warningWrongSkinParameter(attrib, 4, lx)

		def setTempUnits(value):
			self.valTempUnits = list(map(int, value.split(",")))
			lx = len(self.valTempUnits)
			if lx != 4:
				warningWrongSkinParameter(attrib, 4, lx)

		def setWindPict(value):
			self.valWindPict = list(map(int, value.split(",")))
			lx = len(self.valWindPict)
			if lx != 4:
				warningWrongSkinParameter(attrib, 4, lx)

		def setWindPictScale(value):
			self.valWindPictScale = int(value)

		def setWind(value):
			self.valWind = list(map(int, value.split(",")))
			lx = len(self.valWind)
			if lx != 4:
				warningWrongSkinParameter(attrib, 4, lx)

		def setWindUnits(value):
			self.valWindUnits = list(map(int, value.split(",")))
			lx = len(self.valWindUnits)
			if lx != 4:
				warningWrongSkinParameter(attrib, 4, lx)

		def text1Pos(value):
			self.valText1 = list(map(int, value.split(",")))
			lx = len(self.valText1)
			if lx != 4:
				warningWrongSkinParameter(attrib, 4, lx)

		def text2Pos(value):
			self.valText2 = list(map(int, value.split(",")))
			lx = len(self.valText2)
			if lx != 4:
				warningWrongSkinParameter(attrib, 4, lx)

		def text3Pos(value):
			self.valText3 = list(map(int, value.split(",")))
			lx = len(self.valText3)
			if lx != 4:
				warningWrongSkinParameter(attrib, 4, lx)

		def text4Pos(value):
			self.valText4 = list(map(int, value.split(",")))
			lx = len(self.valText4)
			if lx != 4:
				warningWrongSkinParameter(attrib, 4, lx)

		for (attrib, value) in list(self.skinAttributes):
			try:
				locals().get(attrib)(value)
				self.skinAttributes.remove((attrib, value))
			except Exception:
				pass
		self.l.setFont(0, self.font0)
		self.l.setFont(1, self.font1)
		self.l.setFont(2, self.font2)
		self.l.setFont(3, self.font3)
		self.l.setItemHeight(self.itemHeight)
		return GUIComponent.applySkin(self, desktop, parent)

# --------------------------- Go through all list entries ----------------------------------
	def buildEntries(self):
		FAlog("buildEntries:", str(len(self.list)))
		if self.idx == len(self.list):
			self.setList(self.listCompleted)
			if self.callback:
				self.callback()
		else:
			self.downloadThumbnail()

	def downloadThumbnail(self):
		thumbUrl = self.list[self.idx][0]
		windDirection = self.list[self.idx][3]
		self.thumb = THUMB_PATH + str(thumbUrl + ".png")
		self.wind = THUMB_PATH + str(windDirection)
		self.buildEntry(None)

# ----------------------------------- Build entries for list -------------------------------
	def buildEntry(self, picInfo=None):
		self.x = self.list[self.idx]
		self.res = [(self.x[0], self.x[1])]

		violetred = 0xC7D285
		violet = 0xff40b3
		gruen = 0x77f424
		dgruen = 0x53c905
		drot = 0xff4040
		rot = 0xff6640
		orange = 0xffb340
		gelb = 0xffff40
		ddblau = 0x3b62ff
		dblau = 0x408cff
		mblau = 0x40b3ff
		blau = 0x40d9ff
		hblau = 0x40ffff
		weiss = 0xffffff

		if config.plugins.foreca.units.value == "us":
			self.centigrades = round((int(self.x[2]) - 32) / 1.8)
			tempUnit = "°F"
		else:
			self.centigrades = int(self.x[2])
			tempUnit = "°C"
		if self.centigrades <= -20:
			self.tempcolor = ddblau
		elif self.centigrades <= -15:
			self.tempcolor = dblau
		elif self.centigrades <= -10:
			self.tempcolor = mblau
		elif self.centigrades <= -5:
			self.tempcolor = blau
		elif self.centigrades <= 0:
			self.tempcolor = hblau
		elif self.centigrades < 5:
			self.tempcolor = dgruen
		elif self.centigrades < 10:
			self.tempcolor = gruen
		elif self.centigrades < 15:
			self.tempcolor = gelb
		elif self.centigrades < 20:
			self.tempcolor = orange
		elif self.centigrades < 25:
			self.tempcolor = rot
		elif self.centigrades < 30:
			self.tempcolor = drot
		else:
			self.tempcolor = violet

		# Time
		x, y, w, h = self.valTime
		self.res.append(MultiContentEntryText(pos=(x, y), size=(w, h), font=0, text=self.x[1], color=weiss, color_sel=weiss))

		# forecast pictogram
		pngpic = LoadPixmap(self.thumb)
		if pngpic is not None:
			x, y, w, h = self.valPict
			self.res.append(MultiContentEntryPixmapAlphaTest(pos=(x, y), size=(w, h), png=pngpic))

		# Temp
		x, y, w, h = self.valTemp
		self.res.append(MultiContentEntryText(pos=(x, y), size=(w, h), font=0, text=_("Temp"), color=weiss, color_sel=weiss))
		x, y, w, h = self.valTempUnits
		self.res.append(MultiContentEntryText(pos=(x, y), size=(w, h), font=3, text=self.x[2] + tempUnit, color=self.tempcolor, color_sel=self.tempcolor))

		# wind pictogram
		pngpic = LoadPixmap(self.wind + ".png")
		if pngpic is not None:
			x, y, w, h = self.valWindPict
			self.res.append(MultiContentEntryPixmapAlphaTest(pos=(x, y), size=(w, h), png=pngpic))

		# Wind
		x, y, w, h = self.valWind
		self.res.append(MultiContentEntryText(pos=(x, y), size=(w, h), font=0, text=_("Wind"), color=weiss, color_sel=weiss))
		x, y, w, h = self.valWindUnits
		self.res.append(MultiContentEntryText(pos=(x, y), size=(w, h), font=3, text=self.x[4], color=violetred, color_sel=violetred))

		# Text
		x, y, w, h = self.valText1
		self.res.append(MultiContentEntryText(pos=(x, y), size=(w, h), font=3, text=_(self.x[5]), color=weiss, color_sel=weiss))
		x, y, w, h = self.valText2
		textsechs = self.x[6]
		textsechs = textsechs.replace("&deg;", "") + tempUnit
		self.res.append(MultiContentEntryText(pos=(x, y), size=(w, h), font=2, text=textsechs, color=mblau, color_sel=mblau))
		x, y, w, h = self.valText3
		self.res.append(MultiContentEntryText(pos=(x, y), size=(w, h), font=2, text=self.x[7], color=mblau, color_sel=mblau))
		x, y, w, h = self.valText4
		self.res.append(MultiContentEntryText(pos=(x, y), size=(w, h), font=2, text=self.x[8], color=mblau, color_sel=mblau))

		self.listCompleted.append(self.res)
		self.idx += 1
		self.buildEntries()

	def SetList(self, lx):
		FAlog("SetList")
		self.list = lx
		# self.l.setItemHeight(90)
		del self.listCompleted
		self.listCompleted = []
		self.idx = 0
		self.buildEntries()


# ------------------------------------------------------------------------------------------
# ------------------------------------------ Spinner ---------------------------------------
# ------------------------------------------------------------------------------------------


class ForecaPreviewCache(Screen):

	skin = """
		<screen position="center,center" size="76,76" flags="wfNoBorder" backgroundColor="#000000" >
			<eLabel position="2,2" zPosition="1" size="72,72" font="Regular;18" backgroundColor="#40000000" />
			<widget name="spinner" position="14,14" zPosition="4" size="48,48" alphatest="on" />
		</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)

		self["spinner"] = Pixmap()
		self.curr = 0

		self.timer = eTimer()
		self.timer.callback.append(self.showNextSpinner)

	def start(self):
		self.show()
		self.timer.start(120, False)

	def stop(self):
		self.hide()
		self.timer.stop()

	def showNextSpinner(self):
		self.curr += 1
		if self.curr > 11:
			self.curr = 0
		png = LoadPixmap(cached=True, path=PICON_PATH + str(self.curr) + ".png")
		self["spinner"].instance.setPixmap(png)

# ------------------------------------------------------------------------------------------
# ------------------------------ Foreca Preview---------------------------------------------
# ------------------------------------------------------------------------------------------


class ForecaPreview(Screen, HelpableScreen):

	def __init__(self, session):
		global MAIN_PAGE, menu
		self.session = session
		# actual, local Time as Tuple
		lt = localtime()
		# Extract the Tuple, Date
		jahr, monat, tag = lt[0:3]
		heute = "%04i%02i%02i" % (jahr, monat, tag)
		FAlog("determined local date:", heute)
		self.tag = 0

		# Get favorites
		global fav1, fav2, city, start
		"""
		# def load_fav_location(filename, default_location):
			# if exists(USR_PATH + filename):
				# with open(USR_PATH + filename, "r") as file:
					# location = file.readline().strip()
				# return location[location.rfind("/") + 1:]
			# else:
				# return default_location

		# def load_home_location(filename, default_location):
			# if exists(USR_PATH + filename):
				# with open(USR_PATH + filename, "r") as file:
					# location = file.readline().strip()
				# return location[location.rfind("/") + 1:]
			# else:
				# return default_location

		# fav1 = load_fav_location("/fav1.cfg", "New_York_City")
		# print(pluginPrintname, "fav1 location:", fav1)

		# fav2 = load_fav_location("/fav2.cfg", "Rome")
		# print(pluginPrintname, "fav2 location:", fav2)

		# start = load_home_location("/startservice.cfg", "Netherlands/Amsterdam")
		# print(pluginPrintname, "home location:", start)
		"""

		if exists(USR_PATH + "/fav1.cfg"):
			with open(USR_PATH + "/fav1.cfg", "r") as file:
				fav1 = file.readline().strip()
			fav1 = fav1[fav1.rfind("/") + 1:]
		else:
			fav1 = "London"
		print(pluginPrintname, "fav1 location:", fav1)

		if exists(USR_PATH + "/fav2.cfg"):
			with open(USR_PATH + "/fav2.cfg", "r") as file:
				fav2 = file.readline().strip()
			fav2 = fav2[fav2.rfind("/") + 1:]  # Extract only the final part of the path
		else:
			fav2 = "Rome"
		print(pluginPrintname, "fav2 location:", fav2)

		# Get home location
		if exists(USR_PATH + "/startservice.cfg"):
			with open(USR_PATH + "/startservice.cfg", "r") as file:
				self.ort = file.readline().strip()
				start = self.ort[self.ort.rfind("/") + 1:len(self.ort)]
		else:
			self.ort = "Netherlands/Amsterdam"
			start = "Amsterdam"
		print(pluginPrintname, "home location:", self.ort)
		FAlog("home location:", self.ort)
		MAIN_PAGE = "%s%s?lang=%s&details=%s&units=%s&tf=%s" % (BASEURL, pathname2url(self.ort), LANGUAGE, heute, config.plugins.foreca.units.value, config.plugins.foreca.time.value)
		FAlog("initial link:", MAIN_PAGE)

		if HD:
			self.skin = """
				<screen name="ForecaPreview" position="center,center" size="980,505" title="Foreca Weather Forecast" backgroundColor="#00000000" >
					<widget name="MainList" position="0,90" size="980,365" zPosition="3" backgroundColor="#00000000" enableWrapAround="1" scrollbarMode="showOnDemand" />
					<widget source="Titel" render="Label" position="4,10" zPosition="3" size="978,60" font="Regular;24" valign="center" halign="left" transparent="1" foregroundColor="#ffffff"/>
					<widget source="Titel2" render="Label" position="35,15" zPosition="2" size="900,60" font="Regular;26" valign="center" halign="center" transparent="1" foregroundColor="#f47d19"/>
					<eLabel position="5,70" zPosition="2" size="970,2" foregroundColor="#c3c3c9" backgroundColor="#FFFFFF" />
					<eLabel position="5,460" zPosition="2" size="970,2" foregroundColor="#c3c3c9" backgroundColor="#FFFFFF" />
					<widget source="key_red" render="Label" position="39,463" zPosition="2" size="102,40" font="Regular;18" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
					<widget source="key_green" render="Label" position="177,463" zPosition="2" size="110,40" font="Regular;18" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
					<widget source="key_yellow" render="Label" position="325,463" zPosition="2" size="110,40" font="Regular;18" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
					<widget source="key_blue" render="Label" position="473,463" zPosition="2" size="110,40" font="Regular;18" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
					<widget source="key_ok" render="Label" position="621,463" zPosition="2" size="70,40" font="Regular;18" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
					<widget source="key_menu" render="Label" position="729,463" zPosition="2" size="85,40" font="Regular;18" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
					<widget source="key_info" render="Label" position="852,463" zPosition="2" size="85,40" font="Regular;18" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
					<ePixmap position="2,470" size="36,25" pixmap="skin_default/buttons/key_red.png" transparent="1" alphatest="on" />
					<ePixmap position="140,470" size="36,25" pixmap="skin_default/buttons/key_green.png" transparent="1" alphatest="on" />
					<ePixmap position="288,470" size="36,25" pixmap="skin_default/buttons/key_yellow.png" transparent="1" alphatest="on" />
					<ePixmap position="436,470" size="36,25" pixmap="skin_default/buttons/key_blue.png" transparent="1" alphatest="on" />
					<ePixmap position="584,470" size="36,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Foreca/buttons/key_ok.png" transparent="1" alphatest="on" />
					<ePixmap position="692,470" size="36,25" pixmap="skin_default/buttons/key_menu.png" transparent="1" alphatest="on" />
					<ePixmap position="815,470" size="36,25" pixmap="skin_default/buttons/key_info.png" transparent="1" alphatest="on" />
					<ePixmap position="938,470" size="36,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Foreca/buttons/key_help.png" transparent="1" alphatest="on" />
				</screen>"""
		else:
			self.skin = """
				<screen name="ForecaPreview" position="center,65" size="720,480" title="Foreca Weather Forecast" backgroundColor="#00000000" >
					<widget name="MainList" position="0,65" size="720,363" zPosition="3" backgroundColor="#00000000" enableWrapAround="1" scrollbarMode="showOnDemand" />
					<widget source="Titel" render="Label" position="20,3" zPosition="3" size="680,50" font="Regular;20" valign="center" halign="left" transparent="1" foregroundColor="#ffffff"/>
					<widget source="Titel2" render="Label" position="40,5" zPosition="2" size="640,50" font="Regular;22" valign="center" halign="center" transparent="1" foregroundColor="#f47d19"/>
					<eLabel position="5,55" zPosition="2" size="710,2" foregroundColor="#c3c3c9" backgroundColor="#FFFFFF" />
					<eLabel position="5,437" zPosition="2" size="710,2" foregroundColor="#c3c3c9" backgroundColor="#FFFFFF" />
					<widget source="key_red" render="Label" position="50,438" zPosition="2" size="120,40" font="Regular;20" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
					<widget source="key_green" render="Label" position="210,438" zPosition="2" size="100,40" font="Regular;20" valign="center" halign="left" transparent="1" foregroundColor="#ffffff"/>
					<widget source="key_yellow" render="Label" position="350,438" zPosition="2" size="100,40" font="Regular;20" valign="center" halign="left" transparent="1" foregroundColor="#ffffff"/>
					<widget source="key_blue" render="Label" position="490,438" zPosition="2" size="100,40" font="Regular;20" valign="center" halign="left" transparent="1" foregroundColor="#ffffff"/>
					<widget source="key_ok" render="Label" position="630,438" zPosition="2" size="100,40" font="Regular;20" valign="center" halign="left" transparent="1" foregroundColor="#ffffff"/>
					<ePixmap position="10,442" size="36,25" pixmap="skin_default/buttons/key_red.png" transparent="1" alphatest="on" />
					<ePixmap position="170,442" size="36,25" pixmap="skin_default/buttons/key_green.png" transparent="1" alphatest="on" />
					<ePixmap position="310,442" size="36,25" pixmap="skin_default/buttons/key_yellow.png" transparent="1" alphatest="on" />
					<ePixmap position="450,442" size="36,25" pixmap="skin_default/buttons/key_blue.png" transparent="1" alphatest="on" />
					<ePixmap position="590,442" size="36,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Foreca/buttons/key_ok.png" transparent="1" alphatest="on" />
				</screen>"""

		Screen.__init__(self, session)
		self.setup_title = _("Foreca Weather Forecast")
		self["MainList"] = MainMenuList()
		self["Titel"] = StaticText()
		self["Titel2"] = StaticText(_("Please wait ..."))
		self["Titel3"] = StaticText()
		self["Titel4"] = StaticText()
		self["Titel5"] = StaticText()
		self["key_red"] = StaticText(_("Week"))
		self["key_ok"] = StaticText(_("City"))
		if config.plugins.foreca.citylabels.value is True:
			self["key_green"] = StaticText(fav1.replace("_", " "))
			self["key_yellow"] = StaticText(fav2.replace("_", " "))
			self["key_blue"] = StaticText(start.replace("_", " "))
		else:
			self["key_green"] = StaticText(_("Favorite 1"))
			self["key_yellow"] = StaticText(_("Favorite 2"))
			self["key_blue"] = StaticText(_("Home"))
		self["key_info"] = StaticText(_("Legend"))
		self["key_menu"] = StaticText(_("Maps"))
		self.setTitle(_("Foreca Weather Forecast") + " " + _("Version ") + VERSION)

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(self, "ForecaActions",
											{"cancel": (self.exit, _("Exit - End")),
											 "menu": (self.Menu, _("Menu - Weather maps")),
											 "showEventInfo": (self.info, _("Info - Legend")),
											 "ok": (self.OK, _("OK - City")),
											 "left": (self.left, _("Left - Previous day")),
											 "right": (self.right, _("Right - Next day")),
											 "up": (self.up, _("Up - Previous page")),
											 "down": (self.down, _("Down - Next page")),
											 "previous": (self.previousDay, _("Left arrow - Previous day")),
											 "next": (self.nextDay, _("Right arrow - Next day")),
											 "red": (self.red, _("Red - Weekoverview")),
											 # "shift_red": (self.shift_red, _("Red long - 10 day forecast")),
											 "green": (self.Fav1, _("Green - Favorite 1")),
											 "yellow": (self.Fav2, _("Yellow - Favorite 2")),
											 "blue": (self.Fav0, _("Blue - Home")),
											 "0": (self.Tag0, _("0 - Today")),
											 "1": (self.Tag1, _("1 - Today + 1 day")),
											 "2": (self.Tag2, _("2 - Today + 2 days")),
											 "3": (self.Tag3, _("3 - Today + 3 days")),
											 "4": (self.Tag4, _("4 - Today + 4 days")),
											 "5": (self.Tag5, _("5 - Today + 5 days")),
											 "6": (self.Tag6, _("6 - Today + 6 days")),
											 "7": (self.Tag7, _("7 - Today + 7 days")),
											 "8": (self.Tag8, _("8 - Today + 8 days")),
											 "9": (self.Tag9, _("9 - Today + 9 days"))}, -2)

		self.StartPageFirst()

	def StartPageFirst(self):
		FAlog("StartPageFirst...")
		self.cacheDialog = self.session.instantiateDialog(ForecaPreviewCache)
		self["MainList"].callback = self.deactivateCacheDialog
		self.working = False
		self["MainList"].show
		self.cacheTimer = eTimer()
		self.cacheDialog.start()
		self.onLayoutFinish.append(self.getPage)

	def StartPage(self):
		self["Titel"].text = ""
		self["Titel3"].text = ""
		self["Titel4"].text = ""
		self["Titel5"].text = ""
		self["Titel2"].text = _("Please wait ...")
		self.working = False
		FAlog("MainList show...")
		self["MainList"].show
		self.getPage()

	def getPage(self, page=None):
		FAlog("getPage...")
		self.cacheDialog.start()
		self.working = True
		if not page:
			page = ""
		url = "%s%s" % (MAIN_PAGE, page)
		FAlog("page link:", url)
		try:
			req = Request(url, headers=HEADERS)
			resp = urlopen(req, timeout=10)
			self.getForecaPage(resp.read().decode('utf-8') if PY3 else resp.read())
		except Exception as e:
			self.error(repr(e))

	def error(self, err=""):
		FAlog("Error:", err)
		self.working = False
		self.deactivateCacheDialog()

	def deactivateCacheDialog(self):
		self.cacheDialog.stop()
		self.working = False

	def exit(self):
		try:
			unlink(CACHE_PATH + "sat.jpg")
		except Exception:
			pass

		try:
			unlink(CACHE_PATH + "sat.html")
		except Exception:
			pass

		try:
			unlink(CACHE_PATH + "meteogram.png")
		except Exception:
			pass

		self.close()
		self.deactivateCacheDialog()

	def Tag0(self):
		self.tag = 0
		self.Zukunft(self.tag)

	def Tag1(self):
		self.tag = 1
		self.Zukunft(self.tag)

	def Tag2(self):
		self.tag = 2
		self.Zukunft(self.tag)

	def Tag3(self):
		self.tag = 3
		self.Zukunft(self.tag)

	def Tag4(self):
		self.tag = 4
		self.Zukunft(self.tag)

	def Tag5(self):
		self.tag = 5
		self.Zukunft(self.tag)

	def Tag6(self):
		self.tag = 6
		self.Zukunft(self.tag)

	def Tag7(self):
		self.tag = 7
		self.Zukunft(self.tag)

	def Tag8(self):
		self.tag = 8
		self.Zukunft(self.tag)

	def Tag9(self):
		self.tag = 9
		self.Zukunft(self.tag)

	def Fav0(self):
		global start
		if exists(USR_PATH + "/startservice.cfg"):
			with open(USR_PATH + "/startservice.cfg", "r") as file:
				self.ort = file.readline().strip()
		else:
			self.ort = "Netherlands/Amsterdam"
		print(pluginPrintname, "home location:", self.ort)
		start = self.ort[self.ort.rfind("/") + 1:len(self.ort)]
		self.Zukunft(0)

	def Fav1(self):
		global fav1
		if exists(USR_PATH + "/fav1.cfg"):
			with open(USR_PATH + "/fav1.cfg", "r") as file:
				self.ort = file.readline().strip()
		else:
			self.ort = "United_Kingdom/London"
		fav1 = self.ort[self.ort.rfind("/") + 1:len(self.ort)]
		FAlog("fav1 location:", fav1)
		self.Zukunft(0)

	def Fav2(self):
		global fav2
		if exists(USR_PATH + "/fav2.cfg"):
			with open(USR_PATH + "/fav2.cfg", "r") as file:
				self.ort = file.readline().strip()
		else:
			self.ort = "Italy/Rome"
		fav2 = self.ort[self.ort.rfind("/") + 1:len(self.ort)]
		FAlog("fav2 location:", fav2)
		self.Zukunft(0)

	def Zukunft(self, ztag=0):
		global MAIN_PAGE
		# actual, local Time as Tuple
		lt = localtime()
		jahr, monat, tag = lt[0:3]

		# Calculate future date
		ntag = tag + ztag
		zukunft = jahr, monat, ntag, 0, 0, 0, 0, 0, 0
		morgen = mktime(zukunft)
		lt = localtime(morgen)
		jahr, monat, tag = lt[0:3]
		morgen = "%04i%02i%02i" % (jahr, monat, tag)

		MAIN_PAGE = "%s%s?lang=%s&details=%s&units=%s&tf=%s" % (BASEURL, pathname2url(self.ort), LANGUAGE, morgen, config.plugins.foreca.units.value, config.plugins.foreca.time.value)
		FAlog("day link:", MAIN_PAGE)

		# Show in GUI
		self.StartPage()

	def info(self):
		message = "%s" % (_("\n<   >       =   Prognosis next/previous day\n0 - 9       =   Prognosis (x) days from now\n\nVOL+/-  =   Fast scroll 100 (City choice)\nBouquet+/- =   Fast scroll 500 (City choice)\n\nInfo        =   This information\nMenu     =   Satellite photos and maps\n\nRed        =   Temperature chart for the upcoming 5 days\nGreen    =   Go to Favorite 1\nYellow    =   Go to Favorite 2\nBlue        =   Go to Home\n\nWind direction = Arrow to right: Wind from the West"))
		self.session.open(MessageBox, message, MessageBox.TYPE_INFO)

	def OK(self):
		global city
		panelmenu = ""
		city = self.ort
		self.session.openWithCallback(self.OKCallback, CityPanel, panelmenu)

	def OKCallback(self):
		global city, fav1, fav2
		self.ort = city
		self.tag = 0
		self.Zukunft(0)
		if config.plugins.foreca.citylabels.value is True:
			self["key_green"].setText(fav1.replace("_", " "))
			self["key_yellow"].setText(fav2.replace("_", " "))
			self["key_blue"].setText(start.replace("_", " "))
		else:
			self["key_green"].setText(_("Favorite 1"))
			self["key_yellow"].setText(_("Favorite 2"))
			self["key_blue"].setText(_("Home"))
		FAlog("MenuCallback")

	def left(self):
		if not self.working and self.tag >= 1:
			self.tag = self.tag - 1
			self.Zukunft(self.tag)

	def right(self):
		if not self.working and self.tag < 9:
			self.tag = self.tag + 1
			self.Zukunft(self.tag)

	def up(self):
		if not self.working:
			self["MainList"].pageUp()

	def down(self):
		if not self.working:
			self["MainList"].pageDown()

	def previousDay(self):
		self.left()

	def nextDay(self):
		self.right()

	def red(self):
		if not self.working:
			self.url = "%smeteogram.php?loc_id=%s&mglang=%s&units=%s&tf=%s/meteogram.png" % (BASEURL, self.loc_id, LANGUAGE, config.plugins.foreca.units.value, config.plugins.foreca.time.value)
			self.loadPicture(self.url)

	def shift_red(self):
		pass
		# self.session.openWithCallback(self.MenuCallback, Foreca10Days, self.ort)

	def Menu(self):
		self.session.openWithCallback(self.MenuCallback, SatPanel, self.ort)

	def MenuCallback(self):
		global menu, start, fav1, fav2
		if config.plugins.foreca.citylabels.value is True:
			self["key_green"].setText(fav1.replace("_", " "))
			self["key_yellow"].setText(fav2.replace("_", " "))
			self["key_blue"].setText(start.replace("_", " "))
		else:
			self["key_green"].setText(_("Favorite 1"))
			self["key_yellow"].setText(_("Favorite 2"))
			self["key_blue"].setText(_("Home"))

	def loadPicture(self, url=""):
		devicepath = CACHE_PATH + "meteogram.png"
		req = Request(url, headers=HEADERS)
		resp = urlopen(req, timeout=10)
		with open(devicepath, 'wb') as f:
			f.write(resp.read())
		try:
			from PIL import Image
			import warnings
			warnings.filterwarnings("ignore", "(?s).*iCCP.*", category=UserWarning)
			img = Image.open(devicepath)
			img.save(devicepath, icc_profile=None)
		except Exception as e:
			print("Error removing ICC profile:", e)
		self.session.open(PicView, devicepath, 0, False)

	def getForecaPage(self, html):
		# new Ajax.Request('/lv?id=102772400', {
		fulltext = compile(r"id: '(.*?)'", DOTALL)
		id = fulltext.findall('%s' % html)
		# FAlog("fulltext= %s" % fulltext, "id= %s" % id)
		self.loc_id = str(id[0])
		# <!-- START -->
		# <h6><span>Tuesday</span> March 29</h6>
		FAlog("Start: %s" % len(html))
		fulltext = compile(r'<!-- START -->.+?<h6><span>(.+?)</h6>', DOTALL)
		titel = fulltext.findall(html)
		# FAlog("fulltext= %s" % fulltext, "titel= %s" % titel)
		if len(titel) > 0:
			titel[0] = str(sub(r'<[^>]*>', "", titel[0]))
			FAlog("titel[0]=", titel[0])
		# # <a href="/Austria/Linz?details=20110330">We</a>
		# fulltext = compile(r'<!-- START -->(.+?)<h6>', DOTALL)
		# link = str(fulltext.findall(html))
		# # print link

		# fulltext = compile(r'<a href=".+?>(.+?)<.+?', DOTALL)
		# tag = str(fulltext.findall(link))
		# # print "Day ", tag

		# ---------- Wetterdaten -----------

		# <div class="row clr0">
		fulltext = compile(r'<!-- START -->(.+?)<div class="datecopy">', DOTALL)
		html = str(fulltext.findall(html))

		FAlog("searching .....")
		datalist = []

		fulltext = compile(r'<a href="(.+?)".+?', DOTALL)
		taglink = str(fulltext.findall(html))
		# taglink = konvert_uml(taglink)
		FAlog("Daylink ", taglink)

		fulltext = compile(r'<a href=".+?>(.+?)<.+?', DOTALL)
		tag = fulltext.findall(html)
		FAlog("Day", str(tag))

		# <div class="c0"> <strong>17:00</strong></div>
		fulltime = compile(r'<div class="c0"> <strong>(.+?)<.+?', DOTALL)
		zeit = fulltime.findall(html)
		FAlog("Time", str(zeit))

		# <div class="c4">
		# <span class="warm"><strong>+15&deg;</strong></span><br />
		fulltime = compile(r'<div class="c4">.*?<strong>(.+?)&.+?', DOTALL)
		temp = fulltime.findall(html)
		FAlog("Temp", str(temp))

		# <div class="symbol_50x50d symbol_d000_50x50" title="clear"
		fulltext = compile(r'<div class="symbol_50x50.+? symbol_(.+?)_50x50.+?', DOTALL)
		thumbnails = fulltext.findall(html)

		fulltext = compile(r'<div class="c3">.+? (.+?)<br />.+?', DOTALL)
		description = fulltext.findall(html)
		FAlog("description", str(description).lstrip("\t").lstrip())

		fulltext = compile(r'<div class="c3">.+?<br />(.+?)</strong>.+?', DOTALL)
		feels = fulltext.findall(html)
		FAlog("feels", str(feels).lstrip("\t").lstrip())

		fulltext = compile(r'<div class="c3">.+?</strong><br />(.+?)</.+?', DOTALL)
		precip = fulltext.findall(html)
		FAlog("precip", str(precip).lstrip("\t").lstrip())

		fulltext = compile(r'<div class="c3">.+?</strong><br />.+?</strong><br />(.+?)</', DOTALL)
		humidity = fulltext.findall(html)
		FAlog("humidity", str(humidity).lstrip("\t").lstrip())

		fulltext = compile(r'<div class="c2">.+?<img src="//img-b.foreca.net/s/symb-wind/(.+?).gif', DOTALL)
		windDirection = fulltext.findall(html)
		FAlog("windDirection", str(windDirection))

		fulltext = compile(r'<div class="c2">.+?<strong>(.+?)<.+?', DOTALL)
		windSpeed = fulltext.findall(html)
		FAlog("windSpeed", str(windSpeed))

		timeEntries = len(zeit)
		x = 0
		while x < timeEntries:
			description[x] = self.konvert_uml(str(sub(r'<[^>]*>', "", description[x])))
			feels[x] = self.konvert_uml(str(sub(r'<[^>]*>', "", feels[x])))
			precip[x] = self.konvert_uml(str(sub(r'<[^>]*>', "", precip[x])))
			humidity[x] = self.konvert_uml(str(sub(r'<[^>]*>', "", humidity[x])))
			windSpeed[x] = self.filter_dia(windSpeed[x])
			FAlog("weather: %s, %s, %s, %s, %s, %s, %s, %s" % (zeit[x], temp[x], windDirection[x], windSpeed[x], description[x], feels[x], precip[x], humidity[x]))
			datalist.append([thumbnails[x], zeit[x], temp[x], windDirection[x], windSpeed[x], description[x], feels[x], precip[x], humidity[x]])
			x += 1

		self["Titel2"].text = ""
		datum = titel[0]
		foundPos = datum.rfind(" ")
		foundPos2 = datum.find(" ")
		datum2 = datum[:foundPos2] + datum[foundPos:] + "." + datum[foundPos2:foundPos]
		foundPos = self.ort.find("/")
		plaats = _(self.ort[0:foundPos]) + "-" + self.ort[foundPos + 1:len(self.ort)]
		self["Titel"].text = plaats.replace("_", " ") + "  -  " + datum2
		self["Titel4"].text = plaats.replace("_", " ")
		self["Titel5"].text = datum2
		self["Titel3"].text = self.ort[:foundPos].replace("_", " ") + "\r\n" + self.ort[foundPos + 1:].replace("_", " ") + "\r\n" + datum2
		self["MainList"].SetList(datalist)
		self["MainList"].selectionEnabled(0)
		self["MainList"].show

	def filter_dia(self, text):
		# remove diacritics for selected language
		filterItem = 0
		while filterItem < FILTERidx:
			text = text.replace(FILTERin[filterItem], FILTERout[filterItem])
			filterItem += 1
		return text

	def konvert_uml(self, text):
		text = self.filter_dia(text)
		# remove remaining control characters and return
		return text[text.rfind("\\t") + 2:len(text)]


# ------------------------------------------------------------------------------------------
# ------------------------------ City Panel ------------------------------------------------
# ------------------------------------------------------------------------------------------


class CityPanelList(MenuList):
	def __init__(self, list, font0=22, font1=16, itemHeight=30, enableWrapAround=True):
		MenuList.__init__(self, [], False, eListboxPythonMultiContent)
		GUIComponent.__init__(self)
		self.font0 = gFont("Regular", font0)
		self.font1 = gFont("Regular", font1)
		self.itemHeight = itemHeight
		self.foregroundColorSelected = 8900346
		self.foregroundColor = 0xffffff
		self.backgroundColorSelected = 0x565656
		self.column = 30

# ---------------------- get skin attribs ----------------------------
	def applySkin(self, desktop, parent):
		def font(value):
			self.font0 = parseFont(value, ((1, 1), (1, 1)))

		def font1(value):
			self.font1 = parseFont(value, ((1, 1), (1, 1)))

		def itemHeight(value):
			self.itemHeight = int(value)

		def foregroundColor(value):
			self.foregroundColor = parseColor(value).argb()

		def foregroundColorSelected(value):
			self.foregroundColorSelected = parseColor(value).argb()

		def backgroundColorSelected(value):
			self.backgroundColorSelected = parseColor(value).argb()

		def column(value):
			self.column = int(value)

		for (attrib, value) in list(self.skinAttributes):
			try:
				locals().get(attrib)(value)
				self.skinAttributes.remove((attrib, value))
			except Exception:
				pass
		self.l.setFont(0, self.font0)
		self.l.setFont(1, self.font1)
		self.l.setItemHeight(self.itemHeight)
		return GUIComponent.applySkin(self, desktop, parent)


class CityPanel(Screen, HelpableScreen):

	def __init__(self, session, panelmenu):
		self.session = session
		self.skin = """
			<screen name="CityPanel" position="center,60" size="660,500" title="Select a city" backgroundColor="#40000000" >
				<widget name="Mlist" position="10,10" size="640,450" zPosition="3" backgroundColor="#40000000" backgroundColorSelected="#565656" enableWrapAround="1" scrollbarMode="showOnDemand" />
				<eLabel position="0,465" zPosition="2" size="676,2" foregroundColor="#c3c3c9" backgroundColor="#c1cdc1" />
				<widget source="key_green" render="Label" position="50,470" zPosition="2" size="100,30" font="Regular;20" valign="center" halign="left" transparent="1" />
				<widget source="key_yellow" render="Label" position="200,470" zPosition="2" size="100,30" font="Regular;20" valign="center" halign="left" transparent="1" />
				<widget source="key_blue" render="Label" position="350,470" zPosition="2" size="100,30" font="Regular;20" valign="center" halign="left" transparent="1" />
				<widget source="key_ok" render="Label" position="500,470" zPosition="2" size="120,30" font="Regular;20" valign="center" halign="left" transparent="1" />
				<ePixmap position="10,473" size="36,25" pixmap="skin_default/buttons/key_green.png" transparent="1" alphatest="on" />
				<ePixmap position="160,473" size="36,25" pixmap="skin_default/buttons/key_yellow.png" transparent="1" alphatest="on" />
				<ePixmap position="310,473" size="36,25" pixmap="skin_default/buttons/key_blue.png" transparent="1" alphatest="on" />
				<ePixmap position="460,473" size="36,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Foreca/buttons/key_ok.png" transparent="1" alphatest="on" />
				<ePixmap position="624,473" size="36,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Foreca/buttons/key_help.png" transparent="1" alphatest="on" />
			</screen>"""

		Screen.__init__(self, session)
		self.setup_title = _("Select a city")
		self.Mlist = []
		self["Mlist"] = CityPanelList([])

		self.onChangedEntry = []

		self["key_green"] = StaticText(_("Favorite 1"))
		self["key_yellow"] = StaticText(_("Favorite 2"))
		self["key_blue"] = StaticText(_("Home"))
		self["key_ok"] = StaticText(_("Forecast"))
		self.setTitle(_("Select a city"))

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(self, "ForecaActions",
											{"cancel": (self.exit, _("Exit - End")),
											 "left": (self.left, _("Left - Previous page")),
											 "right": (self.right, _("Right - Next page")),
											 "up": (self.up, _("Up - Previous")),
											 "down": (self.down, _("Down - Next")),
											 "ok": (self.ok, _("OK - Select")),
											 "green": (self.green, _("Green - Assign to Favorite 1")),
											 "yellow": (self.yellow, _("Yellow - Assign to Favorite 2")),
											 "blue": (self.blue, _("Blue - Assign to Home")),
											 "nextBouquet": (self.jump500_down, _("Channel+ - 500 back")),
											 "prevBouquet": (self.jump500_up, _("Channel- - 500 forward")),
											 "volumeDown": (self.jump100_up, _("Volume- - 100 forward")),
											 "volumeUp": (self.jump100_down, _("Volume+ - 100 back"))}, -2)

		self.onShown.append(self.prepare)

	def prepare(self):
		self.maxidx = 0
		if fileExists(USR_PATH + "/City.cfg"):
			with open(USR_PATH + "/City.cfg", "r") as content:
				for line in content:
					text = line.strip()
					self.maxidx += 1
					self.Mlist.append(self.CityEntryItem((text.replace("_", " "), text)))
		self["Mlist"].l.setList(self.Mlist)
		self["Mlist"].selectionEnabled(1)

	def jump500_up(self):
		cur = self["Mlist"].l.getCurrentSelectionIndex()
		if (cur + 500) <= self.maxidx:
			self["Mlist"].instance.moveSelectionTo(cur + 500)
		else:
			self["Mlist"].instance.moveSelectionTo(self.maxidx - 1)

	def jump500_down(self):
		cur = self["Mlist"].l.getCurrentSelectionIndex()
		if (cur - 500) >= 0:
			self["Mlist"].instance.moveSelectionTo(cur - 500)
		else:
			self["Mlist"].instance.moveSelectionTo(0)

	def jump100_up(self):
		cur = self["Mlist"].l.getCurrentSelectionIndex()
		if (cur + 100) <= self.maxidx:
			self["Mlist"].instance.moveSelectionTo(cur + 100)
		else:
			self["Mlist"].instance.moveSelectionTo(self.maxidx - 1)

	def jump100_down(self):
		cur = self["Mlist"].l.getCurrentSelectionIndex()
		if (cur - 100) >= 0:
			self["Mlist"].instance.moveSelectionTo(cur - 100)
		else:
			self["Mlist"].instance.moveSelectionTo(0)

	def up(self):
		self["Mlist"].up()
		self["Mlist"].selectionEnabled(1)

	def down(self):
		self["Mlist"].down()
		self["Mlist"].selectionEnabled(1)

	def left(self):
		self["Mlist"].pageUp()

	def right(self):
		self["Mlist"].pageDown()

	def exit(self):
		global menu
		menu = "stop"
		self.close()

	def ok(self):
		global city
		city = self['Mlist'].l.getCurrentSelection()[0][1]
		FAlog("city= %s" % city, "CurrentSelection= %s" % self['Mlist'].l.getCurrentSelection())
		self.close()

	def blue(self):
		global start
		city = sub(r" ", "_", self['Mlist'].l.getCurrentSelection()[0][1])
		FAlog("Home:", city)
		config.plugins.foreca.home.value = city
		config.plugins.foreca.home.save()
		with open(USR_PATH + "/startservice.cfg", "w") as fwrite:
			fwrite.write(city)
		start = city[city.rfind("/") + 1:len(city)]
		message = "%s %s" % (_("This city is stored as home!\n\n                                  "), city)
		self.session.open(MessageBox, message, MessageBox.TYPE_INFO, timeout=8)

	def green(self):
		global fav1
		city = sub(r" ", "_", self['Mlist'].l.getCurrentSelection()[0][1])
		FAlog("Fav1:", city)
		config.plugins.foreca.fav1.value = city
		config.plugins.foreca.fav1.save()
		with open(USR_PATH + "/fav1.cfg", "w") as fwrite:
			fwrite.write(city)
		fav1 = city[city.rfind("/") + 1:len(city)]
		message = "%s %s" % (_("This city is stored as favorite 1!\n\n                             "), city)
		self.session.open(MessageBox, message, MessageBox.TYPE_INFO, timeout=8)

	def yellow(self):
		global fav2
		city = sub(r" ", "_", self['Mlist'].l.getCurrentSelection()[0][1])
		FAlog("Fav2:", city)
		config.plugins.foreca.fav2.value = city
		config.plugins.foreca.fav2.save()
		with open(USR_PATH + "/fav2.cfg", "w") as fwrite:
			fwrite.write(city)
		fav2 = city[city.rfind("/") + 1:len(city)]
		message = "%s %s" % (_("This city is stored as favorite 2!\n\n                             "), city)
		self.session.open(MessageBox, message, MessageBox.TYPE_INFO, timeout=8)

	def CityEntryItem(self, entry):
		mblau = self["Mlist"].foregroundColorSelected
		weiss = self["Mlist"].foregroundColor
		grau = self["Mlist"].backgroundColorSelected

		itemHeight = self["Mlist"].itemHeight

		col = self["Mlist"].column

		res = [entry]
		res.append(MultiContentEntryText(pos=(0, 0), size=(col, itemHeight), font=0, text="", color=weiss, color_sel=mblau, backcolor_sel=grau, flags=RT_VALIGN_CENTER))
		res.append(MultiContentEntryText(pos=(col, 0), size=(1000, itemHeight), font=0, text=entry[0], color=weiss, color_sel=mblau, backcolor_sel=grau, flags=RT_VALIGN_CENTER))
		return res

# ------------------------------------------------------------------------------------------
# ------------------------------ Satellite photos ------------------------------------------
# ------------------------------------------------------------------------------------------


class SatPanelList(MenuList):

	if HD:
		ItemSkin = 143
	else:
		ItemSkin = 123

	def __init__(self, list, font0=28, font1=16, itemHeight=ItemSkin, enableWrapAround=True):
		MenuList.__init__(self, [], False, eListboxPythonMultiContent)
		GUIComponent.__init__(self)
		self.font0 = gFont("Regular", font0)
		self.font1 = gFont("Regular", font1)
		self.itemHeight = itemHeight
		self.pictScale = 0
		self.foregroundColorSelected = 8900346
		self.foregroundColor = 0xffffff
		self.backgroundColorSelected = 0x565656
		self.textPos = 230, 45, 380, 50

# ---------------------- get skin attribs ----------------------------
	def applySkin(self, desktop, parent):
		def warningWrongSkinParameter(string, wanted, given):
			print("[ForecaPreview] wrong '%s' skin parameters. Must be %d arguments (%d given)" % (string, wanted, given))

		def font(value):
			self.font0 = parseFont(value, ((1, 1), (1, 1)))

		def font1(value):
			self.font1 = parseFont(value, ((1, 1), (1, 1)))

		def itemHeight(value):
			self.itemHeight = int(value)

		def setPictScale(value):
			self.pictScale = int(value)

		def foregroundColor(value):
			self.foregroundColor = parseColor(value).argb()

		def foregroundColorSelected(value):
			self.foregroundColorSelected = parseColor(value).argb()

		def backgroundColorSelected(value):
			self.backgroundColorSelected = parseColor(value).argb()

		def textPos(value):
			self.textPos = list(map(int, value.split(",")))
			lx = len(self.textPos)
			if lx != 4:
				warningWrongSkinParameter(attrib, 4, lx)

		for (attrib, value) in list(self.skinAttributes):
			try:
				locals().get(attrib)(value)
				self.skinAttributes.remove((attrib, value))
			except Exception:
				pass
		self.l.setFont(0, self.font0)
		self.l.setFont(1, self.font1)
		self.l.setItemHeight(self.itemHeight)
		return GUIComponent.applySkin(self, desktop, parent)


class SatPanel(Screen, HelpableScreen):

	def __init__(self, session, ort):
		self.session = session
		self.ort = ort

		if HD:
			self.skin = """
				<screen name="SatPanel" position="center,center" size="630,500" title="Satellite photos" backgroundColor="#40000000" >
					<widget name="Mlist" position="10,10" size="600,430" zPosition="3" backgroundColor="#40000000"  backgroundColorSelected="#565656" enableWrapAround="1" scrollbarMode="showOnDemand" />
					<eLabel position="0,445" zPosition="2" size="630,1" backgroundColor="#c1cdc1" />
					<widget source="key_red" render="Label" position="40,450" zPosition="2" size="124,45" font="Regular;20" valign="center" halign="left" transparent="1" />
					<widget source="key_green" render="Label" position="198,450" zPosition="2" size="140,45" font="Regular;20" valign="center" halign="left" transparent="1" />
					<widget source="key_yellow" render="Label" position="338,450" zPosition="2" size="140,45" font="Regular;20" valign="center" halign="left" transparent="1" />
					<widget source="key_blue" render="Label" position="498,450" zPosition="2" size="142,45" font="Regular;20" valign="center" halign="left" transparent="1" />
					<ePixmap position="2,460" size="36,20" pixmap="skin_default/buttons/key_red.png" transparent="1" alphatest="on" />
					<ePixmap position="160,460" size="36,20" pixmap="skin_default/buttons/key_green.png" transparent="1" alphatest="on" />
					<ePixmap position="300,460" size="36,20" pixmap="skin_default/buttons/key_yellow.png" transparent="1" alphatest="on" />
					<ePixmap position="460,460" size="36,20" pixmap="skin_default/buttons/key_blue.png" transparent="1" alphatest="on" />
				</screen>"""
		else:
			self.skin = """
				<screen name="SatPanel" position="center,center" size="630,440" title="Satellite photos" backgroundColor="#40000000" >
					<widget name="Mlist" position="10,10" size="600,370" zPosition="3" backgroundColor="#40000000"  backgroundColorSelected="#565656" enableWrapAround="1" scrollbarMode="showOnDemand" />
					<eLabel position="0,385" zPosition="2" size="630,1" backgroundColor="#c1cdc1" />
					<widget source="key_red" render="Label" position="40,397" zPosition="2" size="124,45" font="Regular;20" valign="center" halign="left" transparent="1" />
					<widget source="key_green" render="Label" position="198,397" zPosition="2" size="140,45" font="Regular;20" valign="center" halign="left" transparent="1" />
					<widget source="key_yellow" render="Label" position="338,397" zPosition="2" size="140,45" font="Regular;20" valign="center" halign="left" transparent="1" />
					<widget source="key_blue" render="Label" position="498,397" zPosition="2" size="142,45" font="Regular;20" valign="center" halign="left" transparent="1" />
					<ePixmap position="2,400" size="36,20" pixmap="skin_default/buttons/key_red.png" transparent="1" alphatest="on" />
					<ePixmap position="160,400" size="36,20" pixmap="skin_default/buttons/key_green.png" transparent="1" alphatest="on" />
					<ePixmap position="300,400" size="36,20" pixmap="skin_default/buttons/key_yellow.png" transparent="1" alphatest="on" />
					<ePixmap position="460,400" size="36,20" pixmap="skin_default/buttons/key_blue.png" transparent="1" alphatest="on" />
				</screen>"""

		Screen.__init__(self, session)
		self.setup_title = _("Satellite photos")
		self["Mlist"] = SatPanelList([])

		self.onChangedEntry = []
		self["key_red"] = StaticText(_("Continents"))
		self["key_green"] = StaticText(_("Europe"))
		self["key_yellow"] = StaticText(_("Germany"))
		self["key_blue"] = StaticText(_("Settings"))
		self.setTitle(_("Satellite photos"))

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(self, "ForecaActions",
											{"cancel": (self.exit, _("Exit - End")),
											 "left": (self.left, _("Left - Previous page")),
											 "right": (self.right, _("Right - Next page")),
											 "up": (self.up, _("Up - Previous")),
											 "down": (self.down, _("Down - Next")),
											 "red": (self.MapsContinents, _("Red - Continents")),
											 "green": (self.MapsEurope, _("Green - Europe")),
											 "yellow": (self.MapsGermany, _("Yellow - Germany")),
											 "blue": (self.PicSetupMenu, _("Blue - Settings")),
											 "ok": (self.ok, _("OK - Show"))}, -2)
		self.onShown.append(self.prepare)

	def prepare(self):
		self.Mlist = []
		self.Mlist.append(self.SatEntryItem((_("Weather map Video"), 'sat')))
		self.Mlist.append(self.SatEntryItem((_("Showerradar Video"), 'rain')))
		self.Mlist.append(self.SatEntryItem((_("Temperature Video"), 'temp')))
		self.Mlist.append(self.SatEntryItem((_("Cloudcover Video"), 'cloud')))
		self.Mlist.append(self.SatEntryItem((_("Air pressure"), 'pressure')))
		self.Mlist.append(self.SatEntryItem((_("Eumetsat"), 'eumetsat')))

		self["Mlist"].l.setList(self.Mlist)
		self["Mlist"].selectionEnabled(1)

	def up(self):
		self["Mlist"].up()
		self["Mlist"].selectionEnabled(1)

	def down(self):
		self["Mlist"].down()
		self["Mlist"].selectionEnabled(1)

	def left(self):
		self["Mlist"].pageUp()

	def right(self):
		self["Mlist"].pageDown()

	def exit(self):
		global menu
		menu = "stop"
		self.close()

	def ok(self):
		menu = self['Mlist'].l.getCurrentSelection()[0][1]
		FAlog("SatPanel menu= %s" % menu, "CurrentSelection= %s" % self['Mlist'].l.getCurrentSelection())
		self.SatBild()

	def MapsGermany(self):
		itemList = [
			(_("Baden-Wuerttemberg"), 'badenwuerttemberg'),
			(_("Bavaria"), 'bayern'),
			(_("Berlin"), 'berlin'),
			(_("Brandenburg"), 'brandenburg'),
			(_("Bremen"), 'bremen'),
			(_("Hamburg"), 'hamburg'),
			(_("Hesse"), 'hessen'),
			(_("Mecklenburg-Vorpommern"), 'mecklenburgvorpommern'),
			(_("Lower Saxony"), 'niedersachsen'),
			(_("North Rhine-Westphalia"), 'nordrheinwestfalen'),
			(_("Rhineland-Palatine"), 'rheinlandpfalz'),
			(_("Saarland"), 'saarland'),
			(_("Saxony"), 'sachsen'),
			(_("Saxony-Anhalt"), 'sachsenanhalt'),
			(_("Schleswig-Holstein"), 'schleswigholstein'),
			(_("Thuringia"), 'thueringen'),
		]
		itemList.sort(key=lambda i: strxfrm(i[0]))
		self.Mlist = []
		for item in itemList:
			self.Mlist.append(self.SatEntryItem(item))
		self.session.open(SatPanelb, self.ort, _("Germany"), self.Mlist)

	def MapsEurope(self):
		itemList = [
			(_("Austria"), 'oesterreich'),
			(_("Belgium"), 'belgien'),
			(_("Czech Republic"), 'tschechien'),
			(_("Denmark"), 'daenemark'),
			(_("France"), 'frankreich'),
			(_("Germany"), 'deutschland'),
			(_("Greece"), 'griechenland'),
			(_("Great Britain"), 'grossbritannien'),
			(_("Hungary"), 'ungarn'),
			(_("Ireland"), 'irland'),
			(_("Italy"), 'italien'),
			(_("Latvia"), 'lettland'),
			(_("Luxembourg"), 'luxemburg'),
			(_("Netherlands"), 'niederlande'),
			(_("Poland"), 'polen'),
			(_("Portugal"), 'portugal'),
			(_("Russia"), 'russland'),
			(_("Slovakia"), 'slowakei'),
			(_("Spain"), 'spanien'),
			(_("Switzerland"), 'schweiz'),
		]
		itemList.sort(key=lambda i: strxfrm(i[0]))
		self.Mlist = []
		for item in itemList:
			self.Mlist.append(self.SatEntryItem(item))
		self.session.open(SatPanelb, self.ort, _("Europe"), self.Mlist)

	def MapsContinents(self):
		self.Mlist = []
		self.Mlist.append(self.SatEntryItem((_("Europe"), 'europa')))
		self.Mlist.append(self.SatEntryItem((_("North Africa"), 'afrika_nord')))
		self.Mlist.append(self.SatEntryItem((_("South Africa"), 'afrika_sued')))
		self.Mlist.append(self.SatEntryItem((_("North America"), 'nordamerika')))
		self.Mlist.append(self.SatEntryItem((_("Middle America"), 'mittelamerika')))
		self.Mlist.append(self.SatEntryItem((_("South America"), 'suedamerika')))
		self.Mlist.append(self.SatEntryItem((_("Middle East"), 'naherosten')))
		self.Mlist.append(self.SatEntryItem((_("East Asia"), 'ostasien')))
		self.Mlist.append(self.SatEntryItem((_("Southeast Asia"), 'suedostasien')))
		self.Mlist.append(self.SatEntryItem((_("Middle Asia"), 'zentralasien')))
		self.Mlist.append(self.SatEntryItem((_("Australia"), 'australienundozeanien')))
		self.session.open(SatPanelb, self.ort, _("Continents"), self.Mlist)

# ------------------------------------------------------------------------------------------
	def SatEntryItem(self, entry):
		pict_scale = self["Mlist"].pictScale
		ItemSkin = self["Mlist"].itemHeight
		mblau = self["Mlist"].foregroundColorSelected
		weiss = self["Mlist"].foregroundColor
		grau = self["Mlist"].backgroundColorSelected

		res = [entry]
		FAlog("entry=", entry)
		thumb = LoadPixmap(THUMB_PATH + entry[1] + ".png")
		thumb_width = 200
		if pict_scale:
			thumb_width = thumb.size().width()
		res.append(MultiContentEntryPixmapAlphaTest(pos=(2, 2), size=(thumb_width, ItemSkin - 4), png=thumb))  # png vorn
		x, y, w, h = self["Mlist"].textPos
		res.append(MultiContentEntryText(pos=(x, y), size=(w, h), font=0, text=entry[0], color=weiss, color_sel=mblau, backcolor_sel=grau, flags=RT_VALIGN_CENTER))
		return res

	def PicSetupMenu(self):
		self.session.open(PicSetup)

# ------------------------------------------------------------------------------------------

	def fetch_url(self, x):
		menu = self['Mlist'].l.getCurrentSelection()[0][1]
		if not x.startswith("http"):
			x = "https:" + x
		url = x
		if '[TYPE]' in url:
			url = url.replace('[TYPE]', menu)

		global foundz
		foundz = 'jpg'
		foundPos = url.find("0000.jpg")
		print("x= {}".format(x), "url= {}, foundPos= {}".format(url, foundPos))
		if foundPos == -1:
			foundPos = url.find(".jpg")
		if foundPos == -1:
			foundPos = url.find(".png")
			foundz = 'png'
		file = url[foundPos - 10:foundPos]
		file2 = file[0:4] + "-" + file[4:6] + "-" + file[6:8] + " - " + file[8:10] + " " + _("h")
		file2 = file2.replace(" ", "")
		print("file= %s" % file, "file2= %s" % file2)
		"""
		# file_path = CACHE_PATH + file2 + '.jpg'
		# def altrern(url):
			# # import urllib.request
			# if PY3:
				# import urllib.request as urllib2
			# else:
				# import urllib2
			# # image_url = 'http://cache.foreca.net/i/sat/__eur__-sat-20241221180000.jpg'

			# try:
				# urllib2.urlretrieve(url, file_path)
				# print("File salvato in:", file_path)
			# except Exception as e:
				# print("Error saving file:", e)
		# if altrern(url):
			# print('FILE SAVED IN ', file_path)
		"""
		req = Request(url, headers=HEADERS)
		resp = urlopen(req, timeout=10)
		with open("%s%s.%s" % (CACHE_PATH, file2, foundz), 'wb') as f:
			f.write(resp.read())

	def doContext(self):
		from Screens.ChoiceBox import ChoiceBox
		import requests
		text = _("Select action")
		base_url = "https://www.sat24.com"

		try:
			response = requests.get(base_url + "/en-gb/continent/eu", headers=HEADERS, timeout=10)
			response.raise_for_status()
			html = response.text
		except requests.RequestException as e:
			print("Error while page download: %s" % str(e))
			return
			"""
			<a class="whitespace-nowrap block py-2 px-4 hover:bg-secondary hover:text-white" target="_self" href="/en-gb/continent/na">
				North America satellite
			</a>
			"""
		pattern = r'<li class=".*?">\s*<a .*?href="([^"]+)".*?>\s*(.*?)\s*</a>'
		matches = findall(pattern, html)

		seen_links = set()
		menu = []

		for href, title in matches:
			if 'satellite' in title.lower():
				link = base_url + href
				if link not in seen_links:
					menu.append((title.strip(), link))
					seen_links.add(link)

		def returnToChoiceBox(result=None):
			self.session.openWithCallback(boxAction, ChoiceBox, title=text, list=menu, windowTitle=_("eumetsat menu"))

		def boxAction(choice):
			if choice:
				title, url = choice
				devicepath = join(CACHE_PATH, "meteogram.png")

				try:
					req = Request(url, headers=HEADERS)
					resp = urlopen(req, timeout=10)
					content = resp.read().decode('utf-8') if PY3 else resp.read()

					pattern = r'<div class="absolute w-full h-full overflow-hidden z-10">.*?<img .*?alt="satLayer".*?src="([^"]+)".*?>'
					matches = findall(pattern, content, DOTALL)
					if matches:
						chosen_link = matches[0]
						print("Link select:", chosen_link)
						if not chosen_link.startswith("http"):
							chosen_link = base_url + chosen_link

						try:
							from PIL import Image
							from io import BytesIO
							img_response = requests.get(chosen_link, headers=HEADERS, timeout=10)

							img = Image.open(BytesIO(img_response.content))
							img = img.convert("RGB")  # Rimuove ICC
							img.save(devicepath, "PNG")
							FAlog("Image dimensions: {}x{}".format(img.width, img.height))

							self.session.openWithCallback(returnToChoiceBox, PicView, devicepath, 0, False)
						except requests.RequestException as e:
							FAlog("Error downloading image: %s" % str(e))
							returnToChoiceBox()
					else:
						FAlog("Image not found on the page.")
						returnToChoiceBox()
				except Exception as e:
					FAlog("Error processing page: %s" % str(e))
					returnToChoiceBox()

		if len(menu) > 0:
			self.session.openWithCallback(boxAction, ChoiceBox, title=text, list=menu, windowTitle=_("eumetsat menu"))

	def SatBild(self):
		try:
			current_selection = self['Mlist'].l.getCurrentSelection()
			if not current_selection or not current_selection[0] or len(current_selection[0]) < 2:
				FAlog("SatBild Error: Invalid selection in CurrentSelection", str(current_selection))
				return
			menu = current_selection[0][1]
			FAlog("SatBild menu= %s" % menu, "CurrentSelection= %s" % current_selection)
			if menu == "eumetsat":
				self.doContext()
			else:
				try:
					# devicepath = CACHE_PATH + "sat.html"  # "/var/volatile/tmp/sat.html"
					url = "%s%s?map=%s" % (BASEURL, pathname2url(self.ort), menu)
					FAlog("VIDEO URL map = %s" % url)
					req = Request(url, headers=HEADERS)
					resp = urlopen(req, timeout=10)
					content = (resp.read().decode('utf-8') if PY3 else resp.read())
					start_pattern = r"var urltemplate"
					end_pattern = r"var timehdrs"
					section_pattern = compile(r"%s(.*?)%s" % (start_pattern, end_pattern), DOTALL)
					section_match = section_pattern.search(content)

					if section_match:
						section_content = section_match.group(1)
						fulltext = compile(r'(\/\/cache.*?\.(jpg|png))', DOTALL)
						urls = fulltext.findall(section_content)
						for url, ext in urls:
							full_url = 'https:' + url  # Ricostruisci l'URL completo
							FAlog("Valid URL:", full_url)
							self.fetch_url(full_url)
						"""
						print("SatBild: Found image URLs: %s" % str(urls))
						threads = [Thread(target=self.fetch_url, args=(url,)) for url in urls]
						for thread in threads:
							thread.start()
						for thread in threads:
							thread.join()
						"""
						self.session.open(View_Slideshow, 0, True)
					else:
						FAlog("SatBild Warning: No image URLs found in page content.")
						self.session.open(MessageBox, _("No satellite images found."), MessageBox.TYPE_INFO)
						return
				except Exception as e:
					self.session.open(MessageBox, _("Failed to process satellite data: %s" % str(e)), MessageBox.TYPE_ERROR)
		except Exception as e:
			FAlog("SatBild Critical Error", str(e))
			self.session.open(MessageBox, _("A critical error occurred: %s" % str(e)), MessageBox.TYPE_ERROR)

# ------------------------------------------------------------------------------------------
# ------------------------------ Weather Maps ----------------------------------------------
# ------------------------------------------------------------------------------------------


class SatPanelListb(MenuList):

	if HD:
		ItemSkin = 143
	else:
		ItemSkin = 123

	def __init__(self, list, font0=24, font1=16, itemHeight=ItemSkin, enableWrapAround=True):
		MenuList.__init__(self, [], False, eListboxPythonMultiContent)
		self.font0 = gFont("Regular", font0)
		self.font1 = gFont("Regular", font1)
		self.itemHeight = itemHeight

# ---------------------- get skin attribs ----------------------------
	def applySkin(self, desktop, parent):
		def font(value):
			self.font0 = parseFont(value, ((1, 1), (1, 1)))

		def font1(value):
			self.font1 = parseFont(value, ((1, 1), (1, 1)))

		def itemHeight(value):
			self.itemHeight = int(value)

		for (attrib, value) in list(self.skinAttributes):
			try:
				locals().get(attrib)(value)
				self.skinAttributes.remove((attrib, value))
			except Exception:
				pass
		self.l.setFont(0, self.font0)
		self.l.setFont(1, self.font1)
		self.l.setItemHeight(self.itemHeight)
		return GUIComponent.applySkin(self, desktop, parent)


class SatPanelb(Screen, HelpableScreen):

	def __init__(self, session, ort, title, mlist):
		self.session = session
		self.ort = ort

		if HD:
			self.skin = """
				<screen name="SatPanelb" position="center,center" size="620,500" backgroundColor="#40000000" >
					<widget name="Mlist" position="10,10" size="600,430" zPosition="3" backgroundColor="#40000000"  backgroundColorSelected="#565656" enableWrapAround="1" scrollbarMode="showOnDemand" />
				</screen>"""
		else:
			self.skin = """
				<screen name="SatPanelb" position="center,center" size="620,440" backgroundColor="#40000000" >
					<widget name="Mlist" position="10,10" size="600,370" zPosition="3" backgroundColor="#40000000"  backgroundColorSelected="#565656" enableWrapAround="1" scrollbarMode="showOnDemand" />
				</screen>"""

		Screen.__init__(self, session)
		self.setup_title = title
		self.Mlist = mlist
		FAlog("Mlist= %s" % self.Mlist, "\nSatPanelListb([])= %s" % SatPanelListb([]))
		self.onChangedEntry = []
		self["Mlist"] = SatPanelListb([])
		self["Mlist"].l.setList(self.Mlist)
		self["Mlist"].selectionEnabled(1)
		self["key_blue"] = StaticText(_("Settings"))
		self.setTitle(title)

		HelpableScreen.__init__(self)
		self["actions"] = HelpableActionMap(self, "ForecaActions",
											{"cancel": (self.Exit, _("Exit - End")),
											 "left": (self.left, _("Left - Previous page")),
											 "right": (self.right, _("Right - Next page")),
											 "up": (self.up, _("Up - Previous")),
											 "down": (self.down, _("Down - Next")),
											 "blue": (self.PicSetupMenu, _("Blue - Settings")),
											 "ok": (self.ok, _("OK - Show"))}, -2)

	def up(self):
		self["Mlist"].up()
		self["Mlist"].selectionEnabled(1)

	def down(self):
		self["Mlist"].down()
		self["Mlist"].selectionEnabled(1)

	def left(self):
		self["Mlist"].pageUp()

	def right(self):
		self["Mlist"].pageDown()

	def Exit(self):
		global menu
		menu = "stop"
		self.close()

	def ok(self):
		menu = self['Mlist'].l.getCurrentSelection()[0][1]
		FAlog("SatPanelb menu= %s" % menu, "CurrentSelection= %s" % self['Mlist'].l.getCurrentSelection())
		self.SatBild()

	def PicSetupMenu(self):
		self.session.open(PicSetup)

	def SatBild(self):
		try:
			current_selection = self['Mlist'].l.getCurrentSelection()
			if not current_selection or not current_selection[0] or len(current_selection[0]) < 2:
				FAlog("SatBild Error: Invalid selection in CurrentSelection", str(current_selection))
				self.session.open(MessageBox, _("Invalid selection. Please select a valid region."), MessageBox.TYPE_ERROR)
				return

			region = current_selection[0][1]
			FAlog("SatBild: Selected region = %s" % region)

			devicepath = CACHE_PATH + "meteogram.png"
			url = "http://img.wetterkontor.de/karten/" + region + "0.jpg"
			FAlog("SatBild: Downloading image from URL = %s" % url)

			try:
				download_image(url, devicepath)
				remove_icc_profile(devicepath)
				self.session.open(PicView, devicepath, 0, False)
			except Exception as e:
				FAlog("SatBild Error: Failed to download or save the image", str(e))
				self.session.open(MessageBox, _("Failed to load the satellite image: %s" % str(e)), MessageBox.TYPE_ERROR)

		except Exception as e:
			FAlog("SatBild Critical Error", str(e))
			self.session.open(MessageBox, _("A critical error occurred: %s" % str(e)), MessageBox.TYPE_ERROR)


# ------------------------------------------------------------------------------------------
# -------------------------- Picture viewer for large pictures -----------------------------
# ------------------------------------------------------------------------------------------


class PicView(Screen):

	def __init__(self, session, filelist, index, startslide):
		self.session = session
		self.bgcolor = config.plugins.foreca.bgcolor.value
		space = config.plugins.foreca.framesize.value

		self.skindir = "/tmp"
		self.skin = "<screen position=\"0,0\" size=\"" + str(size_w) + "," + str(size_h) + "\" > \
			<eLabel position=\"0,0\" zPosition=\"0\" size=\"" + str(size_w) + "," + str(size_h) + "\" backgroundColor=\"" + self.bgcolor + "\" /> \
			<widget name=\"pic\" position=\"" + str(space) + "," + str(space) + "\" size=\"" + str(size_w - (space * 2)) + "," + str(size_h - (space * 2)) + "\" zPosition=\"1\" alphatest=\"on\" /> \
			</screen>"

		Screen.__init__(self, session)
		self["actions"] = ActionMap(["OkCancelActions", "MediaPlayerActions"],
									{"cancel": self.Exit,
									 "stop": self.Exit}, -1)

		self["pic"] = Pixmap()
		self.filelist = filelist
		self.old_index = 0
		self.lastindex = index
		self.currPic = []
		self.shownow = True
		self.dirlistcount = 0
		self.index = 0
		self.picload = ePicLoad()
		self.picload.PictureData.get().append(self.finish_decode)
		self.onLayoutFinish.append(self.setPicloadConf)
		self.startslide = startslide

	def setPicloadConf(self):
		FAlog("[setPicloadConf] setPicloadConf")
		sc = getScale()
		if not sc or len(sc) < 2:
			sc = (1920, 1080)
		if not hasattr(self, 'bgcolor') or not self.bgcolor:
			self.bgcolor = "#000000"
		resize_value = int(config.plugins.foreca.resize.value) if str(config.plugins.foreca.resize.value).isdigit() else 1
		self.picload.setPara([
			self["pic"].instance.size().width(),
			self["pic"].instance.size().height(),
			sc[0],
			sc[1],
			0,
			resize_value,
			self.bgcolor
		])
		self.start_decode()

	def ShowPicture(self):
		FAlog("[setPicloadConf] ShowPicture")
		if self.shownow and len(self.currPic):
			self.shownow = False
			if self.currPic[0]:
				# remove_icc_profile(self.currPic[0])
				print("[ShowPicture] Set the image:", self.currPic[0])
				self["pic"].instance.setPixmap(self.currPic[0].__deref__())
			else:
				print("[ShowPicture] No image data present.")

	def finish_decode(self, picInfo=""):
		FAlog("[setPicloadConf] finish_decode")
		ptr = self.picload.getData()
		if ptr is not None:
			print("[finish_decode] Image data loaded successfully.")
			try:
				# remove_icc_profile(ptr)
				self.currPic = []
				self.currPic.append(ptr)
				self.ShowPicture()
			except Exception as e:
				print("[finish_decode] Error:", str(e))
		else:
			print("[finish_decode] No image data obtained from picload.")

	def start_decode(self):
		FAlog("[setPicloadConf] start_decode")
		self.picload.startDecode(self.filelist)
		# self.picload.startDecode(self.filelist, 0, 0, False)

	def clear_images(self):
		try:
			if exists(self.filelist):
				remove(self.filelist)
			print("Image file removed:", self.filelist)
		except OSError as e:
			print("Error removing file:", e)

	def Exit(self):
		del self.picload
		self.clear_images()
		self.close(self.lastindex + self.dirlistcount)

# ------------------------------------------------------------------------------------------
# ------------------------------ Slide Show ------------------------------------------------
# ------------------------------------------------------------------------------------------


class View_Slideshow(Screen):

	def __init__(self, session, pindex=0, startslide=False):

		print("SlideShow is running...")
		self.textcolor = config.plugins.foreca.textcolor.value
		self.bgcolor = config.plugins.foreca.bgcolor.value
		space = config.plugins.foreca.framesize.value
		fontsize = config.plugins.foreca.fontsize.value

		self.skindir = "/tmp"
		self.skin = "<screen position=\"0,0\" size=\"" + str(size_w) + "," + str(size_h) + "\" flags=\"wfNoBorder\" > \
			<eLabel position=\"0,0\" zPosition=\"0\" size=\"" + str(size_w) + "," + str(size_h) + "\" backgroundColor=\"" + self.bgcolor + "\" /> \
			<widget name=\"pic\" position=\"" + str(space) + "," + str(space + 40) + "\" size=\"" + str(size_w - (space * 2)) + "," + str(size_h - (space * 2) - 40) + "\" zPosition=\"1\" alphatest=\"on\" /> \
			<widget name=\"point\" position=\"" + str(space + 5) + "," + str(space + 10) + "\" size=\"20,20\" zPosition=\"2\" pixmap=\"" + THUMB_PATH + "record.png\" alphatest=\"on\" /> \
			<widget name=\"play_icon\" position=\"" + str(space + 25) + "," + str(space + 10) + "\" size=\"20,20\" zPosition=\"2\" pixmap=\"" + THUMB_PATH + "ico_mp_play.png\"  alphatest=\"on\" /> \
			<widget name=\"file\" position=\"" + str(space + 45) + "," + str(space + 10) + "\" size=\"" + str(size_w - (space * 2) - 50) + "," + str(fontsize + 5) + "\" font=\"Regular;" + str(fontsize) + "\" halign=\"left\" foregroundColor=\"" + self.textcolor + "\" zPosition=\"2\" noWrap=\"1\" transparent=\"1\" /> \
			</screen>"
		Screen.__init__(self, session)

		self["actions"] = ActionMap(["OkCancelActions", "MediaPlayerActions"],
									{"cancel": self.Exit,
									 "stop": self.Exit,
									 "pause": self.PlayPause,
									 "play": self.PlayPause,
									 "previous": self.prevPic,
									 "next": self.nextPic}, -1)
		self["point"] = Pixmap()
		self["pic"] = Pixmap()
		self["play_icon"] = Pixmap()
		self["file"] = Label(_("Please wait, photo is being loaded ..."))
		self.old_index = 0
		self.picfilelist = []
		self.lastindex = pindex
		self.currPic = []
		self.shownow = True
		self.dirlistcount = 0

		self.filelist = FileList(CACHE_PATH, showDirectories=False, matchingPattern=r"^.*\.(jpg|png)$", useServiceRef=False)
		for x in self.filelist.getFileList():
			if x[0][0]:
				if x[0][1] is False:
					self.picfilelist.append(x[0][0] if PY3 else CACHE_PATH + x[0][0])
					# print('picfilelist:', self.picfilelist)
				else:
					self.dirlistcount += 1

		self.maxentry = len(self.picfilelist) - 1
		self.pindex = pindex - self.dirlistcount
		if self.pindex < 0:
			self.pindex = 0
		self.picload = ePicLoad()
		self.picload.PictureData.get().append(self.finish_decode)
		self.slideTimer = eTimer()
		self.slideTimer.callback.append(self.slidePic)
		if self.maxentry >= 0:
			self.onLayoutFinish.append(self.setPicloadConf)
		if startslide is True:
			self.PlayPause()

	def setPicloadConf(self):
		FAlog("[View_Slideshow] setPicloadConf")
		sc = getScale()
		if not sc or len(sc) < 2:
			sc = (1920, 1080)
		if not hasattr(self, 'bgcolor') or not self.bgcolor:
			self.bgcolor = "#000000"
		resize_value = int(config.plugins.foreca.resize.value) if str(config.plugins.foreca.resize.value).isdigit() else 1
		self.picload.setPara([
			self["pic"].instance.size().width(),
			self["pic"].instance.size().height(),
			sc[0],
			sc[1],
			0,
			resize_value,
			self.bgcolor
		])
		if "play_icon" in self and self["play_icon"]:
			self["play_icon"].hide()
		if "file" in self and self["file"] and config.plugins.foreca.infoline.value is False:
			self["file"].hide()
		"""
		FAlog("SetPicloadConf:", {
			"widget_width": self["pic"].instance.size().width(),
			"widget_height": self["pic"].instance.size().height(),
			"scale_x": sc[0],
			"scale_y": sc[1],
			"resize": resize_value,
			"bgcolor": self.bgcolor
		})
		print("SetPicloadConf:", {
			"widget_width": self["pic"].instance.size().width(),
			"widget_height": self["pic"].instance.size().height(),
			"scale_x": sc[0],
			"scale_y": sc[1],
			"resize": resize_value,
			"bgcolor": self.bgcolor
		})
		"""
		self.start_decode()

	def ShowPicture(self):
		FAlog("[View_Slideshow] ShowPicture")
		if self.shownow and len(self.currPic):
			self.shownow = False
			self["file"].setText(self.currPic[0].replace(".jpg", "").replace(".png", ""))
			self.lastindex = self.currPic[1]
			if self.currPic[2]:
				# print("[ShowPicture] Set the image:", self.currPic[0])
				# print("[ShowPicture] Image data:", self.currPic[2])
				self["pic"].instance.setPixmap(self.currPic[2].__deref__())
			else:
				print("[ShowPicture] No image data present.")
			self.currPic = []
			self.nextDay()
			self.start_decode()

	def finish_decode(self, picInfo=""):
		FAlog("[View_Slideshow] finish_decode")
		self["point"].hide()
		ptr = self.picload.getData()
		if ptr is not None:
			print("[finish_decode] Image data loaded successfully.")
			try:
				if picInfo:
					parts = picInfo.split('\n', 1)
					if parts and '/' in parts[0]:
						filename = parts[0].split('/')[-1]
						text = "(" + str(self.pindex + 1) + "/" + str(self.maxentry + 1) + ") " + filename
				self.currPic = [text, self.pindex, ptr]
				self.ShowPicture()
			except Exception as e:
				print("[finish_decode] Error:", str(e))
		else:
			print("[finish_decode] No image data obtained from picload.")

	def start_decode(self):
		FAlog("[View_Slideshow] start_decode")
		if self.pindex < 0 or self.pindex >= len(self.picfilelist):
			print("[start_decode] Index out of bounds: %d" % self.pindex)
			return

		filepath = self.picfilelist[self.pindex]

		if CACHE_PATH not in filepath:
			filepath = CACHE_PATH + filepath

		print("[start_decode] filepath:", filepath)
		if not exists(filepath):
			print("[start_decode] File not found: %s" % filepath)
			return
		# print("[start_decode] decoding image: %s" % filepath)
		try:
			self.picload.startDecode(filepath)
			# self.picload.startDecode(filepath, 0, 0, False)
			# print("[start_decode] Decodifica avviata con successo per: %s" % filepath)
		except Exception as e:
			print("[start_decode] Error while decoding image: %s" % str(e))

		self["point"].show()

	def nextDay(self):
		self.pindex += 1
		if self.pindex > self.maxentry:
			self.pindex = 0

	def prev(self):
		self.pindex -= 1
		if self.pindex < 0:
			self.pindex = self.maxentry

	def slidePic(self):
		FAlog("slide to next Picture index=" + str(self.lastindex))
		if config.plugins.foreca.loop.value is False and self.lastindex == self.maxentry:
			self.PlayPause()
		self.shownow = True
		self.ShowPicture()

	def PlayPause(self):
		FAlog("[View_Slideshow] PlayPause")
		if self.slideTimer.isActive():
			self.slideTimer.stop()
			self["play_icon"].hide()
		else:
			self.slideTimer.start(config.plugins.foreca.slidetime.value * 1000)
			self["play_icon"].show()
			self.nextPic()

	def prevPic(self):
		self.currPic = []
		self.pindex = self.lastindex
		self.prev()
		self.start_decode()
		self.shownow = True

	def nextPic(self):
		self.shownow = True
		self.ShowPicture()

	def clear_images(self):
		try:
			for filepath in self.picfilelist:
				full_path = join(CACHE_PATH, filepath)
				if exists(full_path):
					try:
						remove(full_path)
						print("Image file removed:", full_path)
					except OSError as e:
						print("Error while removing file:", full_path, e)

			self.picfilelist = []

			if exists(CACHE_PATH):
				for filename in listdir(CACHE_PATH):
					if filename.endswith(".jpg") or filename.endswith(".png"):
						file_path = join(CACHE_PATH, filename)
						try:
							remove(file_path)
							print("Image file removed:", file_path)
						except OSError as e:
							print("Error while removing file:", file_path, e)
		except Exception as e:
			print("Error no file:", e)

	def Exit(self):
		del self.picload
		self.clear_images()
		self.close(self.lastindex + self.dirlistcount)


# ------------------------------------------------------------------------------------------
# -------------------------------- Foreca Settings -----------------------------------------
# ------------------------------------------------------------------------------------------

class PicSetup(Screen):

	skin = """
		<screen name="PicSetup" position="center,center" size="660,330" title= "SlideShow Settings" backgroundColor="#000000" >
			<widget name="Mlist" position="5,5" size="650,280" backgroundColor="#000000" enableWrapAround="1" scrollbarMode="showOnDemand" />
			<widget source="key_red" render="Label" position="50,290" zPosition="2" size="150,40" font="Regular;18" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
			<widget source="key_green" render="Label" position="285,290" zPosition="2" size="150,40" font="Regular;18" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" />
			<ePixmap position="5,300" size="36,25" pixmap="skin_default/buttons/key_red.png" transparent="1" alphatest="on" />
			<ePixmap position="240,300" size="36,25" pixmap="skin_default/buttons/key_green.png" transparent="1" alphatest="on" />
		</screen>"""
	FAlog("Setup...")

	def __init__(self, session):
		self.skin = PicSetup.skin
		Screen.__init__(self, session)
		self.setup_title = _("SlideShow Settings")
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self.setTitle(_("SlideShow Settings"))
		self["actions"] = NumberActionMap(["SetupActions", "ColorActions"],
										  {"ok": self.save,
										   "save": self.save,
										   "green": self.save,
										   "cancel": self.cancel,
										   "red": self.cancel,
										   "left": self.keyLeft,
										   "right": self.keyRight,
										   "0": self.keyNumber,
										   "1": self.keyNumber,
										   "2": self.keyNumber,
										   "3": self.keyNumber,
										   "4": self.keyNumber,
										   "5": self.keyNumber,
										   "6": self.keyNumber,
										   "7": self.keyNumber,
										   "8": self.keyNumber,
										   "9": self.keyNumber}, -3)
		self.list = []
		self["Mlist"] = ConfigList(self.list)
		self.list.append(getConfigListEntry(_("Select units"), config.plugins.foreca.units))
		self.list.append(getConfigListEntry(_("Select time format"), config.plugins.foreca.time))
		self.list.append(getConfigListEntry(_("City names as labels in the Main screen"), config.plugins.foreca.citylabels))
		self.list.append(getConfigListEntry(_("Frame size in full view"), config.plugins.foreca.framesize))
		self.list.append(getConfigListEntry(_("Font size in slideshow"), config.plugins.foreca.fontsize))
		self.list.append(getConfigListEntry(_("Scaling Mode"), config.plugins.foreca.resize))
		self.list.append(getConfigListEntry(_("Slide Time (seconds)"), config.plugins.foreca.slidetime))
		self.list.append(getConfigListEntry(_("Show Infoline"), config.plugins.foreca.infoline))
		self.list.append(getConfigListEntry(_("Textcolor"), config.plugins.foreca.textcolor))
		self.list.append(getConfigListEntry(_("Backgroundcolor"), config.plugins.foreca.bgcolor))
		self.list.append(getConfigListEntry(_("Slide picture in loop"), config.plugins.foreca.loop))
		self.list.append(getConfigListEntry(_("Display in extensions menu"), config.plugins.foreca.extmenu))
		self.list.append(getConfigListEntry(_("Debug"), config.plugins.foreca.debug))

	def save(self):
		for x in self["Mlist"].list:
			x[1].save()
		config.save()
		self.refreshPlugins()
		self.close()

	def cancel(self):
		for x in self["Mlist"].list:
			x[1].cancel()
		self.close(False, self.session)

	def keyLeft(self):
		self["Mlist"].handleKey(KEY_LEFT)

	def keyRight(self):
		self["Mlist"].handleKey(KEY_RIGHT)

	def keyNumber(self, number):
		self["Mlist"].handleKey(KEY_0 + number)

	def refreshPlugins(self):
		plugins.clearPluginList()
		plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
