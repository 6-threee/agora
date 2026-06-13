// Wait & Learn (VS Code) - shows language flashcards in Claude Code's thinking
// spinner. On activate it patches Claude Code's webview verb pool with the
// active deck's "front -> back" pairs; while Claude generates, those rotate in
// place of the stock "Discombobulating..." verbs. Reverts cleanly on disable and
// on shutdown so an uninstall never leaves Claude Code modified.

const vscode = require("vscode");
const fs = require("fs");
const { DECKS, getDeck, verbsFromDeck } = require("./lib/decks");
const patcher = require("./lib/patcher");

const ENABLED_KEY = "waitAndLearn.enabled";
let STATE_DIR = null; // stashed for deactivate(), which has no context

function deckKey() {
  return vscode.workspace.getConfiguration("waitAndLearn").get("deck", "spanish");
}

function apply(notify) {
  try { fs.mkdirSync(STATE_DIR, { recursive: true }); } catch (e) {}
  const key = deckKey();
  const verbs = verbsFromDeck(getDeck(key));
  const res = patcher.patchAll(verbs, STATE_DIR);
  if (notify) {
    if (res.patched > 0) {
      vscode.window.showInformationMessage(
        "Wait & Learn: " + getDeck(key).name + " is now in Claude Code's thinking spinner. " +
        "Reload the window (or restart the Claude Code panel) to load it."
      );
    } else if (res.found === 0) {
      vscode.window.showWarningMessage("Wait & Learn: Claude Code does not appear to be installed, so there is nothing to patch yet.");
    } else {
      vscode.window.showWarningMessage("Wait & Learn: could not patch Claude Code (its layout may have changed in this version). Nothing was modified.");
    }
  }
  return res;
}

function activate(context) {
  STATE_DIR = context.globalStorageUri.fsPath;

  // Respect a prior "disable": only patch when enabled (default true).
  const enabled = context.globalState.get(ENABLED_KEY, true);
  if (enabled) apply(false);

  context.subscriptions.push(
    vscode.commands.registerCommand("waitAndLearn.enable", async () => {
      await context.globalState.update(ENABLED_KEY, true);
      apply(true);
    }),
    vscode.commands.registerCommand("waitAndLearn.disable", async () => {
      await context.globalState.update(ENABLED_KEY, false);
      const res = patcher.revertAll(STATE_DIR);
      vscode.window.showInformationMessage(
        "Wait & Learn: restored Claude Code's own thinking verbs (" + res.reverted + " install(s)). Reload the window to see it revert."
      );
    }),
    vscode.commands.registerCommand("waitAndLearn.switchLanguage", async () => {
      const items = Object.keys(DECKS).map(function (k) { return { label: DECKS[k].name, key: k }; });
      const pick = await vscode.window.showQuickPick(items, { placeHolder: "Pick a language deck" });
      if (!pick) return;
      await vscode.workspace.getConfiguration("waitAndLearn").update("deck", pick.key, vscode.ConfigurationTarget.Global);
      await context.globalState.update(ENABLED_KEY, true);
      apply(true);
    })
  );
}

function deactivate() {
  // Best-effort: leave Claude Code clean when our extension stops (incl. uninstall
  // within the session). Next activate re-applies if still enabled.
  try { if (STATE_DIR) patcher.revertAll(STATE_DIR); } catch (e) {}
}

module.exports = { activate, deactivate };
