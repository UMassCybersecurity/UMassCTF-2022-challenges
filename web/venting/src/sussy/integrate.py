import sqlite3 as sql
import re
#will figure out flag + sanitizing later
#flag = ""
def sanitize(query):
    r = re.compile(r"-",re.IGNORECASE)
    query = re.sub(r,"ඞ",str(query))
    return query
def validate(username,password):
    con = sql.connect("data.db")
    cur = con.cursor()
    statement = f"SELECT * from users WHERE username='" + sanitize(username) + "' AND Password = '" + sanitize(password) +"';"
    try:
        cur.execute(statement)
        if not cur.fetchone():  
            return "Invalid login"
        else:
            return "If you're getting this you're not me. You'll never log in! ALSO I DIDNT HIDE ANYTHING IN MY PASSWORD SO DONT TRY!",200
    except sql.Error as er:
        return ''.join("Error when executing statement -> " + str(er) + " " + statement),500
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   