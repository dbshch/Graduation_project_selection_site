import mysql.connector
import copy
import hashlib
import os
import binascii

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
    print(res[0][0])
    print(pwd)
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
    if res[0][0]=="n":
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
#TODO: The insert functions