#!/usr/bin/env python3
"""Install a screenshot helper into the CI-only client checkout, not the build job."""
from pathlib import Path
import json,shutil
shutil.copyfile('tools/ci_client/CiCapture.java','src/main/java/fr/mathsift/sift/CiCapture.java')
f=Path('src/main/resources/fabric.mod.json')
obj=json.loads(f.read_text());obj['entrypoints']['client'].append('fr.mathsift.sift.CiCapture')
f.write_text(json.dumps(obj,indent=2)+'\n')
