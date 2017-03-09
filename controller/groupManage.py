import tornado.httpserver
import tornado.ioloop
import tornado.web
from controller.account import *

class joinGroupHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        user = userDB(uid)
        u_name = user.u_name
        res = user.query()
        stat = res['grouped']
        gid = res['group_id']
        role = res['role']
        res = user.allUsers()
        stat = user.groupStat()
        groups = groupDB().allGroups()
        l = len(groups)
        self.render("groups.html", stat=stat, gid=gid, users=res, u_name=u_name, groups=groups, l=l, role=role)

    @tornado.web.authenticated
    def post(self):
        method = self.get_argument('method')
        uid = int(tornado.escape.xhtml_escape(self.current_user))
        user = userDB(uid)
        if user.isLeader():
            self.write("Sorry you are the leader and you can't join or quit the group")
            return
        if method == 'join':
            groupID = int(self.get_argument('gid'))
            print(groupID)
            user.joinGroup(groupID)
            self.write('success')
        else:
            user.quitGroup()
            self.write('success')