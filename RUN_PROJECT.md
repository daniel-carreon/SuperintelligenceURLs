# 🚀 Cómo Correr LinkProxy Manualmente

## ✅ **ESTADO ACTUAL: BUCLE 1 COMPLETADO**
- ✅ Base de datos configurada en Supabase
- ✅ Backend API funcional (FastAPI)
- ✅ Algoritmo Base62 implementado
- ✅ Click tracking básico funcionando

## 🖥️ **CORRER EL BACKEND (API)**

```bash
# 1. Navegar al directorio backend
cd /Users/danielcarreon/Documents/AI/software/backend/

# 2. Activar el entorno virtual
source venv/bin/activate

# 3. Instalar dependencias (si no están instaladas)
pip install -r requirements.txt

# 4. Ejecutar el servidor FastAPI
python main.py
```

**El servidor se ejecutará en:** http://localhost:8000

### 📊 **Endpoints Disponibles:**
- **🏠 Health Check**: http://localhost:8000/
- **📖 API Docs**: http://localhost:8000/docs
- **🔗 Crear URL corta**: `POST http://localhost:8000/shorten`
- **🔄 Redirect**: `GET http://localhost:8000/{short_code}`
- **📈 Analytics**: `GET http://localhost:8000/analytics/{short_code}`

## 🧪 **PROBAR LA API**

### Método 1: Swagger UI (Recomendado)
1. Ir a http://localhost:8000/docs
2. Usar la interfaz interactiva para crear URLs y probar redirects

### Método 2: cURL
```bash
# Crear URL corta
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://google.com",
    "title": "Google Test",
    "is_active": true
  }'

# Respuesta ejemplo:
# {"short_code": "ABC123", "original_url": "https://google.com", ...}

# Probar redirect
curl -I "http://localhost:8000/ABC123"
# Respuesta: HTTP 301 -> Location: https://google.com

# Ver analytics
curl "http://localhost:8000/analytics/ABC123"
```

### Método 3: Test Script
```bash
# Ejecutar el script de prueba rápida que ya tienes
python test_quick.py
```

## ❌ **NO HAY FRONTEND AÚN**
**Estado actual:** Solo Backend API (Bucle 1 completado)
**Próximo:** Frontend vendrá en Bucle 3 (Dashboard Analytics)

## 🔧 **Para Desarrollo:**

### Ver Logs en Tiempo Real
```bash
python main.py
# Verás logs como:
# URL created: ABC123 -> https://google.com (0.24ms)
# Redirect: ABC123 -> https://google.com (0.07ms)
```

### Correr Tests
```bash
# Unit tests del algoritmo Base62
python -m pytest backend/tests/domain/services/test_url_generator.py -v

# Test rápido E2E de endpoints
python test_quick.py
```

## 🌐 **Base de Datos**
- **Supabase configurado** con tu project-ref: `hodawgekwhmbywubydau`
- **Schema aplicado** con tablas `urls` y `clicks`
- **Analytics functions** disponibles para queries SQL directos

## 🎯 **LO QUE YA FUNCIONA:**
1. ✅ **Crear URLs cortas** con códigos Base62 únicos
2. ✅ **Redirects HTTP 301** ultra-rápidos (<0.1ms)
3. ✅ **Click tracking automático** con metadata
4. ✅ **Analytics básicos** (clicks, devices, IPs)
5. ✅ **Error handling** para códigos inválidos

## 📋 **PRÓXIMOS BUCLES:**
- **Bucle 2.1**: Geolocalización (IP → País/Ciudad)
- **Bucle 2.2**: Device detection avanzado
- **Bucle 3.1**: Dashboard Frontend con Charts
- **Bucle 3.2**: Real-time WebSockets

---
*Ejecuta `python main.py` y ve a http://localhost:8000/docs para empezar a probar!* 🚀