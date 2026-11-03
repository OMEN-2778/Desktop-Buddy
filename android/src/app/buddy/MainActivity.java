package app.buddy;

import android.app.Activity;
import android.os.Bundle;
import android.util.Base64;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/** Buddy 小屋 for Android: the phone page (assets/index.html) in a full-screen WebView.
 *  The page's storage (save, settings) lives as files in the app's private folder (files/store),
 *  through BuddyAndroid; the page swaps it in for localStorage (index.src.html, top). */
public class MainActivity extends Activity {
    static final String HOST = "appassets.androidplatform.net";
    WebView web;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setTextZoom(100);
        web.addJavascriptInterface(new Store(new File(getFilesDir(), "store")), "BuddyAndroid");
        web.setWebViewClient(new Assets(this));
        setContentView(web);
        immersive();
        web.loadUrl("https://" + HOST + "/index.html");
    }


    /** serves assets/www/* at https://appassets.androidplatform.net/ (fetch works there, unlike file://) */
    static class Assets extends WebViewClient {
        final Activity act;
        Assets(Activity a) { act = a; }
        @Override public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest r) {
            if (!HOST.equals(r.getUrl().getHost())) return null;
            String path = r.getUrl().getPath();
            if (path == null || path.equals("/")) path = "/index.html";
            Map<String, String> h = new HashMap<>();
            try {
                InputStream in = act.getAssets().open("www" + path);
                h.put("Cache-Control", "no-cache");
                String m = mime(path);
                return new WebResourceResponse(m, m.startsWith("text") ? "utf-8" : null, 200, "OK", h, in);
            } catch (Exception e) {
                return new WebResourceResponse("text/plain", "utf-8", 404, "Not Found", h, null);
            }
        }
    }

    static String mime(String p) {
        if (p.endsWith(".html")) return "text/html";
        if (p.endsWith(".js")) return "text/javascript";
        if (p.endsWith(".css")) return "text/css";
        if (p.endsWith(".mp3")) return "audio/mpeg";
        if (p.endsWith(".png")) return "image/png";
        if (p.endsWith(".json")) return "application/json";
        return "application/octet-stream";
    }

    void immersive() {
        web.setSystemUiVisibility(View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN);
    }

    @Override public void onWindowFocusChanged(boolean f) { super.onWindowFocusChanged(f); if (f) immersive(); }

    // leaving the app (home, another app, screen off): save right now
    @Override protected void onPause() {
        web.evaluateJavascript("try{autoSave()}catch(e){}", null);
        web.onPause();
        super.onPause();
    }
    @Override protected void onResume() { super.onResume(); web.onResume(); }

    @Override public void onBackPressed() { moveTaskToBack(true); }   // back = leave, the house keeps its state

    /** key -> one file each; written to a temp file, then renamed, so a crash never leaves half a save */
    static class Store {
        final File dir; final Map<String, String> cache = new HashMap<>();
        Store(File d) { dir = d; dir.mkdirs(); }
        File file(String k) { return new File(dir, Base64.encodeToString(k.getBytes(StandardCharsets.UTF_8), Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING)); }
        @JavascriptInterface public synchronized String get(String k) {
            if (cache.containsKey(k)) return cache.get(k);
            File f = file(k); String v = null;
            if (f.exists()) try (FileInputStream in = new FileInputStream(f)) {
                byte[] buf = new byte[(int) f.length()]; int n = 0;
                while (n < buf.length) { int r = in.read(buf, n, buf.length - n); if (r < 0) break; n += r; }
                v = new String(buf, 0, n, StandardCharsets.UTF_8);
            } catch (Exception e) { v = null; }
            cache.put(k, v); return v;
        }
        @JavascriptInterface public synchronized void set(String k, String v) {
            File f = file(k), tmp = new File(dir, f.getName() + ".tmp");
            try (FileOutputStream out = new FileOutputStream(tmp)) {
                out.write(v.getBytes(StandardCharsets.UTF_8)); out.getFD().sync();
            } catch (Exception e) { return; }
            if (tmp.renameTo(f)) cache.put(k, v);
        }
        @JavascriptInterface public synchronized void remove(String k) { file(k).delete(); cache.put(k, null); }
        @JavascriptInterface public synchronized String keys() {
            StringBuilder sb = new StringBuilder("[");
            String[] names = dir.list(); if (names != null) for (String n : names) {
                if (n.endsWith(".tmp")) continue;
                try {
                    String k = new String(Base64.decode(n, Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING), StandardCharsets.UTF_8);
                    if (sb.length() > 1) sb.append(',');
                    sb.append('"').append(k.replace("\\", "\\\\").replace("\"", "\\\"")).append('"');
                } catch (Exception e) { /* not ours */ }
            }
            return sb.append(']').toString();
        }
    }
}
