#$ neutron_plugin 01
# --*-- encoding: utf-8 --*--
# !seen command takes as parameter (nick) first sequence of non-whitespace chars, until first whitespace char occured
# If there's '*' (asterisk) at the end of parameter, then it will search any nick starting with what parameter starting
# until first '*' occured. Any number of '*' to the left end and to the right end of string would be deleted then, and
# only if there was '*' at the end of string (parameter). Be good. Don't play with it. Or!
# If there's no '*' to the right (i.e. at the end of string), !seen will do exact match.
# For regexp !seen there would be !sin command, which be implemented later... (Implemented as !reseen)
# !reseen command allow any regexp, except '.*', maybe even '..*' should do...
#
# TODO:
# Limit search result by certain number; show most recent
# Restrict regexp somehow... Or not...
# This behavior should be nice:
# I found 15 matches to your query.  Here are the 5 most recent (sorted): wasd22 wasd wasd23 wasd32 wasd33. wasd (wasd31@178.187.x.x) was last seen joining #channel 1 hour, 59 minutes ago. wasd is still on #channel.
# Kak-to tak

import re
from datetime import datetime
import pickle
from os import path

MSG_ITS_ME = u'A po4emu vi sprashivaete?'
MSG_NOW_ONLINE = u'Ya ego vizhu! O_O'
MSG_NEVER_SEEN = u'Kto eto?'
MSG_NO_PARAMETER_GIVEN = u'Kakie vashi dokazatelstva?!'
MSG_WAS_SEEN = u'Byl zame4en '
MSG_KGB_DETECTED = u'A ne mnogo li na sebya beryote?'

# This should be acquired elsehow...
MY_NICK = 'wasd22'

SEEN_FILENAME = 'static/seen.txt'
SEEN = {}

SeenLck = threading.Lock()


if os.path.isfile(SEEN_FILENAME):
	SeenLck.acquire()
	fp=file(SEEN_FILENAME,'rb')
	try:
		SEEN = pickle.load(fp)
	# Here to be added more kosher exceptions, because it is nowhere complete list
	except	(pickle.UnpicklingError, AttributeError, EOFError, ImportError, IndexError):
		SEEN = {}
	fp.close()
	SeenLck.release()


def handler_seen(type,source,parameters):
	groupchat = get_groupchat(source)
	if not groupchat:
		return

	seekfor = (parameters.split())[0].strip()

	if not seekfor:
		msg(groupchat, MSG_NO_PARAMETER_GIVEN)
		return

	if re.match('^'+MY_NICK+'$', seekfor):
		msg(groupchat, MSG_ITS_ME)
	elif re.match('^\*$', seekfor):
		msg(groupchat, MSG_KGB_DETECTED)
	elif re.match('^.*\*$', seekfor):
		expr = re.compile('^'+seekfor.strip('*')+'.*')
		found = 0
		for nick in SEEN:
			if expr.search(nick):
				msg(groupchat,MSG_WAS_SEEN+nick+' '+SEEN[nick])
				found += 1
		for nick in GROUPCHATS[groupchat]:
			if expr.search(nick):
				msg(groupchat, MSG_NOW_ONLINE+' '+nick)
				# Following match may be deleted at your whim
				if re.match('^'+MY_NICK+'$', nick):
					msg(groupchat, MSG_ITS_ME)
				found += 1
		if found == 0:
			msg(groupchat, MSG_NEVER_SEEN)
	else:
		if GROUPCHATS[groupchat].has_key(seekfor):
			msg(groupchat, MSG_NOW_ONLINE+' '+seekfor)
		elif SEEN.has_key(seekfor):
			msg(groupchat,MSG_WAS_SEEN+seekfor+' '+SEEN[seekfor])
		else:
			msg(groupchat, MSG_NEVER_SEEN)

def handler_reseen(type,source,parameters):
	groupchat = get_groupchat(source)
	if not groupchat:
		return

	seekfor = (parameters.split())[0].strip()

	if not seekfor:
		msg(groupchat, MSG_NO_PARAMETER_GIVEN)
		return

	if re.match('^'+MY_NICK+'$', seekfor):
		msg(groupchat, MSG_ITS_ME)
	elif re.match('^\.\*$', seekfor):
		msg(groupchat, MSG_KGB_DETECTED)
	else:
		expr = re.compile(seekfor)
		found = 0
		for nick in SEEN:
			if expr.search(nick):
				msg(groupchat,MSG_WAS_SEEN+nick+' '+SEEN[nick])
				found += 1
		for nick in GROUPCHATS[groupchat]:
			if expr.search(nick):
				msg(groupchat, MSG_NOW_ONLINE+' '+nick)
				found += 1
		if found == 0:
			msg(groupchat, MSG_NEVER_SEEN)


def handler_leave_seen(groupchat, nick):
	SeenLck.acquire()

	SEEN[nick]=datetime.now().isoformat(' ')
	seennick = ' '.join([nick,SEEN[nick]])

	fp=file(SEEN_FILENAME,'wb')
	pickle.dump(SEEN, fp)
	fp.close()

	SeenLck.release()


register_command_handler(handler_seen,u'!seen',0,u'seen',u'!seen',[u'!seen'])
register_command_handler(handler_reseen,u'!reseen',0,u'reseen',u'!reseen',[u'!seen'])
register_leave_handler(handler_leave_seen)
