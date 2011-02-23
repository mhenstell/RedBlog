#!/usr/bin/python

import bottle, redis
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
    return "Hello, world!"

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
	#return dict(posts=posts, siteTitle=siteTitle)
	return template('recent', posts=posts, globalVars=globalVars)

@route("/post")
def getPostPage():
	return template('post', globalVars=globalVars)

@route("/post", method="POST")
def setPost():
	title = request.forms.get('title')
	body = request.forms.get('body')
	
	
	r.incr('nextPostId')
	pid = r.get('nextPostId')
	r.set('post:%s:title'%(pid), title)
	r.set('post:%s:body'%(pid), body)
	r.lpush('posts:recent', pid)
	
	return "Success"

def getPostDictById(id):
	title = r.get("post:%s:title"%(id))
	datestamp = r.get("post:%s:datestamp"%(id))
	submitterId = r.get("post:%s:submitterId"%(id))
	submitter = getSubmitterById(submitterId)
	body = r.get("post:%s:body"%(id))
	summary = r.get("post:%s:summary"%(id))
	tagIds = r.smembers("post:%s:tagIds"%(id))
	
	return {'title':title, 'datestamp':datestamp, 'submitterId':submitter, 'body':body, 'summary':summary, 'tagIds':tagIds}


	
def getSubmitterById(id):
	return r.get("users:%s:handle"%(id))

run(host="localhost", port=8080, reloader=False)
