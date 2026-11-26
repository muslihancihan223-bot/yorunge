"""GameDistribution sürümü: portal-gd/index.html + yorunge-gamedistribution.zip
GD kendi reklamlarını kullanır; Adsterra/AdSense/GoatCounter, paylaşım ve dış linkler yoktur.
Reklam: OYNA'ya basınca (oyun başlamadan) ve her 2 oyun sonunda bir gdsdk.showAd().
Kullanım: python3 tools/portal_gd.py GD_GAME_ID
"""
import os, re, sys, zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GAME_ID = sys.argv[1] if len(sys.argv) > 1 else "GD_GAME_ID"
src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

for key in ("adsenseClient", "adsterraBannerKey", "goatcounterCode"):
    src = re.sub(r'(%s:\s*)"[^"]*"' % key, r'\1""', src)
src = re.sub(r'\s*<button id="shareBtn"[^>]*>[^<]*</button>', "", src)
src = re.sub(r'\$\("shareBtn"\)\.onclick = async[\s\S]*?\n\};\n', "", src)
src = re.sub(r'<div class="foot">[\s\S]*?</div>', "", src)
src = re.sub(r'\s*<a class="more"[^>]*>[^<]*</a>', "", src)          # dış link yok
src = src.replace('<div id="banner"></div>', "").replace('<div id="bannerMenu"></div>', "")

sdk = '''<script>
/* GameDistribution SDK */
window.__gdReady = false;
window["GD_OPTIONS"] = {
  gameId: "%s",
  onEvent: function (event) {
    switch (event.name) {
      case "SDK_GAME_PAUSE": window.__adPause = true; try { muted = true; } catch (e) {} break;
      case "SDK_GAME_START": window.__adPause = false; try { muted = false; } catch (e) {} break;
      case "SDK_READY": window.__gdReady = true; break;
    }
  }
};
(function (d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "https://html5.api.gamedistribution.com/main.min.js";
  fjs.parentNode.insertBefore(js, fjs);
}(document, "script", "gamedistribution-jssdk"));
window.__gdShowAd = function () {
  if (typeof gdsdk !== "undefined" && gdsdk.showAd !== undefined) { try { gdsdk.showAd(); } catch (e) {} }
};
window.onGameOverAd = function (games) { if (games %% 2 === 0) window.__gdShowAd(); };
</script>
''' % GAME_ID
src = src.replace("<script>\n/* =====", sdk + "<script>\n/* =====", 1)
assert "gamedistribution-jssdk" in src, "SDK eklenemedi"

# OYNA'ya basınca önce reklam (GD kuralı: oyun başlamadan reklam çağrısı)
old = '$("playBtn").onclick = (e) => { e.stopPropagation(); beep(660, 0.1); start(false); };'
assert old in src
src = src.replace(old, '$("playBtn").onclick = (e) => { e.stopPropagation(); beep(660, 0.1); window.__gdShowAd(); start(false); };')


out = os.path.join(ROOT, "portal-gd")
os.makedirs(out, exist_ok=True)
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(src)
z = os.path.join(ROOT, "yorunge-gamedistribution.zip")
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
    f.write(os.path.join(out, "index.html"), "index.html")
print("hazır:", z)
