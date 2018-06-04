from flask import Flask, render_template,request,redirect,flash,session
from flaskext.mysql import MySQL
from werkzeug.utils import secure_filename
import os
import cgi

##### configuracion de la apliacion
mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'mi clave es secreta'

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'bd_proyecto'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['UPLOAD_FOLDER'] = 'static/Uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

mysql.init_app(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

##### Paginas de redireccion
@app.route('/', methods=['POST', 'GET'])
def main():
    if request.method =='GET':
        if session.get('tipo_usuario') == 2 or session.get('tipo_usuario') is None:
            if not session.get('carroDeCompra'):
                carroDeCompra=[]
                session["CantCarroDeCompra"]=len(carroDeCompra)
                session["carroDeCompra"]=carroDeCompra
                session["precioTotal"]=0
            return render_template('index2.html', productos=listarProductos())
        if session.get('tipo_usuario')==1:
            if not session.get('carroDeCompra'):
                carroDeCompra=[]
                session["CantCarroDeCompra"]=len(carroDeCompra)
                session["carroDeCompra"]=carroDeCompra
                session["precioTotal"]=0
            return render_template('index.html', productos=listarProductos())     

    if request.method =='POST':
        try:
            user_email = request.form['email']
            user_pass = request.form['password']
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute('SELECT * FROM `usuario` WHERE `correo_usuario`= %(user)s and `contrasenia_usuario`= %(pass)s and activo=1',{'user':user_email,'pass':user_pass})
            data = cursor.fetchall()
            if len(data) is 1:
                session['username'] = data[0][6]
                session['tipo_usuario'] = data[0][8]
                if data[0][8]== 1 :
                    return render_template('index.html')
                else:
                    return render_template('index2.html',  productos=listarProductos())
            else:
                return render_template('index2.html',message = 'usuario o contraseña incorrecto', productos=listarProductos())
        except Exception as e:
            return render_template('respuesta.html',respuesta = str(e))
        finally:
            cursor.close()
            con.close()

@app.route('/index')
def inicio():
    if session.get('username'):
        return render_template('index.html')
    else:
        return render_template('respuesta.html',respuesta = 'Aceceso no autorizado')

@app.route('/index2')
def index2():
      return render_template('index2.html',  productos=listarProductos())

@app.route('/detail')
def detail(): 
    codigoDebarra = request.args.get('codigoDebarra')
    data = buscarProductoId(codigoDebarra)
    if len(data) is 0:
        return render_template('404.html', message ='no hay registros')
    else:
        return render_template('detail.html', id = data[0][0], nombre = data[0][1], stock = data[0][3], precio = data[0][4], detalle_producto = data[0][9], imagen = os.path.join(app.config['UPLOAD_FOLDER'], data[0][10]), mensajeBusProd='')

def index2():
      return render_template('index2.html',  productos=listarProductos())

@app.route('/productos')
def productos():
    return render_template('productos.html', productos=listarProductos())

@app.route('/basket')
def basket():
      return render_template('basket.html')

@app.route('/checkout', methods=["GET","POST"])
def checkout():
    if request.method =='GET':
      return render_template('finalizarCompra.html', medioPago=seleccionarMedioDePago())

@app.route('/volver')
def volver():
    if session.get('username'):
        return redirect('/index')
    else:
        return redirect('/')

@app.route('/respuesta')
def respuesta():
    return render_template('respuesta.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login',methods=['POST'])
def webLogin():
    try:
        user_email = request.form['email']
        user_pass = request.form['password']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM `usuario` WHERE `correo_usuario`= %(user)s and `contrasenia_usuario`= %(pass)s and activo=1',{'user':user_email,'pass':user_pass})
        data = cursor.fetchall()
        if len(data) is 1:
            session['username'] = data[0][6]
            session['tipo_usuario'] = data[0][8]
            return render_template('index.html')
        else:
            return render_template('login.html',message = 'usuario o contraseña incorrecto')
    except Exception as e:
        return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()

@app.route('/registro', methods=['POST', 'GET'])
def registro():
    if request.method =='GET':
        return render_template('registro.html', comuna=seleccionar_comunas())
    if request.method =='POST':
        nombres_usuario = request.form['nombres']    
        apellidos_usuario = request.form['apellidos']
        rut = request.form['rut']
        direccion_usuario = request.form['direccion']
        comuna_usuario = request.form['comuna']
        correo_usuario = request.form['email']
        contrasenia_usuario = request.form['password']

        data = agregarUsuario(nombres_usuario,apellidos_usuario,rut,direccion_usuario,comuna_usuario,correo_usuario,contrasenia_usuario, 2)
        if len(data) is 0:
            return render_template('registro.html',message = 'Registro completado', comuna=seleccionar_comunas())
        else:
            return render_template('registro.html',message = 'Error, correo ya utilizado intente nuevamente', comuna=seleccionar_comunas())

@app.route('/desconectar')
def desconectar():
    session.pop('username',None)
    session.pop('tipo_usuario',None)
    session.pop('CantCarroDeCompra',None)
    session.pop('carroDeCompra',None)
    return redirect('/')

##### Carro de compras
@app.route('/agregarProductoAlCarro')
def webAgregarProductoAlCarro():
    idProducto=request.args['id']
    agregarProductoAlCarro(buscarProductoId(idProducto))
    return redirect("/basket")

@app.route('/eliminarProductosCarro')
def webEliminarProductosCarro():
    idProducto=request.args['id']
    eliminarProductosDelCarro(buscarProductoId(idProducto))
    return redirect("/basket")

@app.route('/buscador', methods=['POST', 'GET'])
def webBuscador():
    entrada = request.form['entrada']
    return render_template('productos.html',productos = buscadorProductos(entrada))

##### Funciones Seleccionar
def seleccionar_comunas():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM comuna")
        return cursor
    except Exception as e:
        return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()

def seleccionar_tipo_producto():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT id_tipo_producto,nombre_tipo FROM `tipo_producto`")
        return cursor
    except Exception as e:
        return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()

def seleccionar_categoria_producto():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM `categoria_producto`")
        return cursor
    except Exception as e:
        return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()

def seleccionarMedioDePago():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM `medio_pago`")
        return cursor
    except Exception as e:
        return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()

##### Funciones Producto
def buscarProductoId(codigoDebarra):
        try:
            con = mysql.connect()
            cursor = con.cursor()
            sql='SELECT p.codigo_de_barras,p.nombre_producto,cat.nombre_categoria,i.cantidad_stock,det.precio,tp.nombre_tipo_precio,b.direccion_bodega,tpb.nombre_tipo_bodega,et.nombre_tipo,p.detalle_producto,p.direccion_foto_producto FROM producto p LEFT JOIN inventario i on i.codigo_de_barras=p.codigo_de_barras LEFT JOIN categoria_producto cat on cat.id_categoria=p.id_categoria LEFT JOIN detalle_precio_producto det on det.codigo_de_barras=p.codigo_de_barras LEFT JOIN tipo_precio tp on tp.id_tipo_precio=det.id_tipo_precio LEFT JOIN bodega b on b.id_bodega=i.id_bodega LEFT JOIN tipo_bodega tpb on tpb.id_tipo_bodega=b.id_tipo_bodega LEFT JOIN estado_producto et on et.id_estado_producto=p.id_estado_producto WHERE p.activo = 1 and p.codigo_de_barras= %s GROUP BY p.codigo_de_barras ORDER BY p.codigo_de_barras DESC'            
            cursor.execute(sql,codigoDebarra)
            data = cursor.fetchall()
            return data
        except Exception as e:
            return render_template('respuesta.html',respuesta = str(e))
        finally:
            cursor.close()
            con.close()

def listarProductos():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('SELECT p.codigo_de_barras, p.nombre_producto, cat.nombre_categoria, i.cantidad_stock, det.precio, tp.nombre_tipo_precio, b.direccion_bodega, tpb.nombre_tipo_bodega, et.nombre_tipo, p.detalle_producto, p.direccion_foto_producto FROM producto p LEFT JOIN inventario i ON i.codigo_de_barras = p.codigo_de_barras LEFT JOIN categoria_producto cat ON cat.id_categoria = p.id_categoria LEFT JOIN detalle_precio_producto det ON det.codigo_de_barras = p.codigo_de_barras LEFT JOIN tipo_precio tp ON tp.id_tipo_precio = det.id_tipo_precio LEFT JOIN bodega b ON b.id_bodega = i.id_bodega LEFT JOIN tipo_bodega tpb ON tpb.id_tipo_bodega = b.id_tipo_bodega LEFT JOIN estado_producto et ON et.id_estado_producto = p.id_estado_producto WHERE p.activo =1 GROUP BY p.codigo_de_barras ORDER BY p.codigo_de_barras DESC')
        data = cursor.fetchall()
        return data
    except Exception as e:
         return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()

##### Funciones Usuario
def agregarUsuario(nombres_usuario,apellidos_usuario,rut,direccion_usuario,comuna_usuario,correo_usuario,contrasenia_usuario, tipo_usuario):
    try:
        con = mysql.connect()
        cursor = con.cursor()
        sql = "INSERT INTO `usuario`(`rut_usuario`,`nombre_usuario`, `apellido_usuario`, `direccion`, `id_comuna`, `correo_usuario`, `contrasenia_usuario`, `tipo_usuario`, `activo`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1)"
        cursor.execute(sql, (rut,nombres_usuario, apellidos_usuario, direccion_usuario, comuna_usuario,correo_usuario, contrasenia_usuario, tipo_usuario))
        data = cursor.fetchall()
        if len(data) is 0:
            con.commit()
            return data
        else:
           return data
    except Exception as e:
        return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()

def modificarUsuario(nombre_usuario, apellido_usuario, direccion, id_comuna, contrasenia_usuario, tipo_usuario, activo, correo_usuario):
    con = mysql.connect()
    try:
        with con.cursor() as cursor:
            sql = "UPDATE `usuario` SET `nombre_usuario`= %s,`apellido_usuario`= %s, `direccion`= %s, `id_comuna`= %s, `contrasenia_usuario`= %s, `tipo_usuario`= %s, `activo`= %s WHERE `correo_usuario`= %s"
            cursor.execute(sql, (nombre_usuario, apellido_usuario, direccion, id_comuna, contrasenia_usuario, tipo_usuario, activo, correo_usuario))
            data=cursor.rowcount
            if data==1:
                con.commit()
                return data
            else:
                return data
    except Exception as e:
        return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()

def buscarUsuarioEmail(email_usuario):
        try:
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute('SELECT * FROM usuario WHERE correo_usuario= %(correo)s ',{'correo':email_usuario})
            data = cursor.fetchall()
            return data
        except Exception as e:
            return render_template('respuesta.html',respuesta = str(e))
        finally:
            cursor.close()
            con.close()
    
def listarUsuario():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM usuario')
        data = cursor.fetchall()
        return data
    except Exception as e:
         return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()
  
##### Carro de compra
def agregarProductoAlCarro(producto):
    carroDeCompra=session["carroDeCompra"]
    precioTotal=session["precioTotal"]
    carroDeCompra.append(producto)
    precioTotal+=producto[0][4]
    session["precioTotal"]=precioTotal
    session["CantCarroDeCompra"]=len(carroDeCompra)
    session["carroDeCompra"]=carroDeCompra

def eliminarProductosDelCarro(producto):
    session.get("carroDeCompra")
    precioTotal=session["precioTotal"]
    carroDeCompra=session["carroDeCompra"]
    precioTotal-=producto[0][4]
    carroDeCompra.remove(producto)
    session["precioTotal"]=precioTotal
    session["CantCarroDeCompra"]=len(carroDeCompra)
    session["carroDeCompra"]=carroDeCompra

def descontarProducto(idProducto):
    con = mysql.connect()
    try:
        carroDeCompra=session["carroDeCompra"]
        precioTotal=session["precioTotal"]
        carroDeCompra.append(producto)
        precioTotal+=producto[0][3]
        session["precioTotal"]=precioTotal
        session["CantCarroDeCompra"]=len(carroDeCompra)
        session["carroDeCompra"]=carroDeCompra
        with con.cursor() as cursor:
            sql = "UPDATE `producto` SET `stock_producto`=`stock_producto`-1 WHERE `id_producto`= %s"
            cursor.execute(sql, (idProducto))
            data=cursor.rowcount
            if data==1:
                con.commit()
            else:
                pass
    except Exception as e:
        return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()

def devolverProducto(idProducto):
    con = mysql.connect()
    try:
        with con.cursor() as cursor:
            sql = "UPDATE `producto` SET `stock_producto`=`stock_producto`+1 WHERE `id_producto`= %s"
            cursor.execute(sql, (idProducto))
            data=cursor.rowcount
            if data==1:
                con.commit()
            else:
                pass
    except Exception as e:
        return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()

##### Funciones de buscador de producto
def buscadorProductos(entrada):
    entrada='%'+entrada+'%'
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('SELECT p.codigo_de_barras,p.nombre_producto,cat.nombre_categoria,i.cantidad_stock,det.precio,tp.nombre_tipo_precio,b.direccion_bodega,tpb.nombre_tipo_bodega,et.nombre_tipo,p.detalle_producto,p.direccion_foto_producto FROM producto p LEFT JOIN inventario i on i.codigo_de_barras=p.codigo_de_barras LEFT JOIN categoria_producto cat on cat.id_categoria=p.id_categoria LEFT JOIN detalle_precio_producto det on det.codigo_de_barras=p.codigo_de_barras LEFT JOIN tipo_precio tp on tp.id_tipo_precio=det.id_tipo_precio LEFT JOIN bodega b on b.id_bodega=i.id_bodega LEFT JOIN tipo_bodega tpb on tpb.id_tipo_bodega=b.id_tipo_bodega LEFT JOIN estado_producto et on et.id_estado_producto=p.id_estado_producto WHERE p.activo = 1 and p.detalle_producto LIKE %(entrada)s GROUP BY p.codigo_de_barras ORDER BY p.codigo_de_barras DESC',{'entrada':entrada})
        data = cursor.fetchall()
        return data
    except Exception as e:
         return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()
        

##### ejecucion de la aplicacion
if __name__ == "__main__":
    app.run(debug=True)

