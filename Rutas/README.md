# Proyecto Plataforma de Material de Aprendizaje

## Descripción

Este proyecto es una plataforma web desarrollada con Python Flask y MongoDB que permite la gestión de materiales de aprendizaje. Los usuarios pueden registrarse como estudiantes, mientras que los administradores pueden crear y gestionar usuarios con roles de profesor o administrador. Los profesores pueden agregar y editar materiales, y los estudiantes pueden calificar materiales y profesores.

---

## Características principales

- **Registro y autenticación de usuarios** (solo estudiantes desde el registro público).
- **Gestión de roles:** administrador, profesor y estudiante.
- **Administración de usuarios** (solo por el administrador).
- **Gestión de materiales de aprendizaje** (solo profesores).
- **Calificación de materiales y profesores** (solo estudiantes).
- **Persistencia de datos con MongoDB**.
- **Interfaz web responsiva**.

---

## Arquitectura y buenas prácticas aplicadas

### Principios SOLID implementados

- **SRP (Single Responsibility Principle):**
  - Cada clase tiene una única responsabilidad. Por ejemplo, `UserRepository` solo gestiona el acceso a datos de usuarios, y `UserService` solo contiene la lógica de negocio de usuarios.
- **DIP (Dependency Inversion Principle):**
  - Las rutas dependen de servicios (`UserService`) que a su vez dependen de repositorios (`UserRepository`). Esto permite desacoplar la lógica de negocio del acceso a datos y facilita la escalabilidad y pruebas.

### Patrones de diseño aplicados

- **Repository Pattern:**
  - Implementado en `UserRepository`, que encapsula todas las operaciones de acceso a la base de datos para usuarios. Esto desacopla la lógica de negocio de la persistencia y permite cambiar la base de datos fácilmente si fuera necesario.
- **Service Layer Pattern:**
  - Implementado en `UserService`, que contiene la lógica de negocio relacionada con usuarios (registro, autenticación, etc.). Las rutas utilizan este servicio en lugar de acceder directamente al repositorio o la base de datos.

---

## Estructura de carpetas relevante

```
ProyectoProgreso2/
│
├── Rutas/
│   ├── routes.py           # Rutas principales de la aplicación
│   ├── forms.py            # Formularios WTForms
│   ├── models.py           # Modelos de datos (solo para estructuración, no ORM)
│   ├── UserRepository.py   # Repositorio de acceso a datos de usuario (Repository Pattern)
│   ├── UserService.py      # Lógica de negocio de usuario (Service Layer Pattern)
│   └── ...
│
├── templates/              # Plantillas HTML
├── static/                 # Archivos estáticos (CSS, JS, imágenes)
├── requirements.txt        # Dependencias del proyecto
└── ...
```

---

## Cambios y mejoras realizadas

- **Separación de responsabilidades:**  
  Se crearon los archivos `UserRepository.py` y `UserService.py` para separar el acceso a datos y la lógica de negocio, respectivamente.
- **Inyección de dependencias:**  
  El servicio de usuario (`UserService`) recibe el repositorio como dependencia, facilitando el testeo y la extensión.
- **Refactorización de rutas:**  
  Las rutas de registro y login ahora usan el servicio de usuario, eliminando lógica de negocio y acceso a datos directo en las vistas.
- **Validación y roles:**  
  El registro público solo permite crear estudiantes. Los administradores pueden crear y editar usuarios de cualquier rol.
- **Compatibilidad con MongoDB:**  
  Todo el acceso a datos se realiza usando PyMongo y colecciones de MongoDB, no SQLAlchemy.

---

## Ejemplo de flujo de registro y autenticación

1. **Registro de estudiante:**  
   - El usuario se registra desde la página pública.
   - El formulario no solicita el rol; el backend asigna automáticamente el rol "estudiante".
   - El servicio valida que el correo no exista y guarda el usuario usando el repositorio.

2. **Login:**  
   - El usuario ingresa sus credenciales.
   - El servicio valida el correo y la contraseña usando el repositorio.

3. **Gestión de usuarios (admin):**  
   - El administrador puede crear, editar y eliminar usuarios de cualquier rol desde el panel de administración.

---

## Instalación y ejecución

1. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

2. Configura las variables de entorno en un archivo `.env`:
   ```
   MONGODB_URI=mongodb://localhost:27017/tu_basededatos
   SECRET_KEY=tu_clave_secreta
   ```

3. Ejecuta la aplicación:
   ```
   flask run
   ```

---

## Créditos y agradecimientos

- Desarrollado por [Tu Nombre o Equipo].
- Basado en Flask, WTForms y MongoDB.

---

## Notas finales

Este proyecto es un ejemplo de cómo aplicar principios SOLID y patrones de diseño en una aplicación web real, mejorando la