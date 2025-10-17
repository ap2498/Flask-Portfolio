from flask import Flask, render_template, request, redirect, url_for,session, jsonify
import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()
app=Flask(__name__)
app.secret_key=os.getenv("FLASK_SECRET_KEY")
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route("/",methods=['GET'])
def landing_page():
    return render_template("entry.html")
@app.route('/load_home_page',methods=['GET'])
def load_home_page():
    return render_template('home.html')
@app.route('/load_single_project',methods=['GET'])
def load_single_project():
    return render_template('single_project.html')
@app.route('/load_create_project',methods=["GET"])
def load_create_project():
    return render_template('create.html')

@app.route("/create_db",methods=['POST'])
def create_db():
    conn=sqlite3.connect("flask_portfolio.db")
    cursor=conn.cursor()
    cursor.execute('''
CREATE TABLE if not exists categories(
                   id INTEGER PRIMARY KEY,
                   name VARCHAR(255),
                   value VARCHAR(255))
''')
    conn.commit()
    cursor.execute('''CREATE TABLE if not exists projects(
                   id INTEGER PRIMARY KEY,
                   title TEXT,
                   description TEXT,
                   technology TEXT,
                   url VARCHAR(255),
                   cover VARCHAR(255),
                   client VARCHAR(255),
                   category_id INTEGER,
                   FOREIGN KEY (category_id) REFERENCES categories(id)
                   )''')
    conn.commit()
    cursor.execute('''CREATE TABLE if not exists project_images(
                   id INTEGER PRIMARY KEY,
                   picture VARCHAR(255),
                   project_id INTEGER,
                   FOREIGN KEY(project_id) REFERENCES projects(id)
                   )''')
    conn.commit()
    return jsonify({
        "status":200,
        'message':"DB created Succesfully"
    })
@app.route("/create_project",methods=['POST'])
def create_project():
    title=request.form.get('title')
    description=request.form.get('description')
    url=request.form.get('url')
    technology=request.form.get('technology')
    client=request.form.get('client')
    category=request.form.get('category')
    cover=request.files.get('cover')
    images=request.files.getlist('images')
    filename=cover.filename
    cover.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
    conn=sqlite3.connect('flask_portfolio.db')
    cursor=conn.cursor()
    cursor.execute('''
INSERT INTO projects(title,description,technology,url,cover,client, category_id)
                   VALUES (?,?,?,?,?,?,?)
''',(title,description,technology,url,filename,client,category))
    id=cursor.lastrowid
    conn.commit()
    for img in images:
        filename=img.filename
        img.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        cursor.execute("INSERT INTO project_images(picture,project_id) VALUES (?,?)",(filename,id))
        conn.commit()
    conn.close()
    return jsonify({
        'status':200,
        'message':"Data Inserted Succesfully"
    })

@app.route("/fetch_all_projects",methods=['GET'])
def fetch_all_projects():
    conn=sqlite3.connect('flask_portfolio.db')
    cursor=conn.cursor()
    cursor.execute('''SELECT * from projects
                   LEFT JOIN project_images
                   ON projects.id=project_images.project_id''')
    rows=cursor.fetchall()
    data_dict={}
    for row in rows:
        id,title,description,technology,url,cover,client,category_id,image_id,picture_name,project_id=row
        if id not in data_dict:
            data_dict[id]={
                'id':id,
                'title':title,
                'description':description,
                'technology':technology,
                'url':url,
                'cover':os.path.join(app.config['UPLOAD_FOLDER'],cover),
                'client':client,
                'category_id':category_id,
                'images':[]
            }
        if picture_name:
            data_dict[id]['images'].append(picture_name)
    data_list=list(data_dict.values())
    return jsonify({
        'message':"Data fetched succesfully",
        'status':200,
        'data':data_list
    })
@app.route("/view_one_project/<int:pk>",methods=['GET'])
def view_one_project(pk):
    conn=sqlite3.connect('flask_portfolio.db')
    cursor=conn.cursor()
    cursor.execute('''SELECT * FROM projects
                   LEFT JOIN project_images 
                   ON projects.id=project_images.project_id
                   WHERE projects.id=?

                   ''',(pk,))
    rows=cursor.fetchall()
    data_dict={}
    for row in rows:
        project_id,title,description,technology, url, cover, client, category_id, image_id, picture_name, p_id= row
        if project_id not in data_dict:
            data_dict[project_id]={
                'id':project_id,
                'title':title,
                'description':description,
                'url':url,
                'client':client,
                'technology':technology,
                'images':[]
            }
        if picture_name:
            data_dict[project_id]['images'].append(picture_name)
    data_list=[data_dict[project_id]]
    
    return jsonify({
        'message':"Data fetched succesfully",
        'status':200,
        'data':data_list
    })

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)