# Backend API - La Capital del Móvil

## 📦 Requisitos

- Cuenta de GitHub
- Cuenta en https://render.com

## 🚀 Instrucciones paso a paso

### 1. Sube el proyecto a GitHub

```bash
cd ruta/del/proyecto
git init
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git add .
git commit -m "Backend API con token real y CORS"
git branch -M main
git push -u origin main
```

### 2. Entra a Render

- Ve a https://render.com
- Crea nuevo Web Service
- Conecta tu cuenta de GitHub
- Selecciona el repo
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn Servidor.server:app`
- Python version: `3.11`
- Region: `Frankfurt` (para mejor latencia en Europa)
- Click en **Create Web Service**

Y listo 🎉

Tu API estará disponible en una URL como:  
`https://api-lacapital.onrender.com/categorias`