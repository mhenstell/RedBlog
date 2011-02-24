#!/usr/bin/python

import bottle, redis, time, md5
bottle.debug(True)

from bottle import route, run, request, response, template, view, static_file

r = redis.Redis(host='localhost', port=6380, db=0)



@route('/css/:filename')
def send_css(filename):
	return static_file(filename, root='./css')

@route("/")
def index():
    return getRecentPosts()

@route("/post/:id")
def getPostById(id):
	node = {'post':['title', 'body', 'userName', 'datestamp']}
	return template('node', globalVars=globalVars, node=node)

@route("/recent")
def getRecentPosts():
	recentPosts = r.lrange("posts:recent", 0, 9)
	posts = {}
	for x in range(0, len(recentPosts)):
		posts[x] = getPost(recentPosts[x])
	return template('recent', posts=posts, globalVars=globalVars)

@route("/post")
def getPostPage():
	if auth('post', request):
		return template('post', globalVars=globalVars)
	else:
		return template('message', globalVars=globalVars, message={'error':"Not Authorized."})

@route("/post", method="POST")
def newPost():
	pid = createPost(request.forms.get('title'), time.time(), getCurrentUser(), request.forms.get('body'))
	if pid is not False:
		url = generateUrl(pid)
		return template('message', globalVars=globalVars, message={'success':"Sucessfully created %s"%(url)})


def generateUrl(pid):
	return r.get('global:siteURL') + "post/%s"%(str(pid))
	
def createPost(title, datestamp, user, body):
	try:
		r.incr('global:nextPostId')
		pid = r.get('global:nextPostId')
		r.set('posts:%s:title'%(pid), title)
		r.set('posts:%s:body'%(pid), body)
		r.set('posts:%s:datestamp'%(pid), datestamp)
		r.set('posts:%s:user'%(pid), handle)
		r.lpush('posts:recent', pid)
		return pid
	except e:
		print e
		return False

def refreshSession():
	globalVars['loggedInUser'] = getCurrentUser()

@route("/admin")
def admin():
	refreshSession()
	print "User: " + globalVars['loggedInUser']
	userName = getCurrentUser()
	if userName is None:
		return template('message', globalVars=globalVars, message={'error':"Not Authorized."})
	
	userInfo = getUserInfo(userName)
	
	return template('admin', globalVars=globalVars, userInfo=userInfo)
	
@route("/admin/login")
def login():
	handle = "max"
	m = md5.new(handle + str(time.time()))
	sessionId = m.hexdigest()
	response.set_cookie('sessionId', sessionId)
	
	r.set("sessions:%s:userName"%(sessionId), handle)
	
	print sessionId
	
	return getRecentPosts()


def getCurrentUser():
	sessionId = request.COOKIES.get('sessionId')
	if sessionId is None:
		return None
	userName = r.get('sessions:%s:userName'%(sessionId))
	return userName


def getUserInfo(userName):
	userInfo = {}
	userInfo['userName'] = userName
	userInfo['realName'] = r.get("users:%s:realName"%(userName))
	userInfo['email'] = r.get("users:%s:email"%(userName))
	userInfo['submissions'] = r.lrange("users:%s:submissions"%(userName), 0, -1)
	userInfo['role'] = r.lrange("users:%s:roles"%(userName), 0, -1)
	return userInfo
	

def getPost(id):
	post = {}
	post['title'] = r.get("posts:%s:title"%(id))
	post['datestamp'] = r.get("posts:%s:datestamp"%(id))
	post['user'] = r.get("posts:%s:user"%(id))
	post['body'] = r.get("posts:%s:body"%(id))
	post['summary'] = r.get("posts:%s:summary"%(id))
	post['tagIds'] = r.smembers("posts:%s:tagIds"%(id))
	return post
	
def auth(type, request):
	sessionId = request.COOKIES.get('sessionId')
	if sessionId is None:
		print "No Session ID"
		return False
	print sessionId
	
	userName = r.get('session:%s:userName'%(sessionId))
	
	print "Username: " + str(userName)
	
	permissions = r.smembers('users:%s:permissions'%(userName))
	
	print permissions
	
	if type in permissions:
		print "User %s authorized for %s"%(userName, type)
		return True

globalVars = {}
globalVars['siteTitle'] = r.get('global:siteTitle')
globalVars['siteURL'] = r.get('global:siteURL')
globalVars['loggedInUser'] = False


run(host="localhost", port=8080, reloader=True)
