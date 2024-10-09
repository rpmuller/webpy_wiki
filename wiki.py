#!/usr/bin/python

import web
from markdown import Markdown
import os, time, re, cgi

# For debugging use only
web.internalerror = web.debugerror

page = """
<html><head><title>{title}</title></head><body>
<h1>{title}</h1><ul>
{content}
</body></html>
"""

def list(*items):
	return "<ul>\n" + "\n".join(f"<li>{item}</li>" for item in items) + "\n</ul>\n"


urls = (
    '/', 'WikiPages',
    '/page/([a-zA-Z_]+)', 'WikiPage',
    '/editor/([a-zA-Z_]+)', 'WikiEditor'
)

app = web.application(urls,globals())

wikidir = os.path.realpath('./pages')

class WikiPages:
	
	def GET(self):
		web.header("Content-Type","text/html; charset=utf-8")
		t = re.compile('^[a-zA-Z0-9_]+.md$')
		wikipages = os.listdir(wikidir)
		lines = ["<html><head><title>wiki pages</title></head><body>",
				"<h1>Wiki Pages:</h1><ul>"]
		print(wikipages)
		for wikipage in wikipages:
			if os.path.isfile(os.path.join(wikidir, wikipage)) and t.match(wikipage):
				lines.append("<li><a href=\"%(path)s/page/%(page)s\">%(page)s</a></li>" 
								% {'path':web.ctx.home+web.ctx.path[1:],'page':wikipage})
		lines.append( "</ul></body></html>")
		return "\n".join(lines)

class WikiPage:
	
	def GET(self, name):
		page = os.path.join(wikidir,name)
		web.header("Content-Type","text/html; charset=utf-8")
		lines = []
		if os.path.exists(page):
			lines.append( "<html><head><title>%s</title></head><body>" % name)
			lines.append( "<h1>%s</h1>" % name)
			lines.append( "<p>")
			lines.append( "[<a href=\"%s\">Pages</a>] " 
					% (web.ctx.home+"/"))
			lines.append( "[<a href=\"%s\">Edit</a>] " 
					% (web.ctx.home+'/editor/'+name))
			lines.append( "</p>")
			lines.append( Markdown(open(page).read()))
			lines.append( "</body></html>")
		else:
			web.ctx.status = '404 Not Found'
			lines.append( "<html><head><title>Does not exist: %s</title></head><body>" % name)
			lines.append( "<p>Page %s does not yet exist - " % name)
			lines.append( "<a href=\"%s\">Create</a>" % (web.ctx.home+'/editor/'+name))
		return "\n".join(lines)
	
	def POST(self,name):
		page = os.path.join(wikidir,name)
		if os.path.exists(page):
			newpage = page+'.'+time.strftime("%Y%m%d%H%M%S", time.gmtime())
			os.rename(page,newpage)
		f = open(page, "w")
		f.write(web.input(page='').page)
		f.close()
		web.redirect(web.ctx.home+'/page/'+name)
		return

class WikiEditor:

	def GET(self,name):
		web.header("Content-Type","text/html; charset=utf-8")
		lines = []
		lines.append( "<html><head><title>Editing %s</title></head><body>" % name);
		lines.append ("<h1>Editing: %s</h1>" % name)
		lines.append( "<form method=\"POST\" accept-charset=\"utf-8\" action=\"%s\">" 
			% (web.ctx.home+'/page/'+name))
		lines.append( "<textarea name=\"page\" cols=\"100\" rows=\"20\">")

		page = os.path.join(wikidir,name)
		if os.path.exists(page):
			lines.append( cgi.escape(open(page).read()))
		lines.append( "</textarea><br><input type=\"submit\" value=\"Update\"></form>")
		lines.append( "<p><a href=\"http://daringfireball.net/projects/markdown/syntax\">Markdown Syntax</a></p>")

		lines.append( "</body></html>")
		return "\n".join(lines)
	
if __name__ == "__main__": 
	#web.run(urls)
	app.run()
