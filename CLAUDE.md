# Proyecto: LinkProxy - URL Shortener con Analytics

## 🎯 Principios de Desarrollo (Context Engineering)

### Design Philosophy
- **KISS**: Keep It Simple, Stupid - Prefiere soluciones simples
- **YAGNI**: You Aren't Gonna Need It - Implementa solo lo necesario
- **DRY**: Don't Repeat Yourself - Evita duplicación de código
- **SOLID**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion

### Descripción del Proyecto
**LinkProxy** es un URL shortener minimalista con analytics en tiempo real que funciona como proxy de datos. Enfocado en el 4% de funcionalidades que generan 80% del valor: shortening + click tracking + dashboard analytics. Diseñado para trackear métricas clave (device, location, referrer) de manera simple pero poderosa.

## 🏗️ Tech Stack & Architecture

### Core Stack
- **Frontend**: Next.js 15 + React + TypeScript
- **Backend**: FastAPI + Python + SQLModel
- **Base de Datos**: Supabase (PostgreSQL + Real-time subscriptions)
- **Analytics Engine**: Custom time-series tracking + WebSockets
- **Styling**: Tailwind CSS + Shadcn/ui
- **Charts**: Recharts/Chart.js para dashboard analytics
- **Testing**: Jest + Pytest + Playwright para E2E

### Hybrid Strategic Architecture

**Enfoque: Arquitectura Híbrida Estratégica optimizada para desarrollo asistido por IA**

- **Frontend**: Feature-First Architecture
- **Backend**: Clean Architecture (Layered)
- **Principio**: Cada parte usa la estructura que mejor se adapta a su contexto

#### Frontend: Feature-First (LinkProxy)
```
frontend/
├── src/
│   ├── app/              # Next.js 14 App Router
│   │   ├── (dashboard)/  # Grupo de rutas del dashboard
│   │   │   ├── analytics/ # Página de analytics
│   │   │   └── links/     # Gestión de links
│   │   ├── [shortCode]/  # Dynamic routing para redirects
│   │   ├── layout.tsx    # Layout principal
│   │   └── page.tsx      # Landing page
│   ├── features/         # 🎯 Core Features
│   │   ├── url-shortener/
│   │   │   ├── components/ # URL input, link cards
│   │   │   ├── hooks/      # useShortener, useClipboard
│   │   │   ├── services/   # API calls shortening
│   │   │   └── types/      # URL, Link types
│   │   ├── analytics/
│   │   │   ├── components/ # Charts, metrics widgets
│   │   │   ├── hooks/      # useRealTimeAnalytics
│   │   │   ├── services/   # Analytics API, WebSocket
│   │   │   └── types/      # Analytics, Click types
│   │   └── link-management/
│   │       ├── components/ # Link list, actions
│   │       ├── hooks/      # useLinks, useBulkActions
│   │       └── services/   # CRUD operations
│   └── shared/           # Código reutilizable
│       ├── components/   # UI primitives (Button, Chart, etc.)
│       ├── hooks/        # useWebSocket, useGeolocation
│       ├── stores/       # Estado global (Zustand)
│       ├── types/        # Tipos compartidos
│       ├── utils/        # Helpers, formatters
│       └── lib/          # Supabase, analytics config
```

#### Backend: Clean Architecture (LinkProxy)
```
backend/
├── main.py               # FastAPI app + WebSocket server
├── api/                  # 🌐 Capa de Interfaz/Presentación
│   ├── deps.py           # Dependencias comunes
│   ├── shortener_router.py # Endpoints para URLs (/shorten, /{code})
│   ├── analytics_router.py # Endpoints analytics (/analytics)
│   ├── websocket_router.py # WebSocket para real-time
│   └── health_router.py    # Health checks
├── application/          # 🎯 Casos de Uso/Orquestación
│   └── services/
│       ├── url_shortener_service.py # Lógica shortening
│       ├── analytics_service.py     # Lógica analytics
│       ├── click_tracker_service.py # Click tracking
│       └── geolocation_service.py   # IP to location
├── domain/              # 💎 Lógica de Negocio Pura
│   ├── models/          # Entidades SQLModel
│   │   ├── url.py       # URL, Click models
│   │   └── analytics.py # Analytics aggregations
│   ├── services/        # Domain services
│   │   ├── url_generator.py # Base62 generation
│   │   └── analytics_aggregator.py
│   ├── config/          # Domain config
│   └── interfaces/      # Abstracciones/Contratos
│       ├── url_repository.py
│       └── analytics_repository.py
└── infrastructure/      # 🔧 Implementaciones Externas
    ├── persistence/     # Supabase repositories
    │   ├── supabase_client.py
    │   ├── url_repository_impl.py
    │   └── analytics_repository_impl.py
    ├── external_apis/   # APIs externas
    │   ├── geolocation_client.py # MaxMind/IP-API
    │   └── user_agent_parser.py
    └── config/          # Infrastructure config
        ├── settings.py  # Environment vars
        └── database.py  # Supabase setup
```

### Arquitectura Completa (LinkProxy)
```
linkproxy/
├── frontend/            # Next.js 14 Feature-First
├── backend/            # FastAPI Clean Architecture
├── supabase/          # Database & Real-time
│   ├── migrations/    # Schema evolution
│   ├── schema.sql     # Initial DB structure
│   └── seed.sql       # Test data
├── .claude/           # Claude Code config
│   ├── docs/          # Project docs
│   └── bucle-agentico-mvp.md # Metodología iterativa
├── docs/             # Technical documentation
│   ├── api-spec.md   # OpenAPI documentation
│   ├── analytics-requirements.md
│   └── deployment.md
├── docker-compose.yml # Local development
├── railway.json       # Railway deployment
└── README.md         # Project overview
```

> **🤖 ¿Por qué esta arquitectura?**
> 
> Esta estructura híbrida fue diseñada específicamente para **desarrollo asistido por IA**. La organización clara por capas y features permite que los AI assistants:
> - **Localicen rápidamente** el código relacionado con una funcionalidad específica
> - **Entiendan el contexto** sin necesidad de navegar múltiples archivos dispersos  
> - **Mantengan la separación de responsabilidades** al generar código nuevo
> - **Escalen el proyecto** añadiendo features sin afectar el código existente
> - **Generen código consistente** siguiendo los patrones establecidos en cada capa
>
> *La IA puede trabajar de forma más efectiva cuando la información está organizada siguiendo principios claros y predecibles.*

## 🎯 LinkProxy: Core Features (4% que produce 80% del valor)

### MVP Essentials
1. **URL Shortening**: Algoritmo Base62 para generar códigos únicos (lnk.px/XXXXX)
2. **Click Tracking**: Captura en tiempo real de cada click con metadata
3. **Analytics Dashboard**: 4 widgets clave inspirados en Bitly
   - **Total Clicks Counter**: Métricas generales en tiempo real
   - **Device Breakdown**: Donut chart (Desktop, Mobile, Tablet, Unknown)
   - **Geographic Analytics**: Top países con % distribution
   - **Traffic Sources**: Bar chart (LinkedIn, Google, Facebook, Direct, etc.)
4. **Link Management**: Lista de URLs creadas con stats básicos

### Real-time Capabilities
- **WebSocket Integration**: Analytics en vivo sin polling
- **Geolocation Tracking**: IP to location (país/ciudad)
- **Device Detection**: User-agent parsing para device/OS/browser
- **Referrer Analysis**: Tracking de tráfico source

## 🛠️ Comandos Importantes

### Development (Frontend)
- `npm run dev` - Next.js dev server (localhost:3000)
- `npm run build` - Build optimizado para producción
- `npm run preview` - Preview del build de producción

### Development (Backend)
- `uvicorn main:app --reload` - FastAPI dev server (localhost:8000)
- `python -m pytest` - Ejecutar test suite
- `python scripts/seed_db.py` - Poblar DB con data de prueba

### Quality Assurance
- `npm run test` - Jest + React Testing Library
- `npm run test:e2e` - Playwright E2E tests
- `npm run test:coverage` - Coverage report completo
- `npm run lint` - ESLint + Prettier
- `npm run lint:fix` - Fix automático de código
- `npm run typecheck` - TypeScript verification

### Database & Analytics
- `supabase db reset` - Reset local database
- `supabase gen types typescript` - Generate TypeScript types
- `python scripts/analytics_backfill.py` - Backfill analytics data

### Git Workflow
- `npm run commit` - Commit con Conventional Commits
- `npm run pre-commit` - Hook de pre-commit

## 📝 Convenciones de Código

### File & Function Limits
- **Archivos**: Máximo 500 líneas
- **Funciones**: Máximo 50 líneas
- **Componentes**: Una responsabilidad clara

### Naming Conventions
- **Variables/Functions**: `camelCase`
- **Components**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Files**: `kebab-case.extension`
- **Folders**: `kebab-case`

### TypeScript Guidelines
- **Siempre usar type hints** para function signatures
- **Interfaces** para object shapes
- **Types** para unions y primitives
- **Evitar `any`** - usar `unknown` si es necesario

### Component Patterns
```typescript
// ✅ GOOD: Proper component structure
interface Props {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
  onClick: () => void;
}

export function Button({ children, variant = 'primary', onClick }: Props) {
  return (
    <button 
      onClick={onClick}
      className={`btn btn-${variant}`}
    >
      {children}
    </button>
  );
}
```

## 🧪 Testing Strategy

### Test-Driven Development (TDD)
1. **Red**: Escribe el test que falla
2. **Green**: Implementa código mínimo para pasar
3. **Refactor**: Mejora el código manteniendo tests verdes

### Test Structure (AAA Pattern)
```typescript
// ✅ GOOD: Clear test structure
test('should calculate total with tax', () => {
  // Arrange
  const items = [{ price: 100 }, { price: 200 }];
  const taxRate = 0.1;
  
  // Act
  const result = calculateTotal(items, taxRate);
  
  // Assert  
  expect(result).toBe(330);
});
```

### Coverage Goals
- **Unit Tests**: 80%+ coverage
- **Integration Tests**: Critical paths
- **E2E Tests**: Main user journeys

## 🔒 Security Best Practices

### Input Validation
- Validate all user inputs
- Sanitize data before processing
- Use schema validation (Zod, Yup, etc.)

### Authentication & Authorization
- JWT tokens con expiración
- Role-based access control
- Secure session management

### Data Protection
- Never log sensitive data
- Encrypt data at rest
- Use HTTPS everywhere

## ⚡ Performance Guidelines

### Code Splitting
- Route-based splitting
- Component lazy loading
- Dynamic imports

### State Management
- Local state first
- Global state only when needed
- Memoization for expensive computations

### Database Optimization
- Index frequently queried columns
- Use pagination for large datasets
- Cache repeated queries

## 🔄 Git Workflow & Repository Rules

### Branch Strategy
- `main` - Production ready code
- `develop` - Integration branch
- `feature/TICKET-123-description` - Feature branches
- `hotfix/TICKET-456-description` - Hotfixes

### Commit Convention (Conventional Commits)
```
type(scope): description

feat(auth): add OAuth2 integration
fix(api): handle null user response  
docs(readme): update installation steps
```

### Pull Request Rules
- **No direct commits** a `main` o `develop`
- **Require PR review** antes de merge
- **All tests must pass** antes de merge
- **Squash and merge** para mantener historia limpia

## ❌ No Hacer (Critical)

### Code Quality
- ❌ No usar `any` en TypeScript
- ❌ No hacer commits sin tests
- ❌ No omitir manejo de errores
- ❌ No hardcodear configuraciones

### Security  
- ❌ No exponer secrets en código
- ❌ No loggear información sensible
- ❌ No saltarse validación de entrada
- ❌ No usar HTTP en producción

### Architecture
- ❌ No editar archivos en `src/legacy/`
- ❌ No crear dependencias circulares
- ❌ No mezclar concerns en un componente
- ❌ No usar global state innecesariamente

## 📚 Referencias & Context

### Project Files
- Ver @README.md para overview detallado
- Ver @package.json para scripts disponibles
- Ver @.claude/docs/ para workflows y documentación
- Ver @.mcp.json.examples para MCPs disponibles

### External Dependencies
- Documentación oficial de frameworks
- Best practices guides
- Security guidelines (OWASP)

## 🤖 AI Assistant Guidelines

### When Suggesting Code
- Siempre incluir types en TypeScript
- Seguir principles de CLAUDE.md
- Implementar error handling
- Incluir tests cuando sea relevante

### When Reviewing Code  
- Verificar adherencia a principios SOLID
- Validar security best practices
- Sugerir optimizaciones de performance
- Recomendar mejoras en testing

### Context Priority
1. **CLAUDE.md rules** (highest priority)
2. **.claude/docs/** workflows y guías
3. **Project-specific files** (package.json, etc.)
4. **General best practices**

## 🚀 Pre-Development Validation Protocol

### API & Dependencies Current Check
**CRÍTICO**: Siempre verificar antes de asumir
- [ ] ✅ Verificar que las versiones de APIs/modelos existen (ej: GPT-5 no existe aún)
- [ ] ✅ Confirmar que las librerías están actualizadas
- [ ] ✅ Validar endpoints externos funcionan
- [ ] ✅ Tener fallbacks para todas las dependencias externas

### Simplicity-First Development
- [ ] ✅ Crear versión simplificada primero (`simple_main.py`)
- [ ] ✅ Probar funcionalidad básica antes de agregar complejidad
- [ ] ✅ Mantener siempre una versión "modo demo" que funcione
- [ ] ✅ Implementar mock data para casos donde servicios externos fallen

### Incremental Validation Strategy
- [ ] ✅ Probar cada endpoint inmediatamente después de crearlo
- [ ] ✅ Usar TodoWrite para tracking sistemático de progreso
- [ ] ✅ Validar UI después de cada cambio importante
- [ ] ✅ Mantener logs detallados de errores para debugging

## 🔄 Error-First Development Protocol

### Manejo de Errores Predictivos
```python
# ✅ GOOD: Siempre incluir fallbacks
try:
    ai_result = await openai_call()
except Exception as e:
    print(f"AI call failed: {e}")
    ai_result = get_mock_fallback()  # Siempre tener fallback
```

### Debugging Sin Visibilidad Directa
- **Usar logs extensivos** con emojis para fácil identificación
- **Crear endpoints de testing** (`/test-connection`, `/health`)  
- **Implementar timeouts** en todas las llamadas externas
- **Hacer requests incrementales** - nunca asumir que algo complejo funcionará

## 🎯 Advanced Real-Time Debugging (Expert Level)

### Background Log Streaming Setup
```bash
# 1. Start dev servers with log capture
npm run dev 2>&1 | tee frontend.log
uvicorn main:app --reload 2>&1 | tee backend.log

# 2. Monitor logs in real-time (Claude Code)
tail -f frontend.log | claude -p "Alert me of compilation errors"

# 3. Use Background Commands (Ctrl+B)
npm run dev  # Press Ctrl+B to run in background
# Then use BashOutput tool to monitor status
```

### Claude Code Web Interface
```bash
# Install web interface for visual log monitoring
npm install -g claude-code-web
claude-code-web --debug  # Enhanced logging mode

# Or use alternative: 
npx claude-code-web --dev  # Development mode with verbose logs
```

### Multi-Terminal Monitoring Pattern
```bash
# Terminal 1: Backend with structured logging
python -m uvicorn main:app --reload --log-level debug

# Terminal 2: Frontend with compilation monitoring
npm run dev -- --verbose

# Terminal 3: Claude Code with combined log analysis
tail -f *.log | claude -p "Debug any compilation or runtime errors immediately"
```

### Background Task Management
- **Use Ctrl+B** para run commands in background
- **BashOutput tool** para retrieving incremental output
- **Filter logs** for specific patterns (ERROR, WARN, Compil)
- **Status tracking** (running/completed/killed)

## 🎨 Bucle Agéntico con Playwright MCP

### Metodología de Desarrollo Visual
**Problema:** IA genera frontends genéricos sin poder ver el resultado  
**Solución:** Playwright MCP otorga "ojos" al AI para iteración visual

### Bucle Agéntico Frontend
```
1. Código UI → 2. Playwright Screenshot → 3. Visual Compare → 4. Iterate
```

### Playwright MCP Integration
- **browser_snapshot**: Captura estado actual de la página
- **browser_take_screenshot**: Screenshots para comparación visual
- **browser_navigate**: Navegación automática para testing
- **browser_click/type**: Interacción automatizada con UI
- **browser_resize**: Testing responsive en diferentes viewports

### Visual Development Protocol
1. **Implementar componente** siguiendo specs
2. **Capturar screenshot** con Playwright
3. **Comparar vs design requirements**
4. **Iterar automáticamente** hasta pixel-perfect
5. **Validar responsiveness** en mobile/tablet/desktop

### Integration con Design Review
- Activar review visual automático post-implementación
- Usar criterios objetivos de diseño (spacing, colors, typography)
- Generar feedback específico y accionable
- Prevenir frontends genéricos mediante validación visual

---

*Este archivo es la fuente de verdad para desarrollo en este proyecto. Todas las decisiones de código deben alinearse con estos principios.*