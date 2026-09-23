# 🧪 Guía de Testing - Nuevas Funcionalidades SmartParkU

## 🚀 Preparación del Entorno

### 1. Asegurarse de estar en la rama correcta
```bash
git branch  # Verificar que estés en 'develop'
```

### 2. Levantar los servicios
```bash
# Si Docker no está corriendo:
docker-compose up -d

# Verificar que todos los contenedores estén activos:
docker-compose ps
```

Deberías ver:
- ✅ smartparku_backend (puerto 8000)
- ✅ smartparku_frontend (puerto 3001)
- ✅ smartparku_db (PostgreSQL, puerto 5432)
- ✅ smartparku_mqtt (puerto 1883)
- ✅ smartparku_pgadmin (puerto 8080)

### 3. Acceder a la aplicación
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000/docs (Swagger)
- PgAdmin: http://localhost:8080

---

## ✅ Test 1: Botón "Crear cuenta" en Login

### Pasos:
1. Abrir http://localhost:3001
2. Desplazarse al final de la pantalla
3. Buscar el texto: "¿No tienes cuenta?"
4. Hacer clic en el botón verde **"Crear cuenta"**

### Resultado esperado:
✅ Navega a la página de registro (URL: /register)
✅ Se muestra el formulario completo de registro

### Validación visual:
- Botón en color verde UCC (#6AB023)
- Efecto hover: underline
- Texto en negrita

---

## ✅ Test 2: Registro de Estudiante con Motocicleta

### Datos de prueba:
```
Nombre: Juan Pérez García
Correo: juan.test@ucc.edu.co
Documento: 123456789
Contraseña: test123456
Rol: Estudiante (default)
Tipo Vehículo: Motocicleta
Placa: ABC123
```

### Pasos:
1. Desde login, clic en "Crear cuenta"
2. Completar todos los campos como arriba
3. **Seleccionar ROL:** Clic en card "Estudiante" (debe resaltar en azul)
4. **Seleccionar Tipo Vehículo:** Clic en card "Motocicleta" (debe resaltar en verde)
5. **Campo Placa aparece automáticamente**
6. Ingresar placa "ABC123"
7. Clic en "Crear Cuenta"

### Resultados esperados:
✅ Pantalla de éxito con ícono de usuario
✅ Mensaje: "¡Cuenta Creada!"
✅ Después de 2.5 segundos redirige al login
✅ Backend creó usuario + vehículo en BD

### Validar en Base de Datos:
```sql
-- Conectar a PgAdmin (localhost:8080)
-- Ejecutar:
SELECT * FROM usuarios WHERE correo = 'juan.test@ucc.edu.co';
SELECT * FROM vehiculos WHERE placa = 'ABC123';
```

---

## ✅ Test 3: Registro de Docente SIN Vehículo

### Datos de prueba:
```
Nombre: María González
Correo: maria.docente@ucc.edu.co
Contraseña: docente2026
Rol: Docente
Tipo Vehículo: NO seleccionar
```

### Pasos:
1. Crear cuenta
2. Completar nombre, correo, contraseña
3. Seleccionar ROL: **Docente** (ícono de maleta)
4. **NO seleccionar tipo de vehículo** (dejar en blanco)
5. Clic en "Crear Cuenta"

### Resultados esperados:
✅ Cuenta creada exitosamente
✅ NO se creó vehículo en la BD
✅ Usuario con rol "Docente"

### Validar:
```sql
SELECT * FROM usuarios WHERE correo = 'maria.docente@ucc.edu.co';
-- Verificar: rol = 'Docente'

SELECT * FROM vehiculos WHERE id_usuario = (
  SELECT id_usuario FROM usuarios WHERE correo = 'maria.docente@ucc.edu.co'
);
-- Resultado: vacío (0 rows)
```

---

## ✅ Test 4: Validación - Tipo sin Placa

### Pasos:
1. Crear cuenta
2. Seleccionar tipo vehículo: **Bicicleta**
3. Campo placa aparece pero **NO ingresarla**
4. Intentar crear cuenta

### Resultado esperado:
❌ Error en rojo: "Si seleccionas un tipo de vehículo, debes ingresar la placa"
❌ NO envía el request al backend
✅ Usuario puede corregir y reintentar

---

## ✅ Test 5: Validación - Correo Duplicado

### Pasos:
1. Registrar usuario con correo: test1@ucc.edu.co
2. Completar registro exitosamente
3. Intentar registrar OTRO usuario con el mismo correo

### Resultado esperado:
❌ Error: "El correo ya está registrado. Por favor inicia sesión o recupera tu contraseña."
✅ Usuario no se duplica en BD

---

## ✅ Test 6: Generación de QR - Seleccionar Tipo

### Pre-requisito:
- Usuario registrado e iniciado sesión (usar juan.test@ucc.edu.co)

### Pasos:
1. Hacer login con juan.test@ucc.edu.co
2. Dashboard de estudiante se muestra
3. Clic en pestaña **"QR"** en el menú inferior
4. Ver selector de 4 tipos de vehículo

### Validar UI:
✅ Grid 2x2 con 4 cards:
  - Carro (icono Car, azul)
  - Motocicleta (icono Bike, verde)
  - Bicicleta (icono Zap, lima)
  - VIP (icono Car, navy)
✅ Botón "Generar QR de Ingreso" DESACTIVADO (opaco)

### Continuar:
5. Seleccionar **Motocicleta**
6. Card se resalta en verde
7. Botón se ACTIVA
8. Clic en "Generar QR de Ingreso"

### Resultados esperados:
✅ Mensaje: "Buscando espacio libre..." (loader)
✅ Badge verde: "M-01" o "M-02" (espacio de moto)
✅ Imagen QR se muestra
✅ Línea animada escaneando
✅ Contador: 09:59 → 09:58 → ...

---

## ✅ Test 7: QR - Fallback de Tipo

### Escenario:
Simular que NO hay espacios de "carro" disponibles

### Preparar BD:
```sql
-- Marcar todos los espacios tipo 'carro' como ocupados
UPDATE espacios_parqueo 
SET status = 'ocupado' 
WHERE tipo = 'carro';
```

### Pasos:
1. En pantalla QR, seleccionar **Carro**
2. Clic en "Generar QR"

### Resultado esperado:
✅ Sistema NO falla
✅ Backend asigna un espacio de otro tipo (moto o bicicleta)
✅ QR se genera con label del tipo disponible
✅ Ejemplo: "M-01" (motocicleta) aunque pediste carro

### Restaurar BD después:
```sql
UPDATE espacios_parqueo 
SET status = 'libre' 
WHERE tipo = 'carro';
```

---

## ✅ Test 8: QR - Validación Sin Selección

### Pasos:
1. Pantalla QR
2. **NO seleccionar ningún tipo**
3. Intentar clic en "Generar QR"

### Resultado esperado:
✅ Botón permanece desactivado
✅ No pasa nada
✅ Cursor: not-allowed
✅ Opacidad: 40%

---

## ✅ Test 9: Registro VIP Completo

### Datos:
```
Nombre: Carlos VIP
Correo: carlos.vip@empresa.com
Contraseña: vip2026
Rol: VIP
Tipo Vehículo: VIP
Placa: VIP001
```

### Pasos:
1. Registro completo con datos arriba
2. Seleccionar card "VIP" en rol (color navy)
3. Seleccionar card "VIP" en tipo vehículo
4. Ingresar placa VIP001
5. Crear cuenta

### Validar:
```sql
SELECT u.*, v.* 
FROM usuarios u 
LEFT JOIN vehiculos v ON u.id_usuario = v.id_usuario
WHERE u.correo = 'carlos.vip@empresa.com';
```

✅ Usuario con rol = 'VIP'
✅ Vehículo con tipo = 'vip' y placa = 'VIP001'

### Luego generar QR:
1. Login como VIP
2. Generar QR tipo "VIP"
3. Debe asignar espacio "V-01"

---

## ✅ Test 10: Responsive Mobile

### Dispositivos a probar:
- iPhone 12 (375x667)
- iPhone 14 Pro Max (428x926)
- Samsung Galaxy S21 (360x800)
- iPad (768x1024)

### Herramientas:
- Chrome DevTools → Toggle device toolbar (Ctrl + Shift + M)

### Validar en cada resolución:
1. **Login:**
   - ✅ Panel azul solo en desktop (lg+)
   - ✅ Formulario centrado
   - ✅ Botón "Crear cuenta" visible

2. **Registro:**
   - ✅ Grid de roles responsivo (2 cols mobile, 3 desktop)
   - ✅ Grid de tipos vehículo 2x2
   - ✅ Scroll interno funciona
   - ✅ Todos los campos accesibles

3. **QR:**
   - ✅ Selector de tipos responsive
   - ✅ QR image tamaño adecuado
   - ✅ Contador visible

---

## ✅ Test 11: Navegación Completa

### Flujo end-to-end:

```
1. Landing (login)
   ↓ clic "Crear cuenta"
2. Registro completo
   ↓ submit
3. Éxito → Auto-redirect
   ↓ 2.5 seg
4. Login nuevamente
   ↓ ingresar credenciales
5. Dashboard estudiante
   ↓ clic "QR"
6. Seleccionar tipo
   ↓ generar
7. QR visible con contador
   ↓ simular escaneo (botón prueba)
8. Acceso registrado
   ↓ volver
9. Dashboard
```

✅ Todo el flujo sin errores
✅ Navegación suave
✅ Estados consistentes

---

## 🐛 Casos Edge a Probar

### 1. Placa en Mayúsculas
- Ingresar placa en minúsculas: "abc123"
- ✅ Debe convertirse a "ABC123" automáticamente

### 2. Espacios en Nombre
- Nombre: "  Juan   Pérez  "
- ✅ Backend hace trim(): "Juan Pérez"

### 3. Contraseña Corta
- Contraseña: "12345" (5 caracteres)
- ❌ Error: "La contraseña debe tener al menos 6 caracteres"

### 4. Email Inválido
- Email: "juan@" o "invalido"
- ❌ Validación HTML5 impide submit

### 5. Cambiar de Rol
- Seleccionar "Estudiante", luego "Docente"
- ✅ Solo "Docente" queda seleccionado

### 6. Cambiar de Tipo Vehículo
- Seleccionar "Carro", luego "Moto"
- ✅ Solo "Moto" queda seleccionado

---

## 📊 Checklist de Validación

### Frontend
- [ ] Botón "Crear cuenta" navega correctamente
- [ ] Formulario registro muestra todos los campos
- [ ] Selectores de rol funcionan
- [ ] Selectores de tipo vehículo funcionan
- [ ] Campo placa aparece condicionalmente
- [ ] Validaciones frontend funcionan
- [ ] Mensajes de error claros
- [ ] Animaciones Framer Motion suaves
- [ ] Responsive en mobile
- [ ] QR muestra selector de tipo
- [ ] Botón QR se activa solo con selección
- [ ] Estados loading correctos

### Backend
- [ ] Endpoint /register acepta nuevos campos
- [ ] Usuario se crea con rol especificado
- [ ] Vehículo se crea si hay datos
- [ ] Validación correo único funciona
- [ ] Validación carnet único funciona
- [ ] QR acepta tipo_vehiculo
- [ ] Backend busca espacio del tipo
- [ ] Fallback a otro tipo funciona
- [ ] Response incluye vehiculo_registrado

### Base de Datos
- [ ] Usuarios se insertan correctamente
- [ ] Vehículos se asocian al usuario
- [ ] Relación FK funciona
- [ ] Índices funcionan
- [ ] No hay duplicados de correo
- [ ] No hay duplicados de carnet

---

## 🎯 Métricas de Éxito

### Funcionalidad
- ✅ 100% de casos positivos pasan
- ✅ 100% de validaciones funcionan
- ✅ 0 errores 500 en backend
- ✅ 0 errores de consola en frontend

### Performance
- ✅ Registro < 2 segundos
- ✅ Generación QR < 1 segundo
- ✅ Navegación instantánea
- ✅ Animaciones 60fps

### UX
- ✅ Flujo intuitivo
- ✅ Mensajes claros
- ✅ Estados visibles
- ✅ Sin confusión en selectores

---

## 🚨 Qué Hacer si Falla un Test

### Error de Backend (500):
1. Revisar logs: `docker-compose logs backend`
2. Verificar BD: PgAdmin o psql
3. Verificar schemas en backend/app/schemas/
4. Verificar servicios en backend/app/services/

### Error de Frontend:
1. Abrir DevTools → Console
2. Verificar Network → Failed requests
3. Verificar import statements
4. Limpiar cache: Ctrl + Shift + R

### Error de BD:
1. Conectar a PgAdmin
2. Verificar que existan las tablas
3. Verificar columnas: `\d usuarios`, `\d vehiculos`
4. Si falta columna, ejecutar migración

---

## ✅ Aprobación Final

Para considerar la feature lista para producción:

- [ ] Todos los tests pasan
- [ ] Validaciones funcionan
- [ ] Responsive correcto
- [ ] Sin errores de consola
- [ ] Sin errores de sintaxis
- [ ] Documentación completa
- [ ] Code review aprobado

**Responsable de Testing:** _________
**Fecha de Testing:** _________
**Resultado:** PASS / FAIL
**Observaciones:** _________________
