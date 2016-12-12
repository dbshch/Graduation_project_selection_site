# coding=UTF-8
import tornado.options
from sql import *
import re


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")


class LoginHandler(BaseHandler):  # Todo Jaccount login
    def get(self):
        next = self.get_argument('next')
        self.render('login.html', next=next)

    def post(self):
        uid = self.get_argument('username')
        next = self.get_argument('next')
        self.get_argument('s')

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
            self.redirect(next)


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
