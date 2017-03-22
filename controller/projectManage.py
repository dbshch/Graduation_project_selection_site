import tornado.httpserver
import tornado.ioloop
import tornado.web
from controller.account import *
import time
import os

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
            pic_name = self.get_secure_cookie('pic_name').decode('UTF-8')
            if not pic_name:
                self.finish('Upload error')
            title = self.get_argument("title")
            detail = self.get_argument("detail")
            img = pic_name
            projectDB().newProject(title, detail, img)
            self.write("success")

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

class registerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):  # The register page
        new = self.get_argument("item")  # the new project to be chosen
        new = new.split(",")
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

class detailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        proj = projectDB(id)
        if not self.is_viewed(id):

            proj.view()
        proj = proj.query()
        proj['detail'] = proj['detail'].split('\n')
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        res = userDB(uid).query()
        isIn = id in res['registed']
        role = res['role']
        self.render("detail.html", i=id, proj=proj, u_name=self.get_secure_cookie('u_name'), isIn=isIn, role=role)


class uploadPicHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            if self.request.files:
                myfile = self.request.files['myfile'][0]
                postfix = ''
                fname = myfile['filename']
                if fname.find('.') > -1:
                    postfix = fname.split('.')[-1]
                fileName = str(time.time()) + '.' + postfix
                absPath = os.path.dirname(os.path.abspath("img"))
                fin = open(absPath + "/img/" + fileName, "wb")
                fin.write(myfile["body"])
                fin.close()
            self.set_secure_cookie("pic_name", fileName)
            self.finish(fileName)

class deleteProjHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            pid = int(self.get_argument('id'))
            proj = projectDB(pid)
            proj.deleteProject()
            self.write('success')

class assignProjHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            self.render('assign_projects.html', u_name=u_name, role=role)