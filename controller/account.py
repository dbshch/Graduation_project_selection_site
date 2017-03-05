import tornado.options
from sql import *
import re
import tornado.httpserver
import tornado.ioloop
import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")
    def is_viewed(self, pid):
        viewd = self.get_secure_cookie("vd").decode('UTF-8').split(',')
        if str(pid) in viewd:
            return True
        viewd.append(str(pid))
        viewd = ','.join(viewd)
        self.set_secure_cookie("vd", viewd)
        return False



class LoginHandler(BaseHandler):  # Todo Jaccount login
    def get(self):
        next = self.get_argument('next')
        self.render('login.html', next=next)

    def post(self):
        uid = self.get_argument('username')
        next = self.get_argument('next')
        #self.get_argument('s')

        if not uid.isdigit():
            self.redirect(next)
        else:
            user = userDB(uid)
            pwd = self.get_argument('password')
            # salt = binascii.hexlify(os.urandom(20)).decode()
            res = user.check(pwd)

            if res:
                u_name = user.query()['u_name']
                self.set_secure_cookie("u_name", u_name)
                self.set_secure_cookie("username", str(uid))
                self.set_secure_cookie("vd", '')
            self.redirect(next)

# @TODO, just for dev
class UserRegisterHandler(BaseHandler):
    def get(self):
        self.render('register.html')

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("username")
        self.clear_cookie("u_name")
        self.redirect("/")
    def post(self):
        if (self.get_argument("logout", None)):
            self.clear_cookie("username")
        self.redirect("/")


class optionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = tornado.escape.xhtml_escape(self.current_user)
        user = userDB(uid)
        data = user.query()
        role = data['role']
        self.render("dashboard.html", uid=uid, u_name=self.get_secure_cookie('u_name'), data=data, role=role)

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

class forbiddenHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        u_name = self.get_secure_cookie('u_name').decode('UTF-8')
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        role = userDB(uid).query()['role']
        self.render('403.html', u_name=u_name, role=role)
