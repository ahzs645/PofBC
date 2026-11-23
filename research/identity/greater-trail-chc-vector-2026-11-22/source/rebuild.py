from pathlib import Path
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parent
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
root = ET.Element("{"+NS+"}svg", {"width":"1070", "height":"520", "viewBox":"35 -20 1070 520", "color":"#000000"})
ET.SubElement(root,"{"+NS+"}title").text = "Greater Trail Community Health Council — reconstruction"
for filename in ["symbol-fragment.svg", "rule-fragment.svg", "main-name-fragment.svg", "caption-fragment.svg"]:
    raw = (ROOT / filename).read_text()
    try:
        part = ET.fromstring(raw)
    except ET.ParseError:
        part = ET.fromstring('<svg xmlns="'+NS+'">'+raw+'</svg>')
    for node in part.iter():
        if not node.tag.startswith("{"):
            node.tag = "{"+NS+"}"+node.tag
    if part.tag.rsplit("}",1)[-1] == "svg":
        for node in part:
            if node.tag.rsplit("}",1)[-1] not in ["title","desc","metadata"]:
                root.append(node)
    else:
        root.append(part)
out = ROOT.parent / "Greater-Trail-CHC-Rebuilt.svg"
ET.ElementTree(root).write(out, encoding="UTF-8", xml_declaration=True)
print(out)
