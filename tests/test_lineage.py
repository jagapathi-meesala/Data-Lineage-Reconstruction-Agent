from core.lineage import extract_lineage, analyze_impact, validate_lineage

def test_sql_edges():
    r=extract_lineage({'sql_statements':['CREATE TABLE mart.x AS SELECT * FROM raw.a JOIN raw.b ON a.id=b.id'],'pipeline_dependencies':[]})
    assert {(e['source'],e['target']) for e in r['edges']}=={('raw.a','mart.x'),('raw.b','mart.x')}
def test_explicit_and_normalization():
    r=extract_lineage({'sql_statements':[],'pipeline_dependencies':[{'source':' Raw.A ','target':'MART.B'}]})
    assert r['edges'][0]['source']=='raw.a' and r['edges'][0]['origin']=='explicit_pipeline_dependency'
def test_impact():
    r=analyze_impact([{'source':'a','target':'b'},{'source':'b','target':'c'}],'b')
    assert r['upstream']==['a'] and r['downstream']==['c']
def test_missing_asset(): assert not analyze_impact([],'x')['exists_in_graph']
def test_valid_graph(): assert validate_lineage([{'source':'a','target':'b'}],['a','b'])['valid']
def test_cycle(): assert validate_lineage([{'source':'a','target':'b'},{'source':'b','target':'a'}])['cycle_detected']
def test_unknown_asset():
    r=validate_lineage([{'source':'a','target':'b'}],['a'])
    assert any('Unknown target' in f['message'] for f in r['findings'])
def test_malformed_dependency(): assert extract_lineage({'sql_statements':[],'pipeline_dependencies':[{'source':'a'}]})['warnings']
def test_input_validation():
    try: extract_lineage([])
    except ValueError: return
    assert False
