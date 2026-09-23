# 🏗️ Arquitectura Técnica - Sistema de Registro y QR

## 📐 Diagrama de Flujo de Datos

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   Login      │  │   Register   │  │   StudentDashboard   │ │
│  │   page.tsx   │  │   page.tsx   │  │   (QRAcceso.tsx)     │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘ │
│         │                  │                     │              │
│         │                  ├─────────────────────┘              │
│         │                  │                                    │
│  ┌──────▼──────────────────▼────────────────────▼───────────┐  │
│  │              Store (Zustand)                              │  │
│  │  • authStore.ts - Token, user, login/logout              │  │
│  │  • qrStore.ts - QR generation, scanning                  │  │
│  └──────────────────────────┬────────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────┘
                              │ HTTP Requests
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Layer                              │  │
│  │  • /api/v1/auth/register (POST)                          │  │
│  │  • /api/v1/auth/login (POST)                             │  │
│  │  • /api/v1/qr/generar (POST)                             │  │
│  │  • /api/v1/qr/escanear (POST)                            │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │              Service Layer                                │  │
│  │  • AuthService - Business logic para auth                │  │
│  │  • QRService - Business logic para QR                    │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │            Repository Layer                               │  │
│  │  • UserRepository - DB operations usuarios               │  │
│  │  • VehiculoRepository - DB operations vehículos          │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
│  ┌──────────────────────▼───────────────────────────────────┐  │
│  │                 Models (SQLAlchemy)                       │  │
│  │  • Usuario - users table                                 │  │
│  │  • Vehiculo - vehicles table                             │  │
│  │  • EspacioParqueo - parking spaces                       │  │
│  │  • Acceso - access logs                                  │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────────┘
                          │ SQL Queries
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PostgreSQL Database                           │
│  • usuarios (users)                                             │
│  • vehiculos (vehicles) → FK: id_usuario                        │
│  • espacios_parqueo (parking spaces)                            │
│  • accesos (access logs)                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Registro Completo

### 1. Frontend (register/page.tsx)

```typescript
// Estado del componente
const [nombre, setNombre] = useState("");
const [correo, setCorreo] = useState("");
const [password, setPassword] = useState("");
const [carnetId, setCarnetId] = useState("");
const [rol, setRol] = useState<string>("Estudiante");
const [tipoVehiculo, setTipoVehiculo] = useState<string>("");
const [placaVehiculo, setPlacaVehiculo] = useState("");

// Validación pre-submit
if (tipoVehiculo && !placaVehiculo) {
  setError("Si seleccionas un tipo de vehículo, debes ingresar la placa");
  return;
}

// Request al backend
const body = {
  nombre,
  correo,
  password,
  rol,
  ...(carnetId && { carnet_id: carnetId }),
  ...(tipoVehiculo && { tipo_vehiculo: tipoVehiculo }),
  ...(placaVehiculo && { placa_vehiculo: placaVehiculo }),
};

await fetch(`${API_BASE}/api/v1/auth/register`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});
```

### 2. Backend API (api/auth.py)

```python
@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService(db).register_student(
        nombre=request.nombre,
        correo=request.correo,
        password=request.password,
        carnet_id=request.carnet_id,
        rol=request.rol,
        tipo_vehiculo=request.tipo_vehiculo,
        placa_vehiculo=request.placa_vehiculo
    )
```

### 3. Schema Validation (schemas/auth.py)

```python
class RegisterRequest(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    carnet_id: Optional[str] = None
    rol: Literal["Estudiante", "Docente", "Administrativo", "Invitado", "VIP"]
    tipo_vehiculo: Optional[Literal["carro", "moto", "bicicleta", "vip"]]
    placa_vehiculo: Optional[str] = None
    
    @field_validator('placa_vehiculo')
    @classmethod
    def validate_placa(cls, v, info):
        if info.data.get('tipo_vehiculo') and not v:
            raise ValueError('La placa es obligatoria cuando se especifica un tipo de vehículo')
        return v.strip() if v else None
```

### 4. Service Layer (services/auth_service.py)

```python
def register_student(self, nombre, correo, password, carnet_id, rol, tipo_vehiculo, placa_vehiculo):
    # 1. Validar correo único
    existing_user = self.user_repo.get_by_email(correo)
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # 2. Validar carnet único
    if carnet_id:
        existing_carnet = self.db.query(Usuario).filter(
            Usuario.carnet_id == carnet_id
        ).first()
        if existing_carnet:
            raise HTTPException(status_code=400, detail="El carnet ya está registrado")
    
    # 3. Crear usuario
    hashed_password = get_password_hash(password)
    new_user = Usuario(
        nombre=nombre,
        correo=correo,
        password=hashed_password,
        rol=rol,
        estado="Activo",
        carnet_id=carnet_id
    )
    self.db.add(new_user)
    self.db.commit()
    self.db.refresh(new_user)
    
    # 4. Crear vehículo (opcional)
    vehiculo_registrado = False
    if tipo_vehiculo and placa_vehiculo:
        nuevo_vehiculo = Vehiculo(
            placa=placa_vehiculo,
            tipo=tipo_vehiculo,
            id_usuario=new_user.id_usuario
        )
        self.db.add(nuevo_vehiculo)
        self.db.commit()
        vehiculo_registrado = True
    
    return RegisterResponse(
        mensaje="Cuenta creada exitosamente",
        id_usuario=new_user.id_usuario,
        correo=new_user.correo,
        rol=new_user.rol,
        vehiculo_registrado=vehiculo_registrado
    )
```

---

## 🎫 Flujo de Generación de QR

### 1. Frontend (QRAcceso.tsx)

```typescript
// Estado del selector
const [tipoSeleccionado, setTipoSeleccionado] = useState<string>('');

// Validación pre-generación
const handleGenerarQR = () => {
  if (!tipoSeleccionado) {
    alert('Por favor selecciona el tipo de vehículo');
    return;
  }
  generarQR(idUsuario, idVehiculo, tipoSeleccionado);
};

// Grid de selectores
{TIPOS_VEHICULO.map((tipo) => (
  <button
    onClick={() => setTipoSeleccionado(tipo.value)}
    style={
      isSelected
        ? { borderColor: tipo.color, background: `${tipo.color}15` }
        : { borderColor: '#e2e8f0', background: '#fff' }
    }
  >
    <Icon /> {tipo.label}
  </button>
))}
```

### 2. Store (qrStore.ts)

```typescript
generarQR: async (id_usuario, id_vehiculo, tipo_vehiculo) => {
  set({ step: 'generating', error: null });
  
  const body = { 
    id_usuario,
    ...(id_vehiculo && { id_vehiculo }),
    ...(tipo_vehiculo && { tipo_vehiculo })
  };
  
  const res = await fetch(`${API_BASE}/api/v1/qr/generar`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(body),
  });
  
  const data = await res.json();
  
  // Calcular tiempo de expiración
  const seconds = Math.max(0, Math.floor(
    (new Date(data.expira_en) - new Date()) / 1000
  ));
  
  set({ step: 'show_qr', qrGenerado: data, secondsLeft: seconds });
}
```

### 3. Backend QR Service (services/qr_service.py)

```python
def generar_qr(self, data: QRGenerarRequest):
    # 1. Validar usuario existe
    usuario = self.db.query(Usuario).filter(
        Usuario.id_usuario == data.id_usuario
    ).first()
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    
    # 2. Determinar tipo de vehículo
    tipo_vehiculo = data.tipo_vehiculo  # Prioritario
    
    if not tipo_vehiculo and data.id_vehiculo:
        vehiculo = self.db.query(Vehiculo).filter(
            Vehiculo.id_vehiculo == data.id_vehiculo
        ).first()
        if vehiculo:
            tipo_vehiculo = vehiculo.tipo
    
    # 3. Buscar espacio del tipo especificado
    query = self.db.query(EspacioParqueo).filter(
        EspacioParqueo.status == "libre"
    )
    
    if tipo_vehiculo:
        # Intentar tipo exacto
        espacio = query.filter(EspacioParqueo.tipo == tipo_vehiculo).first()
        if not espacio:
            # Fallback: cualquier espacio libre
            espacio = query.first()
    else:
        espacio = query.first()
    
    if not espacio:
        raise HTTPException(409, "No hay espacios disponibles")
    
    # 4. Generar payload firmado
    now_utc = datetime.now(timezone.utc)
    expira_en = now_utc + timedelta(minutes=10)
    
    payload = {
        "espacio_id": espacio.id,
        "slot_id": espacio.slot_id,
        "id_usuario": data.id_usuario,
        "id_vehiculo": data.id_vehiculo,
        "emitido_en": now_utc.isoformat(),
        "expira_en": expira_en.isoformat(),
    }
    
    qr_token = sign_qr_payload(payload)  # HMAC SHA256
    qr_image_base64 = self._generar_imagen_qr(qr_token)  # qrcode lib
    
    return QRGeneradoResponse(
        espacio_id=espacio.id,
        slot_id=espacio.slot_id,
        label=espacio.label,
        tipo=espacio.tipo,
        qr_token=qr_token,
        qr_image_base64=qr_image_base64,
        expira_en=expira_en,
        mensaje=f"QR generado para el espacio {espacio.label}..."
    )
```

---

## 🗄️ Esquema de Base de Datos

### Tabla: usuarios

```sql
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    rol VARCHAR(50) NOT NULL,  -- Estudiante, Docente, Administrativo, Invitado, VIP
    estado VARCHAR(50) DEFAULT 'Activo',
    carnet_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usuarios_correo ON usuarios(correo);
CREATE INDEX idx_usuarios_carnet ON usuarios(carnet_id);
```

### Tabla: vehiculos

```sql
CREATE TABLE vehiculos (
    id_vehiculo SERIAL PRIMARY KEY,
    placa VARCHAR(20),
    tipo VARCHAR(20),  -- carro, moto, bicicleta, vip
    id_usuario INTEGER REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    rfid_tag_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_vehiculos_usuario ON vehiculos(id_usuario);
CREATE INDEX idx_vehiculos_placa ON vehiculos(placa);
```

### Relación

```
usuarios (1) ───< (N) vehiculos
  └─ id_usuario ───┐
                   │
                   └─> id_usuario (FK)
```

Un usuario puede tener múltiples vehículos (future-proof).

---

## 🔐 Seguridad Implementada

### 1. Password Hashing
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 2. JWT Token
```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 3. QR Token Signing (HMAC)
```python
import hmac
import hashlib
import json
import base64

def sign_qr_payload(payload: dict) -> str:
    json_str = json.dumps(payload, sort_keys=True)
    signature = hmac.new(
        SECRET_KEY.encode(),
        json_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    signed = {"payload": payload, "signature": signature}
    return base64.b64encode(json.dumps(signed).encode()).decode()

def verify_qr_signature(payload_with_sig: dict) -> bool:
    payload = payload_with_sig["payload"]
    signature = payload_with_sig["signature"]
    
    json_str = json.dumps(payload, sort_keys=True)
    expected_sig = hmac.new(
        SECRET_KEY.encode(),
        json_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_sig)
```

---

## 🎨 Componentes UI Reutilizables

### Selector de Opciones (Pattern)

```typescript
// Definir opciones
const OPCIONES = [
  { value: 'opcion1', label: 'Opción 1', icon: Icon1, color: '#color1' },
  { value: 'opcion2', label: 'Opción 2', icon: Icon2, color: '#color2' },
];

// Estado
const [seleccionado, setSeleccionado] = useState<string>('');

// Render
<div className="grid grid-cols-2 gap-2">
  {OPCIONES.map((opcion) => {
    const Icon = opcion.icon;
    const isSelected = seleccionado === opcion.value;
    return (
      <motion.button
        key={opcion.value}
        whileTap={{ scale: 0.96 }}
        onClick={() => setSeleccionado(opcion.value)}
        className="flex flex-col items-center gap-2 p-4 rounded-2xl border-2"
        style={
          isSelected
            ? { borderColor: opcion.color, background: `${opcion.color}15` }
            : { borderColor: '#e2e8f0', background: '#fff' }
        }
      >
        <Icon size={24} style={{ color: isSelected ? opcion.color : '#94a3b8' }} />
        <span className="text-xs font-bold" style={{ color: isSelected ? opcion.color : '#94a3b8' }}>
          {opcion.label}
        </span>
      </motion.button>
    );
  })}
</div>
```

---

## 📊 Performance Optimizations

### Frontend

1. **Lazy Loading del QRScanner**
```typescript
const QRScanner = dynamic(() => import('@/components/QRScanner'), {
  ssr: false,  // No renderizar en servidor (usa html5-qrcode)
  loading: () => <Loader />
});
```

2. **Zustand Store - No re-renders innecesarios**
```typescript
// Solo subscribe a la parte del estado que necesitas
const step = useQRStore((s) => s.step);  // No a todo el store
```

3. **Memoización con useMemo/useCallback**
```typescript
const tiposFiltrados = useMemo(() => 
  TIPOS_VEHICULO.filter(t => t.value !== 'vip' || user.rol === 'VIP'),
  [user.rol]
);
```

### Backend

1. **Índices en BD**
- `idx_usuarios_correo` → búsqueda rápida por email
- `idx_usuarios_carnet` → validación carnet duplicado
- `idx_vehiculos_usuario` → joins eficientes

2. **Query Optimization**
```python
# Evitar N+1
usuarios_con_vehiculos = self.db.query(Usuario).options(
    joinedload(Usuario.vehiculos)
).all()

# En vez de:
for usuario in usuarios:
    vehiculos = self.db.query(Vehiculo).filter(
        Vehiculo.id_usuario == usuario.id
    ).all()  # N queries!
```

---

## 🧩 Patrones de Diseño Utilizados

### 1. Repository Pattern
```python
class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_email(self, email: str) -> Usuario:
        return self.db.query(Usuario).filter(Usuario.correo == email).first()
    
    def create(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
```

### 2. Service Layer Pattern
```python
class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def register_student(self, ...):
        # Business logic aquí
        pass
```

### 3. Dependency Injection
```python
@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService(db).register_student(...)
```

### 4. Factory Pattern (QR Image)
```python
def _generar_imagen_qr(self, qr_token: str) -> str:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    # ... convert to base64
    return f"data:image/png;base64,{b64}"
```

---

## 🔧 Tecnologías Utilizadas

### Frontend
- **Next.js 14** - Framework React
- **TypeScript** - Type safety
- **Zustand** - State management
- **Framer Motion** - Animaciones
- **Tailwind CSS** - Styling
- **Lucide React** - Iconos
- **html5-qrcode** - Escaneo QR con cámara

### Backend
- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **Pydantic** - Validación datos
- **Passlib + Bcrypt** - Password hashing
- **PyJWT** - JWT tokens
- **python-qrcode** - Generación QR
- **Pillow** - Procesamiento imágenes

### Database
- **PostgreSQL 15** - Base de datos relacional
- **Alembic** - Migraciones

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Eclipse Mosquitto** - MQTT broker

---

## 📈 Escalabilidad

### Horizontal Scaling Ready

1. **Stateless Backend**
   - No sesiones en memoria
   - JWT tokens (no server-side sessions)
   - Puede escalar a múltiples instancias

2. **Database Connection Pooling**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

3. **API Rate Limiting** (futuro)
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/register")
@limiter.limit("5/minute")
def register(...):
    pass
```

---

## 📝 Conclusión

El sistema implementa una arquitectura limpia, escalable y mantenible con:
- ✅ Separación clara de responsabilidades (API → Service → Repository)
- ✅ Validaciones en múltiples capas (Frontend, Pydantic, DB constraints)
- ✅ Seguridad robusta (bcrypt, JWT, HMAC)
- ✅ UI/UX moderna con Framer Motion y Tailwind
- ✅ Code reusability (componentes, patterns)
- ✅ Performance optimizations (índices, lazy loading)
- ✅ Future-proof (relación 1-N usuarios-vehículos)
