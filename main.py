#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

# class Handler(webapp2.RequestHandler):

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def renderError(self, error_code):
        self.error(error_code)
        self.response.write("Oops! Something went wrong!")


class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_front(self, title="", blog="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")

        self.render("base.html", title=title, blog=blog, error=error, blogs=blogs)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            a = Blog(title = title, blog = blog)
            a.put()

            self.redirect("/")
        else:
            error = "we need both a title and a blog!"
            self.render_front(title, blog, error)

class NewPost(Handler):
    def render_front(self, title="", blog="", error=""):
        self.render("new-post.html", title=title, blog=blog, error=error,)

    def get(self):
        self.render("new-post.html")

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            blog = Blog(title = title, blog = blog)
            blog.put()

            id = blog.key().id()
            self.redirect("/blog/%s" %id)
        else:
            error = "we need both a title and a blog!"
            self.render_front(title, blog, error)

class ViewPost(Handler):
    def get(self, blog_id):
        blog = Blog.get_by_id(int(blog_id))
        if blog:
            t = jinja_env.get_template("blog.html")
            content = t.render(blog=blog)

        self.response.out.write(content)

            # render_str(self, "blog.html")

        # else:
        #
        #
        # t = jinja_env.get_template('blog.html')
        # content = t.render(blog=blog)

        # self.response.write(content)
            # self.render('blog.html', blog=blog)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<blog_id:\d+>', ViewPost),
], debug=True)
