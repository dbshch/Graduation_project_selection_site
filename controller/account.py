import tornado.options
from sql import *
import re
import tornado.httpserver
import tornado.ioloop
import tornado.web
import urllib
import urllib.request
import urllib.parse
import json
from util.env import *

env = get_env()
base_url = env['domain'] and env['domain'] or 'http://localhost'
if env['port']:
    base_url += ':' + str(env['port'])


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


class LoginHandler(BaseHandler):
    def get(self):
        next = self.get_argument('next')
        self.render('login.html', next=next)

        # def post(self):
        #     uid = self.get_argument('username')
        #     next = self.get_argument('next')
        #     #self.get_argument('s')
        #
        #     if not uid.isdigit():
        #         self.redirect(next)
        #     else:
        #         user = userDB(uid)
        #         pwd = self.get_argument('password')
        #         # salt = binascii.hexlify(os.urandom(20)).decode()
        #         res = user.check(pwd)
        #
        #         if res:
        #             u_name = user.query()['u_name']
        #             self.set_secure_cookie("u_name", u_name)
        #             self.set_secure_cookie("username", str(uid))
        #             self.set_secure_cookie("vd", '')
        #         self.redirect(next)


class UserRegisterHandler(BaseHandler):
    def get(self):
        self.render('register.html')

    def post(self):
        major = self.get_argument('major')
        phone = self.get_argument('phone')
        if not phone.isdigit():
            self.redirect('/userregister')
            return
        u_name = self.get_secure_cookie('u_name_t').decode('UTF-8')
        uid = self.get_secure_cookie('username_t').decode('UTF-8')
        role = self.get_secure_cookie('role').decode('UTF-8')
        gender = self.get_secure_cookie('gender').decode('UTF-8')
        userDB(uid).newUser(u_name, role, 123, phone, major, gender)
        self.set_secure_cookie("u_name", u_name)
        self.set_secure_cookie("username", str(uid))
        self.set_secure_cookie("vd", '')
        self.redirect('/')


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
        projid = []
        stat = res['stat'].split(',')
        for i in range(3):
            if registed[i] == 'n':
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
        if role == 'admin':
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


class memberHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        uid = id
        user = userDB(uid)
        data = user.query()
        role = data['role']
        self.render("memberProfile.html", uid=id, data=data, u_name=self.get_secure_cookie('u_name'), role=role)


class jaloginHandler(BaseHandler):
    def get(self):
        self.redirect(
            "https://jaccount.sjtu.edu.cn/oauth2/authorize?response_type=code&client_id=htAZFp7DCwnd1A9q4yDwbyWX&redirect_uri=" + base_url + "/jacode")


class jacodeHandler(BaseHandler):
    def get(self):
        code = self.get_argument("code")
        url = "https://jaccount.sjtu.edu.cn/oauth2/token"
        postdata = urllib.parse.urlencode({
            "client_id": "htAZFp7DCwnd1A9q4yDwbyWX",
            "client_secret": "9EADF115A76B760B16089708D06D6BF2EC08CE2C5E613D9B",
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": base_url + "/jacode"
        }).encode('utf-8')
        header = {
            "Host": "jaccount.sjtu.edu.cn",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache"
        }
        req = urllib.request.Request(url, postdata, header)
        respond = urllib.request.urlopen(req, timeout=3)
        if respond.status != 200:
            self.write(respond.status)
            return
        res = respond.read().decode('utf-8')
        data = json.loads(res)
        access_token = data['access_token']
        inform = urllib.request.urlopen(
            'https://api.sjtu.edu.cn/v1/me/profile?access_token=%s' % access_token).read().decode('utf8')
        inform = json.loads(inform)
        name = inform['entities'][0]['name']
        id = inform['entities'][0]['code']
        role = inform['entities'][0]['userType']
        gender = inform['entities'][0]['gender']
        if userDB(id).validUser():
            self.set_secure_cookie("u_name", name)
            self.set_secure_cookie("username", str(id))
            self.set_secure_cookie("vd", '')
            self.redirect("/")
        else:
            self.set_secure_cookie("u_name_t", name)
            self.set_secure_cookie("username_t", str(id))
            if role == 'student':
                role = 'stu'
            else:
                role = 'admin'
            self.set_secure_cookie("role", role)
            self.set_secure_cookie("gender", gender)
            self.redirect("userregister")
