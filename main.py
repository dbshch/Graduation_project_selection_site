#!/usr/bin/python3

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define, options
from sql import *
import util.func
import os
from util.pyxlsx import *
from controller.account import *
from controller.groupManage import *
from controller.projectManage import *
from util.env import *

env = get_env()
define("port", default=int(env['port']), help="run on the given port", type=int)

class WelcomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        projs = projectDB().allProjects()
        role = userDB(uid).query()['role']
        sort = self.get_argument('sort', default='')
        name = self.get_argument('name', default='')
        i = 0
        if name == 'fchoice':
            i = 1
        elif name == 'schoice':
            i = 2
        elif name == 'tchoice':
            i = 3
        if i:
            for seq in range(len(projs)):
                projs[seq]['blabla'] = len(projs[seq]['wish%d' % i].split(','))
        if sort:
            if i:
                projs = sorted(projs, key=lambda proj: proj['blabla'])
            else:
                projs = sorted(projs, key=lambda proj: proj[name])
            if sort == 'down':
                projs.reverse()
        for proj in projs:
            for i in range(3):
                k = 0
                for mem in proj['wish%d' % (i + 1)].split(','):
                    if not mem:
                        continue
                    if userDB(int(mem)).isLeader():
                        k += 1
                proj['chosen_num%d' % (i + 1)] = k
        self.render('index.html', u_name=u_name, projs=projs, role=role, sort=sort, flt='')


class filterHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, flt):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        projs = projectDB().allProjects()
        for proj in projs:
            for i in range(3):
                k = 0
                for mem in proj['wish%d' % (i + 1)].split(','):
                    if not mem:
                        continue
                    if userDB(int(mem)).isLeader():
                        k += 1
                proj['chosen_num%d' % (i + 1)] = k
        if flt != 'other':
            projs = filter(lambda proj: proj['major'].lower() == flt, projs)
        else:
            projs = filter(lambda proj: proj['major'].lower() != 'me', projs)
            projs = filter(lambda proj: proj['major'].lower() != 'ece', projs)
        role = userDB(uid).query()['role']
        sort = self.get_argument('sort', default='')
        name = self.get_argument('name', default='')
        i = 0
        if name == 'fchoice':
            i = 1
        elif name == 'schoice':
            i = 2
        elif name == 'tchoice':
            i = 3
        if i:
            for seq in range(len(projs)):
                projs[seq]['blabla'] = len(projs[seq]['wish%d' % i].split(','))
        if sort:
            if i:
                projs = sorted(projs, key=lambda proj: proj['blabla'])
            else:
                projs = sorted(projs, key=lambda proj: proj[name])
            if sort == 'down':
                projs.reverse()
        self.render('index.html', u_name=u_name, projs=projs, role=role, sort=sort, flt=flt)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "login_url": "/login",
        "ui_methods": util.func
    }
    application = tornado.web.Application([
        (r'/', WelcomeHandler),  # the home page
        (r'/login', LoginHandler),
        (r'/logout', LogoutHandler),
        (r"/proj/([0-9]+)", detailHandler),  # The detail of the projects
        (r"/registed", registedHandler),  # for students to view their projects
        (r"/register", registerHandler),  # for students to regist projects
        (r"/userregister", UserRegisterHandler),
        (r"/quit", quitProj),  # for students to quit projects
        (r"/joinGroup", joinGroupHandler),  # for team leader to set groups
        (r"/option", optionHandler),  # for viewing the account status
        (r"/export", exportHandler),  # for exporting the choosing data
        (r"/forbbiden", forbiddenHandler),
        (r"/createproject", createProjectHandler),
        (r"/uploadPic", uploadPicHandler),
        (r"/deleteProj", deleteProjHandler),
        (r"/assign", assignProjHandler),
        (r"/member/([0-9]+)", memberHandler),
        (r"/filter/([a-z]+)", filterHandler),
        (r"/jalogin", jaloginHandler),
        (r"/jacode", jacodeHandler),
        (r'/bower_components/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "bower_components")}),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "static")}),
        (r'/img/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "img")}),
        (r'/exported/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "exported")})
    ], debug=True, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
