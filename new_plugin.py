#$ neutron_plugin 01
# --*-- encoding: utf-8 --*--

HINT_INTERVAL = 15
MAX_HINTCOUNT = 3
MAX_REPLY = 5
TOTAL_LINES = 2
QUEST_FILE = 'static/questions.txt'
RECURSIVE_MAX = 20
VICTORINA = {}
SCORES = {}
FILE_SCORE = 'static/scores.txt'

ScoreLck=threading.Lock()
SysLck=threading.Lock()

def timer_th(groupchat,id):
	time.sleep(HINT_INTERVAL)
	if not VICTORINA.has_key(groupchat):
		return
	VICTORINA[groupchat]['timer_lck'].acquire()
	if not VICTORINA[groupchat].has_key('cur_id'):
		VICTORINA[groupchat]['timer_lck'].release()
		return
	if not id == VICTORINA[groupchat]['cur_id']:
		VICTORINA[groupchat]['timer_lck'].release()
	 	return
	if VICTORINA[groupchat]['hint_count']<MAX_HINTCOUNT:
	 	VICTORINA[groupchat]['hint_count']+=1
		hint=VICTORINA[groupchat]['hint']
		i=random.randrange(0,len(hint))
		while not hint[i] == '*':
			i=random.randrange(0,len(hint))
		hint=hint[0:i]+VICTORINA[groupchat]['answer'][i]+hint[i+1:]
		VICTORINA[groupchat]['hint']=hint
		msg(groupchat,u'Подсказка: (*) '+hint)
		thread.start_new(timer_th,(groupchat,id))
		VICTORINA[groupchat]['timer_lck'].release()
		return
	VICTORINA[groupchat]['hint_count']=0
	msg(groupchat,u'(*) Время вышло. Правильный ответ был: '+VICTORINA[groupchat]['answer'])
	VICTORINA[groupchat]['reply_count']+=1
	if VICTORINA[groupchat]['reply_count']<MAX_REPLY:
		ask_question(groupchat)
		VICTORINA[groupchat]['timer_lck'].release()
		return
	msg(groupchat,u'(*) Слишком долго молчали. Кончилась викторина. Для нового этапа пишите !старт')
	list_scores(groupchat)
	VICTORINA[groupchat]['timer_lck'].release()
	stop_vikt(groupchat)
	
def new_question():
	global RECURSIVE_MAX
	line_num = random.randrange(0,TOTAL_LINES+1)
	fp=file(QUEST_FILE)
	for i in range(line_num+1):
		if i == line_num:
			try:
				(question,answer) = string.split(fp.readline().strip(),'|',1)
				return (unicode(question.strip(),'utf-8'),unicode(answer.strip(),'utf-8'))
			except:
				RECURSIVE_MAX-=1
				if RECURSIVE_MAX:
					return new_question()
				else:
					RECURSIVE_MAX=20
					return (u'Ошибка чтения строки '+str(i),'')
		else:
			fp.readline()
	
def ask_question(groupchat):
	(question, answer) = new_question()
	VICTORINA[groupchat]['answer'] = answer
	hint = ''
	for n in range(len(answer)):
		hint+=u'*'
	VICTORINA[groupchat]['hint']=hint
	VICTORINA[groupchat]['hint_count']=0
	VICTORINA[groupchat]['ask_time']=time.time()
	VICTORINA[groupchat]['cur_id']=random.randrange(0,800)
	thread.start_new(timer_th,(groupchat,VICTORINA[groupchat]['cur_id']))
	msg(groupchat,u'(*) Внимание вопрос: '+question)
	

def answer_question(groupchat, nick, answer):
	if not VICTORINA.has_key(groupchat):
		return
	if not VICTORINA[groupchat].has_key('timer_lck'):
		return
	VICTORINA[groupchat]['timer_lck'].acquire()
	if not VICTORINA[groupchat]['answer'] == answer:
		VICTORINA[groupchat]['timer_lck'].release()
		return
	VICTORINA[groupchat]['reply_count']=0
	answer_time=int(time.time()-VICTORINA[groupchat]['ask_time'])+1
	points=HINT_INTERVAL*MAX_HINTCOUNT/answer_time/3+1
	msg(groupchat,u'(*) Правильный ответ "'+answer+u'" сказал '+nick+u' и заработал '+str(points)+u' очков')
	ScoreLck.acquire()
	if not SCORES.has_key(groupchat):
		SCORES[groupchat]={}
	if SCORES[groupchat].has_key(nick):
	 	SCORES[groupchat][nick]+=points
	else:
		SCORES[groupchat][nick]=points
	ScoreLck.release()
	list_scores(groupchat)
	VICTORINA[groupchat]['cur_id']=random.randrange(0,800)
	VICTORINA[groupchat]['timer_lck'].release()
	ask_question(groupchat)
	return

def list_scores(groupchat):
	ScoreLck.acquire()
	fp=file(FILE_SCORE,'w')
	for i in SCORES:
		for j in SCORES[i]:
			wrds=[]
			wrds.append(i)
			wrds.append(j)
			wrds.append(str(SCORES[i][j]))
			res=string.join(wrds,'|')
			fp.write(res.encode('utf8')+'\n')
	fp.close()
	if SCORES[groupchat]:
		result=u'(*) Текущие очки:'
		for n in SCORES[groupchat]:
			result += u'\n' + n + u': '+ str(SCORES[groupchat][n])
		msg(groupchat,result)
	ScoreLck.release()

def add_hint(groupchat):
	if not VICTORINA.has_key(groupchat):
		return
	VICTORINA[groupchat]['timer_lck'].acquire()
	if VICTORINA[groupchat]['hint_count']<MAX_HINTCOUNT:
	 	VICTORINA[groupchat]['hint_count']+=1
		hint=VICTORINA[groupchat]['hint']
		i=random.randrange(0,len(hint))
		while not hint[i] == '*':
			i=random.randrange(0,len(hint))
		hint=hint[0:i]+VICTORINA[groupchat]['answer'][i]+hint[i+1:]
		VICTORINA[groupchat]['hint']=hint
		msg(groupchat,u'Подсказка: (*) '+hint)
		VICTORINA[groupchat]['cur_id']=random.randrange(0,800)
		VICTORINA[groupchat]['timer_lck'].release()
		thread.start_new(timer_th,(groupchat,VICTORINA[groupchat]['cur_id']))
	else:
		msg(groupchat,u'Кончились подсказки (*)')
		VICTORINA[groupchat]['timer_lck'].release()

def handler_vikt_start(type,source,parameters):
	SysLck.acquire()
	groupchat=get_groupchat(source)
	if not groupchat:
		SysLck.release()
		return
	if VICTORINA.has_key(groupchat):
		msg(groupchat,u'Викторина уже запущена')
		SysLck.release()
		return
	VICTORINA[groupchat]={}
	ScoreLck.acquire()
	fp=file(FILE_SCORE)
	str=fp.readline()
	while(len(str)>0):
		scrs=string.split(str,'|')
		if SCORES.has_key(scrs[0]):
			SCORES[scrs[0]][unicode(scrs[1],'utf8')]=int(string.strip(scrs[2]))
		else:
			SCORES[scrs[0]]={}
			SCORES[scrs[0]][unicode(scrs[1],'utf8')]=int(string.strip(scrs[2]))
		str=fp.readline()
	fp.close()
	ScoreLck.release()
	VICTORINA[groupchat]['reply_count']=0
	VICTORINA[groupchat]['timer_lck']=threading.Lock()
	VICTORINA[groupchat]['answer']=''
	msg(groupchat,u'(*) Поехали')
	ask_question(groupchat)
	SysLck.release()
	return

def stop_vikt(groupchat):
	if VICTORINA.has_key(groupchat):
		del(VICTORINA[groupchat]['timer_lck'])
		del(VICTORINA[groupchat]['ask_time'])
		del(VICTORINA[groupchat]['hint'])
		del(VICTORINA[groupchat]['answer'])
		del(VICTORINA[groupchat])
		del(SCORES[groupchat])

def handler_vikt_stop(type,source,parameters):
	groupchat=get_groupchat(source)
	if groupchat:
		stop_vikt(groupchat)

def handler_quiz_message(type,source,body):
	SysLck.acquire()
	groupchat=get_groupchat(source)
	if groupchat and VICTORINA.has_key(groupchat):
		answer_question(source[1],source[2],body.strip())
	SysLck.release()

def handler_hint(type,source,body):
	groupchat=get_groupchat(source)
	if groupchat and VICTORINA.has_key(groupchat):
		add_hint(groupchat)

register_command_handler(handler_hint,u'!подсказка',0,u'Подсказка',u'!подсказка',[u'!подсказка'])
register_command_handler(handler_vikt_start,u'!старт',0,u'Запуск викторины',u'!старт',[u'!старт'])
register_command_handler(handler_vikt_stop,u'!стоп',0,u'Остановка викторины',u'!стоп',[u'!стоп'])

register_message_handler(handler_quiz_message)
