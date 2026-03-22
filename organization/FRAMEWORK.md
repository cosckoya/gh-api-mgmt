# GitHub Organization Audit Framework

## 📋 Overview
Framework profesional para auditar y mejorar organizaciones GitHub según:
- ✅ GitHub Security Best Practices
- ✅ OWASP Top 10
- ✅ CIS Benchmarks
- ✅ Community Standards
- ✅ Compliance mínima (SOC2, GDPR-ready)

**Objetivo**: Garantizar que la organización es **segura, privada y sin accesos no deseados**

---

## 🎯 Scope de Auditoría

### Datos Recolectados
1. **Organización**: Settings, miembros, permisos, 2FA enforcement
2. **Repositorios**: Visibility, protecciones, secrets, workflows, rulesets
3. **Access Control**: Members, outside collaborators, roles, inactive users
4. **Security Config**: Branch protection, code review requirements, deployment protection
5. **Compliance**: CODEOWNERS, security policies, secret scanning, dependabot

### NO Incluido
- Audit logs detallados (requiere Enterprise)
- SAML/SSO config (free plan no soporta)
- Org-wide policies (Enterprise feature)

---

## 📊 Niveles de Riesgo

```
CRITICAL  → Debe remediarse inmediatamente (seguridad crítica)
HIGH      → Debe remediarse en corto plazo (exposición significativa)
MEDIUM    → Debería remediarse (mejora de postura)
LOW       → Considerar remediarse (optimización)
INFO      → Información para conocimiento
```

---

## 📁 Estructura de Directorios

```
organization/
├── FRAMEWORK.md                    # Este archivo
├── audit/
│   ├── collector.py               # Recolecta datos de la org
│   ├── analyzer.py                # Analiza riesgos según estándares
│   ├── reporter.py                # Genera reporte JSON
│   └── standards.py               # Reglas de compliance
│
├── templates/                     # Templates recomendadas
│   ├── branch-protection/         # Protección de ramas
│   │   ├── sensitive-repos.json
│   │   ├── production-repos.json
│   │   └── standard-repos.json
│   │
│   ├── workflows/                 # GitHub Actions seguro
│   │   ├── security-scan.yml
│   │   ├── dependency-check.yml
│   │   └── secret-scan.yml
│   │
│   ├── governance/                # Governance & Compliance
│   │   ├── CODEOWNERS.template
│   │   ├── SECURITY.md.template
│   │   ├── dependabot.yml.template
│   │   └── .github-settings.yml
│   │
│   └── org-settings/              # Configuración de org
│       ├── base-org-config.yml
│       └── member-roles.yml
│
├── reports/                       # Salida de auditorías
│   └── {org-name}_{timestamp}/
│       ├── audit-report.json      # Reporte completo (programático)
│       ├── audit-report.html      # Reporte visual (stakeholders)
│       ├── executive-summary.txt  # Resumen ejecutivo
│       └── remediation-plan.md    # Plan de acción
│
├── scripts/
│   ├── run_audit.py              # Script principal: ejecuta auditoría
│   ├── generate_html.py           # Genera HTML desde JSON
│   ├── apply_templates.py         # Aplica templates a repos
│   └── check_compliance.py        # Valida compliance continuo
│
├── tests/
│   ├── test_collector.py
│   ├── test_analyzer.py
│   └── test_standards.py
│
├── .github/workflows/
│   ├── org-audit-scheduled.yml    # Auditoría programada (propuesta)
│   └── org-audit-manual.yml       # Auditoría manual
│
└── README.md                      # Documentación de uso
```

---

## 🔍 Estándares de Compliance (Rules Engine)

### Org-Level Checks
- [ ] 2FA enforcement for all members
- [ ] All members have verified email
- [ ] No inactive members (30+ days)
- [ ] Outside collaborators limited & audited
- [ ] Member roles follow principle of least privilege
- [ ] Org has security policy (SECURITY.md)

### Repo-Level Checks
- [ ] Private repos are truly private
- [ ] Branch protection on default branch
- [ ] Require pull request reviews (≥1 reviewer)
- [ ] Require code owner review (si existe CODEOWNERS)
- [ ] Require status checks before merge
- [ ] Dismiss stale PR approvals on new push
- [ ] Allow force pushes: DISABLED
- [ ] Allow deletions: DISABLED
- [ ] Secret scanning: ENABLED
- [ ] Dependabot: ENABLED
- [ ] Deployment protection rules configured
- [ ] No direct commits to main (enforce PRs)

### Security Policies
- [ ] CODEOWNERS file exists en repos críticos
- [ ] SECURITY.md exists con contact & disclosure
- [ ] LICENSE file exists
- [ ] No secrets committed (scan histórico)
- [ ] GitHub Actions workflows are protected
- [ ] Workflow approvals required for external contributors

---

## 📝 Templates Recomendadas

### 1️⃣ **Branch Protection Rules** (3 niveles)
- `sensitive-repos.json` → Máxima protección (secrets, keys, certs)
- `production-repos.json` → Alta protección (main products)
- `standard-repos.json` → Protección estándar (experimental, docs)

### 2️⃣ **GitHub Actions Security** (3 workflows)
- `security-scan.yml` → SAST, linting, type checking
- `dependency-check.yml` → Dependabot checks, CVE scanning
- `secret-scan.yml` → Detección de secretos en commits

### 3️⃣ **Governance Files** (4 templates)
- `CODEOWNERS.template` → Define code owners por área
- `SECURITY.md.template` → Política de disclosure seguro
- `dependabot.yml.template` → Automation de dependency updates
- `.github-settings.yml` → Settings organizacionales

### 4️⃣ **Org-Level Config** (2 templates)
- `base-org-config.yml` → Settings recomendadas de org
- `member-roles.yml` → Mapping de roles y permisos

---

## 📊 Reporte JSON (Estructura)

```json
{
  "audit_metadata": {
    "timestamp": "2026-03-22T14:30:00Z",
    "organization": "VoodoOps",
    "auditor": "gh-audit-framework",
    "scan_duration_seconds": 45
  },
  "summary": {
    "total_findings": 12,
    "critical": 1,
    "high": 3,
    "medium": 5,
    "low": 2,
    "info": 1,
    "compliance_score": 72
  },
  "organization": {
    "login": "VoodoOps",
    "name": "VoodoOps",
    "plan": "free",
    "created_at": "2024-06-15",
    "members_count": 5,
    "findings": [...]
  },
  "repositories": [
    {
      "name": "Lab4PurpleSec",
      "visibility": "public",
      "findings": [...]
    }
  ],
  "remediation_priorities": [
    {
      "priority": 1,
      "risk_level": "CRITICAL",
      "action": "Enable 2FA enforcement for all org members",
      "template_available": false
    }
  ]
}
```

---

## 🌐 Reporte HTML

Template HTML responsivo que visualiza:
- 📊 Donut chart de riesgos (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- 📋 Tabla de hallazgos con filtros
- ✅ Checklist de compliance
- 🎯 Plan de remediación priorizado
- 📈 Scoring histórico (si existen múltiples auditorías)

---

## 🚀 Cómo Usar

### Auditoría Manual (Local)
```bash
cd organization
python scripts/run_audit.py VoodoOps --token $GITHUB_TOKEN
# Genera: reports/VoodoOps_2026-03-22/

python scripts/generate_html.py reports/VoodoOps_2026-03-22/audit-report.json
# Genera: audit-report.html (abre en navegador)
```

### Auditoría Automática (GitHub Actions)
Se propone workflow que:
- Ejecuta auditoría diaria/semanal
- Genera reporte JSON
- Comenta en issue con hallazgos
- Mantiene histórico de compliance

---

## 📋 Checklist de Implementación

- [ ] Implementar `collector.py` (recolecta datos)
- [ ] Implementar `analyzer.py` (analiza riesgos)
- [ ] Implementar `standards.py` (reglas de compliance)
- [ ] Implementar `reporter.py` (genera JSON)
- [ ] Crear `run_audit.py` (CLI principal)
- [ ] Crear `generate_html.py` (HTML renderer)
- [ ] Diseñar template HTML
- [ ] Crear 4 templates de branch protection
- [ ] Crear 3 templates de workflows
- [ ] Crear 4 governance files
- [ ] Crear 2 org-level configs
- [ ] Proponer GitHub Actions workflow
- [ ] Documentar uso en README

---

## 🎓 GitHub Best Practices Incluidas

✅ **GitHub Security Model**
- Branch protection rules
- Code review requirements
- Deployment protection rules
- Secret scanning

✅ **OWASP Top 10**
- A02:2021 – Cryptographic Failures (secret management)
- A05:2021 – Access Control (member roles)
- A06:2021 – Vulnerable & Outdated (dependabot)

✅ **CIS GitHub Foundations Benchmark**
- 2FA enforcement
- Member access auditing
- Repository visibility controls
- Commit signing (future)

✅ **Community Standards**
- CoC compliance
- LICENSE requirements
- CONTRIBUTING guidelines
- Security disclosure (SECURITY.md)

---

## Next Steps
1. Confirmar scope con usuario ✓
2. Usar `/python-architect` para generar código
3. Crear templates
4. Generar workflow GitHub Actions
5. Ejecutar primer audit contra VoodoOps
6. Documentar hallazgos
