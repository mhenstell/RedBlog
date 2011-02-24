#!/usr/bin/python

import bottle, redis, time, hashlib

from bottle import route, run, request, response, template, view, static_file

r = redis.Redis(host='localhost', port=6379, db=0)

ERROR_NOT_LOGGED_IN = 0
ERROR_NOT_AUTHORIZED = 1

PERMISSION_ADMIN = 0
PERMISSION_POST = 1

errors = {ERROR_NOT_LOGGED_IN:"Not logged in.", ERROR_NOT_AUTHORIZED:"Not authorized to view that page."}


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
	
	#return template('recent', posts=posts, globalVars=globalVars)
	return render('recent', posts)

def render(type, dict=None):
	refreshSession()
	return template(type, passed=dict, globalVars=globalVars)

@route("/test")
def test():
	error(ERROR_NOT_AUTHORIZED)


@route("/post")
def getPostPage():

	auth(PERMISSION_POST)
	
	return render('post')


@route("/post", method="POST")
def newPost():
	pid = createPost(request.forms.get('title'), time.time(), getCurrentUser(), request.forms.get('body'))
	if pid is not False:
		url = generateUrl(pid)
		return template('message', globalVars=globalVars, message={'success':"Sucessfully created %s"%(url)})

def auth(type):
	userName = getCurrentUser()
	print userName
	if not userName: 
		error(ERROR_NOT_LOGGED_IN)

	permissions = getPermissions(userName)
	
	if str(type) in permissions:
		return True
	
	error(ERROR_NOT_AUTHORIZED)
	
def getPermissions(userName):
	return r.smembers("users:%s:permissions"%(userName))
	
def error(type):
	return bottle.redirect("/error/%s"%(type))
	
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
	except Exception:
		print Exception[0]
		return False

def refreshSession():
	globalVars['loggedInUser'] = getCurrentUser()

@route("/admin")
def admin():
	
	auth(PERMISSION_ADMIN)
	
	userInfo = getUserInfo(getCurrentUser())
	
	return template('admin', globalVars=globalVars, userInfo=userInfo)
	
@route("/admin/login")
def login():
	userName = "max"
	
	getOrCreateSession(userName)
	
	return "Success"

@route("/error/:error")
def errorPage(error):

	return errors[int(error)]

def getOrCreateSession(userName):
	if getCurrentUser():
		print "User %s already logged in."%(getCurrentUser())
		return True
	
	m = hashlib.md5()
	m.update(userName)
	m.update(str(time.time()))
	sessionId = m.hexdigest()
	
	print "New session for %s: %s"%(userName, sessionId)
	
	response.set_cookie('sessionId', sessionId, path='/')
	r.setex("sessions:%s:userName"%(sessionId), userName, 260000)
	return True

def getUserName(sessionId):
	return r.get('sessions:%s:userName'%(sessionId))

def getCurrentSessionId():
	return request.COOKIES.get('sessionId')

def getCurrentUser():
	sessionId = request.COOKIES.get('sessionId')
	print sessionId
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














def auths(type, request):
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


if __name__ == "__main__":

	bottle.debug(True)
	run( host="localhost", port=8080, reloader=True)
