#$ neutron_plugin 01
# --*-- encoding: utf-8 --*--
# !seen command takes as parameter (nick) first sequence of non-whitespace chars, until first whitespace char occured
# now, regexp only, but!
#
# TODO:
# Return 'already on channels' check
#
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

seen_join='J'
seen_leave='L'

# This should be acquired elsehow...
MY_NICK = 'wasd22'

SEEN_FILENAME = 'static/seen.txt'
SEEN = {}
seenlist = []
maxfind = 5

SeenLck = threading.Lock()


if os.path.isfile(SEEN_FILENAME):
	SeenLck.acquire()
	fp=file(SEEN_FILENAME,'rb')
	try:
		(SEEN, seenlist) = pickle.load(fp)
	except	(pickle.UnpicklingError, AttributeError, EOFError, ImportError, IndexError, ValueError):
		SEEN = {}
	fp.close()
	SeenLck.release()

def seen_new(nick, flag):
	SEEN[nick]=(datetime.now(), flag)
	while seenlist.count(nick):
		seenlist.remove(nick)
	seenlist.insert(0, nick)


def show_seen(groupchat, nick):
	if SEEN[nick][1] == seen_join:
		msg(groupchat, "%s was joining %s" % (nick, SEEN[nick][0].isoformat(' ')))
	elif SEEN[nick][1] == seen_leave:
		msg(groupchat, "%s was leaving %s" % (nick, SEEN[nick][0].isoformat(' ')))


def handler_reseen(type,source,parameters):
	groupchat = get_groupchat(source)
	if not groupchat:
		return

	if not parameters:
		msg(groupchat, MSG_NO_PARAMETER_GIVEN)
		return

	seekfor = (parameters.split())[0].strip()
	expr = re.compile(seekfor)
	found = []
	cnt = 0
	for nick in seenlist:
		if expr.match(nick):
			found.append(nick)
			cnt+=1

	if cnt:
		nicks = ''
		if cnt == 1:
			show_seen(groupchat, found[0])
		elif cnt <= maxfind:
			for i in range(0, cnt):
				nicks+=found[i]+' '
			msg(groupchat, "I found %d matches to your query (sorted): %s" % (cnt, nicks))
			show_seen(groupchat, found[0])
		else:
			for i in range(0, maxfind):
				nicks+=found[i]+' '
			msg(groupchat, "I found %d matches to your query, here %d most recent (sorted): %s" % (cnt, maxfind, nicks))
			show_seen(groupchat, found[0])
	else:
		msg(groupchat, MSG_NEVER_SEEN)


def handler_leave_seen(groupchat, nick):
	SeenLck.acquire()

	seen_new(nick, seen_leave)

	fp=file(SEEN_FILENAME,'wb')
	pickle.dump(SEEN, fp)
	fp.close()

	SeenLck.release()


def handler_join_seen(groupchat, nick):
	SeenLck.acquire()

	seen_new(nick, seen_join)

	fp=file(SEEN_FILENAME,'wb')
	pickle.dump((SEEN, seenlist), fp)
	fp.close()

	SeenLck.release()


register_command_handler(handler_reseen,u'!seen',0,u'seen',u'!seen',[u'!seen'])
#register_command_handler(handler_reseen,u'!reseen',0,u'reseen',u'!reseen',[u'!seen'])
register_leave_handler(handler_leave_seen)
register_join_handler(handler_join_seen)
