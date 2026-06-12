var WL = (typeof window !== "undefined") ? (window.WL = window.WL || {}) : {};

// WL.Speech - thin wrapper over the browser SpeechSynthesis API. Pronounces a
// word in a target language using an installed OS voice. Fail-silent: if speech
// synthesis is unavailable or no matching voice exists, it no-ops (never throws,
// never blocks the page). No network, no API key - uses the voices already on
// the machine (macOS ships Spanish, French, etc.).
WL.Speech = (function () {
  var synth = (typeof window !== "undefined") ? window.speechSynthesis : null;

  // Upgrade a bare deck lang code to a fuller BCP-47 hint for better voice
  // matching. Bare codes still work as a hint; this just helps common ones.
  var LANG_HINT = {
    es: "es-ES", fr: "fr-FR", de: "de-DE", it: "it-IT", pt: "pt-PT",
    en: "en-US", ja: "ja-JP", zh: "zh-CN", ko: "ko-KR", ru: "ru-RU"
  };

  function resolveLang(lang) {
    if (!lang) return "";
    return LANG_HINT[lang] || lang;
  }

  // Voices load asynchronously; getVoices() can be empty on first call until the
  // "voiceschanged" event fires. We cache and refresh on that event.
  var voiceCache = [];
  function refreshVoices() {
    try { voiceCache = (synth && synth.getVoices()) || []; } catch (e) { voiceCache = []; }
  }
  if (synth) {
    refreshVoices();
    try { synth.addEventListener("voiceschanged", refreshVoices); } catch (e) {}
  }

  // Pick the best installed voice for a language: exact tag match, else same
  // base language ("es-MX" satisfies "es"). Returns null if none / not loaded;
  // callers still set utterance.lang so the browser can pick a default.
  function pickVoice(lang) {
    if (!voiceCache.length) refreshVoices();
    if (!voiceCache.length) return null;
    var want = resolveLang(lang).toLowerCase();
    var base = String(lang || "").toLowerCase().split("-")[0];
    var prefix = null;
    for (var i = 0; i < voiceCache.length; i++) {
      var vl = (voiceCache[i].lang || "").toLowerCase().replace("_", "-");
      if (vl === want) return voiceCache[i];
      if (!prefix && vl.split("-")[0] === base) prefix = voiceCache[i];
    }
    return prefix;
  }

  function cancel() {
    try { if (synth) synth.cancel(); } catch (e) {}
  }

  // Speak `text` in `lang`. Cancels any in-flight utterance first so a rapid
  // run of cards does not pile up a backlog of speech.
  function speak(text, lang) {
    try {
      if (!synth || !text) return;
      cancel();
      var u = new SpeechSynthesisUtterance(String(text));
      var resolved = resolveLang(lang);
      if (resolved) u.lang = resolved;
      var v = pickVoice(lang);
      if (v) u.voice = v;
      u.rate = 0.95;
      synth.speak(u);
    } catch (e) {
      // fail silent
    }
  }

  // True if speech synthesis exists at all (used to hide the button if not).
  function available() {
    return !!synth;
  }

  return { speak: speak, cancel: cancel, available: available };
})();

if (typeof module !== "undefined" && module.exports) module.exports = WL.Speech;
