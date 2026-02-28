import json
import yaml
import pathlib

def validate():
    for path in pathlib.Path('.').rglob('*'):
        if path.suffix == '.json':
            json.load(open(path))
        elif path.suffix in ['.yaml', '.yml']:
            yaml.safe_load(open(path))
    print("✅ All JSON/YAML files are syntactically valid.")

if __name__ == "__main__":
    validate()
