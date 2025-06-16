EDUFLEX
------------------------------------
Sistema para monitorio de estudiantes con problemas de aprendisaje 

INTEGRANTES
-------------------------------------------------------
-Jean Carlos Suarez Acevedo

-Ricardo Alexander Diaz Rivas

-Francisco Javier Ronquillo Jimenez


DESCRIPCIÓN
---------------------------------------------------------
EDUFLEX es una plataforma web que combina inteligencia artificial y análisis visual en tiempo real para detectar somnolencia y distracción en niños durante juegos educativos. Utiliza un modelo preentrenado (MediaPipe Face Mesh) para analizar expresiones faciales y dirección de la mirada, generando reportes automáticos con métricas y evidencias visuales. Estos informes permiten a padres y docentes evaluar la atención y el estado cognitivo del niño de forma personalizada.

Caracteristicas 
--------------------------------------------------------
-Análisis facial en tiempo real usando MediaPipe Face Mesh.

-Evaluación continua durante la interacción lúdica.

-Juegos dinámicos diseñados para mantener la atención del niño.

-Seguimiento personalizado del rendimiento y estado de atención del niño.

-Panel para padres y profesores para visualizar reportes.

Requistos para correcto funcionamiento
---------------------------------------------------------
-Python 3.10 o superior

-SQL SERVER 2019 o superior

-Visual C++ Redistributable

-Git

Instrucciones de instalación y ejecución
----------------------------------------------------------
1. Crear entorno virtual
   
        python -m venv nombre_entorno #se recomiendo poner como nombre (ent,venv)
           
2. Activa el entorno

           # En Windows:
                nombre_entorno\Scripts\activate
           # En Mac/Linux:
                source venv/bin/activate

3. Instalacion de dependecias

           pip install -r requirements.txt

4. Crear un archivo .env

                touch .env

5. Debemos debemos configurar sql server
          #Si no sabes como mirar el video, minuto 6:12      
          https://www.youtube.com/watch?v=uMjYrfzwUpc&t=649s 

6. Agregar las configuracion de la base de datos en el archivo .env
   
        #Estos campos deben ir sin comillas, ya sean simples o dobles        
        DB_NAME=nombre_base_datos    
        DB_USER=usario_base_datos
        DB_PASSWORD=contraseña_base
        DB_HOST=localhost
        DB_PORT=1433
        
        SECRET_KEY=django-insecure-t+qa7xze3hqu@)#c26x1=*p-$czi6pst7oddcl0c29*4y-&7n^
        DEBUG=True      
        
7. Agregar las configuraciones de la recuperacion de contraseñas en el archivo .env

   video explicativo para conseguir la contraseña de aplicacion https://youtu.be/xnbGakU7vhE
   
        EMAIL_BACKEND = django.core.mail.backends.smtp.EmailBackend
        EMAIL_HOST = smtp.gmail.com 
        EMAIL_PORT = 587
        EMAIL_HOST_USER = correo_a_usar #usar un correo con dominio gmail.com
        EMAIL_HOST_PASSWORD = contraseña_aplicacion #no confundir con la contraseña del correo son diferentes
        EMAIL_USE_TLS = True

8. Iniciar la ejecucion

         python manage.py runserverr
   
Breve descripción de funcionalidades
----------------------------------------------------------
-Detección en tiempo real de somnolencia y distracción durante actividades mediante visión por computadora con MediaPipe.

-Juegos interactivos y educativos que evalúan la atención y el estado del niño.

-Generación automática de reportes con capturas e indicadores de comportamiento detectado (mirada desviada, ojos cerrados, etc.).

-Paneles diferenciados para profesores y padres, donde pueden visualizar los reportes y el progreso de cada niño.

-Almacenamiento organizado de evidencia visual (imágenes clasificadas por tipo de evento y niño).

-Gestión de usuarios, niños y sesiones de evaluación dentro de una plataforma web sencilla e intuitiv

