import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define, options
from sql import *
import func
import os
from account import *

define("port", default=8080, help="run on the given port", type=int)


class WelcomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        projs = allProjects()
        role = queryUser(uid)['role']
        self.render('index.html', user=u_name, projs=projs, role=role)
        # TODO: the sort and filter functions; The way to show brief view of projects


class detailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        proj = queryProjects(id)
        proj['detail'] = proj['detail'].split('\n')
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        isIn = id in queryUser(uid)['registed']
        role = queryUser(uid)['role']
        self.render("detail.html", i=id, proj=proj, u_name=self.get_secure_cookie('u_name'), isIn=isIn, role=role)
        # TODO quit and register button


class registerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self): # The register page
        new = self.get_argument("item") # the new project to be chosen
        new = new.split(";")
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = queryUser(uid)['role']
        self.render("register.html", new=new, role=role)

    @tornado.web.authenticated
    def post(self): # Post the result of chosen project
        res = self.get_argument("result")
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        group_stat = queryUser(uid)
        if (group_stat['grouped'] == 'l'):
            group_member = queryGroup(int(group_stat['group_id']))
            for m in group_member:
                updateUser(int(m), res)
        updateUser(uid, res)
        self.write('success')


class quitProj(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        id = int(self.get_argument("id"))
        wish_i = int(self.get_argument("wish_i"))
        quitProj(uid, id, wish_i)



class registedHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        res = queryUser(uid)
        role = queryUser(uid)['role']
        self.render("registed.html", registed=res['registed'], u_name=self.get_secure_cookie("u_name"), stat=res['stat'], role=role)


class joinGroupHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        res = queryUser(uid)
        stat = res['grouped']
        role = res['role']
        res = allUsers()
        stat = groupStat(uid)
        groups = allGroups()
        l = len(groups)
        self.render("groups.html", stat=stat, users=res, u_name=u_name, groups=groups, l=l, role=role)
    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        res = allUsers()
        stat = groupStat(uid)
        self.render("groups.html", users=res, u_name=u_name)




if __name__ == "__main__":
    tornado.options.parse_command_line()
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "login_url": "/login",
        "ui_methods": func
    }
    application = tornado.web.Application([
        (r'/', WelcomeHandler),  # the home page
        (r'/login', LoginHandler),
        (r'/logout', LogoutHandler),
        (r"/proj/([0-9]+)", detailHandler),  # The detail of the projects
        (r"/registed", registedHandler),  # for students to view their projects
        (r"/register", registerHandler),  # for students to regist projects
        (r"/quit", quitProj),  # for students to quit projects
        (r"/joinGroup", joinGroupHandler),  # for team leader to set groups
        (r"/option", optionHandler),  # for viewing the account status
    ], debug=True, **settings)
    # Todo The admin pages
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
