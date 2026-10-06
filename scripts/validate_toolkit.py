"""Validate skill/agent metadata, local links, reachability, fences and shell syntax.\nRun: uv run --no-project --with pyyaml python scripts/validate_toolkit.py\n"""
from pathlib import Path
import re
import subprocess
import sys
import yaml

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
def validate_skill(folder):
    text = (folder / 'SKILL.md').read_text()
    if not text.startswith('---\n'):
        return False, 'Missing YAML frontmatter'
    try:
        meta = yaml.safe_load(text.split('---', 2)[1])
    except (IndexError, yaml.YAMLError) as error:
        return False, str(error)
    if set(meta) != {'name', 'description'}:
        return False, 'Expected portable name and description metadata'
    if not re.fullmatch(r'[a-z0-9-]{1,64}', meta['name']):
        return False, 'Invalid skill name'
    if not isinstance(meta['description'], str) or not meta['description'].strip():
        return False, 'Missing description'
    return True, 'Skill metadata valid'

errors = []
skills = {}
for entry in sorted((root / 'skills').glob('*/SKILL.md')):
    ok, message = validate_skill(entry.parent)
    print(f'{entry.parent.name}: {message}')
    if not ok:
        errors.append(f'{entry}: {message}')
    meta = yaml.safe_load(entry.read_text().split('---', 2)[1])
    name = meta['name']
    if name != entry.parent.name or name in skills:
        errors.append(f'Nonunique or mismatched skill name: {entry}')
    skills[name] = entry

wrds_agents = [p for p in (root / 'agents').glob('*.md') if 'wrds' in p.stem]
expected_agents = {'wrds-psql-agent', 'wrds-taq-agent'}
if {p.stem for p in wrds_agents} != expected_agents:
    errors.append(f'WRDS agent inventory: {[p.stem for p in wrds_agents]}')
for entry in wrds_agents:
    content = entry.read_text()
    meta = yaml.safe_load(content.split('---', 2)[1])
    if meta['name'] != entry.stem or not isinstance(meta.get('description'), str):
        errors.append(f'Invalid agent metadata: {entry}')
    expected = ['wrds-psql', 'wrds-schema'] if entry.stem == 'wrds-psql-agent' else ['wrds-ssh', 'wrds-taq']
    if meta.get('skills') != expected:
        errors.append(f'Wrong skill attachments: {entry}')
    if len(content.splitlines()) > 45 or '```sql' in content or '```sas' in content:
        errors.append(f'Database knowledge left in agent: {entry}')

files = list((root / 'skills').rglob('*.md')) + wrds_agents + [root / 'README.md', root / 'CLAUDE.md']
edges = {}
shell_blocks = 0
link_count = 0
for entry in files:
    content = entry.read_text()
    edges[entry.resolve()] = []
    for target in re.findall(r'\[[^\]]+\]\(([^\s)]+)\)', content):
        if target.startswith(('https://', 'http://', 'mailto:', '#')):
            continue
        target = target.split('#', 1)[0]
        dest = (entry.parent / target).resolve()
        link_count += 1
        if not dest.is_file():
            errors.append(f'Broken link in {entry.relative_to(root)}: {target}')
        else:
            edges[entry.resolve()].append(dest)
    fences = re.findall(r'^\s*(`{3,}|~{3,}).*$', content, re.MULTILINE)
    if len(fences) % 2:
        errors.append(f'Unbalanced fences: {entry}')
    for block in re.findall(r'^```(?:bash|sh)\n(.*?)^```', content, re.MULTILINE | re.DOTALL):
        shell_blocks += 1
        check = subprocess.run(['bash', '-n'], input=block, text=True, capture_output=True)
        if check.returncode:
            errors.append(f'Shell syntax in {entry}: {check.stderr.strip()}')

seen = set()
queue = [p.resolve() for p in skills.values()]
while queue:
    item = queue.pop()
    if item in seen:
        continue
    seen.add(item)
    queue.extend(edges.get(item, []))
for entry in (root / 'skills').glob('*/references/*.md'):
    if entry.resolve() not in seen:
        errors.append(f'Unreachable reference: {entry.relative_to(root)}')

print(f'{len(skills)} skills, {len(wrds_agents)} WRDS agents, {link_count} local links, {shell_blocks} shell blocks checked')
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print('All metadata, reference reachability, link, fence, and shell syntax checks passed.')
