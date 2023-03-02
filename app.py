from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL
from waitress import serve
import math

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

def getLogsOfIPQuery(ipAddress):
    return "SELECT SR_IP, IP, INPUT, OUTPUT, REQUEST_TIME,CASE	WHEN SR_IP%5 = 0 THEN 'BLOCKED'	ELSE 'OPEN'END AS BLOCKED FROM(	SELECT	*,	ROW_NUMBER() OVER(PARTITION BY IP ORDER BY REQUEST_TIME) SR_IP	FROM cloudcomputing.IP_LOGS) A WHERE IP='"+ipAddress+"' ORDER BY REQUEST_TIME DESC" 

@app.route("/", methods=["POST"])
def home():
    requestData = request.json
    ipAddress = requestData["ipAddress"]
    input = requestData["input"]
    cursor = mysql.connection.cursor()
    output = round(eval(input),10)
    query = createInsertQuery(ipAddress, input, output)
    cursor.execute(query)
    mysql.connection.commit()

    countQuery = getRequestCountQuery(ipAddress)
    cursor.execute(countQuery)
    isBlocked = cursor.fetchone()[0] == 1

    cursor.close()
    return jsonify(output=output, blocked=isBlocked)

@app.route("/<ipAddress>", methods=["GET"])
def fetchLogsOfIpAddress(ipAddress):
    print(ipAddress)
    cursor = mysql.connection.cursor()
    query = getLogsOfIPQuery(ipAddress)
    cursor.execute(query)
    logs = cursor.fetchall()
    cursor.close()
    return jsonify(logs)

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=3000)