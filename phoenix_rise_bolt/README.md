# Phoenix Rise & Dojo Mental 🧘‍♂️✨

> Mental traction ecosystem for the Phoenix platform - Production-ready monorepo with event-sourcing architecture.

## 🎯 Mission

Bridge the gap between intention and action through **Journal Kaizen**, **Zazen rituals**, and **intelligent insights**. Built for the Phoenix ecosystem with security-first design and RGPD compliance.

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + SQLAlchemy (async) + PostgreSQL + Redis  
- **Auth**: Supabase Auth with JWT validation
- **Event System**: JSONB event-sourcing with smart routing
- **Security**: AES-256 encryption, PBKDF2, rate limiting, OWASP compliance
- **Infrastructure**: Docker Compose, Alembic migrations, Celery workers

### Monorepo Structure
```
phoenix-rise/
├── apps/
│   ├── web/                 # Next.js frontend
│   └── api/                 # FastAPI backend
├── packages/shared/         # Common schemas & types
├── infrastructure/          # Docker, configs
├── Makefile                # Development commands
└── docker-compose.yml      # Local environment
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local web development)
- Python 3.11+ (for local API development)

### Development Setup

```bash
# Clone and start
git clone <repo>
cd phoenix-rise
make dev

# Services will be available at:
# 🌐 Web App: http://localhost:3000
# 🔧 API: http://localhost:8000
# 📧 Mailhog: http://localhost:8025
# 📊 API Docs: http://localhost:8000/docs
```

The `make dev` command:
1. Starts all Docker services (PostgreSQL, Redis, Mailhog)
2. Runs database migrations
3. Seeds sample data
4. Launches both frontend and backend

### Manual Setup
```bash
# Start infrastructure
make docker-up

# Run migrations
make migrate

# Seed demo data
make seed

# Check health
make health
```

## 🎨 Core Features

### 📖 Journal Kaizen (`/rise/journal`)
- **Markdown editor** with live preview
- **AES-256 encryption** for sensitive content
- **Mood tracking** (1-5 scale) with analytics
- **Smart tagging** and search
- **AI insights** (ready for GPT/Gemini integration)

### 🧘 Dojo Mental (`/rise/dojo`)
- **Zazen rituals**: "Légitimité", "Clarté", "Courage"
- **Breathing timer** (4-4-6 pattern)
- **Session tracking** with focus ratings
- **Streak counters** and achievements

### 📊 Dashboard (`/rise`)
- **7-day mood trends** (Recharts visualizations)
- **Recent journal entries** preview
- **Ritual suggestions** based on content analysis
- **Smart notifications** with contextual timing

### 🔐 Privacy & RGPD (`/settings/privacy`)
- **One-click data export** (JSON format)
- **Right to erasure** with audit trail
- **Granular consent** management
- **Retention policies** (configurable)

### 🔔 Event Bridge
- **Event-sourcing** with PostgreSQL JSONB
- **Smart routing** for notifications
- **Cross-app integration** (ready for Phoenix Letters/CV)
- **Webhook endpoints** for external systems

## 🛡️ Security Features

### OWASP Top 10 Protection
- ✅ **Injection**: SQLAlchemy ORM + parameterized queries
- ✅ **Broken Authentication**: Supabase JWT + secure sessions  
- ✅ **Sensitive Data Exposure**: AES-256 field-level encryption
- ✅ **XXE**: JSON-only APIs, no XML processing
- ✅ **Broken Access Control**: RLS policies + middleware validation
- ✅ **Security Misconfiguration**: Secure headers, CORS restrictions
- ✅ **XSS**: Content sanitization (Bleach), CSP headers
- ✅ **Insecure Deserialization**: Pydantic validation, no pickle
- ✅ **Known Vulnerabilities**: Dependency scanning, regular updates
- ✅ **Insufficient Logging**: Structured logs, security events

### Additional Security Measures
- **Rate limiting**: 100 req/min per IP (configurable)
- **Input sanitization**: HTML/Markdown cleaning
- **Secure headers**: HSTS, X-Frame-Options, CSP
- **Data encryption**: Fernet (AES-256) for PII fields
- **Audit logging**: All sensitive operations tracked
- **Session management**: Secure JWT handling

## 📊 Data Model

### Core Entities
```sql
users               # Supabase auth integration
├── journal_entries # Encrypted content, mood, tags
├── mood_logs      # Daily mood tracking (1-5)
├── zazen_sessions # Ritual tracking, breathing patterns
├── notifications  # Smart suggestions, reminders
└── events         # Event-sourcing log (JSONB)
```

### Event Types
- `USER_REGISTERED`, `SUBSCRIPTION_ACTIVATED`
- `JOURNAL_ENTRY_CREATED`, `MOOD_LOGGED`  
- `ZAZEN_STARTED`, `ZAZEN_COMPLETED`
- `NOTIFICATION_PUSHED`, `NOTIFICATION_READ`

### Smart Routing Examples
```python
# Détection d'intention → Suggestion de rituel
if "illégitime" in journal_content:
    → Notification("Rituel Zazen - Bâtir sa légitimité (10 min)")

# Streak milestone → Encouragement  
if zazen_streak == 7:
    → Notification("7 jours de Zazen ! Momentum en place 🔥")
```

## 🧪 Testing Strategy

```bash
# Run all tests
make test

# Specific test suites  
make test-api          # Backend unit tests
make test-web          # Frontend unit tests
make test-e2e          # End-to-end tests

# Coverage report
make test-api          # Generates HTML coverage report
```

### Test Coverage Goals
- **Backend**: ≥70% coverage on services (journal, mood, notifications)
- **Frontend**: Component testing with Vitest + Playwright E2E
- **Security**: OWASP validation, penetration testing ready

## 🔧 Development Commands

```bash
# Environment management
make dev               # Full development setup
make docker-up         # Start infrastructure only
make docker-clean      # Clean reset

# Database operations
make migrate           # Apply migrations
make migrate-create MESSAGE="description"  # Create migration
make seed              # Load sample data
make reset-db          # ⚠️ Reset with sample data

# Code quality
make lint              # Run all linters
make format            # Auto-format code
make security-scan     # Security vulnerability scan

# Monitoring
make logs              # All service logs
make logs-api          # API logs only
make health            # Service health check
```

## 📈 Monitoring & Observability

### Health Endpoints
- `GET /health` - Service health status
- `GET /metrics` - Prometheus metrics
- Structured logging with correlation IDs

### Key Metrics
- Request latency, error rates
- Database connection pool usage  
- Redis cache hit rates
- Event processing throughput
- User engagement metrics

## 🌍 Environment Configuration

### Required Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db

# Redis
REDIS_URL=redis://localhost:6379

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx
SUPABASE_JWT_SECRET=xxx

# Security
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-fernet-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=xxx
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
```

### Development vs Production
- **Development**: `DEBUG=true`, verbose logging, hot reload
- **Production**: Rate limiting, security headers, monitoring

## 🎯 Acceptance Criteria ✅

1. **Journal → Event → Notification**
   - ✅ Create journal entry → `JOURNAL_ENTRY_CREATED` event logged
   - ✅ Content contains "illégitime" → Zazen notification queued
   - ✅ Notification acknowledging works

2. **Zazen Session Tracking**  
   - ✅ Start/complete ritual → timer functional
   - ✅ `ZAZEN_COMPLETED` event emitted → streak incremented
   - ✅ Session visible on dashboard

3. **Mood Analytics**
   - ✅ Log daily mood → weekly chart updates
   - ✅ `MOOD_LOGGED` event written → insights generated
   - ✅ Ritual recommendations based on patterns

4. **RGPD Compliance**
   - ✅ Export user data → complete JSON download
   - ✅ Erase account → soft delete + audit event
   - ✅ Consent management functional

5. **Security Validation**
   - ✅ HTML input sanitized (XSS protection)
   - ✅ Rate limiting active (429 responses)  
   - ✅ CORS restricted to allowed origins
   - ✅ Sensitive fields encrypted (verify read/write)

## 🚦 Deployment Readiness

### Production Checklist
- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] SSL certificates installed
- [ ] Monitoring dashboards setup
- [ ] Backup strategy implemented
- [ ] Security scan passed
- [ ] Load testing completed
- [ ] Documentation updated

### CI/CD Pipeline Ready
```bash
make ci-test           # CI test suite
make ci-build          # Production builds
make deploy-prepare    # Pre-deployment validation
```

## 🤝 Contributing

1. **Code Standards**: Black (Python), ESLint/Prettier (TypeScript)
2. **Testing**: All features require tests (unit + integration)
3. **Security**: Security implications documented
4. **Documentation**: README + inline documentation updated

## 🔮 Future Roadmap (Phase 2-3)

### Phase 2: Ecosystem Integration
- **Event Bridge** enhancement (cross-app triggers)  
- **Smart notifications** based on Phoenix Letters/CV usage
- **Team features** (shared rituals, group challenges)

### Phase 3: AI Enhancement
- **GPT/Gemini integration** for journal insights
- **Vector search** (pgvector) for semantic journal search
- **Personalized rituals** based on user patterns
- **Consciousness score** (Flywheel 2.0 integration)

## 📞 Support & Contact

- **Tech Lead**: Phoenix Core Team
- **Documentation**: This README + `/docs` folder
- **Issues**: Internal tracker
- **Security**: security@phoenix.team

---

**Phoenix Rise** - Transforming intention into action, one breath at a time. 🧘‍♂️✨

Built with ❤️ by the Phoenix Tech Team | 2025