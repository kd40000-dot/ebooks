#!/usr/bin/env python3
"""Try to create a real Smart Book SB2 in the Android emulator; capture UI on failure."""
from pathlib import Path
import re, subprocess, sys, time, xml.etree.ElementTree as ET, zipfile
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"debug"
D.mkdir(exist_ok=True)
O=ROOT/"artifacts"
O.mkdir(exist_ok=True)
CHAPTERS=[
  {
    "title": "Chương 1 - Lời thì thầm lúc nửa đêm",
    "vi": "Chương 1 - Lời thì thầm lúc nửa đêm.txt",
    "en": "01 - The Midnight Whisper - English.txt"
  },
  {
    "title": "Chương 2 - Giọng nói qua lỗ thông gió",
    "vi": "Chương 2 - Giọng nói qua lỗ thông gió.txt",
    "en": "02 - The Voice Through the Vent - English.txt"
  },
  {
    "title": "Chương 3 - Điều không được nhắc đến",
    "vi": "Chương 3 - Điều không được nhắc đến.txt",
    "en": "03 - The Forbidden Subject - English.txt"
  },
  {
    "title": "Chương 4 - Vương quốc bí mật",
    "vi": "Chương 4 - Vương quốc bí mật.txt",
    "en": "04 - The Secret Kingdoms - English.txt"
  },
  {
    "title": "Chương 5 - Điều ước về tuyết",
    "vi": "Chương 5 - Điều ước về tuyết.txt",
    "en": "05 - A Wish to See Snow - English.txt"
  },
  {
    "title": "Chương 6 - Sau lời kể",
    "vi": "Chương 6 - Sau lời kể.txt",
    "en": "06 - After the Story - English.txt"
  }
]
CHAPTERS_ROOT=ROOT/"books"/"air-vent"/"chapters"
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
    if c<=a or d<=b:return None
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

def pick_txt_from_documents_ui(nodes, filename, prefix):
    """Select the exact staged TXT. Never confuse a canceled picker with success."""
    def ready(items, suffix):
        for attempt in range(6):
            if items and (resource(items,"/option_menu_search") or has(items,"Show roots") or has(items,filename)):
                return items
            time.sleep(2)
            items=snapshot(prefix+suffix+f"_wait_{attempt}")
            if has(items,"enter a book name"):
                print("DOCUMENT_PICKER_CLOSED_UNEXPECTEDLY",filename,flush=True)
                return []
        return items
    nodes=ready(nodes,"_initial")
    if not nodes or has(nodes,"enter a book name"):
        print("PICKER_NOT_READY",filename,flush=True)
        return None
    if click(nodes,[filename]):
        page=snapshot(prefix+"_selected_direct")
        print("EXACT_DOCUMENT_SELECTED",filename,flush=True)
        return page if has(page,"enter a book name") else None

    # Search FIRST after a direct match fails. Scrolling the DocumentsUI
    # Recent grid repeatedly has closed the picker or caused empty UI dumps
    # after chapter 3 on Android 33. All chapter filenames include an ASCII
    # chapter number, so one-digit search safely distinguishes the files.
    search=resource(nodes,"/option_menu_search")
    if search:
        tap_at(*pos(search))
        page=snapshot(prefix+"_search_open")
        field=resource(page,"/search_src_text")
        if field is not None:
            tap_at(*pos(field))
            m=re.search(r"(?<![0-9])([0-9]{1,2})(?![0-9])",filename)
            query=m.group(1) if m else filename.split(" ")[0]
            print("SEARCH_DOCUMENTS_UI",filename,"query",query,flush=True)
            run(["shell","input","text",query])
            time.sleep(3)
            # Do not send ENTER/BACK: they previously closed the file picker.
            for q in range(4):
                results=snapshot(prefix+f"_search_live_{q}")
                if click(results,[filename]):
                    page=snapshot(prefix+"_selected_search")
                    print("EXACT_DOCUMENT_SELECTED_VIA_SEARCH",filename,flush=True)
                    return page if has(page,"enter a book name") else None
                time.sleep(2)
            # One Back only closes SearchView; verify DocumentsUI survived.
            run(["shell","input","keyevent","KEYCODE_BACK"],check=False)
            nodes=ready(snapshot(prefix+"_search_cancelled"),"_search_back")
            if not nodes or has(nodes,"enter a book name"):
                return None

    # Search may be unavailable while indexing. Do a single short Recent
    # scroll as a fallback, not multiple swipes that destabilize DocumentsUI.
    for index in range(1):
        if not nodes or has(nodes,"enter a book name"):
            print("PICKER_NOT_OPEN_AFTER_SEARCH",filename,flush=True)
            return None
        run(["shell","input","swipe","420","1230","420","850","300"])
        nodes=ready(snapshot(prefix+"_recent_fallback"),"_recent")
        if nodes and click(nodes,[filename]):
            page=snapshot(prefix+"_selected_recent")
            return page if has(page,"enter a book name") else None
    if not click(nodes,["Show roots"]):
        print("PICKER_ROOTS_NOT_FOUND",filename,flush=True)
        return None
    nodes=ready(snapshot(prefix+"_roots"),"_roots")
    if not click(nodes,["Android SDK built for x86_64","Internal storage","Internal shared storage","sdk_gphone"]):
        print("PICKER_PHYSICAL_STORAGE_NOT_FOUND",filename,flush=True)
        return None
    nodes=ready(snapshot(prefix+"_device_storage"),"_storage")
    for directory in ("Download","ebooks-air-vent"):
        if not click(nodes,[directory]):
            print("PICKER_FOLDER_NOT_FOUND",directory,flush=True)
            return None
        nodes=ready(snapshot(prefix+"_folder_"+directory),"_folder")
    if click(nodes,[filename]):
        page=snapshot(prefix+"_selected_from_folder")
        print("EXACT_DOCUMENT_SELECTED_IN_STORAGE",filename,flush=True)
        return page if has(page,"enter a book name") else None
    print("STAGED_FILE_NOT_FOUND",filename,flush=True)
    return None

def stage_chapter(index,target):
    book=CHAPTERS[index]
    for lang,filename in (("vi",book["vi"]),("en",book["en"])):
        source=CHAPTERS_ROOT/lang/filename
        if not source.exists(): raise FileNotFoundError(source)
        run(["push",str(source),target+"/"+filename])
        shell('am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d "file://'+target+'/'+filename+'"')
    print("STAGED_CHAPTER",index+1,book["title"],flush=True)

def latest_chapter_menu(nodes):
    xs=[n for n in nodes if (n.get("resource-id") or "").endswith("/menu") and pos(n)]
    return max(xs,key=lambda n:pos(n)[1]) if xs else None

def automate():
    for book in CHAPTERS:
        for lang,filename in (("vi",book["vi"]),("en",book["en"])):
            if not (CHAPTERS_ROOT/lang/filename).exists():
                raise FileNotFoundError(CHAPTERS_ROOT/lang/filename)
    subprocess.run(["bash",str(ROOT/"scripts"/"build_share_sink.sh")],check=True,timeout=120)
    target="/sdcard/Download/ebooks-air-vent"
    shell(f"mkdir -p {target}")
    stage_chapter(0,target)
    cover=ROOT/"books"/"air-vent"/"art"/"cover.jpg"
    assert cover.exists(),str(cover)
    run(["push",str(cover),target+"/cover.jpg"])
    shell('am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d "file://'+target+'/cover.jpg"')
    print("COVER_JPEG_STAGED",cover.stat().st_size,flush=True)
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
        # Isolated native cover-image test. Picker support was confirmed
        # in run 38102529571; choose our staged JPEG and continue the
        # fully validated three-chapter parallel-book export.
        thumbnail=resource(nodes,"/thumbnail_layout")
        if thumbnail is None or not pos(thumbnail):
            print("COVER_PICKER_CONTROL_NOT_FOUND",flush=True)
            return False
        tap_at(*pos(thumbnail))
        nodes=snapshot("native_cover_picker")
        # Select the filename portion, not the preview-icon child.
        tile=next((n for n in nodes if n.get("class","").endswith("LinearLayout") and "cover.jpg" in n.get("content-desc","")),None)
        if tile is None:
            print("COVER_TILE_NOT_FOUND",flush=True)
            return False
        # DocumentsUI renders a dedicated preview icon in the top-right
        # part of this tile. Tap the LOWER half of the tile to SELECT the
        # JPEG instead of opening Preview. Avoid double-escaped regex
        # parsing of bounds (the previous experiment returned False here).
        center=pos(tile)
        if center is None:
            print("COVER_TILE_HAS_NO_BOUNDS",flush=True)
            return False
        x=center[0]-35
        y=center[1]+58
        print("COVER_TILE_SELECT_NOT_PREVIEW",x,y,flush=True)
        tap_at(x,y)
        nodes=snapshot("native_cover_tile_selection")
        if not has(nodes,"enter a book name"):
            print("COVER_IMAGE_NOT_SELECTED",flush=True)
            return False
        print("NATIVE_COVER_IMAGE_SELECTED",flush=True)
        nodes=snapshot("book_editor_cover_selected")
        if not replace_edittext(nodes,"/name","I Caught My Grandfather Talking to an Air Vent"):
            print("BOOK_TITLE_FAILED",flush=True)
            return False
        nodes=snapshot("named_book")
        if not replace_edittext(nodes,"/author","Anonymous"):
            print("AUTHOR_FIELD_FAILED",flush=True)
            return False
        nodes=snapshot("author_set")
        if not has(nodes,"End of sentence"):
            print("END_OF_SENTENCE_SETTING_NOT_FOUND",flush=True)
            return False
        print("PARAGRAPH_SEPARATOR_VERIFIED: End of sentence",flush=True)
        nodes=select_vietnamese(nodes)
        if not has(nodes,"Vietnamese"):
            print("VIETNAMESE_LANGUAGE_NOT_SELECTED",flush=True)
            return False
        print("BOOK_METADATA: I Caught My Grandfather Talking to an Air Vent / Anonymous",flush=True)
        for index,chapter in enumerate(CHAPTERS):
            n=index+1
            if index:
                if not click(nodes,["add a chapter"]):
                    run(["shell","input","swipe","420","1300","420","550","380"])
                    nodes=snapshot(f"chapter_{n}_scroll_for_add")
                    if not click(nodes,["add a chapter"]):
                        print("ADD_CHAPTER_NOT_FOUND",n,flush=True)
                        return False
                nodes=snapshot(f"chapter_{n}_empty")
                stage_chapter(index,target)
            if not click(nodes,["upload a file","upload file","choose a file"]):
                print("PRIMARY_UPLOAD_NOT_FOUND",n,flush=True)
                return False
            nodes=snapshot(f"chapter_{n}_vi_picker")
            nodes=pick_txt_from_documents_ui(nodes,chapter["vi"],f"chapter_{n}_vi")
            if nodes is None:
                print("VIETNAMESE_PICKER_SELECTION_FAILED",n,flush=True)
                return False
            if not has(nodes,chapter["title"]):
                print("NUMBERED_CHAPTER_NOT_PRESENT",n,chapter["title"],flush=True)
                return False
            print("NUMBERED_CHAPTER_IMPORTED",n,chapter["title"],flush=True)
            m=latest_chapter_menu(nodes)
            if m is None:
                print("CHAPTER_MENU_NOT_FOUND",n,flush=True)
                return False
            tap_at(*pos(m))
            nodes=snapshot(f"chapter_{n}_three_dot")
            if not click(nodes,["translation"]):
                print("TRANSLATION_ACTION_NOT_FOUND",n,flush=True)
                return False
            nodes=snapshot(f"chapter_{n}_translation_entry")
            if not click(nodes,["upload a file","upload file"]):
                print("TRANSLATION_UPLOAD_NOT_FOUND",n,flush=True)
                return False
            nodes=snapshot(f"chapter_{n}_en_picker")
            nodes=pick_txt_from_documents_ui(nodes,chapter["en"],f"chapter_{n}_en")
            if nodes is None:
                print("ENGLISH_PICKER_SELECTION_FAILED",n,flush=True)
                return False
            attached=sum((x.get("resource-id") or "").endswith("/target") for x in nodes)
            if attached < n:
                print("ENGLISH_TRANSLATION_TARGET_NOT_CREATED",n,"targets=",attached,flush=True)
                return False
            print("BILINGUAL_CHAPTER_READY",n,chapter["title"],flush=True)
            nodes=snapshot(f"chapter_{n}_bilingual_ready")
        print("ALL_NUMBERED_CHAPTERS_READY",len(CHAPTERS),flush=True)
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
            if has(nodes,"I Caught My Grandfather Talking to an Air Vent"):
                print("BOOK_SHOWN_IN_LIBRARY_OR_READER",flush=True)
            if click(nodes,["I Caught My Grandfather Talking to an Air Vent","Chương 1 - Lời thì thầm lúc nửa đêm"]):
                nodes=snapshot("library_book_selected")
            # Probe native saved-book overflow menu then the dedicated
            # share control seen in previous verified UI hierarchy.
            opts=next((n for n in nodes if "more options" in (n.get("content-desc") or "").lower() and pos(n)),None)
            if opts is not None:
                tap_at(*pos(opts))
                nodes=snapshot("saved_book_more_options")
                if has(nodes,"export") or has(nodes,"save as"):
                    click(nodes,["export","save as"])
                    nodes=snapshot("saved_book_native_export")
                else:
                    run(["shell","input","keyevent","KEYCODE_BACK"],check=False)
                    nodes=snapshot("saved_book_options_dismissed")
            native_share=resource(nodes,"/action_share")
            if native_share is not None and pos(native_share):
                shell("logcat -c")
                tap_at(*pos(native_share))
                nodes=snapshot("saved_book_native_share")
                # Installed test receiver is typically not one of Android
                # Sharesheet's four suggested targets. The "Apps list" XML
                # nodes may have zero-sized bounds; tapping them just taps
                # (0,0). Expand the sheet with a gesture instead.
                print("SHARE_RECEIVER_RESOLUTION",
                      shell("cmd package query-activities -a android.intent.action.SEND -t application/zip"),
                      flush=True)
                target_chosen=False
                for share_step in range(7):
                    if click(nodes,["Save SB2 locally"]):
                        nodes=snapshot("native_share_receiver_activated")
                        target_chosen=True
                        break
                    print("EXPAND_SHARE_SHEET_UPWARD",share_step,flush=True)
                    run(["shell","input","swipe","420","1540","420","460","500"])
                    time.sleep(2)
                    nodes=snapshot(f"native_share_expanded_{share_step}")
                if not target_chosen:
                    # ADB supports launching our explicit receiver, but a
                    # separate content URI is still needed. Capture the chooser
                    # state and ActivityManager intent so the missing match can
                    # be diagnosed without reporting false success.
                    print("NATIVE_SHARE_RECEIVER_NOT_VISIBLE_AFTER_SWIPES",flush=True)
                    (D/"resolver_activity.txt").write_text(
                        shell("dumpsys activity top | tail -180"),encoding="utf-8")
                (D/"native_share_logcat.txt").write_text(
                    shell("logcat -d -s SMARTBOOK_SINK:I ActivityTaskManager:I AndroidRuntime:E"),
                    encoding="utf-8")
            else:
                print("NATIVE_SHARE_ACTION_NOT_VISIBLE",flush=True)
            # Also capture current activity + file paths to distinguish a reader
            # from the creator and understand where native exports are written.
            (D/"activity_dump.txt").write_text(
                shell("dumpsys activity activities | grep -E 'mResumedActivity|topResumedActivity|ResumedActivity'"),
                encoding="utf-8")
        else:
            print("SAVE BUTTON NOT FOUND",flush=True)
    print("Finished current automatic navigation; searching for real exports.",flush=True)
    exported=shell("find /sdcard/Download /sdcard/Documents /sdcard/Android/data/io.github.kd40000.smartbooksink/files/native-share -type f \\( -iname '*.sb2' -o -iname 'shared-file*' -o -iname '*.zip' \\) 2>/dev/null")
    print("EXPORT_PATHS",repr(exported),flush=True)
    found=0
    for remote in exported.splitlines():
        remote=remote.strip()
        if not remote.startswith("/sdcard/"): continue
        local=O/Path(remote).name
        run(["pull",remote,str(local)])
        try:
            with zipfile.ZipFile(local) as z:
                entries=z.infolist()
                meta=[f for f in entries if f.filename.lower().endswith(".sb")]
                encrypted=sum(bool(f.flag_bits & 1) for f in meta)
                if meta and encrypted:
                    found+=1
                    verified=O/"I Caught My Grandfather Talking to an Air Vent_native.sb2"
                    verified.write_bytes(local.read_bytes())
                    print("GENUINE_APP_GENERATED_SB2:",verified,
                          "native_sb_entries=",len(meta),"encrypted=",encrypted,flush=True)
                else:
                    print("SHARE_CONTENT_NOT_NATIVE_SB2",local,"entries=",
                          [f.filename for f in entries[:12]],flush=True)
        except (zipfile.BadZipFile, OSError) as e:
            print("SHARE_CONTENT_NOT_ZIP",local,repr(e),flush=True)
    return found>0

try:
    sys.exit(0 if automate() else 2)
except Exception as e:
    print("Automation error",repr(e),file=sys.stderr,flush=True)
    try:snapshot("error")
    except Exception:pass
    sys.exit(1)
