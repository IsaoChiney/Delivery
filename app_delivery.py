import streamlit as st
import requests
import time
import re

# Configuración de la página
st.set_page_config(
    page_title="FLASH",
    page_icon="🍕",
    layout="wide"
)

# CSS para mejor apariencia
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #00C389;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        width: 100%;
        margin: 5px 0;
    }
    .stButton>button:hover {
        background-color: #00A375;
        color: white;
    }
    .admin-button {
        background-color: #FF6B00 !important;
    }
    .admin-button:hover {
        background-color: #E55A00 !important;
    }
    .client-button {
        background-color: #00C389 !important;
    }
    .admin-badge {
        background-color: #FF6B00;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
    }
    .client-badge {
        background-color: #00C389;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
    }
    .product-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# URL de tu API
API_URL = "https://olivedrab-woodcock-467386.hostingersite.com/"

def llamar_api(endpoint, datos=None, method='POST', files=None):
    """Función mejorada para llamar a la API PHP"""
    try:
        url = f"{API_URL}{endpoint}"
        
        if method == 'POST':
            if files:
                # Para envío de archivos
                respuesta = requests.post(url, data=datos, files=files, timeout=10)
            else:
                # Para datos JSON normales
                headers = {'Content-Type': 'application/json'}
                respuesta = requests.post(url, json=datos, headers=headers, timeout=10)
        else:  # GET
            respuesta = requests.get(url, timeout=10)
        
        # Verificar el estado HTTP primero
        if respuesta.status_code != 200:
            try:
                return respuesta.json()  # ← Aquí ya viene {"error": "..."}
            except ValueError:
                return {
                    "success": False,
                    "error": f"Error HTTP {respuesta.status_code}",
                    "raw_response": respuesta.text
                }

        
        # Verificar si la respuesta está vacía
        if not respuesta.text.strip():
            return {
                "success": False,
                "error": "La API devolvió una respuesta vacía",
                "raw_response": ""
            }
        
        # Intentar parsear JSON
        try:
            resultado = respuesta.json()
            return resultado
        except requests.exceptions.JSONDecodeError as e:
            return {
                "success": False,
                "": f"Respuesta no es JSON válido: {str(e)}",
                "raw_response": respuesta.text[:500]  # Primeros 500 caracteres
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Timeout: La API no respondió a tiempo"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Error de conexión: No se pudo conectar a la API"}
    except Exception as e:
        return {"success": False, "error": f"Error inesperado: {str(e)}"}

def llamar_api_upload(endpoint, datos, files):
    """Función específica para subir archivos con mejor manejo de errores"""
    try:
        url = f"{API_URL}{endpoint}"
        
        respuesta = requests.post(url, data=datos, files=files, timeout=30)
        
    
        # Verificar el estado HTTP primero
        if respuesta.status_code != 200:
            return {
                "success": False, 
                "error": f"Error HTTP {respuesta.status_code}",
                "raw_response": respuesta.text[:1000] if respuesta.text else "Respuesta vacía",
                "status_code": respuesta.status_code
            }
        
        # Verificar si la respuesta está vacía
        if not respuesta.text or not respuesta.text.strip():
            return {
                "success": False,
                "error": "La API devolvió una respuesta vacía",
                "raw_response": "",
                "status_code": respuesta.status_code
            }
        
        # Intentar parsear JSON
        try:
            resultado = respuesta.json()
            resultado["status_code"] = respuesta.status_code
            return resultado
        except Exception as e:
            return {
                "success": False,
                "error": f"Respuesta no es JSON válido: {str(e)}",
                "raw_response": respuesta.text[:1000] if respuesta.text else "Respuesta vacía",
                "status_code": respuesta.status_code
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Timeout: La API no respondió a tiempo"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Error de conexión: No se pudo conectar a la API"}
    except Exception as e:
        return {"success": False, "error": f"Error inesperado: {str(e)}"}    
        
# INICIALIZAR ESTADO DE LA APLICACIÓN
if 'logueado' not in st.session_state:
    st.session_state.logueado = False
if 'usuario' not in st.session_state:
    st.session_state.usuario = None
if 'pagina' not in st.session_state:
    st.session_state.pagina = "login"
if 'carrito' not in st.session_state:
    st.session_state.carrito = []
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "inicio"
if 'es_admin' not in st.session_state:
    st.session_state.es_admin = False
if 'producto_editar' not in st.session_state:
    st.session_state.producto_editar = None
if 'producto_eliminar' not in st.session_state:
    st.session_state.producto_eliminar = None
if 'editar_imagen_producto' not in st.session_state:
    st.session_state.editar_imagen_producto = None

# --- PÁGINA DE LOGIN ---
def mostrar_login():
    st.title("FLASH - Login")
    st.write("Bienvenido a tu app FLASH")
    
    with st.form("form_login"):
        correo = st.text_input("📧 Correo electrónico")
        password = st.text_input("🔒 Contraseña", type="password")
        
        if st.form_submit_button("🚀 Ingresar"):
            if correo and password:
                with st.spinner("Verificando credenciales..."):
                    resultado = llamar_api("login.php", {
                        "correo": correo, 
                        "password": password
                    })
                    
                    if "usuario" in resultado:
                        st.session_state.logueado = True
                        st.session_state.usuario = resultado["usuario"]
                        st.session_state.pagina_actual = "inicio"
                        
                        # Determinar si es administrador basado en el rol
                        if resultado["usuario"].get("rol") == "administrador":
                            st.session_state.es_admin = True
                        else:
                            st.session_state.es_admin = False
                        
                        st.success("¡Login exitoso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"{resultado.get('', 'Credenciales incorrectas')}")
            else:
                st.warning("Por favor completa todos los campos")
    
    st.write("---")
    if st.button("📝 Crear cuenta nueva"):
        st.session_state.pagina = "registro"
        st.rerun()

# --- PÁGINA DE REGISTRO ---
def mostrar_registro():
    st.title("📝 Crear Cuenta Nueva")
    
    with st.form("form_registro"):
        nombre = st.text_input("👤 Nombre completo")
        correo = st.text_input("📧 Correo electrónico")
        telefono = st.text_input("📱 Teléfono")
        password = st.text_input("🔒 Contraseña", type="password")
        confirmar = st.text_input("✅ Confirmar contraseña", type="password")
        
        # Información sobre roles
        st.info("🔐 Todas las cuentas nuevas se crean como **Clientes**. Contacta al administrador para cambiar de rol.")
        
        if st.form_submit_button("🚀 Registrarse"):
            if not all([nombre, correo, telefono, password, confirmar]):
                st.warning("Por favor completa todos los campos")
            elif password != confirmar:
                st.error("Las contraseñas no coinciden")
            elif len(password) < 8:
                st.error("❌ La contraseña debe tener al menos 8 caracteres")
            elif not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
                st.error("❌ La contraseña debe ser alfanumérica (letras y números)")    
            elif not re.search(r"[^A-Za-z0-9]", password):  
                st.error("La contraseña debe incluir al menos un caracter especial (ej: @, #, $, !)")
            elif not re.search(r"[A-Z]", password):
                st.error("La contraseña debe incluir al menos una letra mayúscula")
            elif not re.search(r"[a-z]", password):
                st.error("La contraseña debe incluir al menos una letra minúscula")
            else:
                with st.spinner("Creando cuenta..."):
                    # Datos que vamos a enviar
                    data = {
                        "nombre": nombre,
                        "correo": correo, 
                        "telefono": telefono,
                        "password": password
                    }

                    url = API_URL + "registro_usuario.php"
                    try:
                        resp = requests.post(url, json=data)
                        resultado = resp.json()
                        
                        if "mensaje" in resultado:
                            st.success(f"✅ {resultado['mensaje']}")
                            st.info(f"Tu ID de usuario es: {resultado['usuario_id']}")
                            st.caption(f"Fecha de registro: {resultado['fecha_registro']}")
                            
                            time.sleep(2)
                            st.session_state.pagina = "login"
                            st.rerun()
                        else:
                            st.error(resultado.get("error", "Error desconocido"))
                        
                        if resp.status_code == 200:
                            resultado = resp.json()
                            
                            if resultado.get("success"):
                                st.success("✅ ¡Cuenta creada exitosamente!")
                                st.info("Ahora puedes iniciar sesión")
                                time.sleep(2)
                                st.session_state.pagina = "login"
                                return  # Sale de la función
                            else:
                                mensaje_error = resultado.get("qUE PUES", "Error desconocido")
                                #st.error(f"⚠️ {resp.text}")
                        else:
                            mensaje_error = resultado.get("error", "Error desconocido")
                            #st.error(f"⚠️ {resp.text}")
                    
                    except Exception:
                        st.error(f"⚠️ Error inesperado: {resp.text}")
                        return
                    
                        
    if st.button("← Volver al login"):
        st.session_state.pagina = "login"
        return

# --- SECCIÓN INICIO ---
def mostrar_inicio():
    st.title("🏠 Inicio - FLASH")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🍔 **100+ Restaurantes**\n\nLos mejores de tu ciudad")
    with col2:
        st.info("🚗 **Entrega Rápida**\n\n30 minutos o menos")
    with col3:
        st.info("⭐ **Calidad Garantizada**\n\nProductos frescos")
    
    st.write("---")
    st.subheader("🚀 Comienza a ordenar")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🍕 Ver Menú Completo", use_container_width=True, type="primary"):
            st.session_state.pagina_actual = "pedidos"
            st.rerun()
    with col2:
        if st.button("📞 Contactar Soporte", use_container_width=True):
            st.info("📞 Llama al: 555-1234")

# --- SECCIÓN PEDIDOS ---
def mostrar_pedidos():
    st.title("Realizar Pedido")
    
    # Obtener productos de la base de datos
    resultado = llamar_api("obtener_productos.php", method='GET')
    
    if resultado.get('success') and resultado.get('productos'):
        productos = resultado['productos']
        
        # Mostrar productos
        for producto in productos:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                with col1:
                    # Mostrar imagen si existe
                    if producto.get('imagen_url'):
                        st.image(f"{API_URL}{producto['imagen_url']}", width=100)
                    else:
                        st.write("📷")
                    
                    st.write(f"**{producto['nombre']}**")
                    st.write(f"{producto['descripcion'] or 'Sin descripción'}")
                    st.write(f"**${producto['precio']}** • {producto['categoria']}")
                
                with col2:
                    cantidad = st.number_input(
                        "Cantidad", 
                        min_value=0, 
                        max_value=10, 
                        key=f"cant_{producto['id']}"
                    )
                with col3:
                    subtotal = float(producto['precio']) * cantidad
                    st.write(f"**${subtotal:.2f}**" if cantidad > 0 else "$0.00")
                with col4:
                    if cantidad > 0 and st.button("🛒 Agregar", key=f"btn_{producto['id']}"):
                        # Agregar al carrito
                        item_carrito = {
                            "id": producto["id"],
                            "nombre": producto["nombre"],
                            "precio": float(producto["precio"]),
                            "cantidad": cantidad
                        }
                        st.session_state.carrito.append(item_carrito)
                        st.success(f"✅ {producto['nombre']} agregado!")
                        time.sleep(1)
                        st.rerun()
    else:
        st.info("No hay productos disponibles en este momento")
        if st.session_state.es_admin:
            if st.button("📤 Agregar Primer Producto"):
                st.session_state.pagina_actual = "gestion_productos"
                st.rerun()

# --- SECCIÓN CARRITO ---
def mostrar_carrito():
    st.title("🛒 Mi Carrito")
    
    if not st.session_state.carrito:
        st.info("Tu carrito está vacío")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🍕 Ver Productos", use_container_width=True):
                st.session_state.pagina_actual = "pedidos"
                st.rerun()
        return
    
    total = 0
    # Mostrar items del carrito
    for i, item in enumerate(st.session_state.carrito):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.write(f"**{item['nombre']}**")
        with col2:
            st.write(f"${item['precio']} x {item['cantidad']}")
        with col3:
            subtotal = item['precio'] * item['cantidad']
            st.write(f"**${subtotal:.2f}**")
            total += subtotal
        with col4:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.carrito.pop(i)
                st.rerun()
    
    st.write("---")
    st.write(f"## 💰 Total: ${total:.2f}")
    
    # FORMULARIO DE ENTREGA (CORREGIDO)
    with st.form("form_entrega"):
        direccion = st.text_input("🏠 Dirección de entrega", placeholder="Ingresa tu dirección completa")
        notas = st.text_area("📝 Notas adicionales", placeholder="Instrucciones especiales para la entrega...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("✅ Confirmar Pedido", use_container_width=True, type="primary"):
                if direccion:
                    with st.spinner("Procesando pedido..."):
                        # Crear pedido en la base de datos
                        resultado = llamar_api("crear_pedido.php", {
                            "usuario_id": st.session_state.usuario["id"],
                            "productos": st.session_state.carrito,
                            "direccion_entrega": direccion,
                            "notas": notas,
                            "total": total
                        })
                        
                        if resultado.get('success'):
                            st.success(f"🎉 ¡Pedido #{resultado['pedido_id']} realizado con éxito!")
                            st.session_state.carrito = []
                            time.sleep(2)
                            st.session_state.pagina_actual = "mis_pedidos"
                            st.rerun()
                        else:
                            st.error(f"{resultado.get('error')}")
                else:
                    st.error("Por favor ingresa la dirección de entrega")
        with col2:
            if st.form_submit_button("🗑️ Vaciar Carrito", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()

# --- SECCIÓN MIS PEDIDOS ---
def mostrar_mis_pedidos():
    st.title("📋 Mis Pedidos")
    
    # Obtener pedidos del usuario
    resultado = llamar_api(f"obtener_pedidos_usuario.php?usuario_id={st.session_state.usuario['id']}", method='GET')
    
    if resultado.get('success') and resultado.get('pedidos'):
        pedidos = resultado['pedidos']
        
        for pedido in pedidos:
            with st.expander(f"Pedido #{pedido['id']} - {pedido['fecha_pedido']} - ${pedido['total']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Estado:** {pedido['estado']}")
                with col2:
                    st.write(f"**Productos:** {pedido['total_productos']}")
                with col3:
                    st.write(f"**Total:** ${pedido['total']}")
                
                if pedido['notas']:
                    st.write(f"**Notas:** {pedido['notas']}")
                
                st.write(f"**Dirección:** {pedido['direccion_entrega']}")
    else:
        st.info("Aún no has realizado ningún pedido")

# --- SECCIÓN GESTIÓN DE USUARIOS (Solo Admin) ---
def mostrar_gestion_usuarios():
    st.title("👥 Gestión de Usuarios")
    st.write("🔧 **Panel de Administrador**")
    
    # Obtener lista de usuarios (necesitarías crear este endpoint PHP)
    st.info("📋 Lista de usuarios registrados en el sistema")
    
    # Ejemplo de usuarios (en producción obtendrías de la BD)
    usuarios_ejemplo = [
        {"id": 1, "nombre": "Admin Principal", "correo": "admin@delivery.com", "rol": "administrador"},
        {"id": 2, "nombre": "Cliente Ejemplo", "correo": "cliente@ejemplo.com", "rol": "cliente"},
    ]
    
    for usuario in usuarios_ejemplo:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                st.write(f"**{usuario['nombre']}**")
                st.write(usuario['correo'])
            with col2:
                if usuario['rol'] == 'administrador':
                    st.markdown('<div class="admin-badge">ADMIN</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="client-badge">HOLA</div>', unsafe_allow_html=True)
            with col3:
                if usuario['rol'] == 'cliente':
                    if st.button("👑 Hacer Admin", key=f"make_admin_{usuario['id']}"):
                        # Llamar API para cambiar rol
                        st.success(f"Usuario {usuario['nombre']} ahora es administrador")
                else:
                    if st.button("👤 Hacer Cliente", key=f"make_client_{usuario['id']}"):
                        # Llamar API para cambiar rol
                        st.success(f"Usuario {usuario['nombre']} ahora es cliente")
            with col4:
                if st.button("🗑️", key=f"delete_{usuario['id']}"):
                    st.warning("Función de eliminar usuario (implementar)")

# --- SECCIÓN GESTIÓN DE PRODUCTOS (Solo Admin) ---
def mostrar_gestion_productos():
    st.title("📤 Gestión de Productos")
    st.write("🔧 **Panel de Administrador**")

    # Pestañas para diferentes acciones
    tab1, tab2, tab3 = st.tabs(["📥 Subir Producto", "📋 Productos Existentes", "📊 Estadísticas"])

    # ----------------- TAB 1: SUBIR PRODUCTO -----------------
    with tab1:
        with st.form("form_subir_producto", clear_on_submit=True):
            nombre = st.text_input("👤 Nombre del Producto*")
            descripcion = st.text_area("📝 Descripción")
            precio = st.number_input("💰 Precio*", min_value=0.0, step=0.5, format="%.2f")
            categoria = st.selectbox("📂 Categoría*",
                                      ["pizza", "hamburguesa", "sushi", "mexicana", "italiana", "china", "postres", "bebidas"])

            imagen = st.file_uploader("🖼️ Imagen del Producto",
                                       type=['jpg', 'jpeg', 'png', 'gif'],
                                       help="Sube una imagen para el producto")

            if st.form_submit_button("🚀 Subir Producto", type="primary"):
                if not all([nombre, precio, categoria]):
                    st.warning("Por favor completa los campos obligatorios (*)")
                else:
                    with st.spinner("Subiendo producto..."):
                        datos = {
                            "nombre": nombre,
                            "descripcion": descripcion,
                            "precio": float(precio),
                            "categoria": categoria
                        }

                        if imagen is not None:
                            files = {'imagen': (imagen.name, imagen.getvalue(), imagen.type)}
                            resultado = llamar_api_upload("subir_producto.php", datos, files)
                        else:
                            resultado = llamar_api("subir_producto.php", datos)

                        if resultado.get('success'):
                            st.success(f"✅ {resultado.get('message', 'Producto subido exitosamente')}")
                            st.success("✅ Producto actualizado correctamente", icon="✔️")
                            time.sleep(2)
                            return
                        else:
                            error_msg = resultado.get('error', 'Error desconocido')
                            st.error(f"❌ Error: {error_msg}")

    # ----------------- TAB 2: PRODUCTOS EXISTENTES -----------------
    with tab2:
        st.subheader("Productos en el Sistema")
        resultado = llamar_api("obtener_productos.php", method='GET')
        if resultado.get('success') and resultado.get('productos'):
            productos = resultado['productos']

            for producto in productos:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                    with col1:
                        st.write(f"**{producto['nombre']}**")
                        st.write(f"${producto['precio']} • {producto['categoria']}")
                        if producto.get('descripcion'):
                            st.write(f"_{producto['descripcion']}_")
                    with col2:
                        if producto.get('imagen_url'):
                            st.image(f"{API_URL}{producto['imagen_url']}", width=80)
                        else:
                            st.write("📷 Sin imagen")
                    with col3:
                        if st.button("✏️ Editar", key=f"edit_{producto['id']}"):
                            st.session_state.producto_editar = producto
                            st.rerun()
                    with col4:
                        if st.button("🔄 Imagen", key=f"update_img_{producto['id']}"):
                            st.session_state.editar_imagen_producto = producto['id']
                            st.session_state.editar_imagen_producto_nombre = producto['nombre']
                            st.rerun()
                    with col5:
                        if st.button("❌ Eliminar", key=f"delete_{producto['id']}"):
                            st.session_state.producto_eliminar = producto
                            st.rerun()

                    st.write("---")
        else:
            st.info("No hay productos en el sistema")

    # ----------------- FORMULARIO EDITAR PRODUCTO -----------------
    if st.session_state.get("producto_editar"):
        producto = st.session_state.producto_editar
        st.subheader(f"✏️ Editando: {producto['nombre']}")

        with st.form(f"form_editar_producto_{producto['id']}"):
            nombre_edit = st.text_input("👤 Nombre del Producto*", value=producto['nombre'])
            descripcion_edit = st.text_area("📝 Descripción", value=producto.get('descripcion', ''))
            precio_edit = st.number_input("💰 Precio*", min_value=0.0, step=0.5, format="%.2f", value=float(producto['precio']))

            categorias = ["pizza", "hamburguesa", "sushi", "mexicana", "italiana", "china", "postres", "bebidas"]
            index_actual = categorias.index(producto['categoria']) if producto['categoria'] in categorias else 0
            categoria_edit = st.selectbox("📂 Categoría*", categorias, index=index_actual)

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                    if not all([nombre_edit, precio_edit, categoria_edit]):
                        st.warning("Por favor completa los campos obligatorios (*)")
                    else:
                        with st.spinner("Actualizando producto..."):
                            resultado = llamar_api("actualizar_producto.php", {
                                "id": producto['id'],
                                "nombre": nombre_edit,
                                "descripcion": descripcion_edit,
                                "precio": precio_edit,
                                "categoria": categoria_edit
                            })
                            if resultado.get('success'):
                                st.success("✅ Producto actualizado correctamente")
                                st.session_state.producto_editar = None
                                time.sleep(2)
                                return
                            else:
                                st.error(f"❌ Error: {resultado.get('error', 'Error al actualizar producto')}")
            with col2:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.producto_editar = None
                    return

    # ----------------- FORMULARIO ACTUALIZAR IMAGEN -----------------
    if st.session_state.get("editar_imagen_producto") is not None:
        formulario_actualizar_imagen(
            st.session_state.editar_imagen_producto,
            st.session_state.get("editar_imagen_producto_nombre", "")
        )

    # ----------------- CONFIRMAR ELIMINAR PRODUCTO -----------------
    if st.session_state.get("producto_eliminar"):
        producto = st.session_state.producto_eliminar
        st.subheader("❌ Confirmar Eliminación")
        st.warning(f"¿Estás seguro de que quieres eliminar el producto **{producto['nombre']}**?")
        st.write(f"**Precio:** ${producto['precio']}")
        st.write(f"**Categoría:** {producto['categoria']}")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Sí, Eliminar", type="primary", key=f"confirmar_eliminar_{producto['id']}"):
                with st.spinner("Eliminando producto..."):
                    resultado = llamar_api("eliminar_producto.php", {"id": producto['id']})
                    if resultado.get('success'):
                        st.success("✅ Producto eliminado correctamente")
                        st.session_state.producto_eliminar = None
                        time.sleep(2)
                        return
                    else:
                        st.error(f"❌ Error: {resultado.get('error', 'Error al eliminar producto')}")
        with col2:
            if st.button("❌ No, Cancelar", key=f"cancelar_eliminar_{producto['id']}"):
                st.session_state.producto_eliminar = None
                st.rerun()
        with col3:
            if st.button("📝 Editar en lugar de Eliminar", key=f"editar_en_lugar_{producto['id']}"):
                st.session_state.producto_editar = producto
                st.session_state.producto_eliminar = None
                st.rerun()

    # ----------------- TAB 3: ESTADÍSTICAS -----------------
    with tab3:
        st.subheader("Estadísticas de Productos")
        resultado = llamar_api("obtener_productos.php", method='GET')
        if resultado.get('success') and resultado.get('productos'):
            productos = resultado['productos']
            total_productos = len(productos)
            categorias = set(p['categoria'] for p in productos)
            total_categorias = len(categorias)

            if productos:
                producto_mas_caro = max(productos, key=lambda x: float(x['precio']))
            else:
                producto_mas_caro = None
        else:
            total_productos = 0
            total_categorias = 0
            producto_mas_caro = None

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Productos", total_productos)
            st.metric("Categorías", total_categorias)
        with col2:
            st.metric("Productos Activos", total_productos)
            if producto_mas_caro:
                st.metric("Producto Más Caro", f"{producto_mas_caro['nombre']} (${producto_mas_caro['precio']})")
            else:
                st.metric("Producto Más Caro", "N/A")

def formulario_actualizar_imagen(producto_id, producto_nombre):
    st.subheader("🔄 Actualizar Imagen del Producto")
    st.write(f"Producto: {producto_nombre} (ID: {producto_id})")

    form_key = f"form_actualizar_imagen_{producto_id}"
    uploader_key = f"uploader_{producto_id}"

    with st.form(key=form_key):
        nueva_imagen = st.file_uploader("Selecciona nueva imagen",
                                         type=['jpg', 'jpeg', 'png', 'gif'],
                                         key=uploader_key)

        if nueva_imagen:
            st.write("📸 Información de la imagen seleccionada:")
            st.write(f"   - Nombre: {nueva_imagen.name}")
            st.write(f"   - Tamaño: {len(nueva_imagen.getvalue())} bytes")
            st.write(f"   - Tipo: {nueva_imagen.type}")
        else:
            st.write("❌ No se ha seleccionado ninguna imagen")

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("✅ Actualizar Imagen"):
                if nueva_imagen:
                    try:
                        files = {'imagen': (nueva_imagen.name, nueva_imagen.getvalue(), nueva_imagen.type)}
                        datos = {"id": producto_id}
                        resultado = llamar_api_upload("actualizar_imagen_producto.php", datos, files)

                        if resultado.get('success'):
                            st.success("✅ Imagen actualizada correctamente")
                            st.success("✅ Producto actualizado correctamente")
                            st.session_state.editar_imagen_producto = None
                            st.session_state.editar_imagen_producto_nombre = None
                            return
                        else:
                            st.error(f"❌ Error: {resultado.get('error', 'Error desconocido')}")
                    except Exception as e:
                        st.error(f"💥 Error inesperado: {str(e)}")
                else:
                    st.warning("⚠️ Por favor selecciona una imagen")
        with col2:
            if st.form_submit_button("❌ Cancelar"):
                st.info("Operación cancelada")
                st.session_state.editar_imagen_producto = None
                st.session_state.editar_imagen_producto_nombre = None
                return

# --- DASHBOARD PRINCIPAL ---
def mostrar_dashboard():
    # Barra lateral con MENÚ
    with st.sidebar:
        # Mostrar badge según el rol
        if st.session_state.es_admin:
            st.markdown('<div class="admin-badge">👑 ADMINISTRADOR</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="client-badge">👤 CLIENTE</div>', unsafe_allow_html=True)
            
        st.title(f"👋 Hola, {st.session_state.usuario['nombre']}")
        st.write("---")
        
        # BOTONES DE NAVEGACIÓN COMUNES
        if st.button("🏠 Inicio", use_container_width=True, key="btn_inicio"):
            st.session_state.pagina_actual = "inicio"
            st.rerun()
            
        if st.button("🍕 Realizar Pedido", use_container_width=True, key="btn_pedidos"):
            st.session_state.pagina_actual = "pedidos"
            st.rerun()
            
        if st.button("🛒 Mi Carrito", use_container_width=True, key="btn_carrito"):
            st.session_state.pagina_actual = "carrito"
            st.rerun()
            
        if st.button("📋 Mis Pedidos", use_container_width=True, key="btn_mis_pedidos"):
            st.session_state.pagina_actual = "mis_pedidos"
            st.rerun()
            
        # BOTONES SOLO PARA ADMINISTRADORES
        if st.session_state.es_admin:
            st.write("---")
            st.write("**🔧 Panel de Administrador**")
            if st.button("📤 Gestionar Productos", use_container_width=True, type="secondary", key="btn_gestion_productos"):
                st.session_state.pagina_actual = "gestion_productos"
                st.rerun()
                
            if st.button("👥 Gestionar Usuarios", use_container_width=True, type="secondary", key="btn_gestion_usuarios"):
                st.session_state.pagina_actual = "gestion_usuarios"
                st.rerun()
                
            if st.button("📊 Ver Reportes", use_container_width=True, type="secondary", key="btn_reportes"):
                st.session_state.pagina_actual = "reportes"
                st.rerun()
        
        st.write("---")
        if st.button("👤 Mi Perfil", use_container_width=True, key="btn_perfil"):
            st.session_state.pagina_actual = "perfil"
            st.rerun()
            
        st.write("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True, key="btn_logout"):
            st.session_state.logueado = False
            st.session_state.usuario = None
            st.session_state.es_admin = False
            st.session_state.pagina = "login"
            st.rerun()
    def mostrar_reportes():
        st.subheader("📊 Reportes")
        st.write("En construcción")

    # Mostrar contenido según la página actual
    if st.session_state.pagina_actual == "inicio":
        mostrar_inicio()
    elif st.session_state.pagina_actual == "pedidos":
        mostrar_pedidos()
    elif st.session_state.pagina_actual == "carrito":
        mostrar_carrito()
    elif st.session_state.pagina_actual == "mis_pedidos":
        mostrar_mis_pedidos()
    elif st.session_state.pagina_actual == "gestion_productos":
        mostrar_gestion_productos()
    elif st.session_state.pagina_actual == "gestion_usuarios":
        mostrar_gestion_usuarios()
    elif st.session_state.pagina_actual == "reportes":
        mostrar_reportes()
    elif st.session_state.pagina_actual == "perfil":
        mostrar_perfil()

# --- APLICACIÓN PRINCIPAL ---
def main():
    # Verificar si el usuario está logueado
    if not st.session_state.logueado:
        if st.session_state.pagina == "login":
            mostrar_login()
        elif st.session_state.pagina == "registro":
            mostrar_registro()
    else:
        mostrar_dashboard()

if __name__ == "__main__":
    main()