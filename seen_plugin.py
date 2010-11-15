#$ neutron_plugin 01
# --*-- encoding: utf-8 --*--
# !seen command takes as parameter (nick) first sequence of non-whitespace chars, until first whitespace char occured
# now, regexp only, but!
#
# TODO:
#
# Do something to allow exact match right away?
# Kak eto putet po ruski?
# Get correct bot-own nick correct way. This is MY_NICK variable that should be set to.
# Comment code a bit
# new comment

import re
from datetime import datetime
import pickle
from os import path

seen_join='J'
seen_leave='L'

MSG_NO_PARAMETER_GIVEN=u'Какие Ваши доказательства¿'
MSG_NEVER_SEEN='Кто это¿'

# This should be acquired elsehow...
MY_NICK = 'wasd22'

SEEN_FILENAME = 'static/seen.txt'
SEEN = {}
seenlist = []
MAXFIND = 5

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
	result = ''
	if SEEN[nick][1] == seen_join:
		result = u'%s заходил %s' % (nick, SEEN[nick][0].isoformat(' '))
	elif SEEN[nick][1] == seen_leave:
		result = u'%s ушёл %s' % (nick, SEEN[nick][0].isoformat(' '))
	else:
		result = u'%s чего-то делал %s' % (nick, SEEN[nick][0].isoformat(' '))
	if GROUPCHATS[groupchat].has_key(nick):
		result += u'. %s всё ещё здесь.' % nick
	return result


def handler_reseen(type,source,parameters):
	groupchat = get_groupchat(source)
	querast = source[2]
	if not groupchat:
		return

	if not parameters:
		msg(groupchat, MSG_NO_PARAMETER_GIVEN)
		return

	seekfor = (parameters.split())[0].strip()
	expr = re.compile(seekfor, re.IGNORECASE|re.UNICODE)

# Here you may or may not check for exact match.

	found = [nick for nick in seenlist if expr.match(nick)]
	cnt = len(found)

	if cnt:
		if cnt == 1:
			result = "%s: " % querast
		else:
			if cnt <= MAXFIND:
				result=u'%s: Найдено %d совпадений с запросом (отсортировано): ' % (querast, cnt)
			else:
				result=u'%s: Найдено %d совпадений с запросом, %d наиболее свежих (отсортировано): ' % (querast, cnt, maxfind)
			nicks = ' '.join(found[1..MAXFIND])
			result += "%s" % nicks + '. '

		result += show_seen(groupchat, found[0])
	else:
		result = MSG_NEVER_SEEN

	msg(groupchat, result)


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
register_leave_handler(handler_leave_seen)
register_join_handler(handler_join_seen)
