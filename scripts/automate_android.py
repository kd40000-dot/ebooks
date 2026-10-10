#!/usr/bin/env python3
"""Try to create a real Smart Book SB2 in the Android emulator; capture UI on failure."""
from pathlib import Path
import re, subprocess, sys, time, xml.etree.ElementTree as ET, zipfile
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"debug"
D.mkdir(exist_ok=True)
O=ROOT/"artifacts"
O.mkdir(exist_ok=True)
SOURCE=ROOT/"books"/"unicorn"/"vietnamese_hyphenated.txt"
STEP=0

def run(args, check=True, binary=False):
    p=subprocess.run(["adb"]+list(args), capture_output=True,timeout=75,
                     **({} if binary else {"text":True}))
    if check and p.returncode: raise RuntimeError(str(p.stderr)[-600:])
    return p.stdout

def shell(command):
    return run(["shell","sh","-c",command],check=False)

def snapshot(label):
    global STEP
    STEP+=1
    stem=D/(f"{STEP:02d}_"+label)
    (stem.with_suffix(".png")).write_bytes(run(["exec-out","screencap","-p"],binary=True))
    dump=run(["shell","uiautomator","dump","/sdcard/ui.xml"],check=False)
    print("UI dump:",dump[:400],flush=True)
    raw=run(["exec-out","cat","/sdcard/ui.xml"],check=False)
    stem.with_suffix(".xml").write_text(raw,encoding="utf-8")
    try:
        nodes=list(ET.fromstring(raw).iter("node"))
    except ET.ParseError:
        nodes=[]
    labels=[n.get("text") or n.get("content-desc") for n in nodes]
    print(f"[{label}]: "+ " | ".join(x[:90] for x in labels if x)[:7000],flush=True)
    return nodes

def pos(node):
    m=re.search(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]",node.get("bounds",""))
    if not m:return None
    a,b,c,d=map(int,m.groups())
    return ((a+c)//2,(b+d)//2)

def click(nodes, terms):
    for term in terms:
        for n in nodes:
            s=((n.get("text") or "")+" "+(n.get("content-desc") or "")).lower()
            if term.lower() in s and pos(n):
                x,y=pos(n)
                print("CLICK",term,x,y,flush=True)
                run(["shell","input","tap",str(x),str(y)])
                time.sleep(3)
                return True
    return False

def has(nodes,term):
    return any(term.lower() in ((n.get("text") or "")+" "+(n.get("content-desc") or "")).lower() for n in nodes)

def automate():
    assert SOURCE.exists(),str(SOURCE)
    target="/sdcard/Download/ebooks-unicorn"
    shell(f"mkdir -p {target}")
    for filename in ["vietnamese_hyphenated.txt","english.txt"]:
        run(["push",str(ROOT/"books"/"unicorn"/filename),target+"/"+filename])
    run(["shell","monkey","-p","com.kursx.smartbook","-c","android.intent.category.LAUNCHER","1"])
    time.sleep(10)
    nodes=snapshot("launched")
    # Fresh installs launch a multi-page welcome wizard; advance the
    # visible Continue button at the bottom, capturing each step.
    for page in range(4):
        if click(nodes,["continue","next","get started","start reading"]):
            nodes=snapshot(f"onboarding_{page + 1}")
            continue
        # On some Android images uiautomator cannot dump the Compose UI.
        # Only use coordinate fallback when the known welcome screen is first.
        if page==0 and not nodes:
            print("Trying bottom-center Continue on fresh-install welcome screen")
            run(["shell","input","tap","416","1648"])
            time.sleep(4)
            nodes=snapshot("onboarding_1")
        else:
            break
    # Text share intent may expose native Create Parallel Book path.
    remote=target+"/vietnamese_hyphenated.txt"
    cmd=('am start -a android.intent.action.SEND -t text/plain '
         '-p com.kursx.smartbook --es android.intent.extra.TEXT "$(cat '+remote+')"')
    print("Share intent:",shell(cmd)[:600],flush=True)
    time.sleep(8)
    nodes=snapshot("shared_text")
    if click(nodes,["create parallel book","create a parallel book","create book"]):
        nodes=snapshot("book_editor")
    if not has(nodes,"enter a book name"):
        if click(nodes,["add book","import text file","new book"]):
            nodes=snapshot("navigation")
    if has(nodes,"enter a book name"):
        edits=[n for n in nodes if "EditText" in n.get("class","") and pos(n)]
        edits.sort(key=lambda n:pos(n)[1])
        if edits:
            x,y=pos(edits[0])
            run(["shell","input","tap",str(x),str(y)])
            run(["shell","input","keyevent","KEYCODE_CTRL_LEFT","KEYCODE_A"],check=False)
            run(["shell","input","text","I_Found_a_Unicorn"])
            run(["shell","input","keyevent","KEYCODE_BACK"])
        nodes=snapshot("named_book")
        if click(nodes,["end of sentence","paragraph separator"]):
            nodes=snapshot("separator_menu")
            if click(nodes,["empty line","blank line","empty string"]):
                nodes=snapshot("separator_set")
        if click(nodes,["upload a file"]):
            nodes=snapshot("file_picker")
            if click(nodes,["ebooks-unicorn"]):
                nodes=snapshot("selected_folder")
            if click(nodes,["vietnamese_hyphenated.txt"]):
                nodes=snapshot("primary_imported")
        if click(nodes,["chapter 1"]):
            nodes=snapshot("chapter_editor")
            if click(nodes,["translation","add language","english"]):
                nodes=snapshot("translation_editor")
    print("Finished current automatic navigation; searching for real exports.",flush=True)
    exported=shell("find /sdcard/Download /sdcard/Documents -type f -iname '*.sb2' 2>/dev/null")
    found=0
    for remote in exported.splitlines():
        remote=remote.strip()
        if not remote.lower().endswith(".sb2") or not remote.startswith("/sdcard/"):
            continue
        local=O/Path(remote).name
        run(["pull",remote,str(local)])
        with zipfile.ZipFile(local) as z:
            if any(f.filename.endswith(".sb") for f in z.infolist()):
                found+=1
                print("EXPORTED BY APP",local,flush=True)
    return found>0

try:
    sys.exit(0 if automate() else 2)
except Exception as e:
    print("Automation error",repr(e),file=sys.stderr,flush=True)
    try:snapshot("error")
    except Exception:pass
    sys.exit(1)
