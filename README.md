Memoria Técnica

1. URL pública donde se ha desplegado la aplicación en el cloud:

https://parcial2-ignacio-segovia.vercel.app/

2. URL del repositorio GitHub desde el que se realiza el despliegue:

https://github.com/IgnacioSZ1904/Parcial2IgnacioSegovia

3. Tecnologías utilizadas:

# 3.1. Infraestructura y Despliegue (Cloud Provider)
Vercel: Plataforma Platform as a Service (PaaS) seleccionada para el despliegue en producción.

Justificación: Vercel adapta automáticamente la aplicación FastAPI a una arquitectura Serverless Function, lo que optimiza el consumo de recursos y facilita la integración continua (CI/CD) directamente desde el repositorio de GitHub.

# 3.2. Backend (Lógica del Servidor)
Lenguaje: Python 3.12: Elegido por su legibilidad, tipado estático opcional (Type Hints) y amplio ecosistema de librerías.

Framework Web: FastAPI: Utilizado para la gestión de rutas HTTP, inyección de dependencias y validación de datos.

Componentes clave:

Uvicorn: Servidor ASGI de alto rendimiento para procesar peticiones asíncronas.

Starlette SessionMiddleware: Gestión de sesiones de usuario mediante cookies firmadas segura.

Jinja2: Motor de plantillas utilizado para el renderizado del HTML en el servidor (SSR), inyectando los datos de la base de datos directamente en las vistas.

# 3.3. Persistencia de Datos
Base de Datos: MongoDB Atlas: Base de datos NoSQL orientada a documentos, desplegada en la nube (DBaaS).

Justificación: El formato de documentos BSON/JSON se adapta naturalmente a la estructura variable de las reseñas y permite escalabilidad horizontal.

Driver: PyMongo: Librería cliente para realizar operaciones síncronas de inserción y consulta desde Python.

# 3.4. Servicios Externos (APIs de Terceros)
Autenticación (OAuth 2.0): Google Identity Services.

Librería: Authlib. Se utiliza el flujo de Authorization Code para obtener tokens de acceso seguros, garantizando la identidad del autor de la reseña y extrayendo metadatos de auditoría (iat, exp).

Almacenamiento de Medios: Cloudinary.

Servicio SaaS utilizado para almacenar las imágenes subidas por los usuarios. Esto evita guardar archivos binarios en el sistema de archivos efímero de Vercel, devolviendo únicamente la URL pública para su almacenamiento en base de datos.

Geocoding: Nominatim (OpenStreetMap).

API REST consumida vía requests y fetch (cliente) para convertir direcciones postales en coordenadas geográficas (Latitud/Longitud).

# 3.5. Frontend y Visualización
Mapas Interactivos: Leaflet.js: Librería JavaScript ligera de código abierto.

Justificación: Permite renderizar mapas interactivos utilizando tiles de OpenStreetMap sin depender de claves de API propietarias (como Google Maps), favoreciendo una arquitectura basada en estándares abiertos.

Interfaz de Usuario: HTML5 semántico y CSS3 (Diseño Flexbox) para la maquetación de la interfaz tipo "dashboard" (Listado + Mapa). JavaScript (Vanilla ES6) para la interactividad asíncrona del buscador y los modales.

4. Instrucciones de instalacion y despliegue  en local y en la nube.

# 4.1. Ejecución en Entorno Local
Para ejecutar la aplicación en local, es necesario disponer de Python 3.10 o superior y Git instalados en el sistema.

Descomprimir y acceder al directorio: Descomprima el archivo entregado o clone el repositorio y abra una terminal en la raíz del proyecto ReViews/.

Creación del Entorno Virtual: Se recomienda aislar las dependencias del proyecto creando un entorno virtual.

Bash

# En Windows:
python -m venv entorno
.\entorno\Scripts\activate

# En macOS/Linux:
python3 -m venv entorno
source entorno/bin/activate
Instalación de Dependencias: Instale las librerías necesarias listadas en el archivo requirements.txt:

Bash

pip install -r requirements.txt

(En un proyecto real no deberíamos pasar el archivo .env por cuestiones de seguridad, pero al tratarse de una evaluación de mi trabajo va adjunto entre los entregables. En caso contrario se debería crear dicho archivo con los parámetros que contiene y enviar las claves de forma segura)

Ejecución del Servidor: Inicie el servidor ASGI Uvicorn:

Bash

uvicorn main:app --reload --host 0.0.0.0 --port 8000


La aplicación estará disponible en http://localhost:8000.

# 4.2. Despliegue en la Nube (Vercel)
El despliegue se ha realizado utilizando la integración continua de Vercel con GitHub.

Control de Versiones: El código fuente se sube a un repositorio de GitHub (excluyendo el archivo .env y la carpeta del entorno virtual mediante .gitignore).

Configuración del Proyecto en Vercel:

Se importa el repositorio desde el panel de control de Vercel.

Vercel detecta automáticamente el entorno Python.

En la sección "Environment Variables", se añaden manualmente todas las claves definidas en el archivo .env

Ajuste de OAuth (Crítico): Una vez desplegado, Vercel proporciona una URL pública (ej. https://reviews-app.vercel.app). Es necesario volver a la consola de Google Cloud Platform > Credenciales > Cliente OAuth y añadir esta nueva ruta a las URIs de redireccionamiento autorizadas:

https://reviews-app.vercel.app/auth/callback

Verificación: Tras el despliegue, la aplicación es accesible públicamente vía HTTPS, conectándose a la misma base de datos MongoDB Atlas y utilizando los servicios de Cloudinary configurados.

5. URI o credenciales de acceso a la base de datos:

MONGO_URI=mongodb+srv://ignaciosegovia:Database15*@enero2025.jbhtczc.mongodb.net/?retryWrites=true&w=majority&appName=enero2025

6. funcionalidad que se ha implementado, así como posibles limitaciones de la misma y problemas encontrados durante el desarrollo de la aplicación.

# 6.1. Funcionalidad Implementada
La aplicación ReViews ha sido desarrollada cumpliendo la totalidad de los requisitos funcionales especificados en el enunciado, organizándose en los siguientes módulos:

Autenticación y Sesiones (OAuth 2.0):

Sistema de Login/Logout integrado con Google.

Protección de rutas: El acceso al feed y a la creación de reseñas está restringido a usuarios autenticados.

Persistencia de sesión mediante cookies firmadas seguras.

Auditoría de seguridad: Almacenamiento del token de acceso original, junto con sus marcas de tiempo de emisión (iat) y expiración (exp) para garantizar la trazabilidad de la autoría.

Gestión de Reseñas (CRUD):

Visualización: Interfaz de doble panel (Listado + Mapa). Las reseñas muestran nombre, dirección, coordenadas GPS calculadas, valoración numérica e imágenes asociadas.

Creación: Formulario avanzado que permite la subida de múltiples imágenes simultáneas (procesadas en la nube) y geocodificación automática de la dirección postal introducida.

Detalles: Modal interactivo que expande la información de la reseña, mostrando la galería de imágenes completa y los metadatos técnicos del token OAuth.

Geolocalización y Mapas:

Integración de mapas interactivos mediante Leaflet.js.

Geocoding Servidor: Conversión de direcciones a coordenadas (Lat/Lon) utilizando la API de Nominatim durante el guardado de la reseña.

Buscador Asíncrono: Implementación de una API interna (/api/search) consumida vía AJAX para permitir al usuario buscar direcciones y recentrar el mapa dinámicamente sin necesidad de recargar la página completa.

# 6.2. Limitaciones del Sistema
A pesar de cumplir con los objetivos académicos, el sistema presenta limitaciones propias de un prototipo que deberían abordarse en un entorno de producción real:

Escalabilidad del Geocoding: El servicio Nominatim (OpenStreetMap) tiene políticas de uso estricto (límite de 1 petición/segundo). En un escenario de alta concurrencia, el sistema podría recibir errores HTTP 429. Solución: Implementar una cola de tareas (Celery) o migrar a un proveedor de pago.

Ausencia de Paginación: Actualmente, el sistema carga la totalidad de las reseñas de la base de datos en la vista principal. Con un volumen masivo de datos (ej. miles de reseñas), esto afectaría gravemente al rendimiento del navegador y del servidor. Solución: Implementar paginación o infinite scroll en el backend.

Persistencia de Imágenes: La dependencia de un servicio externo gratuito (Cloudinary) implica límites en el ancho de banda y almacenamiento.

# 6.3. Problemas Encontrados y Soluciones
Durante el ciclo de desarrollo se superaron varios desafíos técnicos significativos:

Serialización JSON de Objetos MongoDB:

Problema: El motor de plantillas Jinja2 lanzaba excepciones al intentar convertir los objetos nativos de la base de datos (como ObjectId y datetime) a formato JSON para ser consumidos por JavaScript.

Solución: Se implementó una capa de saneamiento (sanitization) en el controlador antes de enviar los datos a la vista, convirtiendo los identificadores y fechas a cadenas de texto estándar (String e ISO 8601).

Configuración de OAuth en Despliegue:

Problema: Google OAuth rechazaba las peticiones tras el despliegue en la nube debido a la discrepancia entre las URIs de redirección (localhost vs vercel.app).

Solución: Se configuró el cliente OAuth para detectar dinámicamente el entorno y se actualizaron las credenciales en Google Cloud Console para admitir ambas URIs de callback.