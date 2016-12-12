# coding=UTF-8
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define, options
from sql import *
import func
import os
import pyxlsx
from account import *

define("port", default=8080, help="run on the given port", type=int)


class WelcomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        projs = projectDB().allProjects()
        role = userDB(uid).query()['role']
        self.render('index.html', u_name=u_name, projs=projs, role=role)
        # TODO: the sort and filter functions; The way to show brief view of projects


class detailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        proj = projectDB(id).query()
        proj['detail'] = proj['detail'].split('\n')
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        res = userDB(uid).query()
        isIn = id in res['registed']
        role = res['role']
        self.render("detail.html", i=id, proj=proj, u_name=self.get_secure_cookie('u_name'), isIn=isIn, role=role)
        # TODO quit and register button


class registerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):  # The register page
        new = self.get_argument("item")  # the new project to be chosen
        new = new.split(";")
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        self.render("register.html", new=new, role=role)

    @tornado.web.authenticated
    def post(self):  # Post the result of chosen project
        res = self.get_argument("res")
        pref = int(self.get_argument("pref"))
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        user = userDB(uid)
        data = user.query()
        if data['grouped'] == 'y':
            self.write('You need to ask team leader to register the project')
        else:
            data = data['registed'].split(',')
            data[pref] = res
            data = ','.join(data)
            user.register(data)
            self.write('success')


class quitProj(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        id = int(self.get_argument("id"))
        user = userDB(uid)
        res = user.query()
        if res['grouped']=='y':
            self.write('You need to ask team leader to quit the project')
        else:
            registed = res['registed'].split(',')
            if str(id) in registed:
                registed[registed.index(str(id))] = 'n'
                user.register(','.join(registed))
                self.write("success")
            else:
                self.write("You havn't registered the project")


class registedHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        user = userDB(uid)
        res = user.query()
        role = res['role']
        u_name = user.u_name
        registed = res['registed'].split(',')
        statstr = []
        projid=[]
        stat = res['stat'].split(',')
        for i in range(3):
            if registed[i]=='n':
                registed[i] = 'None'
                projid.append(0)
            else:
                proj = projectDB(int(registed[i])).query()
                registed[i] = proj['title']
                projid.append(proj['id'])
            if int(stat[i]) == 0:
                statstr.append('Not chosen yet')
            if int(stat[i]) == 1:
                statstr.append('Need verified by instructor')
            if int(stat[i]) == 2:
                statstr.append('Succeed')
            stat[i] = int(stat[i])
        if role=='admin':
            self.render('403.html', u_name=u_name, role=role)
        else:
            self.render("registed.html", registed=registed, u_name=u_name,
                    stat=stat, role=role, statstr=statstr, projid=projid)


class joinGroupHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        user = userDB(uid)
        u_name = user.u_name
        res = user.query()
        stat = res['grouped']
        role = res['role']
        res = user.allUsers()
        stat = user.groupStat()
        groups = groupDB().allGroups()
        l = len(groups)
        self.render("groups.html", stat=stat, users=res, u_name=u_name, groups=groups, l=l, role=role)

    @tornado.web.authenticated
    def post(self):
        pass


class forbiddenHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        self.render('403.html', u_name=u_name, role=role)

class exportHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role=='stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            self.render('export.html', u_name=u_name, role=role)

    @tornado.web.authenticated
    def post(self):
        data = []
        output = self.get_argument('output')
        if not output:
            self.write("no file name")
            return
        if '/' in output:
            self.write("illegal file name")
            return
        res = projectDB().allProjects()
        for i in range(len(res)):
            all_grp = []
            for k in range(3):
                w_group = []
                groups = res[i]['wish' + str(k+1)].split(',')
                for group in groups:
                    if not group:
                        w_group.append([])
                        continue
                    g_usr = []
                    #print(group)
                    if int(group)>100:
                        g_usr.append("%s %s" % (group, userDB(group).query()['u_name']))
                    else:
                        ids = groupDB(group).all_users()
                        for id in ids:
                            g_usr.append("%s %s" % (id, userDB(id).query()['u_name']))
                    w_group.append(g_usr)
                all_grp.append(w_group)
            data.append({"i":i+1,'title':res[i]['title'],'groups':all_grp})
        if '.' in output:
            pyxlsx.export(data, "exported/%s" % output)
            self.redirect('/exported/%s' % output)
        else:
            pyxlsx.export(data, "exported/%s.xlsx" % output)
            self.redirect('/exported/%s.xlsx' % output)


class createProjectHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            self.render('create_project.html', u_name=u_name, role=role)

    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            title = self.get_argument("title")
            detail = self.get_argument("detail")
            img = "img2.jpg"
            projectDB().newProject(title, detail, img)
            self.write("success")


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
        (r"/export", exportHandler),  # for exporting the choosing data
        (r"/forbbiden", forbiddenHandler),
        (r"/createproject", createProjectHandler)
        # ----------------------------------------
        # If in DEVELOP and want simple static file handler (without nginx), uncomment them
        #(r'/bower_components/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "bower_components")}),
        #(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "static")})
        # ----------------------------------------
    ], debug=True, **settings)
    # Todo The create project page
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
