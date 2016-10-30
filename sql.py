import mysql.connector

config = {
    'user': 'root',
    'password': 'chuibi',
    'host': '127.0.0.1',
    'database': 'ipp',
    'raise_on_warnings': True,
}


def dataQuery(qry):
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute(qry)
    t = []
    for i in cursor:
        t.append(i)
    cursor.close()
    cnx.close()
    return t


def check(uid, pwd):
    qry = ("SELECT pwd FROM users WHERE id = %s" % uid)
    res = dataQuery(qry)
    if res[0]:
        pd = int(res[0][0])
        # pwd = hashlib.new("md5", pwd + salt).hexdigest()
        if int(pwd) == pd:
            return True
    return False


def allProjects():
    qry = dataQuery(("SELECT title, id FROM projects"))
    res = {}
    for (title, id) in qry:
        res[id] = title
    return res


def allUsers():
    qry = dataQuery(("SELECT u_name FROM users"))
    res = []
    for (u_name) in qry:
        res.append(u_name[0])
    return res


def queryUser(uid):
    qry = dataQuery(("SELECT role, registed FROM users WHERE id = '%s'" % uid))
    res = {}
    for (role, registed) in qry:
        res["role"] = role
        res["registed"] = registed
    return res


def queryProjects(id):
    qry = dataQuery(("SELECT title, detail, wish1, wish2, wish3 FROM projects WHERE id = %d" % int(id)))
    res = {}
    for (title, detail, wish1, wish2, wish3) in qry:
        res["title"] = title
        res["detail"] = detail
        res["wish1"] = wish1
        res["wish2"] = wish2
        res["wish3"] = wish3
    return res


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


def isLeader(userid):
    res = dataQuery(("SELECT grouped FROM users WHERE id=%d" % userid))
    if res[0][0] == "l":
        return True
    return False


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
