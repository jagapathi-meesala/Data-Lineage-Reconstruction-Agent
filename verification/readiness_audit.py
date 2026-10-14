from pathlib import Path
import yaml
root=Path(__file__).resolve().parents[1]
required=['agent.yaml','README.md','SOUL.md','RULES.md','DUTIES.md','AGENTS.md','EXPLAINABILITY.md','requirements.txt','.env.example','.gitignore','pytest.ini','core/__init__.py','core/lineage.py','core/cli.py','tools/extract-lineage.yaml','tools/analyze-impact.yaml','tools/validate-lineage.yaml','skills/lineage-reconstruction/SKILL.md','skills/impact-analysis/SKILL.md','skills/lineage-validation/SKILL.md','tests/test_lineage.py','examples/lineage_case.json','verification/readiness_audit.py']
missing=[x for x in required if not (root/x).is_file()]
m=yaml.safe_load((root/'agent.yaml').read_text())
assert m['name']=='data-lineage-reconstruction-agent' and len(m['tools'])==3 and len(m['skills'])==3
doc=(root/'EXPLAINABILITY.md').read_text()
for h in ['## Inputs','## Decision','## Limits']: assert h in doc
for p in (root/'tools').glob('*.yaml'):
 d=yaml.safe_load(p.read_text()); assert d['input_schema']['type']=='object' and d['input_schema']['additionalProperties'] is False
if missing: print('FAIL missing:',missing); raise SystemExit(1)
print('PASS: manifest name normalized')
print('PASS: flat tools listed')
print('PASS: required explainability headings')
print('PASS: strict tool schemas')
print(f'PASS: {len(required)}/{len(required)} required files present')
