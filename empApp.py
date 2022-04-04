from flask import Flask, render_template, request, redirect
from pymysql import connections
import os
import boto3
import os.path
from config import *


app = Flask(__name__, template_folder='awsWebsite')

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'Employee'

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/addEmp")
def home():
    return render_template('addEmp.html')

@app.route("/displayEmp")
def displayEmp():
    cursor = db_conn.cursor()
    cursor.execute("SELECT * from employee")
    data = cursor.fetchall()
    return render_template('displayEmp.html', data=data)

@app.route("/addLeave")
def home():
    return render_template('addLeave.html')

@app.route("/disPayroll")
def home():
    return render_template('disPayroll.html')


@app.route("/addEmp", methods=['POST'])
def AddEmp():
    empID = request.form['empID']
    fName = request.form['fName']
    lName = request.form['lName']
    position = request.form['position']
    payscale = request.form['payscale']
    hireDate = request.form['hDate']
    
    emp_image_file = request.files['empImage']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (empID, fName, lName, position, payscale, hireDate))
        db_conn.commit()
        emp_name = "" + fName + " " + lName 
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(empID) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


