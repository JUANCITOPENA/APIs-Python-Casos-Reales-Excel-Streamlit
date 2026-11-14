# 📘 Manual Maestro: Creación de Repositorio en GitHub y Despliegue en Streamlit Cloud
### *Guía Definitiva Paso a Paso: Método Manual (Arrastrar y Soltar), Método por Comandos (Git CLI) y Publicación en la Nube*

[![GitHub](https://img.shields.io/badge/GitHub-Repo_Setup-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)
[![Git](https://img.shields.io/badge/Git-CLI_Commands-F05032?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)
[![Streamlit Cloud](https://img.shields.io/badge/Streamlit_Cloud-Deploy_24%2F7-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://share.streamlit.io/)
[![Author](https://img.shields.io/badge/Author-Ing._Juancito_Peña-1E3A8A?style=for-the-badge&logo=github&logoColor=white)](https://github.com/JUANCITOPENA)

---

## 🎯 Objetivo del Manual

Este manual ha sido elaborado para que cualquier estudiante, desarrollador o analista de datos aprenda **desde cero y sin frustraciones** a:
1. Subir su proyecto local a un repositorio oficial en **GitHub** utilizando **dos métodos alternativos**:
   * **Método 1 (Gráfico / Principiantes):** Arrastrar y soltar (*Drag & Drop*) directamente desde el navegador web.
   * **Método 2 (Terminal / Profesional):** Mediante comandos estándar de **Git** en la consola.
2. Desplegar la aplicación web interactiva en la nube de forma **100% gratuita** utilizando **Streamlit Community Cloud**, dejándola disponible en internet con una URL pública accesible desde cualquier computadora o teléfono móvil.

---

## 🖱️ MÉTODO 1: Creación y Subida Manual en GitHub (Arrastrar y Soltar)

Este método es ideal si no tienes Git instalado en tu computadora o si prefieres una interfaz 100% visual en el navegador.

### Paso 1.1: Iniciar sesión en GitHub y crear el repositorio
1. Abre tu navegador web e ingresa a [https://github.com](https://github.com).
2. Inicia sesión con tu usuario (por ejemplo, **JUANCITOPENA**).
3. En la esquina superior derecha, haz clic en el icono **`+`** y selecciona **"New repository"** (o ingresa directamente a [https://github.com/new](https://github.com/new)).

### Paso 1.2: Configurar los datos del repositorio
Completa los campos tal como se indica a continuación:
* **Repository name:** `APIs-Python-Casos-Reales-Excel-Streamlit` *(o el nombre alusivo que prefieras)*.
* **Description:** `Ecosistema de APIs en Python con casos reales: monitor de divisas, pipeline ETL con Excel contable y dashboard ejecutivo en Streamlit Cloud.`
* **Visibility:** Selecciona **`Public`** (obligatorio para desplegar gratis en Streamlit Cloud).
* ⚠️ **MUY IMPORTANTE (Atención aquí):**
  * **NO** marques la casilla *"Add a README file"*.
  * **NO** agregues `.gitignore`.
  * **NO** elijas licencia en este paso.
  *(Debe crearse un repositorio totalmente vacío para que GitHub te muestre la pantalla de subida manual).*
4. Haz clic en el botón verde **"Create repository"**.

### Paso 1.3: Acceder a la zona de carga de archivos
Al crearse el repositorio vacío, verás una pantalla con instrucciones de código. Busca el enlace que dice:
> *"Get started by creating a new file or **uploading an existing file**."*

Haz clic directamente en el texto azul **"uploading an existing file"**.

### Paso 1.4: Arrastrar los archivos del proyecto
1. Abre el **Explorador de Archivos de Windows** y navega a la carpeta de tu proyecto:
   `C:\Users\User\Desktop\USO DE API CON PYTHON, REPO EXCEL EN GITHUB  + DASHBOARD EN STREAMLIT`
2. Selecciona los siguientes archivos clave:
   * ✅ `app.py`
   * ✅ `estados_financieros_rd_Stramlit.py`
   * ✅ `estados_financieros_rd.py`
   * ✅ `divisas.py`
   * ✅ `estados_financieros_rd.xlsx`
   * ✅ `requirements.txt`
   * ✅ `README.md`
   * ✅ `MANUAL_CREACION_REPO_Y_DESPLIEGUE.md`
   * ✅ Las guías adicionales con extensión `.md`
3. Arrástralos con el ratón y suéltalos dentro del recuadro punteado de GitHub que dice:  
   **"Drag files here to add them to your repository"**.
4. Verás una barra de progreso mientras los archivos se cargan al servidor.

> 🚫 **REGLA DE ORO / ADVERTENCIA CRÍTICA:**  
> **NUNCA arrastres la carpeta `venv`**. Esa carpeta contiene miles de archivos temporales del entorno virtual de tu computadora que pesan cientos de megabytes. GitHub bloqueará la subida o tu repositorio quedará dañado.

### Paso 1.5: Guardar el Commit inicial
1. En la parte inferior de la página, en la sección **"Commit changes"**:
   * En el título escribe: `feat: carga inicial del ecosistema de APIs, ETL Excel y Streamlit`
   * En la descripción (opcional): `Incluye scripts de consola, libro contable y app web.`
2. Asegúrate de que esté seleccionada la opción **"Commit directly to the main branch"**.
3. Haz clic en el botón verde **"Commit changes"**.
4. ¡Listo! En unos segundos verás tu repositorio completamente estructurado con su `README.md` formateado.

---

## 💻 MÉTODO 2: Creación y Subida Profesional con Comandos de Git (CLI)

Este es el estándar industrial utilizado por ingenieros de software, automatizable y perfecto para versionar cambios continuos.

### Paso 2.1: Verificar Git y configurar identidad
Abre tu terminal (**PowerShell** o **Git Bash**) y confirma que tienes Git instalado:
```bash
git --version
```
Si es la primera vez que usas Git en esta máquina, define tu nombre y correo:
```bash
git config --global user.name "JUANCITOPENA"
git config --global user.email "juancito.pena.v@hotmail.com"
```

### Paso 2.2: Ubicarse en la carpeta del proyecto
```powershell
Set-Location "C:\Users\User\Desktop\USO DE API CON PYTHON, REPO EXCEL EN GITHUB  + DASHBOARD EN STREAMLIT"
```

### Paso 2.3: Inicializar el repositorio Git
```bash
git init
```
*(Esto creará la carpeta oculta `.git` donde se almacenará el historial de versiones).*

### Paso 2.4: Crear el archivo `.gitignore`
Para evitar subir archivos innecesarios como el entorno virtual o cachés de Python, crea el archivo `.gitignore` con este contenido:
```text
# Entorno virtual
venv/
env/
.venv/

# Caché de Python
__pycache__/
*.pyc

# Archivos de sistema operativo e IDEs
.DS_Store
Thumbs.db
.vscode/
.idea/
```

### Paso 2.5: Agregar los archivos al área de preparación (*Staging Area*)
```bash
git add .
```
*(El punto `.` indica que se agregarán todos los archivos respetando las exclusiones del `.gitignore`).*

### Paso 2.6: Registrar el primer commit
```bash
git commit -m "feat: initial commit con arquitectura de APIs, Excel ETL y Streamlit Dashboard"
```

### Paso 2.7: Renombrar la rama principal a `main`
```bash
git branch -M main
```

### Paso 2.8: Crear el repositorio remoto en GitHub
1. Ve a [https://github.com/new](https://github.com/new).
2. Crea el repositorio con el nombre: `APIs-Python-Casos-Reales-Excel-Streamlit` en modo **`Public`** (sin marcar README ni `.gitignore`).
3. Copia la URL del repositorio creado:
   `https://github.com/JUANCITOPENA/APIs-Python-Casos-Reales-Excel-Streamlit.git`

### Paso 2.9: Vincular el repositorio remoto y subir el código
En tu terminal ejecuta:
```bash
git remote add origin https://github.com/JUANCITOPENA/APIs-Python-Casos-Reales-Excel-Streamlit.git
git push -u origin main
```

*(Si Git te solicita autenticación, se abrirá una ventana de GitHub para autorizar con un clic mediante el Git Credential Manager de Windows o introduciendo un Personal Access Token).*

---

## ☁️ CÓMO PUBLICAR EL DASHBOARD EN STREAMLIT COMMUNITY CLOUD

Una vez que tu repositorio está subido en GitHub, el despliegue en la nube toma menos de 2 minutos y es totalmente gratuito.

### Paso 3.1: Entrar a Streamlit Community Cloud
1. Abre tu navegador y dirígete a: [https://share.streamlit.io](https://share.streamlit.io).
2. Haz clic en **"Sign in"** o **"Continue with GitHub"**.
3. Autoriza la conexión para que Streamlit pueda leer tus repositorios públicos de GitHub.

### Paso 3.2: Iniciar un nuevo despliegue
En tu panel principal de Streamlit (*Workspace*), haz clic en el botón azul superior:
👉 **"Create app"** (o **"New app"**).

Si te da opciones, selecciona:
* **"Deploy a public app from GitHub"** (o *"I already have an app"*).

### Paso 3.3: Configurar los parámetros del despliegue
Se presentará un formulario con tres casillas obligatorias:

1. **Repository:**
   Escribe o selecciona tu repositorio en la lista desplegable:
   ```text
   JUANCITOPENA/APIs-Python-Casos-Reales-Excel-Streamlit
   ```
2. **Branch:**
   Escribe la rama principal:
   ```text
   main
   ```
3. **Main file path:**
   Indica el archivo ejecutable de la aplicación:
   ```text
   app.py
   ```
   *(También puedes indicar `estados_financieros_rd_Stramlit.py`, pero `app.py` es el estándar internacional reconocido automáticamente por Streamlit).*

4. **App URL (Opcional - Personalización):**
   Puedes hacer clic en *"Advanced settings"* o en el lápiz de edición de la URL para asignarle un nombre personalizado, por ejemplo:
   `https://finanzas-api-rd.streamlit.app`

### Paso 3.4: Desplegar la aplicación
Haz clic en el botón azul:
🚀 **"Deploy!"**

### Paso 3.5: Monitorear el proceso de construcción (*Build Logs*)
1. En la esquina inferior derecha verás un icono de terminal o un globo flotante que dice *"Your app is baking"*.
2. Puedes hacer clic en **"Manage app"** -> **"View logs"** para ver cómo el servidor de Streamlit ejecuta:
   * Clonación de tu repositorio desde GitHub.
   * Detección automática del archivo `requirements.txt`.
   * Instalación de las librerías: `streamlit`, `pandas`, `openpyxl`, `requests`, `plotly`.
   * Puesta en marcha del proceso con `streamlit run app.py`.
3. En aproximadamente **45 a 90 segundos**, la pantalla cambiará y verás tu **Dashboard Financiero Interactivo** funcionando en vivo.

### Paso 3.6: Compartir tu Dashboard
* Copia la URL que aparece en la barra de direcciones de tu navegador (ejemplo: `https://tu-usuario-api-rd.streamlit.app`).
* Esta URL es pública, segura (HTTPS) y accesible desde cualquier navegador web en computadoras, tablets o smartphones.

---

## 🔄 ¿Cómo Actualizar el Dashboard en el Futuro?

Una de las grandes ventajas de Streamlit Community Cloud es el **Despliegue Continuo (CI/CD Automático)**:

* **Si modificas un archivo en tu computadora:**
  Solo debes hacer commit y push con Git:
  ```bash
  git add .
  git commit -m "update: ajustados indicadores financieros"
  git push origin main
  ```
* **Si usas la web de GitHub:**
  Solo edita o reemplaza el archivo en la página web de GitHub y guarda el commit.

⚡ **Streamlit Cloud detectará el cambio en GitHub automáticamente y reiniciará la aplicación en cuestión de segundos sin que tengas que hacer nada más.**

---

## 🛠️ Preguntas Frecuentes y Resolución de Incidencias

| Problema detectado | Causa probable | Solución inmediata |
| :--- | :--- | :--- |
| **`ModuleNotFoundError: No module named 'plotly'`** | El archivo `requirements.txt` falta o tiene errores tipográficos en el nombre de la librería. | Asegúrate de que `requirements.txt` esté en la raíz del repositorio con `plotly`, `pandas`, `openpyxl`, `requests` y `streamlit`. |
| **`FileNotFoundError: estados_financieros_rd.xlsx`** | El archivo Excel no se subió a la raíz del repositorio en GitHub. | Verifica en la pestaña *"Code"* de GitHub que el archivo `.xlsx` esté presente con el nombre exacto. |
| **La app tarda mucho en cargar o se duerme** | Las apps gratuitas de Streamlit se suspenden (*sleep*) tras varios días de inactividad. | Al ingresar a la URL, simplemente haz clic en el botón *"Yes, get this app back up!"* y despertará en 30 segundos. |
| **Error al subir archivos por Git: `remote origin already exists`** | Ya tenías un enlace remoto previo configurado. | Ejecuta: `git remote remove origin` y luego vuelve a vincularlo con `git remote add origin <URL>`. |

---

<!-- =========================================================================
     SECCIÓN: BIOGRAFÍA PROFESIONAL, FILOSOFÍA & STACK TÉCNICO (ING. JUANCITO PEÑA)
========================================================================== -->
<div align="center" style="margin-top: 40px; margin-bottom: 20px;">
  <hr style="border: 2px solid #000000; margin-bottom: 30px;" />
</div>

<div style="background: #FFFFFF; border: 2.5px solid #000000; border-radius: 14px; padding: 2rem; box-shadow: 6px 6px 0px #000000; margin-bottom: 2rem;">
  <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 2rem;">
    
    <!-- LATERAL IZQUIERDO: BIOGRAFÍA, FILOSOFÍA Y DOCENCIA -->
    <div style="flex: 1 1 480px;">
      
      <!-- Encabezado con Avatar Oficial y Badges -->
      <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
        <img 
          src="https://avatars.githubusercontent.com/u/38921558?v=4" 
          alt="Ing. Juancito Peña Vizcaíno" 
          style="width: 86px; height: 86px; object-fit: cover; border-radius: 50%; border: 2.5px solid #000000; box-shadow: 3px 3px 0px #000000; flex-shrink: 0;"
        >
        <div>
          <h3 style="color: #000000; font-weight: 800; margin: 0 0 6px 0;">Ing. Juancito Peña Vizcaíno</h3>
          <div style="display: flex; flex-wrap: wrap; gap: 6px;">
            <span style="background: #000000; color: #FFFFFF; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold;">Data Analyst</span>
            <span style="background: #DA291C; color: #FFFFFF; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold;">Full Stack Dev</span>
            <span style="background: #0D6EFD; color: #FFFFFF; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold;">AI &amp; API Expert</span>
            <span style="background: #FFC107; color: #000000; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: bold;">Líder I+D+i</span>
          </div>
        </div>
      </div>
      
      <!-- PÁRRAFO 1: Trayectoria, Formación y Foco en I+D+i -->
      <p style="color: #0F172A; font-weight: 500; line-height: 1.65; margin-bottom: 0.75rem;">
        <strong>Ingeniero en Sistemas y Computación</strong> con Postgrado en <strong>Ingeniería de Software</strong> y Maestría en <strong>Sistemas Mención Gerencial</strong> (<em>Universidad Dominicana O&amp;M</em>). Con más de <strong>15 años de trayectoria</strong>, transformo problemas de alta complejidad en soluciones escalables. Durante el último año, he centrado mi trabajo en <strong>I+D+i (Investigación, Desarrollo e Innovación)</strong>, explorando arquitecturas de <strong>IA Generativa (RAG / LLMs)</strong>, integración de agentes autónomos con bases de datos y orquestación de APIs empresariales.
      </p>

      <!-- PÁRRAFO 2: ADN Técnico, Pasión por los Casos de Uso y Docencia Práctica -->
      <p style="color: #0F172A; font-weight: 500; line-height: 1.65; margin: 0;">
        🔬 <strong>Mi motor es el aprendizaje a través de los retos:</strong> me apasionan los <em>casos de uso reales</em>, las <strong>pruebas técnicas rigurosas</strong>, la investigación profunda y el diseño de soluciones directas a problemas de ingeniería. 🎓 Como <strong>docente universitario</strong> y creador del canal educativo <strong>@JuancitoDevV</strong>, comparto este conocimiento práctico mediante ejercicios y proyectos de código abierto para acercar la tecnología a problemas reales. 🚀
      </p>

    </div>

    <!-- LATERAL DERECHO: STACK VISUAL AGRUPADO & CANALES OFICIALES -->
    <div style="flex: 1 1 380px;">
      
      <div style="margin-bottom: 1.25rem;">
        <h4 style="font-weight: 800; margin: 0 0 10px 0; color: #000000;">
          ⚡ Ecosistema de Tecnologías:
        </h4>

        <!-- 1. Frontend & Web -->
        <div style="margin-bottom: 8px;">
          <small style="display: block; font-weight: bold; color: #000000; font-size: 0.8rem; margin-bottom: 3px;">🖥️ Frontend &amp; Web:</small>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" width="14" style="vertical-align: middle;"> HTML5</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" width="14" style="vertical-align: middle;"> CSS3</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" width="14" style="vertical-align: middle;"> JavaScript</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg" width="14" style="vertical-align: middle;"> React</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/nextjs/nextjs-original.svg" width="14" style="vertical-align: middle;"> Next.js</span>
        </div>

        <!-- 2. Backend & Multiplataforma -->
        <div style="margin-bottom: 8px;">
          <small style="display: block; font-weight: bold; color: #000000; font-size: 0.8rem; margin-bottom: 3px;">⚙️ Backend &amp; Multiplataforma:</small>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/csharp/csharp-original.svg" width="14" style="vertical-align: middle;"> C#</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/dot-net/dot-net-original.svg" width="14" style="vertical-align: middle;"> .NET / MAUI</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="14" style="vertical-align: middle;"> Python</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/php/php-original.svg" width="14" style="vertical-align: middle;"> PHP</span>
        </div>

        <!-- 3. Datos & Analítica -->
        <div style="margin-bottom: 8px;">
          <small style="display: block; font-weight: bold; color: #000000; font-size: 0.8rem; margin-bottom: 3px;">📊 Data Analytics &amp; Bases de Datos:</small>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/microsoftsqlserver/microsoftsqlserver-plain.svg" width="14" style="vertical-align: middle;"> SQL Server</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" width="14" style="vertical-align: middle;"> PostgreSQL</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mysql/mysql-original.svg" width="14" style="vertical-align: middle;"> MySQL</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;">📊 Power BI / DAX</span>
        </div>

        <!-- 4. IA, APIs & Cloud -->
        <div>
          <small style="display: block; font-weight: bold; color: #000000; font-size: 0.8rem; margin-bottom: 3px;">🤖 IA + APIs &amp; Despliegue (I+D+i):</small>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;">🔌 APIs REST</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;">🧠 IA + LLMs (RAG)</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;">🤖 Agentes IA</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" width="14" style="vertical-align: middle;"> Git</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;"><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" width="14" style="vertical-align: middle;"> GitHub</span>
          <span style="display: inline-block; background: #FFFFFF; border: 1.5px solid #000000; padding: 2px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: bold; margin: 2px; box-shadow: 2px 2px 0 #000000;">▲ Vercel</span>
        </div>
      </div>

      <!-- Redes Sociales Oficiales -->
      <div>
        <h5 style="font-weight: 800; margin: 0 0 8px 0; color: #000000;">Canales Oficiales &amp; Redes:</h5>
        
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
          <a href="https://www.linkedin.com/in/juancitope%C3%B1a/" target="_blank" style="width: 42px; height: 42px; background: #FFFFFF; border: 2px solid #000000; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.2rem; box-shadow: 3px 3px 0px #000000; text-decoration: none;" title="LinkedIn Oficial" rel="noopener noreferrer">
            🔗
          </a>
          <a href="https://www.youtube.com/@JuancitoDevV" target="_blank" style="width: 42px; height: 42px; background: #FFFFFF; border: 2px solid #000000; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.2rem; box-shadow: 3px 3px 0px #000000; text-decoration: none;" title="YouTube @JuancitoDevV" rel="noopener noreferrer">
            📺
          </a>
          <a href="https://github.com/JUANCITOPENA" target="_blank" style="width: 42px; height: 42px; background: #FFFFFF; border: 2px solid #000000; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.2rem; box-shadow: 3px 3px 0px #000000; text-decoration: none;" title="GitHub @JUANCITOPENA" rel="noopener noreferrer">
            🐙
          </a>
          <a href="https://twitter.com/JuancitoPenaV" target="_blank" style="width: 42px; height: 42px; background: #FFFFFF; border: 2px solid #000000; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.2rem; box-shadow: 3px 3px 0px #000000; text-decoration: none;" title="X (Twitter) @JuancitoPenaV" rel="noopener noreferrer">
            🐦
          </a>
          <a href="mailto:juancito.pena@gmail.com" style="width: 42px; height: 42px; background: #FFFFFF; border: 2px solid #000000; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.2rem; box-shadow: 3px 3px 0px #000000; text-decoration: none;" title="Correo Electrónico">
            ✉️
          </a>
        </div>

        <!-- Tarjeta Promocional de YouTube -->
        <div style="padding: 10px 14px; background: #FFFFFF; border: 2px solid #000000; border-radius: 8px; box-shadow: 3px 3px 0px #000000;">
          <small style="display: block; font-weight: bold; color: #DC2626;">Canal Educativo de YouTube:</small>
          <a href="https://www.youtube.com/@JuancitoDevV" target="_blank" style="font-weight: 800; color: #000000; text-decoration: none; font-size: 0.9rem;" rel="noopener noreferrer">
            ▶️ @JuancitoDevV · Algoritmos, SQL, IA &amp; .NET ↗
          </a>
        </div>

      </div>

    </div>

  </div>
</div>

<!-- =========================================================================
     FOOTER OFICIAL NEO-BRUTALIST (ING. JUANCITO PEÑA)
========================================================================== -->
<footer style="background: #FFFFFF; border-top: 3px solid #000000; padding: 2rem 1.5rem; width: 100%; color: #000000;">
  <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
    <div>
      <span style="background: #000000; color: #FFFFFF; border: 1.5px solid #000000; padding: 3px 8px; font-size: 0.75rem; font-weight: bold; margin-right: 8px;">PROYECTO OFICIAL JPV</span>
      <strong>Sistemas, Datos &amp; Arquitectura de Software</strong>
      <p style="font-size: 0.85rem; margin: 4px 0 0 0; color: #64748B;">
        Plataforma de grado industrial desarrollada bajo estándares de alto rendimiento, accesibilidad universal y diseño limpio.
      </p>
      <p style="font-size: 0.75rem; margin: 6px 0 0 0; color: #475569;">
        <strong>Aviso Académico &amp; Autoría:</strong> Diseñado, desarrollado y certificado por el <strong>Ing. Juancito Peña Vizcaíno</strong>. Todos los derechos reservados.
      </p>
    </div>
    <div>
      <a href="#" style="color: #DC2626; font-weight: bold; text-decoration: none; font-size: 0.9rem;">
        ⬆️ Volver al Inicio
      </a>
    </div>
  </div>
</footer>
