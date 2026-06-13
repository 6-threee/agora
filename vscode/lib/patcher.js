// patcher.js - the one fragile, Claude-Code-specific module.
//
// Claude Code's VS Code extension hardcodes its "thinking" verb pool as a flat
// JS array literal inside webview/index.js (there is NO supported settings hook
// for the webview, unlike the CLI's spinnerVerbs). To show flashcards only while
// Claude generates, we replace that array with our "front -> back" verbs.
//
// Everything here is reversible and defensive:
//  - the original array text is backed up (per CC install) before the first patch,
//  - our injected array is wrapped in /*WL:START*/ ... /*WL:END*/ so we can find,
//    refresh, or revert it precisely,
//  - writes are atomic (temp sibling + rename),
//  - a flat-array sanity guard aborts if the anchor ever matches something
//    unexpected, so we never corrupt the file.
//
// If Claude Code updates, webview/index.js is rewritten unpatched; patchAll()
// re-applies on the next activate. Node only (runs in the VS Code extension host).

const fs = require("fs");
const os = require("os");
const path = require("path");

const ANCHOR = '"Discombobulating"'; // a made-up verb, present once in CC's verb pool
const START = "/*WL:START*/";
const END = "/*WL:END*/";

// All installed Claude Code extension webview bundles (one per installed version).
function claudeWebviewFiles() {
  const extRoot = path.join(os.homedir(), ".vscode", "extensions");
  const out = [];
  let dirs;
  try { dirs = fs.readdirSync(extRoot); } catch (e) { return out; }
  for (const d of dirs) {
    if (!d.startsWith("anthropic.claude-code-")) continue;
    const f = path.join(extRoot, d, "webview", "index.js");
    if (fs.existsSync(f)) out.push({ id: d, file: f });
  }
  return out;
}

function backupPath(stateDir, id) {
  return path.join(stateDir, "cc-verbs-backup__" + id.replace(/[^a-zA-Z0-9._-]/g, "_") + ".txt");
}

function atomicWrite(file, text) {
  const tmp = file + ".wl-tmp." + process.pid;
  try {
    fs.writeFileSync(tmp, text);
    fs.renameSync(tmp, file);
    return true;
  } catch (e) {
    try { fs.unlinkSync(tmp); } catch (e2) {}
    return false;
  }
}

// Locate the original (unpatched) verb-array span [start,end) around the anchor.
// Returns null if not found or if the span fails the flat-array sanity guard.
function locateOriginalArray(src) {
  const a = src.indexOf(ANCHOR);
  if (a === -1) return null;
  const start = src.lastIndexOf("[", a);
  const end = src.indexOf("]", a);
  if (start === -1 || end === -1 || end < start) return null;
  const span = src.slice(start, end + 1);
  // Sanity: must look like a flat array of many short quoted strings and contain
  // no nested brackets (the verb pool is flat). Guards against a stray anchor.
  if (span.indexOf("[", 1) !== -1 || span.indexOf("]") !== span.length - 1) return null;
  const commas = (span.match(/","/g) || []).length;
  if (commas < 10) return null;
  // Authoritative guard: the span must parse as a flat array of strings. This
  // catches a start "[" that landed INSIDE a string element (e.g. a future verb
  // containing "["), which the cheap checks above would miss and which would
  // otherwise corrupt the bundle on patch.
  try {
    const parsed = JSON.parse(span);
    if (!Array.isArray(parsed) || parsed.length < 10) return null;
    if (!parsed.every(function (v) { return typeof v === "string"; })) return null;
  } catch (e) { return null; }
  return { start, end: end + 1, text: span };
}

// Span of our previously-injected array, including the markers, or null.
function locateInjected(src) {
  const s = src.indexOf(START);
  if (s === -1) return null;
  const e = src.indexOf(END, s);
  if (e === -1) return null;
  return { start: s, end: e + END.length };
}

function injectedLiteral(verbs) {
  return START + JSON.stringify(verbs) + END;
}

// Patch a single CC install. Returns { ok, status }.
function patchFile(file, id, verbs, stateDir) {
  let src;
  try { src = fs.readFileSync(file, "utf8"); } catch (e) { return { ok: false, status: "read-failed" }; }

  const injected = locateInjected(src);
  if (injected) {
    // Already ours: refresh the verbs in place (deck may have changed).
    const next = src.slice(0, injected.start) + injectedLiteral(verbs) + src.slice(injected.end);
    return { ok: atomicWrite(file, next), status: "refreshed" };
  }

  const orig = locateOriginalArray(src);
  if (!orig) return { ok: false, status: "anchor-not-found" };

  // Back up the original verb pool before the first patch of this install.
  // Fail CLOSED: if we cannot confirm the backup exists on disk, do NOT patch.
  // Otherwise a swallowed backup failure would leave an unrevertable bundle.
  const bp = backupPath(stateDir, id);
  try {
    if (!fs.existsSync(bp)) {
      fs.mkdirSync(stateDir, { recursive: true });
      atomicWrite(bp, orig.text);
    }
  } catch (e) { /* fall through to the existence check below */ }
  if (!fs.existsSync(bp)) return { ok: false, status: "backup-failed" };

  const next = src.slice(0, orig.start) + injectedLiteral(verbs) + src.slice(orig.end);
  return { ok: atomicWrite(file, next), status: "patched" };
}

// Revert a single CC install to its backed-up original verb pool.
function revertFile(file, id, stateDir) {
  let src;
  try { src = fs.readFileSync(file, "utf8"); } catch (e) { return { ok: false, status: "read-failed" }; }
  const injected = locateInjected(src);
  if (!injected) return { ok: true, status: "not-patched" };

  let original;
  try { original = fs.readFileSync(backupPath(stateDir, id), "utf8"); } catch (e) { original = null; }
  if (!original) return { ok: false, status: "no-backup" }; // never guess; leave our patch in place

  const next = src.slice(0, injected.start) + original + src.slice(injected.end);
  return { ok: atomicWrite(file, next), status: "reverted" };
}

// Patch every installed Claude Code. Never throws.
function patchAll(verbs, stateDir) {
  const targets = claudeWebviewFiles();
  let patched = 0;
  const details = [];
  for (const t of targets) {
    let r;
    try { r = patchFile(t.file, t.id, verbs, stateDir); } catch (e) { r = { ok: false, status: "threw" }; }
    if (r.ok) patched++;
    details.push({ id: t.id, status: r.status });
  }
  return { patched, found: targets.length, details };
}

// Revert every installed Claude Code. Never throws.
function revertAll(stateDir) {
  const targets = claudeWebviewFiles();
  let reverted = 0;
  const details = [];
  for (const t of targets) {
    let r;
    try { r = revertFile(t.file, t.id, stateDir); } catch (e) { r = { ok: false, status: "threw" }; }
    if (r.ok && r.status === "reverted") reverted++;
    details.push({ id: t.id, status: r.status });
  }
  return { reverted, found: targets.length, details };
}

module.exports = {
  claudeWebviewFiles,
  locateOriginalArray,
  locateInjected,
  injectedLiteral,
  patchFile,
  revertFile,
  patchAll,
  revertAll
};
