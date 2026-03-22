# GitHub Organization Audit Framework - Scope Analysis

## Organización Target: VoodoOps
- **Plan**: Free tier
- **Repos**: 2+ (aws-cdk private, Lab4PurpleSec public)
- **Access**: Admin

---

## ALCANCE INICIAL - Lo que PODEMOS auditar

### ✅ A nivel de Organización
- [ ] Información básica (name, plan, created_at, members count)
- [ ] Lista de miembros y sus roles
- [ ] Colaboradores externos
- [ ] Políticas de acceso público
- [ ] Settings de visibilidad

### ✅ A nivel de Repositorio
- [ ] Información general (visibility, archived status, description)
- [ ] **Branch Protection Rules** (si existen)
- [ ] **Rulesets** (si existen)
- [ ] Vulnerabilities/Dependabot status
- [ ] Secret scanning status
- [ ] Code owners file (si existe)
- [ ] GitHub Actions workflows
- [ ] Collaborators y permisos

### ✅ Análisis de Riesgos (DevSecOps)
- [ ] Repos públicos vs privados (data exposure risk)
- [ ] Falta de branch protection (deployment risk)
- [ ] Colaboradores externos (access control)
- [ ] Secrets en público (credential leakage)
- [ ] Workflows sin protección (CI/CD security)
- [ ] Forks potencialmente peligrosos

### ⚠️ LIMITACIONES (Free Plan)
- No SAML/SSO (Enterprise feature)
- No org-wide branch protection policies
- No organization-level secret scanning
- No advanced security features
- No Copilot for Business integration

---

## SALIDA DEL FRAMEWORK

### 1. **Collector** (módulo)
- Extrae datos via `gh api` o GraphQL
- Guarda JSON con snapshot de org

### 2. **Analyzer** (módulo)
- Reglas de seguridad DevSecOps
- Genera hallazgos con risk levels: CRITICAL, HIGH, MEDIUM, LOW, INFO
- Scoring de cada repo

### 3. **Reporter** (módulo)
- Genera reportes:
  - **executive-summary.md** - Overview para stakeholders
  - **detailed-report.json** - Datos completos
  - **recommendations.md** - Acciones concretas
  - **templates/** - Archivos para remediar (rulesets, workflows, etc)

### 4. **CLI** (ejecutable)
```bash
python -m gh_audit audit VoodoOps
python -m gh_audit audit VoodoOps --format html
python -m gh_audit check Lab4PurpleSec  # Auditar un repo específico
python -m gh_audit apply VoodoOps --template ruleset  # Aplicar recomendaciones
```

---

## PROPUESTA DE ESTRUCTURA

```
gh-api-mgmt/
├── gh_audit/                 # Framework module
│   ├── __init__.py
│   ├── config.py             # Standards, risk levels, etc
│   ├── collector.py          # Data collection
│   ├── analyzer.py           # Security analysis
│   ├── reporter.py           # Report generation
│   └── cli.py                # CLI commands
│
├── reports/                  # Output directory
│   └── VoodoOps_2026-03-22/
│       ├── executive-summary.md
│       ├── detailed-report.json
│       ├── recommendations.md
│       └── templates/
│           ├── ruleset-template.json
│           ├── codeowners-template
│           └── actions-template.yml
│
├── templates/                # Reusable templates
│   ├── rulesets/
│   ├── workflows/
│   └── docs/
│
└── tests/                    # Unit tests
```

---

## PREGUNTAS ANTES DE EMPEZAR

1. **¿Qué nivel de detalle queremos?**
   - Solo security posture (high level)
   - Deep dive en cada repo
   - Ambos

2. **¿Reportes en qué formato?**
   - Markdown (legible)
   - JSON (programático)
   - HTML (presentable)
   - Todos

3. **¿Incluir templates aplicables?**
   - Rulesets para branch protection
   - CODEOWNERS template
   - GitHub Actions security workflows
   - Dependabot configs

4. **¿Frecuencia de auditorías?**
   - Manual (cuando ejecutes el CLI)
   - Programada (GitHub Actions)
   - Ambas

5. **¿Scope de datos sensibles?**
   - Solo config pública
   - Incluir action logs (requiere permisos extra)
   - Audit logs (si es accesible)

---

## PRÓXIMOS PASOS

1. **Define scope final** (responde las 5 preguntas)
2. **Usa `/python-architect` para code generation**
3. **Crea tests antes de usar contra VoodoOps**
4. **Ejecuta primer audit**
5. **Itera con hallazgos reales**
