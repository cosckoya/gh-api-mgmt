# ✅ READ — funciona con el subcomando nativo
gh ruleset list --repo owner/repo
gh ruleset view <id> --repo owner/repo
gh ruleset check --branch main --repo owner/repo

# ✅ WRITE — hay que pasar por gh api + archivo JSON
gh api \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  repos/{owner}/{repo}/rulesets \
  --input ruleset-baseline.json

# ✅ UPDATE
gh api \
  -X PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  repos/{owner}/{repo}/rulesets/{ruleset_id} \
  --input ruleset-updated.json

# ✅ DELETE
gh api \
  -X DELETE \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2026-03-10" \
  repos/{owner}/{repo}/rulesets/{ruleset_id}

# ✅ HISTORIAL (feature nueva)
gh api \
  repos/{owner}/{repo}/rulesets/{ruleset_id}/history
