import json,sys
from pathlib import Path
from .lineage import extract_lineage
def main():
    if len(sys.argv)!=2: print('Usage: python -m core.cli <input.json>',file=sys.stderr); return 2
    try: print(json.dumps(extract_lineage(json.loads(Path(sys.argv[1]).read_text())),indent=2)); return 0
    except Exception as exc: print(json.dumps({'error':str(exc)}),file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())
