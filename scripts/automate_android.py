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
    # ADB shell executes its final argument as a complete shell command.
    # Do not use "sh -c" with separate unquoted tokens: Android otherwise
    # executes only the first word (for example, `am` with no arguments).
    return run(["shell",command],check=False)

def snapshot(label):
    global STEP
    STEP+=1
    stem=D/(f"{STEP:02d}_"+label)
    (stem.with_suffix(".png")).write_bytes(run(["exec-out","screencap","-p"],binary=True))
    # Remove previous dump before every capture. Android uiautomator can
    # return an empty error, leaving an old XML file from the creator screen.
    # That previously hid a SUCCESSFUL Save to the real reader.
    shell("rm -f /sdcard/ui.xml")
    dump=run(["shell","uiautomator","dump","/sdcard/ui.xml"],check=False)
    print("UI dump:",dump[:400],flush=True)
    raw=run(["exec-out","cat","/sdcard/ui.xml"],check=False)
    if "<hierarchy" not in raw:
        print("UI_DUMP_UNAVAILABLE (not reusing stale content)",flush=True)
        raw=""
    stem.with_suffix(".xml").write_text(raw,encoding="utf-8")
    try:
        nodes=list(ET.fromstring(raw).iter("node"))
    except ET.ParseError:
        nodes=[]
    labels=[n.get("text") or n.get("content-desc") for n in nodes]
    print(f"[{label}]: "+ " | ".join(x[:90] for x in labels if x)[:7000],flush=True)
    clickable=[(n.get("resource-id") or n.get("class") or "?")+
               ":"+(n.get("content-desc") or n.get("text") or "[unlabelled]")+
               "@"+str(pos(n)) for n in nodes if n.get("clickable")=="true"]
    print(f"[{label}] CLICKABLE: "+" | ".join(clickable)[:6000],flush=True)
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

def resource(nodes, suffix):
    for n in nodes:
        if (n.get("resource-id") or "").endswith(suffix) and pos(n):
            return n
    return None

def tap_at(x,y):
    run(["shell","input","tap",str(x),str(y)])
    time.sleep(2)

def replace_edittext(nodes, suffix, value):
    n=resource(nodes,suffix)
    if n is None or "EditText" not in n.get("class",""):
        print("FIELD NOT FOUND",suffix,flush=True)
        return False
    x,y=pos(n)
    old=n.get("text") or ""
    tap_at(x,y)
    run(["shell","input","keyevent","KEYCODE_MOVE_END"])
    # Deterministically clear the existing text. Ctrl+A did not work in the
    # initial experiment and inserted the title into the placeholder.
    count=min(120,max(35,len(old)+15))
    run(["shell","input","keyevent"]+["KEYCODE_DEL"]*count)
    run(["shell","input","text",value.replace(" ","%s")])
    run(["shell","input","keyevent","KEYCODE_BACK"])
    return True

def select_language_list_item(nodes, language="Vietnamese"):
    # Filter search EditText and actual language TextView can contain the same
    # string; only the android:id/text1 item selects a language.
    for n in nodes:
        if (n.get("resource-id") or "")=="android:id/text1" and (n.get("text") or "").strip().lower()==language.lower() and pos(n):
            x,y=pos(n)
            print("LANGUAGE RESULT SELECTED",language,x,y,flush=True)
            tap_at(x,y)
            return True
    return False

def select_vietnamese(nodes):
    spinners=[n for n in nodes if
              (n.get("resource-id") or "").endswith("/spinner") and pos(n)]
    if not spinners: return nodes
    spinners.sort(key=lambda n:pos(n)[1])
    x,y=pos(spinners[-1])
    tap_at(x,y)
    page=snapshot("language_picker")
    # The KursX picker has a com.kursx.smartbook:id/edit search field.
    field=resource(page,"/edit")
    if field is not None and pos(field):
        x,y=pos(field)
        tap_at(x,y)
        run(["shell","input","text","Vietnamese"])
        time.sleep(2)
        run(["shell","input","keyevent","KEYCODE_BACK"])
        page=snapshot("language_filtered")
        if select_language_list_item(page):
            return snapshot("vietnamese_selected")
    # Backup: scroll alphabetically past V. 13 swipes previously only reached K.
    for i in range(35):
        if select_language_list_item(page):
            return snapshot("vietnamese_selected")
        run(["shell","input","swipe","360","1450","350","350","150"])
        time.sleep(0.3)
        if i%4==3:
            page=snapshot(f"language_scroll_{i}")
        else:
            # A fast XML-only dump reduces time pressure from emulator limits.
            run(["shell","uiautomator","dump","/sdcard/ui.xml"],check=False)
            raw=run(["exec-out","cat","/sdcard/ui.xml"],check=False)
            try:page=list(ET.fromstring(raw).iter("node"))
            except ET.ParseError:page=[]
    print("Vietnamese not found after search and scrolling",flush=True)
    return snapshot("language_unknown")

def automate():
    assert SOURCE.exists(),str(SOURCE)
    target="/sdcard/Download/ebooks-unicorn"
    shell(f"mkdir -p {target}")
    for filename in ["vietnamese_hyphenated.txt","english.txt"]:
        run(["push",str(ROOT/"books"/"unicorn"/filename),target+"/"+filename])
    shell("pm grant com.kursx.smartbook android.permission.POST_NOTIFICATIONS")
    run(["shell","monkey","-p","com.kursx.smartbook","-c","android.intent.category.LAUNCHER","1"])
    time.sleep(22)
    nodes=snapshot("launched")
    # Handle system first-run windows, onboarding and occasional ANRs.
    # Prefer UIAutomator controls over screen coordinates, and re-snapshot
    # after every change instead of sending the book to an unready app.
    ready=False
    anr_count=0
    for page in range(12):
        if has(nodes,"system ui isn't responding") or has(nodes,"isn't responding"):
            anr_count+=1
            if anr_count>=3:
                print("SYSTEM_UI_ANR_UNRECOVERABLE: aborting rather than retrying forever",flush=True)
                return False
            if click(nodes,["wait"]):
                time.sleep(10)
                nodes=snapshot(f"system_recovery_{page}")
                continue
        if click(nodes,["got it","don't allow","don’t allow"]):
            nodes=snapshot(f"system_prompt_{page}")
            continue
        if has(nodes,"notifications?") or has(nodes,"send you notifications"):
            if click(nodes,["allow"]):
                nodes=snapshot(f"notification_{page}")
                continue
        if click(nodes,["continue","get started","start reading","next"]):
            nodes=snapshot(f"onboarding_{page}")
            continue
        if has(nodes,"library") or has(nodes,"my books") or has(nodes,"create book"):
            ready=True
            print("APP_HOME_READY",flush=True)
            break
        if not nodes and page<3:
            time.sleep(8)
            nodes=snapshot(f"wait_for_home_{page}")
            continue
        print("Unknown onboarding state, capturing before share",flush=True)
        break
    if not ready:
        print("APP_HOME_NOT_READY: skipping share fallback",flush=True)
        return False
    # Open the native library rather than sharing text to the URI-only reader.
    if click(nodes,["library"]):
        nodes=snapshot("library_home")
    if click(nodes,["my books"]):
        nodes=snapshot("my_books")
    if click(nodes,["add book","create book","new book"]):
        nodes=snapshot("add_book_dialog")
    # In the native Add Book dialog the action text is exactly
    # "Create a parallel book". Use it directly: earlier code missed the
    # indefinite article and unnecessarily invoked Android ACTION_SEND.
    if click(nodes,["create a parallel book","create parallel book"]):
        nodes=snapshot("native_parallel_book_editor")
    # Only fall back to text sharing if native creator is unavailable.
    # The shared activity is a separate "Open a book"/"Share" resolver.

    if not has(nodes,"enter a book name"):
        remote=target+"/vietnamese_hyphenated.txt"
        cmd=('am start -a android.intent.action.SEND -t text/plain '
             '-p com.kursx.smartbook --es android.intent.extra.TEXT "$(cat '+remote+')"')
        print("Share intent:",shell(cmd)[:600],flush=True)
        time.sleep(8)
        nodes=snapshot("shared_text")
        # The resolver has two "Smart Book" activities. The first is "Open a
        # book" (expects a content URI); the second is the text share target.
        targets=[n for n in nodes if (n.get("text") or "")=="Smart Book" and pos(n)]
        if has(nodes,"just once") and len(targets)>=2:
            targets.sort(key=lambda n:pos(n)[1])
            x,y=pos(targets[-1])
            run(["shell","input","tap",str(x),str(y)])
            time.sleep(2)
            nodes=snapshot("selected_text_share_target")
            if click(nodes,["just once"]):
                nodes=snapshot("text_share_activity")
        for dialog in range(3):
            if has(nodes,"isn't responding"):
                if click(nodes,["wait"]):
                    time.sleep(15)
                    nodes=snapshot(f"share_anr_{dialog}")
                    continue
            if click(nodes,["got it","don't allow","don’t allow"]):
                nodes=snapshot(f"share_prompt_{dialog}")
                continue
            break
    # Find the creator in the real app rather than requiring a guessed deep link.
    if click(nodes,["create parallel book","create a parallel book","create book","new book"]):
        nodes=snapshot("book_editor")
    if not has(nodes,"enter a book name"):
        if click(nodes,["main"]):
            nodes=snapshot("main_tab")
        if click(nodes,["create parallel book","create a book","new book","add book","import text file","create book"]):
            nodes=snapshot("creation_navigation")
    if not has(nodes,"enter a book name"):
        if click(nodes,["library","my books"]):
            nodes=snapshot("library_tab")
        if click(nodes,["create parallel book","create a book","new book","add book","import text file","create book"]):
            nodes=snapshot("creation_from_library")
    if has(nodes,"enter a book name"):
        replace_edittext(nodes,"/name","I_Found_a_Unicorn")
        nodes=snapshot("named_book")
        if click(nodes,["end of sentence","paragraph separator"]):
            nodes=snapshot("separator_menu")
            # Smart Book calls the blank-line paragraph separator "Empty string".
            if click(nodes,["empty string"]):
                nodes=snapshot("separator_set")
        nodes=select_vietnamese(nodes)
        if resource(nodes,"/chapter") is not None:
            replace_edittext(nodes,"/chapter","Chapter 1")
            nodes=snapshot("chapter_named")
        # In the direct native editor an empty chapter offers Paste text or
        # Upload a file. Prefer file picker so UTF-8 Vietnamese is unchanged.
        if click(nodes,["upload a file","upload file","choose a file"]):
            nodes=snapshot("native_source_file_picker")
            if click(nodes,["downloads","download"]):
                nodes=snapshot("native_downloads")
            if click(nodes,["ebooks-unicorn"]):
                nodes=snapshot("native_unicorn_folder")
            if click(nodes,["vietnamese_hyphenated.txt","vietnamese_hyphenated"]):
                nodes=snapshot("native_vietnamese_imported")
        # The primary file picker has already loaded the TXT chapter.
        # Do not reopen /source: that restarts Android's file chooser.
        if not has(nodes,"vietnamese_hyphenated"):
            print("PRIMARY_CHAPTER_NOT_PRESENT: abort before Save",flush=True)
            return False
        print("PRIMARY_CHAPTER_PRESENT",flush=True)
        # User-confirmed native workflow (Fairphone / LineageOS):
        # Vietnamese chapter's 3-dot menu → Translation → Upload a file →
        # english.txt. The English file must be added BEFORE Save/Export.
        # Use the actual resource ID /menu rather than guessing coordinates.
        chapter_menu=resource(nodes,"/menu")
        if chapter_menu is None or pos(chapter_menu) is None:
            print("CHAPTER_MENU_NOT_FOUND: cannot attach English",flush=True)
            return False
        x,y=pos(chapter_menu)
        print("CHAPTER_THREE_DOT_MENU",x,y,flush=True)
        tap_at(x,y)
        nodes=snapshot("chapter_three_dot_actions")
        if not click(nodes,["translation"]):
            print("TRANSLATION_ACTION_NOT_FOUND",flush=True)
            return False
        nodes=snapshot("chapter_translation_controls")
        if not click(nodes,["upload a file","upload file"]):
            print("TRANSLATION_UPLOAD_NOT_FOUND",flush=True)
            return False
        nodes=snapshot("english_translation_file_picker")
        if not click(nodes,["english.txt"]):
            # DocumentsUI may initially show another folder, but the paired
            # files are both in the emulator's Downloads/ebooks-unicorn folder.
            if click(nodes,["downloads","download"]):
                nodes=snapshot("translation_picker_downloads")
            if click(nodes,["ebooks-unicorn"]):
                nodes=snapshot("translation_picker_story_folder")
            if not click(nodes,["english.txt"]):
                print("ENGLISH_TXT_NOT_FOUND_IN_PICKER",flush=True)
                return False
        nodes=snapshot("english_translation_imported")
        if not has(nodes,"english"):
            print("ENGLISH_TRANSLATION_NOT_CONFIRMED_IN_EDITOR",flush=True)
            return False
        print("ENGLISH_TRANSLATION_ATTACHED_BEFORE_SAVE",flush=True)
        # Save now opens the NATIVE BOOK READER (verified by last-run PNG).
        # Last run's uiautomator XML was stale and misleading, not Save failure.
        if click(nodes,["save"]):
            time.sleep(7)
            nodes=snapshot("reader_after_save")
            print("SAVE_TAPPED_READER_SCREENSHOT_CAPTURES_BOOK",flush=True)
            # The app shows a first-run reader tutorial after Save and after
            # the first menu tap. Dismiss it *before* trying to export.
            for n in range(4):
                if click(nodes,["ok","got it","skip","close"]):
                    nodes=snapshot(f"reader_tutorial_dismissed_{n}")
                else:
                    break
            # Reader hamburger observed at (778,109) on 832x1843.
            for n in range(3):
                tap_at(778,109)
                nodes=snapshot(f"reader_hamburger_menu_{n}")
                if has(nodes,"make a short press") or has(nodes,"note") and has(nodes,"translation"):
                    if click(nodes,["ok","got it","skip","close"]):
                        nodes=snapshot(f"reader_tutorial_after_menu_{n}")
                        continue
                if click(nodes,["share book","export book","export","share","send book","save to file"]):
                    nodes=snapshot("native_export_or_share")
                else:
                    # Exact Android resource ID: the previous broad word
                    # "settings" accidentally opened *Quick settings*.
                    book_settings=resource(nodes,"/book_settings")
                    if book_settings is not None and pos(book_settings):
                        x,y=pos(book_settings)
                        print("CLICK_EXACT_BOOK_SETTINGS",x,y,flush=True)
                        tap_at(x,y)
                        nodes=snapshot("book_settings_actual")
                        if click(nodes,["export book","share book","export","share","save to file","book translation","edit book"]):
                            nodes=snapshot("book_settings_export_or_edit")
                    else:
                        print("BOOK_SETTINGS_RESOURCE_NOT_VISIBLE",flush=True)
                break
            print("READER_MENU_PROBED",flush=True)
            # If export isn't visible here, return to the Library and inspect
            # the saved book's management actions; this is a discovery capture.
            run(["shell","input","keyevent","KEYCODE_BACK"],check=False)
            time.sleep(2)
            nodes=snapshot("after_book_settings_back")
            run(["shell","input","keyevent","KEYCODE_BACK"],check=False)
            time.sleep(2)
            nodes=snapshot("after_reader_back")
            if has(nodes,"I_Found_a_Unicorn"):
                print("BOOK_SHOWN_IN_LIBRARY_OR_READER",flush=True)
            if click(nodes,["I_Found_a_Unicorn","Vietnamese_hyphenated"]):
                nodes=snapshot("library_book_selected")
            # Also capture current activity + file paths to distinguish a reader
            # from the creator and understand where native exports are written.
            (D/"activity_dump.txt").write_text(
                shell("dumpsys activity activities | grep -E 'mResumedActivity|topResumedActivity|ResumedActivity'"),
                encoding="utf-8")
        else:
            print("SAVE BUTTON NOT FOUND",flush=True)
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
