#!/usr/bin/python

import bottle, redis, time, md5
bottle.debug(True)

from bottle import route, run, request, response, template, view, static_file

r = redis.Redis(host='localhost', port=6380, db=0)

globalVars = {}
globalVars['siteTitle'] = r.get('site:title')

@route('/css/:filename')
def send_css(filename):
	return static_file(filename, root='./css')

@route("/")
def index():
    return getRecentPosts()

@route("/post/:id")
def getPostById(id):
	pass

@route("/recent")
def getRecentPosts():
	recentPosts = r.lrange("posts:recent", 0, 9)
	posts = {}
	for x in range(0, len(recentPosts)):
		posts[x] = getPostDictById(recentPosts[x])
	print posts
	return template('recent', posts=posts, globalVars=globalVars)

@route("/post")
def getPostPage():
	if auth('post', request):
		return template('post', globalVars=globalVars)
	else:
		return template('error', globalVars=globalVars, error="Not Authorized.")

@route("/post", method="POST")
def setPost():
	title = request.forms.get('title')
	body = request.forms.get('body')
	datestamp = time.time()
	handle = r.get('sessions:%s:userName'%(request.COOKIES.get('sessionId')))
	
	r.incr('global:nextPostId')
	pid = r.get('global:nextPostId')
	r.set('posts:%s:title'%(pid), title)
	r.set('posts:%s:body'%(pid), body)
	r.set('posts:%s:datestamp'%(pid), datestamp)
	r.set('posts:%s:user'%(pid), handle)
	
	r.lpush('posts:recent', pid)
	
	return "Success"

@route("/admin")
def admin():

	
	userName = getCurrentUser()
	if userName is None:
		return template('error', globalVars=globalVars, error="Not Authorized.")
	
	userInfo = getUserInfo(userName)
	
	
	return template('admin', globalVars=globalVars, userInfo=userInfo)
	
@route("/admin/login")
def login():
	handle = "max"
	m = md5.new(handle + str(time.time()))
	sessionId = m.hexdigest()
	response.set_cookie('sessionId', sessionId)
	
	r.set("sessions:%s:userName"%(sessionId), handle)
	
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
	

def getPostDictById(id):
	title = r.get("posts:%s:title"%(id))
	datestamp = r.get("posts:%s:datestamp"%(id))
	user = r.get("posts:%s:user"%(id))
	body = r.get("posts:%s:body"%(id))
	summary = r.get("posts:%s:summary"%(id))
	tagIds = r.smembers("posts:%s:tagIds"%(id))
	
	return {'title':title, 'datestamp':datestamp, 'user':user, 'body':body, 'summary':summary, 'tagIds':tagIds}

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


run(host="localhost", port=8080, reloader=False)
