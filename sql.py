import mysql.connector
import copy

config = {
    'user': 'root',
    'password': 'chuibi',
    'host': '127.0.0.1',
    'database': 'ipp',
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
    def dataQuery(self, qry):
        self.cursor.execute(qry)
        t = []
        for i in self.cursor:
            t.append(i)
        return t

    def dataInsert(self, insrt):
        self.cursor.execute(insrt)
        self.cnx.commit()


class userDB(dbFunction):
    def __init__(self, uid):
        self.uid = uid
    def check(self, pwd):
        qry = ("SELECT pwd FROM users WHERE id = %s" % self.uid)
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
        return self.dataQuery(("SELECT u_name, role, registed, stat, grouped, group_id FROM users WHERE id = %s" % self.uid))

    def isLeader(self):
        res = self.dataQuery(("SELECT grouped FROM users WHERE id=%d" % int(self.uid)))
        if res[0][0] == "l":
            return True
        return False

    def queryGroup(self):
        qry = self.dataQuery(("SELECT user_id FROM groups WHERE id=%d" % int(self.uid)))
        for (user_id) in qry:
            res = user_id.split(";")
        return res

class projectDB(dbFunction):
    def __init__(self, id):
        self.id = id
    def allProjects(self):
        return = self.dataQuery(("SELECT * FROM projects"))

    def queryProjects(self):
        return self.dataQuery(
            ("SELECT * FROM projects WHERE id = %d" % int(self.id)))


def updateWish(userid, id, seq):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    qry = ("SELECT wish%d FROM projects WHERE id = %d" % (seq, id))
    cursor.execute(qry)
    for (wish) in cursor:
        res = wish
    res = res + userid + ";"
    op = ("UPDATE projects SET wish%d='%s' where id=%d" % (seq, res, id))
    cursor.execute(op)
    cnx.commit()
    cursor.close()
    cnx.close()


def updateUser(uid, res):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    op = ("UPDATE users SET registed='%s' where id=%s" % (res, uid))
    cursor.execute(op)
    cnx.commit()
    cursor.close()
    cnx.close()


def quitProj(userid, id, wish_i):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    qry = ("SELECT wish%d FROM projects WHERE id = %d" % (wish_i, id))
    cursor.execute(qry)
    for (wish) in cursor:
        res = wish
    res = res.split(";").remove('')
    res.remove(userid)
    res = ';'.join(res) + ';'
    op = ("UPDATE projects SET wish%d='%s' where id=%d" % (wish_i, res, id))
    cursor.execute(op)
    cnx.commit()
    cursor.close()
    cnx.close()


def isGrouped(userid):
    res = dataQuery(("SELECT grouped FROM users WHERE id=%d" % userid))
    if res[0][0] == "n":
        return False
    return True





def groupStat(userid):
    res = dataQuery(("SELECT grouped FROM users WHERE id=%d" % userid))
    return res[0][0]


def newUser(userid, u_name, role, pwd):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    op = ("INSERT INTO users VALUES ('%s', '%s', '{1:\'None\',2:\'None\',3:\'None\'}', '%s', 'n,n,n', %d, 'n'" % (
        u_name, role, pwd, int(userid)))
    cursor.execute(op)
    cnx.commit()
    cursor.close()
    cnx.close()


def newProject(title, detial):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    max = cursor.execute("SELECT MAX(id) FROM projects")[0][0]
    op = ("INSERT INTO projects VALUES (%d, '%s', '%s', 'None', 'None', 'None')" % (max + 1, title, detial))
    cursor.execute(op)
    cnx.commit()
    cursor.close()
    cnx.close()


def deleteProject(id):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    op = ("DELETE FROM projects WHERE id=%d" % int(id))
    cursor.execute(op)
    cnx.commit()
    cursor.close()
    cnx.close()


def deleteUser(userid):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    op = ("DELETE FROM users WHERE id=%d" % int(userid))
    cursor.execute(op)
    cnx.commit()
    cursor.close()
    cnx.close()


def allGroups():
    qry = dataQuery(("SELECT * FROM groups"))
    groups = []
    res = {}
    for (id, leader, users, leader_id, user_id, isFull) in qry:
        res['leader'] = leader
        res['id'] = id
        res['users'] = users
        res['leader_id'] = leader_id
        res['user_id'] = user_id
        res['isFull'] = isFull
        groups.append(copy.deepcopy(res))
    return groups



