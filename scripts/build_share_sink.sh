#!/usr/bin/env bash
# CI-only receiver for the *native* Android ACTION_SEND stream from Smart Book.
# It never generates an SB2: it saves the byte stream received from Smart Book.
set -euo pipefail
SDK="${ANDROID_HOME:-/usr/local/lib/android/sdk}"
BT="$(find "$SDK/build-tools" -maxdepth 1 -mindepth 1 -type d | sort -V | tail -1)"
JAR="$SDK/platforms/android-33/android.jar"
W=/tmp/smartbook-share-sink
mkdir -p "$W/src/io/github/kd40000/smartbooksink" "$W/classes" "$W/dex"
cat > "$W/AndroidManifest.xml" <<'EOF'
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="io.github.kd40000.smartbooksink">
  <uses-sdk android:minSdkVersion="23" android:targetSdkVersion="28" />
  <application android:label="Save SB2 locally" android:theme="@android:style/Theme.Material.Light.NoActionBar" android:usesCleartextTraffic="false">
    <activity android:name=".ShareSink" android:exported="true">
      <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="*/*" />
      </intent-filter>
    </activity>
  </application>
</manifest>
EOF
cat > "$W/src/io/github/kd40000/smartbooksink/ShareSink.java" <<'EOF'
package io.github.kd40000.smartbooksink;
import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.util.Log;
import android.database.Cursor;
import android.provider.OpenableColumns;
import java.io.*;
public class ShareSink extends Activity {
  private static final String TAG="SMARTBOOK_SINK";
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    Intent intent=getIntent();
    Uri uri=(Uri)intent.getParcelableExtra(Intent.EXTRA_STREAM);
    if (uri==null && intent.getData()!=null) uri=intent.getData();
    if (uri==null) { Log.e(TAG,"NO_STREAM: action="+intent.getAction()+" type="+intent.getType()+" text="+intent.getStringExtra(Intent.EXTRA_TEXT)); finish(); return; }
    String name="shared-file";
    try (Cursor c=getContentResolver().query(uri,new String[]{OpenableColumns.DISPLAY_NAME},null,null,null)) {
      if(c!=null&&c.moveToFirst()&&!c.isNull(0)) name=c.getString(0);
    } catch(Exception ignored) {}
    name=name.replaceAll("[^A-Za-z0-9._-]","_");
    if(name.isEmpty()) name="shared-file";
    File directory=getExternalFilesDir("native-share");
    if(directory!=null) directory.mkdirs();
    File out=new File(directory,name);
    long length=0;
    try (InputStream in=getContentResolver().openInputStream(uri); OutputStream dest=new FileOutputStream(out)) {
      if(in==null) throw new IOException("null source stream");
      byte[] data=new byte[32768]; int n;
      while((n=in.read(data))!=-1) {dest.write(data,0,n); length+=n;}
      dest.flush();
      Log.i(TAG,"SAVED_NATIVE_SHARE: "+out.getAbsolutePath()+" bytes="+length+" uri="+uri+" mime="+intent.getType());
    } catch(Exception e) { Log.e(TAG,"SHARE_FAILED uri="+uri,e); }
    finish();
  }
}
EOF
javac -source 8 -target 8 -cp "$JAR" -d "$W/classes" "$W/src/io/github/kd40000/smartbooksink/ShareSink.java"
"$BT/d8" --min-api 23 --lib "$JAR" --output "$W/dex" "$W/classes/io/github/kd40000/smartbooksink/ShareSink.class"
"$BT/aapt" package -f -M "$W/AndroidManifest.xml" -I "$JAR" -F "$W/unsigned.apk"
(cd "$W/dex" && zip -q "$W/unsigned.apk" classes.dex)
"$BT/zipalign" -f 4 "$W/unsigned.apk" "$W/aligned.apk"
keytool -genkeypair -keystore "$W/test.jks" -alias local -keyalg RSA -keysize 2048 -validity 10 -storepass changeit -keypass changeit -dname "CN=Test Share Sink" -noprompt >/dev/null 2>&1
"$BT/apksigner" sign --ks "$W/test.jks" --ks-key-alias local --ks-pass pass:changeit --key-pass pass:changeit --out "$W/sink.apk" "$W/aligned.apk"
adb install -r "$W/sink.apk"
echo "Installed Save SB2 locally Android share stream receiver"
