import tornado.httpserver
import tornado.ioloop
import tornado.web
from controller.account import *
import time
import os
from util.env import *

env = get_env()
base_url = env['domain'] and env['domain'] or 'http://localhost'
if env['port']:
    base_url += ':' + str(env['port'])

class createProjectHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        pid = self.get_argument('id', default='')
        if pid:
            project = projectDB(int(pid)).query()
            title = project['title']
            detail = project['detail']
            isedit = "true"
        else:
            project = {'instructor': '', 'sponsor': '', 'major': ''}
            title = ''
            detail = ''
            isedit = 'false'
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            self.render('create_project.html', u_name=u_name, proj=project, role=role, title=title, detail=detail, isedit=isedit, pid=pid, baseurl=base_url)

    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            pic_name = self.get_secure_cookie('pic_name')
            if pic_name:
                pic_name = pic_name.decode('UTF-8')
            else:
                pic_name = ''
            isedit = self.get_argument("isedit")
            if not pic_name and isedit == "false":
                self.finish('Upload error')
            title = self.get_argument("title")
            detail = self.get_argument("detail")
            sponsor = self.get_argument("sponsor")
            instructor = self.get_argument("instructor")
            major = self.get_argument('major')
            detail = detail.replace("'", "''")
            sponsor = sponsor.replace("'", "''")
            instructor = instructor.replace("'", "''")
            major = major.replace("'", "''")
            img = pic_name
            if isedit == "false":
                projectDB().newProject(title, detail, img, sponsor, major, instructor)
            else:
                pid = self.get_argument("pid")
                projectDB(pid).editProject(title, detail, img, sponsor, instructor, major)
            self.clear_cookie("pic_name")
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
        self.render("detail.html", i=id, proj=proj, u_name=self.get_secure_cookie('u_name'), isIn=isIn, role=role, baseurl=base_url)


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
        projs = projectDB().allProjects()
        for proj in projs:
            proj['all'] = []
            for i in range(3):
                grp = []
                indiv = []
                stus = proj['wish' + str(i + 1)].split(',')
                for member in stus:
                    if not member:
                        continue
                    inf = userDB(int(member)).query()
                    if inf['grouped'] == 'n':
                        indiv.append(inf['u_name'])
                        proj['all'].append(inf['u_name'])
                    elif inf['grouped'] == 'y':
                        tmp = groupDB(int(inf['group_id'])).all_users()
                        tp = []
                        for usr in tmp:
                            uname = userDB(int(usr)).query()['u_name']
                            tp.append(uname)
                            proj['all'].append(uname)
                        grp.append(','.join(tp))
                proj['grpwish' + str(i + 1)] = grp
                proj['indivwish' + str(i + 1)] = indiv

        if role == 'stu':
            self.render('403.html', u_name=u_name, role=role)
        else:
            self.render('assign_projects.html', u_name=u_name, role=role, projs=projs)

    @tornado.web.authenticated
    def post(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        if role == 'stu':
            self.write("not authorized")
