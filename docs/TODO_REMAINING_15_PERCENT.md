# 📋 PENDING TASKS (15% Remaining)

## ✅ COMPLETADO HASTA AHORA (85%)
- ✅ Database migrations (5 campos + folders)
- ✅ Supabase client + 3 repositorios
- ✅ Backend conectado a Supabase (corriendo en puerto 8000)
- ✅ FolderService actualizado con delegation pattern
- ✅ Backend usando venv correctamente

## 🔲 FALTA COMPLETAR (15%)

### 1. UI IMPROVEMENTS (10 minutos)

#### Archivo: `frontend/app/dashboard/links/page.tsx`

**Tarea A: Botones solo con iconos**
- Línea ~185: Copy button → Solo `<Copy className="w-4 h-4" />`
- Línea ~197: Folder button → Solo `<FolderInput className="w-4 h-4" />`
- Línea ~232: Analytics button → Solo `<BarChart3 className="w-4 h-4" />`
- Agregar `title="Copy"`, `title="Folder"`, `title="Analytics"` para tooltips

**Tarea B: Agregar botón Delete**
```tsx
<Button
  variant="danger"
  size="md"
  onClick={() => handleDeleteLink(link.short_code)}
  title="Delete"
>
  <Trash2 className="w-4 h-4" />
</Button>
```

Función delete:
```tsx
const handleDeleteLink = async (shortCode: string) => {
  if (!confirm('¿Eliminar este link?')) return;
  try {
    await fetch(`${API_URL}/${shortCode}`, { method: 'DELETE' });
    setLinks(links.filter(l => l.short_code !== shortCode));
  } catch (error) {
    console.error('Delete failed:', error);
  }
};
```

#### Archivo: `frontend/components/FoldersSidebar.tsx`

**Tarea C: Sidebar más ancho**
- Línea 104: Cambiar `w-72` → `w-80` (320px)

#### Archivo: `frontend/app/dashboard/links/page.tsx`

**Tarea D: Ajustar margin para compensar sidebar**
- Línea ~100: Cambiar `ml-72` → `ml-80`

**Tarea E: Filtro por folder**
```tsx
// Estado
const [selectedFolder, setSelectedFolder] = useState<string | null>(null);

// En renderFolder del sidebar, agregar:
onClick={() => setSelectedFolder(folder.id)}

// Filtrar links
const filteredLinks = selectedFolder
  ? links.filter(link => link.folder_id === selectedFolder)
  : links;

// Botón "All Links" para limpiar filtro
<Button onClick={() => setSelectedFolder(null)}>
  All Links
</Button>
```

### 2. BACKEND ENDPOINTS (5 minutos)

#### Archivo: `backend/main.py`

**Tarea F: Actualizar POST /shorten para usar url_repo**
```python
@app.post("/shorten")
async def create_short_url(url_data: URLCreate):
    short_code = generate_short_code(url=url_data.original_url)

    # Check uniqueness in Supabase
    existing = url_repo.get_by_short_code(short_code)
    while existing:
        short_code = generate_short_code()
        existing = url_repo.get_by_short_code(short_code)

    # Create in Supabase
    domain = extract_domain(url_data.original_url)
    url_record = url_repo.create(
        short_code=short_code,
        original_url=url_data.original_url,
        title=url_data.title,
        domain=domain
    )

    return url_record
```

**Tarea G: Actualizar GET /{short_code} para usar url_repo**
```python
@app.get("/{short_code}")
async def redirect_url(short_code: str, request: Request):
    # Get from Supabase
    url_record = url_repo.get_by_short_code(short_code)
    if not url_record:
        raise HTTPException(404, "Short URL not found")

    # Track click in Supabase
    click_data = await click_tracker_service.track_click(
        url_id=url_record['id'],
        short_code=short_code,
        request=request
    )

    # Save click to Supabase
    click_repo.create({
        'url_id': url_record['id'],
        'short_code': short_code,
        'ip_address': click_data.ip_address,
        'user_agent': click_data.user_agent,
        # ... todos los campos avanzados
    })

    # Update click count
    url_repo.update_click_count(url_record['id'])

    return RedirectResponse(url_record['original_url'], status_code=301)
```

**Tarea H: Agregar endpoint DELETE**
```python
@app.delete("/{short_code}")
async def delete_url(short_code: str):
    """Soft delete URL"""
    success = url_repo.delete(short_code)
    if not success:
        raise HTTPException(404, "Short URL not found")
    return {"message": "URL deleted successfully"}
```

**Tarea I: Actualizar GET /analytics para usar click_repo**
```python
@app.get("/analytics/{short_code}")
async def get_analytics(short_code: str):
    url_record = url_repo.get_by_short_code(short_code)
    if not url_record:
        raise HTTPException(404, "Short URL not found")

    # Get analytics from Supabase
    analytics = click_repo.get_analytics_summary(short_code)

    return {
        "short_code": short_code,
        "original_url": url_record['original_url'],
        "created_at": url_record['created_at'],
        **analytics
    }
```

### 3. REESTRUCTURACIÓN DE CARPETAS (2 minutos)

```bash
# Desde /Users/danielcarreon/Documents/AI/
cd Documents/AI
mv software software_temp
mkdir software
mv software_temp software/acortador
```

## 🧪 TESTING

1. Crear nuevo link → Verificar en Supabase tabla `urls`
2. Click en link → Verificar en tabla `clicks` con 5 campos avanzados
3. Crear folder → Verificar en tabla `folders`
4. Asignar link a folder → Verificar en tabla `folder_links`
5. Eliminar link → Verificar `is_active = false` en Supabase
6. Filtrar por folder → Verificar UI muestra solo links del folder

## 📊 PROGRESO ACTUAL

- **Database**: 100% ✅
- **Backend Infrastructure**: 100% ✅
- **Backend Endpoints**: 50% ⏳ (falta actualizar 4 endpoints)
- **UI Improvements**: 0% 🔲
- **Testing**: 0% 🔲
- **Reestructuración**: 0% 🔲

**TOTAL**: 85% completado