#!/usr/bin/python

import bottle, redis, time, md5
bottle.debug(True)

from bottle import route, run, request, response, template, view, static_file

r = redis.Redis(host='localhost', port=6379, db=0)

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
	handle = r.get('session:%s:handle'%(request.COOKIES.get('sessionId')))
	
	r.incr('nextPostId')
	pid = r.get('nextPostId')
	r.set('post:%s:title'%(pid), title)
	r.set('post:%s:body'%(pid), body)
	r.set('post:%s:datestamp'%(pid), datestamp)
	r.set('post:%s:user'%(pid), handle)
	
	r.lpush('posts:recent', pid)
	
	return "Success"

@route("/admin")
def admin():
	permissions = {}
	return template('admin', globalVars=globalVars, permissions=permissions)
	
@route("/admin/login")
def login():
	handle = "max"
	m = md5.new(handle + str(time.time()))
	sessionId = m.hexdigest()
	response.set_cookie('sessionId', sessionId)
	
	r.set("session:%s:handle"%(sessionId), handle)
	
	return getRecentPosts()


def getPostDictById(id):
	title = r.get("post:%s:title"%(id))
	datestamp = r.get("post:%s:datestamp"%(id))
	user = r.get("post:%s:user"%(id))
	body = r.get("post:%s:body"%(id))
	summary = r.get("post:%s:summary"%(id))
	tagIds = r.smembers("post:%s:tagIds"%(id))
	
	return {'title':title, 'datestamp':datestamp, 'user':user, 'body':body, 'summary':summary, 'tagIds':tagIds}

def auth(type, request):
	sessionId = request.COOKIES.get('sessionId')
	if sessionId is None:
		print "No Session ID"
		return False
	print sessionId
	
	handle = r.get('session:%s:handle'%(sessionId))
	
	print "Username: " + str(handle)
	
	permissions = r.smembers('users:%s:permissions'%(handle))
	
	print permissions
	
	if type in permissions:
		print "User %s authorized for %s"%(handle, type)
		return True


run(host="localhost", port=8080, reloader=False)
