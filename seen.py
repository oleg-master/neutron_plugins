#$ neutron_plugin 01
# --*-- encoding: utf-8 --*--
import re
from datetime import datetime

MSG_ITS_ME = u'A po4emu vi sprashivaete?'
MSG_NOW_ONLINE = u'Ya ego vizhu! O_O'
MSG_NEVER_SEEN = u'Kto eto?'
MSG_NO_PARAMETER_GIVEN = u'Kakie vashi dokazatelstva?!'
MSG_WAS_SEEN = u'Byl zame4en '

SEEN_FILENAME = 'static/seen.txt'
SEEN = {}

SeenLck = threading.Lock()

SeenLck.acquire()
fp=file(SEEN_FILENAME,'r')
lines = fp.readlines()
for line in lines:
	line=line.strip()
	(nick,date)=line.split(' ', 1)
	SEEN[nick] = date
fp.close()
SeenLck.release()


def handler_seen(type,source,parameters):
	groupchat = get_groupchat(source)
	if not groupchat:
		return

	nick = parameters
	
# Fix this to allow search in base in case there's more matches exists.
# Thus to show people in room and people absent together, but don't show any twice.
# Also, now works only with exact match. Shoud be fixed to allow wildcards||regexp
	if nick:
		if re.match('wasd22', nick):
			msg(groupchat, MSG_ITS_ME)
# Enable if what (but fix to not use global variable)
#		elif GROUPCHATS[groupchat].has_key(nick):
#			msg(groupchat, MSG_NOW_ONLINE)
		else:
			if SEEN.has_key(nick):
				msg(groupchat,MSG_WAS_SEEN+nick+' '+SEEN[nick])
			else:
				msg(groupchat, MSG_NEVER_SEEN)
	else:
		msg(groupchat, MSG_NO_PARAMETER_GIVEN)


def handler_leave_seen(groupchat, nick):
	SeenLck.acquire()

	SEEN[nick]=datetime.now().isoformat(' ')
	seennick = ' '.join([nick,SEEN[nick]])

	fp=file(SEEN_FILENAME,'w')
	for nick in SEEN:
		seennick = ' '.join([nick,SEEN[nick]])
		fp.write(seennick+'\n')
	fp.close()

	SeenLck.release()


register_command_handler(handler_seen,u'!seen',0,u'seen',u'!seen',[u'!seen'])
register_leave_handler(handler_leave_seen)
