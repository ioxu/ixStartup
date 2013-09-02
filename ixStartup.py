# ixStartup Plug-in
# Initial code generated by Softimage SDK Wizard
# Executed Sun Aug 18 21:21:47 UTC+0930 2013 by ben
# 
# Tip: To add a command to this plug-in, right-click in the 
# script editor and choose Tools > Add Command.
import win32com.client, os
from win32com.client import constants
import inspect
import ntpath

null = None
false = 0
true = 1

recent_paths = []
recent_groups_list = []

def XSILoadPlugin( in_reg ):
	in_reg.Author = "ben@ioxu.com"
	in_reg.Name = "ixStartup Plug-in"
	in_reg.Major = 1
	in_reg.Minor = 0

	in_reg.RegisterEvent("Startup",constants.siOnStartup)
	
	in_reg.RegisterCommand("ixStartupSplash","ixStartupSplash")
	#RegistrationInsertionPoint - do not remove this line

	return true

def XSIUnloadPlugin( in_reg ):
	strPluginName = in_reg.Name
	Application.LogMessage(str(strPluginName) + str(" has been unloaded."),constants.siVerbose)
	return true


# Callback for the Startup event.
def Startup_OnEvent( in_ctxt ):
	Application.LogMessage("ixStartup: Startup_OnEvent called",constants.siVerbose)

# 	TODO: Put your code here.
	Application.ixStartupSplash()

# 	Return value is ignored as this event can not be aborted.
	return true

def ixStartupSplash_Init( in_ctxt ):
	oCmd = in_ctxt.Source
	oCmd.Description = "command for calling the startup splash"
	oCmd.SetFlag(constants.siCannotBeUsedInBatch,true)
	oCmd.ReturnValue = true

	return true

def ixStartupSplash_Execute(  ):

	Application.LogMessage("ixStartupSplash_Execute called",constants.siVerbose)

	DoSplash() 

	return true


def DoSplash():
	import os
	global recent_groups_list 
	global recent_paths 

	recentPathsFile = os.path.join( os.getenv("XSI_USERHOME"), 'Data', 'Preferences', 'RecentFileMenus.xml')
	print("recent paths file: %s"%recentPathsFile)

	from xml.dom import minidom
	xmldoc = minidom.parse(recentPathsFile)

	groupslist = xmldoc.getElementsByTagName('recent_file_menu')
	recent_groups_list = [str(i.attributes['name'].value) for i in groupslist]
	recent_paths = [None]*len(recent_groups_list)

	# build
	for g in groupslist:
		n = str(g.attributes['name'].value)
		recent_paths[ recent_groups_list.index(n) ] = [str(c.childNodes[0].nodeValue) for c in g.getElementsByTagName('recent_file')]

	# log
	"""
	RECENT_MODELS_MENU
	RECENT_SCENES_MENU
	RECENT_SCRIPTS_MENU
	RECENT_SHADERCODE_MENU
	"""
	"""
	for i in recent_groups_list:
		print(i)
		for rf in recent_paths[ recent_groups_list.index(i) ]:
			print("    %s"%rf)
	"""

	root = Application.ActiveProject.ActiveScene.Root
	
	# cleanup old props
	for p in root.Properties:
		if "ixStartup" in p.Name:
			print "ixStartup: cleaning up '%s'"%p.FullName
			Application.DeleteObj( p )

	# make prop
	prop = root.AddCustomProperty("ixStartup")
	layout = prop.PPGLayout
	prop.Parameters("Name").SetCapabilityFlag( constants.siNotInspectable, True  )

	buttons_scenes_callback_basenames = []

	layout.Clear()
	layout.AddGroup("Scenes")
	button_number = 0
	for p in recent_paths[ recent_groups_list.index("RECENT_SCENES_MENU") ]:
		layout.AddRow()
		buttonbasename = "s%s"%button_number
		Application.LogMessage( "ixStartup: add button %s"%buttonbasename )
		basep = ntpath.basename(p)
		#Application.LogMessage("#####################%s"%p)
		layout.AddButton( buttonbasename , basep )
		prop.AddParameter3( buttonbasename + "_path", constants.siString, p)
		#pathitem = layout.AddItem( buttonbasename + "_path" )
		#pathitem.SetAttribute(constants.siUINoLabel, True)
		buttons_scenes_callback_basenames.append( buttonbasename )
		layout.AddSpacer()
		modtime = modification_date(p)
		#layout.AddStaticText(  prettydate(modtime) +" "+ modtime.strftime("%a  %c  %p") , 0, 0)
		layout.AddStaticText( prettydate(modtime), 0, 0)
		#layout.AddStaticText( modtime.strftime("%a  %c  %p"), 0, 0)
		layout.EndRow()
		button_number += 1

	layout.EndGroup()

	buttons_models_callback_basenames = []

	layout.AddGroup("Models")
	model_number = 0
	for p in recent_paths[ recent_groups_list.index("RECENT_MODELS_MENU") ]:
		layout.AddRow()
		buttonbasename = "m%s"%button_number
		basep = ntpath.basename(p)
		layout.AddButton( buttonbasename , basep )
		buttons_models_callback_basenames.append( buttonbasename )
		layout.AddSpacer()
		modtime = modification_date(p)
		#layout.AddStaticText(  prettydate(modtime) +" "+ modtime.strftime("%a  %c  %p") , 0, 0)		
		layout.AddStaticText( prettydate(modtime), 0, 0)
		#layout.AddStaticText( modtime.strftime("%a  %c  %p"), 0, 0)
		layout.EndRow()
		model_number += 1

	layout.EndGroup()

	# 400 x 800 is good
	layout.SetViewSize( 850, 800 )


	#print buttons_scenes_callback_basenames
	# logic
	logicstr = "# DYNAMICALLY GENERATED BUTTON CALLBACKS"
	for i in buttons_scenes_callback_basenames:
		Application.LogMessage("""\ndef """ + i + """_OnClicked():""" ) 
		logicstr += """\ndef """ + i + """_OnClicked():
			    #Application.LogMessage( "ixStartup: button pressed: %s "%\""""+i+"""\")
			    #recent_paths[ recent_groups_list.index("RECENT_SCENES_MENU") ]["""+i+"""]


			    #this_buttons_path = PPG.PPGLayout.Item( \""""+i+"""\").Label
			    this_buttons_path = PPG."""+i+"""_path.Value

			    Application.LogMessage( "ixStartup: opening scene %s "%this_buttons_path)
			    
			    PPG.Close()
			    Application.DeleteObj( PPG.Inspected)
			    Application.OpenScene( this_buttons_path )
			    #PPG.Close()
				\n"""
	
	#print logicstr

	layout.Language = "Python"
	layout.Logic = logicstr

	# inspect
	#button = Application.InspectObj( prop, None, "ixStartup", constants.siModal, False )
	button = Application.InspectObj( prop, None, "ixStartup", constants.siLockAndForceNew , False )
	#print "ixStartup: %s"%button # returns False if "okay" button and True if "Cancel"  button
	
	#Application.DeleteObj( prop )



import datetime
def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def prettydate(d):
    diff = datetime.datetime.now() - d #utcnow() - d
    s = diff.seconds
    if diff.days > 7 :#or diff.days < 0:
        return d.strftime('%d %b %y')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{0} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{0} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{0} minutes ago'.format(s/60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{0} hours ago'.format(s/3600)

