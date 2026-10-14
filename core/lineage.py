import re
from collections import defaultdict, deque
IDENT = r'(?:[A-Za-z_][\w$]*\.)*[A-Za-z_][\w$]*'
def norm(value): return str(value).strip().strip('`"[]').lower()
def extract_lineage(payload):
    if not isinstance(payload, dict): raise ValueError('Input must be a JSON object.')
    statements, deps = payload.get('sql_statements', []), payload.get('pipeline_dependencies', [])
    known = {norm(x) for x in payload.get('known_assets', [])}
    if not isinstance(statements, list) or not isinstance(deps, list): raise ValueError('sql_statements and pipeline_dependencies must be lists.')
    edges, warnings, seen = [], [], set()
    def add(s,t,origin,evidence):
        s,t=norm(s),norm(t)
        if not s or not t: warnings.append('Skipped dependency with empty endpoint.'); return
        key=(s,t,origin)
        if key not in seen:
            seen.add(key); edges.append({'source':s,'target':t,'origin':origin,'evidence':evidence})
    for d in deps:
        if not isinstance(d,dict) or not d.get('source') or not d.get('target'): warnings.append('Skipped malformed pipeline dependency.'); continue
        add(d['source'],d['target'],'explicit_pipeline_dependency',d.get('evidence','Supplied dependency metadata'))
    for i,sql in enumerate(statements):
        if not isinstance(sql,str): warnings.append(f'Skipped non-string SQL statement at index {i}.'); continue
        clean=re.sub(r'--[^\n]*|/\*.*?\*/',' ',sql,flags=re.S)
        clean=re.sub(r"'(?:''|[^'])*'", "''", clean)
        targets=re.findall(r'\b(?:INSERT\s+INTO|MERGE\s+INTO|UPDATE)\s+('+IDENT+r')',clean,re.I)
        targets+=re.findall(r'\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW)\s+(?:IF\s+NOT\s+EXISTS\s+)?('+IDENT+r')',clean,re.I)
        sources=re.findall(r'\b(?:FROM|JOIN)\s+('+IDENT+r')',clean,re.I)
        if not targets: warnings.append(f'SQL statement {i} has no recognized target; no SQL edge inferred.'); continue
        for target in targets:
            for source in sources:
                if norm(source)!=norm(target): add(source,target,'inferred_sql_reference',sql[:240])
        if not sources: warnings.append(f'SQL statement {i} has a target but no recognized FROM/JOIN source.')
    unresolved=[]
    if known:
        for e in edges:
            for a in (e['source'],e['target']):
                if a not in known: unresolved.append(a)
    return {'edges':edges,'warnings':warnings,'unresolved_assets':sorted(set(unresolved)),'asset_count':len({x for e in edges for x in (e['source'],e['target'])})}
def analyze_impact(edges, asset):
    asset=norm(asset); up,down=defaultdict(set),defaultdict(set); all_assets=set()
    for e in edges:
        s,t=norm(e['source']),norm(e['target']); up[t].add(s); down[s].add(t); all_assets.update((s,t))
    def walk(graph):
        found=set(); q=deque(graph.get(asset,set()))
        while q:
            n=q.popleft()
            if n==asset or n in found: continue
            found.add(n); q.extend(graph.get(n,set())-found)
        return sorted(found)
    return {'asset':asset,'exists_in_graph':asset in all_assets,'upstream':walk(up),'downstream':walk(down),'direct_dependents':sorted(down.get(asset,set()))}
def validate_lineage(edges, known_assets=None):
    known={norm(x) for x in (known_assets or [])}; findings=[]; seen=set(); graph=defaultdict(list)
    for i,e in enumerate(edges):
        if not isinstance(e,dict) or not e.get('source') or not e.get('target'):
            findings.append({'severity':'high','message':f'Edge {i} has invalid endpoint.'}); continue
        s,t=norm(e['source']),norm(e['target'])
        if s==t: findings.append({'severity':'medium','message':f'Self-reference detected: {s}.'})
        if (s,t) in seen: findings.append({'severity':'low','message':f'Duplicate edge: {s} -> {t}.'})
        seen.add((s,t)); graph[s].append(t)
        if known and s not in known: findings.append({'severity':'medium','message':f'Unknown source asset: {s}.'})
        if known and t not in known: findings.append({'severity':'medium','message':f'Unknown target asset: {t}.'})
    state={}; cyc=set()
    def visit(n,stack):
        state[n]=1; stack.append(n)
        for nxt in graph.get(n,[]):
            if state.get(nxt,0)==0: visit(nxt,stack)
            elif state.get(nxt)==1: cyc.update(stack[stack.index(nxt):])
        stack.pop(); state[n]=2
    for n in list(graph):
        if state.get(n,0)==0: visit(n,[])
    if cyc: findings.append({'severity':'medium','message':'Directed cycle detected involving: '+', '.join(sorted(cyc))+'.'})
    return {'valid':not any(f['severity']=='high' for f in findings),'findings':findings,'edge_count':len(edges),'cycle_detected':bool(cyc)}
