from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flask import send_from_directory
from flask.helpers import flash
from flaskext.mysql import MySQL
from datetime import date, datetime
import os

import pymysql


app= Flask(__name__)

#Configuracion de base de datos
mysql= MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sistema2123'
mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA

#ruteo para que mande la foto al index
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
   return send_from_directory(app.config['CARPETA'], nombreFoto)

#Ruteo
@app.route('/')
def index():
    sql="SELECT * FROM `empleados`;"
    conn=mysql.connect()    
    cursor=conn.cursor()
    cursor.execute(sql)
    conn.commit()
    empleados=cursor.fetchall()
    
    return render_template('empleados/index.html',empleados=empleados)

@app.route('/destroy/<int:id>')
def destroy(id):
   conn=mysql.connect()
   cursor=conn.cursor()

   #pido a la base de datos que me traiga el nombre de la foto
   cursor.execute("SELECT foto FROM empleados WHERE id=%s",id)
   fila=cursor.fetchall()
   #pido que elimine la foto
   os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

   #Para el boton eliminar
   cursor.execute("DELETE FROM empleados WHERE id=%s", (id))
   conn.commit()
   return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id))
    empleados=cursor.fetchall()
    conn.commit()
    return render_template('empleados/edit.html',empleados=empleados)


@app.route('/update',methods=['POST'])
def update():
   _nombre=request.form['txtNombre']
   _correo=request.form['txtCorreo']
   _foto=request.files['txtFoto']
   id=request.form['txtId']

   sql="UPDATE empleados SET  nombre=%s, correo=%s WHERE id=%s;"
   datos=(_nombre,_correo,id)
   conn=mysql.connect()
   cursor=conn.cursor()

   now=datetime.now()
   tiempo=now.strftime('%Y%H%M%S')

   if _foto.filename!='':
      nuevoNombreFoto=tiempo+_foto.filename
      _foto.save("uploads/"+nuevoNombreFoto)

      #con esto llamo a la base de datos a preguntar el nombre de la foto
      cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
      fila=cursor.fetchall()
      #print(os.path.join(app.config[0][0])) - para ver la foto
      #con esto elimino la foto que ya existe
      os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
      #con esto actualizo la foto nueva
      cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevoNombreFoto,id))
      conn.commit()

   cursor.execute (sql, datos)
   conn.commit()
   return redirect('/')



@app.route('/create')
def create():
   return render_template ('empleados/create.html')


@app.route('/store',methods = ['POST'])
def storage():
   _nombre = request.form['txtNombre']
   _correo = request.form['txtCorreo']
   _foto = request.files['txtFoto']

   if _nombre=='' or _correo=='' or _foto=='':
      flash('Falta rellenar algun dato')
      return redirect(url_for('create'))

   now = datetime.now()
   tiempo=now.strftime("%Y%H%M%S")

   if _foto.filename!='':
       nuevoNombreFoto=tiempo+_foto.filename
       _foto.save("uploads/"+nuevoNombreFoto)


   sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s,%s,%s);"
   datos= (_nombre, _correo, nuevoNombreFoto)

   #Al crear un empleado, se dirige al index
   conn=mysql.connect()
   cursor=conn.cursor()
   cursor.execute(sql, datos)
   conn.commit()
   return redirect('/')



if __name__=='__main__':
    app.run(debug=True)
    