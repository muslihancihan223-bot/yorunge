"""Oyun portalları (GameMonetize) için ayrı sürüm üretir: portal/index.html + yorunge-gamemonetize.zip
Portallar kendi reklamlarını kullanır; bu sürümde Adsterra/AdSense/GoatCounter, paylaşım butonu ve
dış linkler yoktur. Kullanım: python3 tools/portal.py [GAMEMONETIZE_GAME_ID]
"""
import os, re, sys, zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GAME_ID = sys.argv[1] if len(sys.argv) > 1 else "GAMEMONETIZE_GAME_ID"
src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

for key in ("adsenseClient", "adsterraBannerKey", "goatcounterCode"):
    src = re.sub(r'(%s:\s*)"[^"]*"' % key, r'\1""', src)
src = re.sub(r'\s*<button id="shareBtn"[^>]*>[^<]*</button>', "", src)
src = re.sub(r'\$\("shareBtn"\)\.onclick = async[\s\S]*?\n\};\n', "", src)
src = re.sub(r'<div class="foot">[\s\S]*?</div>', "", src)
src = src.replace('<div id="banner"></div>', "").replace('<div id="bannerMenu"></div>', "")

sdk = '''<script>
/* GameMonetize SDK: oyun sonunda her 2 oyunda bir reklam; reklam sırasında ses kapalı */
window.SDK_OPTIONS = {
  gameId: "%s",
  onEvent: function (a) {
    switch (a.name) {
      case "SDK_GAME_PAUSE": window.__adPause = true; try { muted = true; } catch (e) {} break;
      case "SDK_GAME_START": window.__adPause = false; try { muted = false; } catch (e) {} break;
      case "SDK_READY": window.__sdkReady = true; break;
    }
  }
};
(function (a, b, c) {
  var d = a.getElementsByTagName(b)[0];
  if (a.getElementById(c)) return;
  a = a.createElement(b); a.id = c; a.src = "https://api.gamemonetize.com/sdk.js";
  d.parentNode.insertBefore(a, d);
})(document, "script", "gamemonetize-sdk");
window.onGameOverAd = function (games) {
  if (games %% 2 === 0 && typeof sdk !== "undefined" && sdk.showBanner) sdk.showBanner();
};
</script>
''' % GAME_ID
src = src.replace("<script>\n/* =====", sdk + "<script>\n/* =====", 1)

out = os.path.join(ROOT, "portal")
os.makedirs(out, exist_ok=True)
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(src)
z = os.path.join(ROOT, "yorunge-gamemonetize.zip")
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
    f.write(os.path.join(out, "index.html"), "index.html")
print("hazır:", z)
