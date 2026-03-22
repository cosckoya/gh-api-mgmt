# Implementation Plan - GitHub Audit Framework

## 📦 Módulos a Implementar

### 1. **audit/collector.py**
Recolecta todos los datos de la organización via GitHub API

**Métodos principales:**
```python
- get_org_info(org_name) → dict
- get_org_members(org_name) → list
- get_org_outside_collaborators(org_name) → list
- get_org_repos(org_name) → list
- get_repo_details(owner, repo) → dict
- get_repo_branch_protection(owner, repo, branch) → dict
- get_repo_rulesets(owner, repo) → list
- get_repo_workflows(owner, repo) → list
- audit_org_complete(org_name) → AuditData
```

**Entrada:** Org name + GitHub token
**Salida:** Dictionary con estructura completa de datos

---

### 2. **audit/standards.py**
Define reglas de compliance y genera hallazgos

**Componentes:**
```python
- class ComplianceRule:
    - rule_id: str
    - risk_level: str (CRITICAL, HIGH, MEDIUM, LOW, INFO)
    - category: str (org-security, repo-security, access-control, compliance)
    - title: str
    - description: str
    - check: callable (recibe datos, retorna bool)
    - remediation: str
    - template_available: bool

- GITHUB_STANDARDS = {
    "org": [...],  # Org-level rules
    "repo": [...]  # Repo-level rules
}
```

**Reglas a Incluir:**
- Org: 2FA enforcement, member activity, outside collaborators, roles
- Repo: Branch protection, PR reviews, secret scanning, deployments, workflows

---

### 3. **audit/analyzer.py**
Aplica reglas a datos recolectados y genera hallazgos

**Métodos principales:**
```python
- class Finding:
    - rule_id: str
    - risk_level: str
    - title: str
    - description: str
    - affected_items: list
    - remediation: str
    - template_url: str (si aplica)

- analyze_org(audit_data) → List[Finding]
- analyze_repos(audit_data) → List[Finding]
- calculate_compliance_score(findings) → float (0-100)
```

**Lógica:**
- Para cada regla en `GITHUB_STANDARDS`
- Ejecuta `rule.check(audit_data)`
- Si falla → genera `Finding`
- Calcula score: (reglas_ok / total_reglas) * 100

---

### 4. **audit/reporter.py**
Genera reporte JSON con estructura estándar

**Métodos principales:**
```python
- class AuditReport:
    - metadata: dict (timestamp, org, duration)
    - summary: dict (total findings, score, breakdown)
    - organization: dict (org data + findings)
    - repositories: list (repo data + findings)
    - remediation_priorities: list (sorted by risk)

- to_json() → str
- to_file(filepath) → None
```

**Estructura JSON:** (ver FRAMEWORK.md)

---

### 5. **scripts/run_audit.py**
CLI principal - orquesta todo el proceso

**Uso:**
```bash
python scripts/run_audit.py VoodoOps --token $GITHUB_TOKEN --output reports/

# Resultado:
# reports/VoodoOps_2026-03-22/
#   ├── audit-report.json
#   ├── executive-summary.txt
#   └── remediation-plan.md
```

---

### 6. **scripts/generate_html.py**
Convierte JSON → HTML visual

**Entrada:** `audit-report.json`
**Salida:** `audit-report.html`

**Visualizaciones:**
- Pie/Donut chart de findings por risk level
- Tabla interactiva de hallazgos (con filtros)
- Compliance checklist (✓/✗)
- Remediation roadmap
- Repo-by-repo summary

---

### 7. **scripts/apply_templates.py**
Aplica templates recomendadas a repos

**Uso:**
```bash
python scripts/apply_templates.py VoodoOps --template branch-protection-standard
# O interactivo: elige repo + template
```

---

## 📋 Templates a Crear

### A. Branch Protection (3 niveles)

#### `templates/branch-protection/sensitive-repos.json`
Para repos con secretos, keys, certs
```json
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 2,
    "require_code_owner_review": true,
    "require_last_push_approval": true,
    "dismiss_stale_reviews": true
  },
  "required_status_checks": {
    "strict": true,
    "contexts": ["security-scan", "tests"]
  },
  "restrictions": {
    "allow_force_pushes": false,
    "allow_deletions": false
  }
}
```

#### `templates/branch-protection/production-repos.json`
Para repos de producción
```json
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "require_code_owner_review": false,
    "dismiss_stale_reviews": true
  },
  "required_status_checks": {
    "strict": true,
    "contexts": ["tests"]
  },
  "restrictions": {
    "allow_force_pushes": false,
    "allow_deletions": false
  }
}
```

#### `templates/branch-protection/standard-repos.json`
Para repos experimentales/docs
```json
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": {
    "allow_force_pushes": false,
    "allow_deletions": false
  }
}
```

---

### B. GitHub Actions Security (3 workflows)

#### `templates/workflows/security-scan.yml`
```yaml
name: Security Scan
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run lint  # o python ruff check
  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run type-check  # o pyright
```

#### `templates/workflows/dependency-check.yml`
```yaml
name: Dependency Check
on: [push, pull_request]
jobs:
  deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v3
```

#### `templates/workflows/secret-scan.yml`
```yaml
name: Secret Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
```

---

### C. Governance Files (4 templates)

#### `templates/governance/CODEOWNERS.template`
```
# Security critical
/src/auth/ @devops @security
/src/payments/ @devops @security

# DevOps infrastructure
/infra/ @devops
/.github/workflows/ @devops

# Documentation
/docs/ @*
```

#### `templates/governance/SECURITY.md.template`
```markdown
# Security Policy

## Reporting Security Issues

⚠️ **DO NOT** open public issues for security vulnerabilities.

Email: security@voodoops.com

## Supported Versions

| Version | Status |
|---------|--------|
| 1.x     | Supported |
| 0.x     | Unsupported |

## Security Response

- Acknowledge: 48 hours
- Fix: 30 days
- Disclosure: Coordinated with reporter
```

#### `templates/governance/dependabot.yml.template`
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    reviewers:
      - "devops"
    allow:
      - dependency-type: "all"
```

#### `templates/governance/.github-settings.yml`
```yaml
# Organization settings reference
name: Organization Settings
description: |
  Apply these settings in GitHub org settings:

  Security:
  - Enable 2FA enforcement
  - Require members to have verified emails
  - Enable secret scanning for public repos

  Access:
  - Default role for new members: Member (no admin)
  - Allow org members to create repos: true
  - Allow org members to create internal repos: true
  - Allow org members to create private repos: true
  - Allow org members to create public repos: false
```

---

### D. Org-Level Config (2 templates)

#### `templates/org-settings/base-org-config.yml`
```yaml
name: VoodoOps Base Configuration
settings:
  2fa_requirement: required  # Enforce 2FA
  verified_email_requirement: true
  allow_member_repo_creation:
    public: false
    private: true
    internal: true
  default_member_permission: pull  # Minimal privilege
  allow_forking: true

security:
  secret_scanning: enabled
  secret_scanning_push_protection: enabled
  dependabot_alerts: enabled
```

#### `templates/org-settings/member-roles.yml`
```yaml
roles:
  admin:
    permissions: ["all"]
    members: ["@cosckoya"]

  member:
    permissions: ["pull", "push", "maintain"]
    members: []

  outside-collaborator:
    permissions: ["pull"]
    max_duration_days: 90
```

---

## 🌐 HTML Template

**Componentes:**
```html
<head>
  <!-- Bootstrap 5 / TailwindCSS -->
  <!-- Chart.js para gráficas -->
  <!-- DataTables para tablas interactivas -->
</head>

<body>
  <!-- Header con metadata -->
  <h1>GitHub Organization Audit Report</h1>
  <p>VoodoOps | 2026-03-22</p>

  <!-- Summary Section -->
  <section id="summary">
    <h2>Executive Summary</h2>
    <div class="metrics">
      <div>Compliance Score: 72%</div>
      <div>Total Findings: 12</div>
    </div>
    <canvas id="riskChart"></canvas>
  </section>

  <!-- Findings Table -->
  <section id="findings">
    <table class="datatable">
      <thead>
        <tr>
          <th>Risk Level</th>
          <th>Category</th>
          <th>Title</th>
          <th>Affected Items</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <!-- Generado desde JSON -->
      </tbody>
    </table>
  </section>

  <!-- Compliance Checklist -->
  <section id="compliance">
    <h2>Compliance Checklist</h2>
    <div class="checklist">
      <label><input type="checkbox" checked> 2FA Enforcement</label>
      <label><input type="checkbox"> Branch Protection</label>
      <!-- ... -->
    </div>
  </section>

  <!-- Remediation Roadmap -->
  <section id="roadmap">
    <h2>Remediation Priority</h2>
    <ol>
      <li>CRITICAL: Enable 2FA enforcement</li>
      <!-- ... -->
    </ol>
  </section>
</body>
```

---

## 🤖 GitHub Actions Workflow (Propuesto)

### `organization/.github/workflows/org-audit-scheduled.yml`

```yaml
name: Organization Audit - Scheduled

on:
  schedule:
    - cron: '0 2 * * 0'  # Every Sunday at 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  audit:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write

    steps:
      - uses: actions/checkout@v4
        with:
          sparse-checkout: organization

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd organization
          pip install -r requirements.txt

      - name: Run audit
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          cd organization
          python scripts/run_audit.py ${{ github.repository_owner }} \
            --output reports/

      - name: Generate HTML report
        run: |
          cd organization
          python scripts/generate_html.py \
            reports/$(ls -t reports | head -1)/audit-report.json

      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: audit-reports
          path: organization/reports/

      - name: Post comment in issue
        uses: actions/github-script@v7
        with:
          script: |
            // Parse JSON, create comment with summary
            const fs = require('fs');
            const report = JSON.parse(
              fs.readFileSync('organization/reports/.../audit-report.json', 'utf8')
            );
            github.rest.issues.createComment({
              issue_number: 1,  // GitHub Issues board
              body: `## Audit Results\n...`
            });
```

---

## ✅ Checklist de Entregables

**Core Modules:**
- [ ] `audit/collector.py` - Data collection
- [ ] `audit/standards.py` - Compliance rules
- [ ] `audit/analyzer.py` - Risk analysis
- [ ] `audit/reporter.py` - JSON report generation
- [ ] `audit/__init__.py` - Package init

**CLI & Utilities:**
- [ ] `scripts/run_audit.py` - Main CLI
- [ ] `scripts/generate_html.py` - HTML rendering
- [ ] `scripts/apply_templates.py` - Template application
- [ ] `requirements.txt` - Dependencies

**Templates:**
- [ ] 3x Branch Protection JSONs
- [ ] 3x GitHub Actions workflows
- [ ] 4x Governance files
- [ ] 2x Org-level configs

**GitHub Actions:**
- [ ] `org-audit-scheduled.yml` - Automated audits
- [ ] `org-audit-manual.yml` - Manual trigger

**Documentation:**
- [ ] `organization/README.md` - How to use
- [ ] `organization/TEMPLATES.md` - Template guide
- [ ] `organization/STANDARDS.md` - Compliance rules

**Testing:**
- [ ] `tests/test_collector.py`
- [ ] `tests/test_analyzer.py`
- [ ] `tests/test_standards.py`

---

## 🎯 Success Criteria

✅ Auditoría completa de VoodoOps en < 30 segundos
✅ JSON reporte con 15+ hallazgos de seguridad
✅ HTML visual, interactivo y profesional
✅ Compliance score calculado automáticamente
✅ Templates aplicables a repos
✅ Código modular y reutilizable
✅ Documentación completa

---

## Next: Use `/python-architect` to generate all code
