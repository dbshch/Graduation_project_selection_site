import mysql.connector
import copy
from util.env import *

env = get_env()
config = {
    'user': str(env['user']),
    'password': str(env['password']),
    'host': '127.0.0.1',
    'database': str(env['database']),
    'raise_on_warnings': True,
}


class ippDB():
    def __init__(self):
        self.config = config
        self.cnx = mysql.connector.connect(**self.config)
        self.cursor = self.cnx.cursor(dictionary=True)

    def __del__(self):
        self.cursor.close()
        self.cnx.close()


class dbFunction(ippDB):
    def __init(self):
        ippDB.__init__(self)

    def dataQuery(self, qry):
        k=0
        self.cursor.execute(qry)
        t = []
        for i in self.cursor:
            t.append(i)
        return t

    def dataUpdate(self, insrt):
        self.cursor.execute(insrt)
        self.cnx.commit()


class userDB(dbFunction):
    def __init__(self, uid):
        dbFunction.__init__(self)
        self.uid = int(uid)
        res = self.dataQuery(("SELECT u_name, group_id FROM users WHERE id=%d" % self.uid))
        if res:
            self.group_id = int(res[0]['group_id'])
            self.u_name = res[0]['u_name']
        else:
            self.u_name = ''

    def validUser(self):
        if self.u_name:
            return True
        return False

    def check(self, pwd):
        qry = ("SELECT pwd FROM users WHERE id = %d" % self.uid)
        res = self.dataQuery(qry)
        if res:
            pd = res[0]['pwd']
            # pwd = hashlib.new("md5", pwd + salt).hexdigest()
            if pwd == pd:
                return True
        return False

    def allUsers(self):
        return self.dataQuery(("SELECT id, u_name FROM users"))

    def query(self):
        return \
            self.dataQuery(
                ("SELECT u_name, role, registed, stat, grouped, group_id, role, sex, phone, major FROM users WHERE id = %d" % self.uid))[0]

    def isLeader(self):
        res = self.dataQuery(("SELECT grouped FROM users WHERE id=%d" % self.uid))
        if res[0]['grouped'] == "l":
            return True
        return False

    def isGrouped(self):
        res = self.dataQuery(("SELECT grouped FROM users WHERE id=%d" % self.uid))
        if res[0]['grouped'] == 'n':
            return False
        return True

    def groupStat(self):
        res = self.dataQuery(("SELECT grouped FROM users WHERE id=%d" % self.uid))
        return res[0]['grouped']

    def register(self, res):
        old = self.dataQuery(("SELECT registed FROM users WHERE id=%d" % self.uid))[0]['registed']
        old = old.split(',')
        p = []
        for i in range(3):
            if old[i] == 'n':
                p.append(0)
            else:
                p.append(projectDB(old[i]))
        res = res.split(',')
        if self.group_id:
            my_group = groupDB(self.group_id).all_users()
            for member in my_group:
                mem = userDB(member)
                mem.register_helper(res, old)
            for i in range(3):
                if old[i] == res[i]:
                    continue
                if res[i] != 'n':
                    p[i] = projectDB(res[i])
                    p[i].newWish(self.group_id, i + 1)
        else:
            self.register_helper(res, old)
            for i in range(3):
                if old[i] == res[i]:
                    continue
                if res[i] != 'n':
                    p[i] = projectDB(res[i])
                    p[i].newWish(self.uid, i + 1)

    def register_helper(self, res, old):
        stat = self.query()['stat'].split(',')
        for i in range(3):
            if old[i] == res[i]:
                continue
            if old[i] != 'n':
                self.quitProj(old[i], i + 1)
                stat[i] = str(0)
            if res[i] != 'n':
                stat[i] = str(1)
        res = ','.join(res)
        stat = ','.join(stat)
        op = ("UPDATE users SET registed='%s', stat='%s' where id=%s" % (res, stat, self.uid))
        self.dataUpdate(op)

    def newUser(self, u_name, role, pwd):
        self.u_name = u_name
        self.group_id = 0
        op = ("INSERT INTO users VALUES ('%s', '%s', 'n,n,n', '%s', 'n,n,n', %d, 'n', 0)" % (
            u_name, role, pwd, self.uid))
        self.dataUpdate(op)

    def deleteUser(self):
        op = ("DELETE FROM users WHERE id=%d" % self.uid)
        self.dataUpdate(op)

    def quitProj(self, id, wish_i):
        wish_i = int(wish_i)
        id = int(id)
        qry = ("SELECT wish%d FROM projects WHERE id = %d" % (wish_i, id))
        res = self.dataQuery(qry)[0]['wish%d' % wish_i]
        res = res.split(",")
        gid = str(self.group_id)
        if self.group_id:
            if gid in res:
                res.remove(gid)
        else:
            res.remove(str(self.uid))
        res = ','.join(res)
        op = ("UPDATE projects SET wish%d='%s' where id=%d" % (wish_i, res, id))
        self.dataUpdate(op)

    def joinGroup(self, id):
        qry = self.dataQuery(("SELECT users, user_id FROM groups WHERE id=%d" % id))[0]
        users = qry['users'].split(',')
        ids = qry['user_id'].split(',')
        ids.append(str(self.uid))
        users.append(self.u_name)
        ids = ','.join(ids)
        users = ','.join(users)
        op = ("UPDATE groups SET users='%s', user_id='%s' WHERE id=%d" % (users, ids, id))
        self.dataUpdate(op)
        op = ("UPDATE users SET group_id=%d, grouped='y' WHERE id=%d" % (id, self.uid))
        self.dataUpdate(op)
        leader = self.dataQuery("SELECT leader_id FROM groups WHERE id=%d" % id)[0]['leader_id']
        res = self.dataQuery("SELECT registed FROM users WHERE id=%d" % leader)[0]['registed']
        self.register(res)

    def quitGroup(self):
        qry = self.dataQuery(("SELECT users, user_id FROM groups WHERE id=%d" % self.group_id))[0]
        users = qry['users'].split(',')
        ids = qry['user_id'].split(',')
        ids.remove(str(self.uid))
        users.remove(self.u_name)
        ids = ','.join(ids)
        users = ','.join(users)
        op = ("UPDATE groups SET users='%s', user_id='%s' WHERE id=%d" % (users, ids, self.group_id))
        self.dataUpdate(op)
        op = ("UPDATE users SET grouped='n', group_id=0 WHERE id=%d" % self.uid)
        self.dataUpdate(op)

    def leaderQuit(self):
        gid = self.query()['group_id']
        op = ("DELETE FROM groups WHERE id=%d" % gid)
        self.dataUpdate(op)
        op = ("UPDATE users SET grouped='n', group_id=0 WHERE id=%d" % self.uid)
        self.dataUpdate(op)

    def createGroup(self):
        new_group = groupDB().newGroup(self)
        self.group_id = new_group.id
        self.dataUpdate(("UPDATE users SET group_id=%d WHERE id=%d" % (self.group_id, self.uid)))


class groupDB(dbFunction):
    def __init__(self, id=0):
        dbFunction.__init__(self)
        if id == 0:
            max = self.dataQuery(("SELECT MAX(id) FROM groups"))[0]['MAX(id)']
            if max:
                self.id = max + 1
            else:
                self.id = 1
        else:
            self.id = int(id)

    def allGroups(self):
        return self.dataQuery(("SELECT * FROM groups"))

    def all_users(self):
        res = [self.dataQuery(("SELECT leader_id FROM groups WHERE id=%d" % self.id))[0]['leader_id']]
        for i in self.dataQuery(("SELECT user_id FROM groups WHERE id=%d" % self.id))[0]['user_id'].split(','):
            res.append(i)
        return res

    def members(self):
        qry = self.dataQuery(("SELECT user_id FROM groups WHERE id=%d" % self.id))[0]['user_id']
        res = qry.split(',')
        return res

    def leader(self):
        return self.dataQuery(("SELECT leader_id FROM groups WHERE id=%d" % self.id))[0]['leader_id']

    def leaderName(self):
        return self.dataQuery(("SELECT leader FROM groups WHERE id=%d" % self.id))[0]['leader']

    def memberName(self):
        return self.dataQuery(("SELECT users FROM groups WHERE id=%d" % self.id))[0]['users']

    def newGroup(self, user):
        op = ("INSERT INTO groups VALUES (%d, '%s', '', %d, '', '0')" % (self.id, user.u_name, user.uid))
        self.dataUpdate(op)

    def deleteMember(self, uid):
        op = ("UPDATE groups SET users")
        self.dataUpdate(op)


class projectDB(dbFunction):
    def __init__(self, id=0):
        dbFunction.__init__(self)
        if id == 0:
            max = self.dataQuery(("SELECT MAX(id) FROM projects"))[0]['MAX(id)']
            self.id = max + 1
        else:
            self.id = int(id)

    def allProjects(self):
        return self.dataQuery(("SELECT * FROM projects"))

    def view(self):
        viewed = int(self.query()['views']) + 1
        op = ("UPDATE projects SET views=%d WHERE id=%d" % (viewed, self.id))
        self.dataUpdate(op)

    def query(self):
        return self.dataQuery(
            ("SELECT * FROM projects WHERE id = %d" % self.id))[0]

    def newWish(self, userid, seq):
        qry = ("SELECT wish%d FROM projects WHERE id = %d" % (seq, self.id))
        res = self.dataQuery(qry)[0]['wish%d' % seq]
        if res:
            res += ','
            res = res + str(userid)
        else:
            res = str(userid)
        op = ("UPDATE projects SET wish%d='%s' where id=%d" % (seq, res, self.id))
        self.dataUpdate(op)

    def newProject(self, title, detail, img, sponsor=''):
        op = (
            "INSERT INTO projects VALUES (%d, '%s', '%s', '%s', '%s', '', '', '')" % (
                self.id, title, img, sponsor, detail))
        self.dataUpdate(op)

    def deleteProject(self):
        qry = self.query()
        for i in range(1,4):
            user = qry['wish' + str(i)]
            if user:
                db = userDB(user)
                if not db.validUser():
                    db = userDB(groupDB(user).leader())
                registed = db.query()['registed'].split(',')
                registed[i - 1] = 'n'
                db.register(','.join(registed))
        op = ("DELETE FROM projects WHERE id=%d" % self.id)
        self.dataUpdate(op)