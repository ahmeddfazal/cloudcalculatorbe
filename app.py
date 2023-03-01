from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL

app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'cloudcomputing'

mysql = MySQL(app)

def createInsertQuery(ipAddress, input, output):
    return "INSERT INTO cloudcomputing.ip_logs (IP, INPUT, OUTPUT, REQUEST_TIME) VALUES ('" + str(ipAddress) + "', '" + str(input) + "', '" + str(output) + "', CURRENT_TIMESTAMP)"

def getRequestCountQuery(ipAddress):
    return "SELECT COUNT(*)%5=0 COUNT FROM cloudcomputing.ip_logs WHERE IP = '" + ipAddress + "'"

@app.route("/", methods=["POST"])
def home():
    requestData = request.json
    ipAddress = requestData["ipAddress"]
    input = requestData["input"]
    cursor = mysql.connection.cursor()
    output = eval(input)
    query = createInsertQuery(ipAddress, input, output)
    cursor.execute(query)
    mysql.connection.commit()

    countQuery = getRequestCountQuery(ipAddress)
    cursor.execute(countQuery)
    isBlocked = cursor.fetchone()[0] == 1

    cursor.close()
    return jsonify(output=output, blocked=isBlocked)