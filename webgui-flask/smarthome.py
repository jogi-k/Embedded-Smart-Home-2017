from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from tiles import SimpleTile, TileManager
from helper import PageContext

import sqlite3
from flask import g


app = Flask(__name__)
Bootstrap(app)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

DATABASE = "sample_database.sqlite"


def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False ):
    cur = get_db().execute(query,args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g,'_database',None)
    if db is not None:
        db.close()




@app.route('/')
def main():
    temp = query_db("SELECT wert,einheit FROM sensoren ORDER BY zeit DESC", one=True)
    print(temp)



    tiles = [
        SimpleTile("Licht", "#EEEE00", "light/"),
        SimpleTile("Heizung", "#FF0000", "heaters/"),
        SimpleTile("Sicherheit", "#30FF00", "security/"),
        SimpleTile("Wasser", "#0000FF", "water/"),
        SimpleTile("Innentemperatur : " + temp[0] + " " + temp[1], "#0000FF", "tempchart/"),
        SimpleTile("Humidity", "#FF0000", "/"),
        SimpleTile("Extrapunkt 3", "#A0FFA0", "/"),
        SimpleTile("Extrapunkt 4", "#00A0FF", "/"),
    ]

    manager = TileManager(tiles)
    context = PageContext("Smarthome Projekt", "Home")
    return render_template("main.html", tilerows=manager, context=context)

@app.route('/light/')
def light():
    living_room = True
    sleeping_room = False

    if("living_room" in request.args):
        living_room = True if request.args["living_room"] == "on" else False

    if("sleeping_room" in request.args):
        sleeping_room = True if request.args["sleeping_room"] == "on" else False

    tiles=[]

    tile = SimpleTile("Wohnzimmer: ", "", "?living_room=")
    tile.items[0].text += "an" if living_room else "aus"
    tile.link += "off" if living_room else "on"
    tile.bg = "#AAFF00" if living_room else "#338800"
    tiles.append(tile)

    tile = SimpleTile("Schlafzimmer: ", "", "?sleeping_room=")
    tile.items[0].text += "an" if sleeping_room else "aus"
    tile.link += "off" if sleeping_room else "on"
    tile.bg = "#6666BB" if sleeping_room else "#333388"
    tiles.append(tile)

    manager = TileManager(tiles)
    context = PageContext("Smarthome Projekt", "Licht", [["/", "Home"]])
    return render_template("main.html", tilerows=manager, context=context)


@app.route('/tempchart/')
def tempchart():
    context = PageContext("Smarthome-Projekt-Temperaturkurve","Temperatur", [["/", "Home"]])
    temp = query_db("SELECT wert,zeit FROM sensoren WHERE name='temp'")
    print(temp)
    tempvalues = []
    temptimes = []

    for singlevalues in temp:
        tempvalues.append(singlevalues[0])
        temptimes.append(singlevalues[1])

    return render_template("linechart.html", values=tempvalues, times= temptimes, context = context)

if __name__ == "__main__":
    app.run(debug=True)