import datetime
import json
import os
import sys
import random
import string

# SBOM 기본 구조
sbom_json = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.4",
    "serialNumber": "",
    "version": 1,
    "metadata": {
        "timestamp": "",
        "authors": [{"name": "IoTcube - https://iotcube.net"}],
        "component": {
            "group": "",
            "name": "",
            "version": "",
            "type": "application",
            "bom-ref": "",
            "purl": ""
        }
    },
    "components": [],
    "dependencies": [{"ref": "", "dependsOn": []}]
}

file2hash = {}  # 파일 디렉토리 -> 해시값 매핑 딕셔너리

def generate_serial_number():
    """
    CycloneDX UUID 형식의 고유 시리얼 번호 생성.
    """
    return f"urn:uuid:{'-'.join([''.join(random.choices(string.hexdigits.lower()[:16], k=n)) for n in (8, 4, 4, 4, 12)])}"

def map_file_to_hash(hidx_path):
    """
    .hidx 파일에서 파일 디렉토리와 해시값을 매핑.

    Args:
        hidx_path (str): .hidx 파일 경로.
    """
    with open(hidx_path, 'r', encoding="UTF-8") as fp:
        lines = fp.readlines()

    # 첫 번째 줄은 헤더로 처리
    sbom_json["dependencies"][0]["ref"] = lines[0].split()[1]

    # 나머지 라인을 처리하여 파일 디렉토리와 해시값 매핑
    for line in lines[1:]:
        parts = line.strip().split('\t')
        if len(parts) >= 2:
            hash_val, file_dir = parts[0], parts[1]
            file2hash[file_dir] = hash_val

def build_components(dep_data):
    """
    SBOM 구성 요소를 생성.

    Args:
        dep_data (dict): OSS 데이터.
    """
    added_components = set()  # 중복 방지를 위한 세트

    for oss, files in dep_data.items():
        sbom_json["dependencies"][0]["dependsOn"].append(oss)
        oss_name = oss.split()[0]

        for file_path in files:
            component_key = f"{oss_name}:{file_path}"
            if component_key in added_components:
                continue

            component = {
                "group": oss_name,
                "name": os.path.splitext(os.path.basename(file_path))[0],
                "version": "",
                "type": "file",
                "bom-ref": "",
                "purl": "",
                "hashes": []
            }

            md5hash = {"alg": "MD5", "content": file2hash[file_path]}
            component["hashes"].append(md5hash)
            short_hash = md5hash["content"][:12]
            component["version"] = f"0.0.0-{short_hash}"
            component["purl"] = (
                f"pkg:generic/{oss_name}/{component['name']}@{component['version']}#{file_path}"
            )
            component["bom-ref"] = component["purl"]

            sbom_json["components"].append(component)
            added_components.add(component_key)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: script.py <hidx_path> <dep_data_file_path> <session_key>")
        sys.exit(1)

    hidx_path, dep_data_file_path, session_key = sys.argv[1:4]

    with open(dep_data_file_path, 'r', encoding='utf-8') as json_file:
        dep_data = json.load(json_file)

    map_file_to_hash(hidx_path)
    build_components(dep_data)

    os.remove(dep_data_file_path)

    sbom_json["serialNumber"] = generate_serial_number()
    sbom_json["metadata"]["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    input_name = sbom_json["dependencies"][0]["ref"]
    sbom_json["metadata"]["component"].update({
        "name": input_name,
        "purl": f"pkg:generic/{input_name}",
        "bom-ref": f"pkg:generic/{input_name}"
    })

    result = {
        "sbom": sbom_json,
        "file_count": len(sbom_json["components"])
    }
    print(json.dumps(result, indent=4))
