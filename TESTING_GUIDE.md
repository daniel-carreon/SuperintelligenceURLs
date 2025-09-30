# 🧪 LinkProxy - Guía de Testing

## 🎯 Estado Actual

### Servidores Corriendo
- ✅ **Backend:** `http://localhost:8000`
- ✅ **Frontend:** `http://localhost:3001` (puerto 3000 estaba ocupado)

### URL de Prueba Creada
- **Short Code:** `KBLM46`
- **Original URL:** `https://youtube.com/@danielcarreon`
- **Title:** Canal de YouTube
- **Clicks:** 1 (testing)

---

## 📝 TESTING PASO A PASO

### 1️⃣ Abrir la Aplicación

```bash
# En tu navegador:
http://localhost:3001
```

**Qué deberías ver:**
- ✨ Background mesh con orbs flotantes (cyan, purple, pink)
- 🎨 Hero section con texto holográfico "Shorten URLs with Superintelligence"
- 📊 4 Feature cards con gradientes
- 🔗 URL Shortener component (glassmorphism card)

---

### 2️⃣ Crear una URL Corta

1. **En el input del homepage**, pega una URL larga:
   ```
   https://github.com/anthropics/claude-code
   ```

2. **Opcional:** Añade un título:
   ```
   Claude Code GitHub
   ```

3. **Click en "Shorten URL →"**

**Qué debería pasar:**
- ✅ Animación de loading
- ✅ Se muestra la URL acortada: `http://localhost:3001/XXXXXX`
- ✅ La URL está clickeable y es un link
- ✅ Aparecen 2 botones: "Copy Link" y "View Analytics"

---

### 3️⃣ Copiar el Link

1. **Click en "Copy Link"**

**Qué debería pasar:**
- ✅ Botón cambia a "Copied!" con checkmark
- ✅ URL copiada al clipboard
- ✅ Después de 2 segundos vuelve a "Copy Link"

---

### 4️⃣ Probar el Redirect

1. **Copia el short code** (ej: `KBLM46`)
2. **Abre en nueva pestaña:**
   ```
   http://localhost:8000/KBLM46
   ```

**Qué debería pasar:**
- ✅ Redirect instantáneo a YouTube
- ✅ Click registrado en analytics

---

### 5️⃣ Ver Analytics Dashboard

**Opción A:** Click en "View Analytics" del resultado

**Opción B:** Manualmente:
```
http://localhost:3001/dashboard/analytics?code=KBLM46
```

**Qué deberías ver:**
- ✨ Background futurista con glassmorphism
- 📊 **Widget 1:** Total Clicks (número grande holográfico)
- 📱 **Widget 2:** Device Breakdown (pie chart con colores neon)
- 🌍 **Widget 3:** Top Countries (bar chart verde)
- 🔗 **Widget 4:** Traffic Sources (horizontal bar chart naranja/rojo)
- 📋 **Tabla:** Recent Clicks con detalles (time, location, device, browser, source)

---

### 6️⃣ Ver Links Management

```
http://localhost:3001/dashboard/links
```

**Qué deberías ver:**
- 📋 Lista de 2 links mock (abc123, xyz789)
- 🎨 Cards glassmorphism con glow cyan
- 📊 Stats: clicks count, created date, domain badge
- 🔘 Botones: "Copy" y "Analytics"

**Nota:** Los links son MOCK data por ahora (línea 10-29 de `dashboard/links/page.tsx`)

---

## 🎨 Verificación de Diseño

### Homepage
- [ ] Background mesh visible con blur
- [ ] 3 orbs flotantes animados (cyan, purple, pink)
- [ ] Texto holográfico con gradiente animado
- [ ] Navigation bar sticky al hacer scroll
- [ ] URLShortener card con glow cyan
- [ ] Botón "Shorten URL" con gradiente holográfico

### Analytics Dashboard
- [ ] Charts renderizando correctamente
- [ ] Colores neon visibles: #00fff5, #8b5cf6, #ff006e
- [ ] Glassmorphism effect (blur + transparencia)
- [ ] Tabla responsive con hover effects
- [ ] Pulse animation en indicators

### Links Page
- [ ] Cards con hover effect (gradiente holográfico sutil)
- [ ] Clicks counter con neon cyan
- [ ] Copy button funciona
- [ ] Analytics link abre dashboard correctamente

---

## 🐛 Testing de Errores Comunes

### Error 1: "Cannot read properties of undefined"
**Causa:** Analytics sin datos
**Solución:** Primero crea una URL y haz click en el link

### Error 2: "Connection refused"
**Causa:** Backend no corriendo
**Solución:**
```bash
cd backend
source venv/bin/activate
python main.py
```

### Error 3: "Module not found"
**Causa:** Dependencies no instaladas
**Solución:**
```bash
cd frontend
npm install
```

---

## 📊 Testing de Analytics

### Crear Clicks Realistas

**Con Browser (RECOMENDADO):**
1. Abre `http://localhost:8000/KBLM46` en Chrome
2. Abre en Firefox
3. Abre en Safari
4. Abre en mobile (responsive mode)

**Con cURL (para testing):**
```bash
# Desktop Chrome
curl -L -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0" \
  http://localhost:8000/KBLM46

# Mobile iPhone
curl -L -A "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Safari/604.1" \
  http://localhost:8000/KBLM46

# From LinkedIn
curl -L -A "Mozilla/5.0 Chrome/120.0" \
  -H "Referer: https://linkedin.com" \
  http://localhost:8000/KBLM46
```

### Verificar Analytics Actualizado

```bash
# Ver analytics por API
curl -s http://localhost:8000/analytics/KBLM46 | python3 -m json.tool

# Ver en dashboard
http://localhost:3001/dashboard/analytics?code=KBLM46
```

---

## 🎥 Para tus Videos de YouTube

### Workflow Recomendado:

1. **Crear URL antes del video:**
   ```bash
   # En terminal
   curl -X POST http://localhost:8000/shorten \
     -H "Content-Type: application/json" \
     -d '{"original_url":"https://tu-video.com","title":"Mi Video"}'
   ```

2. **Copiar la URL completa:**
   ```
   http://localhost:8000/ABC123
   ```

3. **Pegar en descripción del video:**
   ```markdown
   🔗 Links mencionados:
   - Mi proyecto: http://localhost:8000/ABC123
   - Documentación: http://localhost:8000/XYZ789
   ```

4. **Ver analytics después:**
   - Cuántos clicks desde YouTube
   - Qué dispositivos usan (mobile/desktop)
   - De qué países son
   - Qué navegadores usan

---

## 🔧 Comandos Útiles

### Ver Logs del Backend
```bash
# En tiempo real
tail -f backend/logs/*.log

# O con BashOutput tool
BashOutput 2a8bd6
```

### Ver Logs del Frontend
```bash
BashOutput 93f00f
```

### Reiniciar Servidores
```bash
# Matar procesos
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3001 | xargs kill -9  # Frontend

# Reiniciar
cd backend && source venv/bin/activate && python main.py &
cd frontend && npm run dev &
```

### Crear Múltiples URLs de Prueba
```bash
# Script para crear 5 URLs
for i in {1..5}; do
  curl -X POST http://localhost:8000/shorten \
    -H "Content-Type: application/json" \
    -d "{\"original_url\":\"https://example.com/page$i\",\"title\":\"Test $i\"}"
  echo ""
done
```

---

## ✅ Checklist Final

### Frontend
- [ ] Homepage carga correctamente
- [ ] URL shortener funciona
- [ ] Copy to clipboard funciona
- [ ] Analytics dashboard muestra datos
- [ ] Links page muestra mock data
- [ ] Responsive en mobile
- [ ] Sin errores en consola

### Backend
- [ ] `/shorten` crea URLs correctamente
- [ ] `/{code}` redirect funciona
- [ ] `/analytics/{code}` retorna datos
- [ ] Click tracking registra device/location
- [ ] Geolocation detecta país
- [ ] User-agent parsing funciona

### Diseño
- [ ] Glassmorphism visible
- [ ] Colores neon destacan
- [ ] Animaciones smooth (60fps)
- [ ] Orbs flotantes animados
- [ ] Gradientes holográficos
- [ ] Glow effects en hover

---

## 🎨 Screenshots Recomendados

Para mostrar en tu portfolio:

1. **Homepage Hero** (full screen)
2. **URL Result Card** (después de acortar)
3. **Analytics Dashboard** (con datos reales)
4. **Device Breakdown Chart** (pie chart)
5. **Recent Clicks Table** (scrolled down)
6. **Links Management** (lista completa)
7. **Mobile View** (responsive)

---

## 🚀 Próximos Pasos

Una vez que verifiques todo funciona:

1. **Supabase Migration** (si quieres persistencia)
2. **Deploy to Railway** (backend en producción)
3. **Deploy to Vercel** (frontend en producción)
4. **Custom Domain** (linkproxy.com)

Ver `ROADMAP.md` para detalles.

---

## 📞 Troubleshooting

**Problema:** "No veo los orbs flotantes"
**Solución:** Verifica que `bg-mesh` class esté en globals.css

**Problema:** "Charts no renderizan"
**Solución:** Verifica que recharts esté instalado: `npm list recharts`

**Problema:** "URL no funciona"
**Solución:** Verifica backend corriendo en puerto 8000

**Problema:** "Analytics vacío"
**Solución:** Primero crea una URL y haz click en el link

---

**Happy Testing! 🎉**

Cuando termines de probar, avísame qué te pareció el diseño futurista 🚀