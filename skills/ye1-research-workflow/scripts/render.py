# Data streams require the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

"""Render with explicit bundled tools and existing macOS font directories.
Never installs fonts or guesses system LibreOffice. Every page still needs visual QA.
"""
import argparse,json,os,sys,tempfile,hashlib
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
import materialize
p=argparse.ArgumentParser(description=__doc__);p.add_argument('docx',type=Path);p.add_argument('--runtime-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
a=p.parse_args();b=a.runtime_root/'dependencies'/'bin'/'override'
tools={'enabled':True,**{k:{'executable':str((b/k).resolve()),'sha256':sha(b/k) if (b/k).is_file() else ''} for k in ['soffice','pdftoppm']}}
r=materialize.render(a.docx,tools,a.out)
(a.out/'render-receipt.json').write_text(json.dumps(r,indent=2))
print('Rendered; inspect every page before marking visual PASS: '+str(a.out))
