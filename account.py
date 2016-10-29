import tornado.options
from sql import *


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")


class LoginHandler(BaseHandler):  # Todo Jaccount login
    def get(self):
        self.render('login.html')

    def post(self):
        uid = self.get_argument('username')
        pwd = self.get_argument('password')
        # salt = binascii.hexlify(os.urandom(20)).decode()
        res = check(uid, pwd)
        if res:
            self.set_secure_cookie("username", str(uid))
        self.redirect("/")


class LogoutHandler(BaseHandler):
    def post(self):
        if (self.get_argument("logout", None)):
            self.clear_cookie("username")
        self.redirect("/")


class optionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = tornado.escape.xhtml_escape(self.current_user)
        self.render("option.html")
