import {
  App,
  FileSystemAdapter,
  MarkdownView,
  Modal,
  Notice,
  Plugin,
  PluginSettingTab,
  Setting,
  SuggestModal,
  TFile,
  normalizePath,
} from "obsidian";
import { execFile, spawn } from "child_process";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { findMarkerAt } from "./marker.js";

interface T9xSettings {
  t9xPath: string;
  pathPrepend: string;
  defaultAgent: string;
  agents: Record<string, string[]>;
  pickupPrompt: string;
  delegatePrompt: string;
}

const DEFAULT_SETTINGS: T9xSettings = {
  t9xPath: "t9x",
  pathPrepend: [
    "/opt/homebrew/bin",
    "/usr/local/bin",
    path.join(os.homedir(), ".local/bin"),
    path.join(os.homedir(), ".bun/bin"),
  ].join(":"),
  defaultAgent: "claude",
  agents: {
    claude: ["claude", "-p", "--permission-mode", "acceptEdits", "{{PROMPT}}"],
    pi: ["pi", "-p", "{{PROMPT}}"],
    omp: ["omp", "-p", "{{PROMPT}}"],
    opencode: ["opencode", "run", "{{PROMPT}}"],
    hermes: ["hermes", "-z", "{{PROMPT}}"],
  },
  pickupPrompt: [
    "In {{FILE}} at line {{LINE}} there is an in-text task marker:",
    "",
    "{{MARKER}}",
    "",
    "Follow .agents/skills/manuscript-tasks: extract the marker into t9x",
    "task(s), replace it in the file with the @id anchor(s), then execute",
    "the resulting task(s) per .agents/skills/using-t9x (open a run before",
    "working, record findings in the run file, finish the run, close tasks",
    "when done). If a task's capabilities word matches an execution skill",
    "(writing, model, literature, empirics, editing), follow that skill.",
  ].join("\n"),
  delegatePrompt: [
    "Work on t9x task {{ID}} in this workspace. Follow",
    ".agents/skills/using-t9x: open a run before working, record findings",
    "in the run file, finish the run, close the task if done. If the",
    "task's capabilities word matches an execution skill (writing, model,",
    "literature, empirics, editing), follow that skill.",
  ].join("\n"),
};

const BASE_FILE = "t9x-tasks.base";
const BASE_TEMPLATE = `filters:
  and:
    - file.inFolder("_agents/tasks")
views:
  - type: table
    name: Open
    filters:
      and:
        - status == "open"
    order:
      - file.name
      - status
      - capabilities
      - blocked_by
  - type: table
    name: All
    order:
      - file.name
      - status
      - capabilities
      - blocked_by
`;

function render(template: string, vars: Record<string, string>): string {
  return template.replace(/\{\{(\w+)\}\}/g, (_, k) => vars[k] ?? "");
}

export default class T9xPlugin extends Plugin {
  settings: T9xSettings = DEFAULT_SETTINGS;

  async onload() {
    await this.loadSettings();
    this.addSettingTab(new T9xSettingTab(this.app, this));
    this.app.workspace.onLayoutReady(() => this.bootstrap());

    this.addCommand({
      id: "pickup-marker",
      name: "Pick up task at cursor (@(...) marker)",
      editorCallback: (editor, view) => this.pickup(editor, view as MarkdownView),
    });
    this.addCommand({
      id: "new-task",
      name: "New task",
      callback: () => new PromptModal(this.app, "Task title", "", (title) => this.newTask(title)).open(),
    });
    this.addCommand({
      id: "close-task",
      name: "Close task in active file",
      callback: () => this.taskVerb("close"),
    });
    this.addCommand({
      id: "reopen-task",
      name: "Reopen task in active file",
      callback: () => this.taskVerb("reopen"),
    });
    this.addCommand({
      id: "promote-note",
      name: "Promote active note to human workspace",
      callback: () => this.promote(),
    });
    this.addCommand({
      id: "demote-note",
      name: "Demote active note to agent space",
      callback: () => this.demote(),
    });
    this.addCommand({
      id: "delegate-task",
      name: "Delegate a task to an agent",
      callback: () => this.delegate(),
    });
    this.addCommand({
      id: "ready-list",
      name: "Open task review (Base)",
      callback: () => this.openBase(),
    });
  }

  // --- environment -------------------------------------------------------

  basePath(): string | null {
    const adapter = this.app.vault.adapter;
    return adapter instanceof FileSystemAdapter ? adapter.getBasePath() : null;
  }

  /** Vault base path, or null (with a Notice) when not a t9x workspace. */
  workspaceRoot(): string | null {
    const root = this.basePath();
    if (!root || !fs.existsSync(path.join(root, ".agents"))) {
      new Notice("t9x: no .agents/ in this vault");
      return null;
    }
    return root;
  }

  env(): NodeJS.ProcessEnv {
    return {
      ...process.env,
      PATH: `${this.settings.pathPrepend}:${process.env.PATH ?? ""}`,
    };
  }

  t9x(args: string[]): Promise<string> {
    const root = this.workspaceRoot();
    if (!root) return Promise.reject(new Error("not a t9x workspace"));
    return new Promise((resolve, reject) => {
      execFile(
        this.settings.t9xPath,
        args,
        { cwd: root, env: this.env() },
        (err, stdout, stderr) => (err ? reject(new Error(stderr || err.message)) : resolve(stdout)),
      );
    });
  }

  bootstrap() {
    const root = this.basePath();
    if (!root || !fs.existsSync(path.join(root, ".agents"))) return;
    try {
      const link = path.join(root, "_agents");
      if (!fs.existsSync(link)) {
        fs.symlinkSync(".agents", link, "dir");
        // Obsidian does not index folders that appear at runtime via symlink
        new Notice("t9x: created _agents symlink — restart Obsidian to index it", 10000);
      }
      const base = path.join(root, BASE_FILE);
      if (!fs.existsSync(base)) fs.writeFileSync(base, BASE_TEMPLATE);
    } catch (e) {
      new Notice(`t9x bootstrap failed: ${e}`);
    }
  }

  /** _agents/... (vault view) -> .agents/... (canonical, for the CLI). */
  toReal(vaultPath: string): string {
    return vaultPath.replace(/^_agents\//, ".agents/");
  }

  toVault(realPath: string): string {
    return realPath.replace(/^\.agents\//, "_agents/");
  }

  // --- commands ----------------------------------------------------------

  async pickup(editor: import("obsidian").Editor, view: MarkdownView) {
    if (!this.workspaceRoot() || !view.file) return;
    const text = editor.getValue();
    const offset = editor.posToOffset(editor.getCursor());
    const m = findMarkerAt(text, offset);
    if (!m) {
      new Notice("t9x: cursor is not inside a @(...) marker");
      return;
    }
    await this.app.vault.modify(view.file, text); // persist the buffer the agent will edit
    const line = text.slice(0, m.start).split("\n").length;
    const prompt = render(this.settings.pickupPrompt, {
      FILE: this.toReal(view.file.path),
      LINE: String(line),
      MARKER: m.text,
    });
    const stamp = new Date().toISOString().replace(/[:.]/g, "-");
    this.spawnAgent(this.settings.defaultAgent, prompt, `pickup-${stamp}`);
  }

  async newTask(title: string) {
    if (!title.trim()) return;
    try {
      const out = await this.t9x(["task", "new", title.trim()]);
      const [id, realPath] = out.trim().split(/\s+/);
      new Notice(`t9x: created ${id}`);
      const file = this.app.vault.getAbstractFileByPath(normalizePath(this.toVault(realPath)));
      if (file instanceof TFile) await this.app.workspace.getLeaf().openFile(file);
    } catch (e) {
      new Notice(`t9x: ${e}`);
    }
  }

  activeId(): string | null {
    const file = this.app.workspace.getActiveFile();
    const id = file && this.app.metadataCache.getFileCache(file)?.frontmatter?.id;
    if (!id) new Notice("t9x: active file has no id: frontmatter");
    return id ?? null;
  }

  async taskVerb(verb: "close" | "reopen") {
    const id = this.activeId();
    if (!id) return;
    try {
      new Notice((await this.t9x([verb, id])).trim());
    } catch (e) {
      new Notice(`t9x: ${e}`);
    }
  }

  async promote() {
    const file = this.app.workspace.getActiveFile();
    if (!this.workspaceRoot() || !file) return;
    if (!file.path.startsWith("_agents/")) {
      new Notice("t9x: active file is not in agent space");
      return;
    }
    new PromptModal(this.app, "Promote to (path)", `docs/${file.name}`, async (target) => {
      try {
        await this.t9x(["promote", this.toReal(file.path), target]);
        new Notice(`t9x: promoted to ${target}`);
      } catch (e) {
        new Notice(`t9x: ${e}`);
      }
    }).open();
  }

  async demote() {
    const file = this.app.workspace.getActiveFile();
    if (!this.workspaceRoot() || !file) return;
    if (file.path.startsWith("_agents/")) {
      new Notice("t9x: file is already in agent space");
      return;
    }
    await this.app.fileManager.renameFile(file, normalizePath(`_agents/notes/${file.name}`));
    new Notice(`t9x: moved to _agents/notes/${file.name}`);
  }

  delegate() {
    const root = this.workspaceRoot();
    if (!root) return;
    // read straight from the filesystem: delegation must not depend on
    // Obsidian having indexed the _agents symlink
    const dir = path.join(root, ".agents", "tasks");
    const tasks = fs
      .readdirSync(dir)
      .filter((f) => f.endsWith(".md"))
      .map((f) => {
        const text = fs.readFileSync(path.join(dir, f), "utf8");
        return {
          name: f.replace(/\.md$/, ""),
          id: /^id:\s*['"]?([A-Za-z0-9_-]+)/m.exec(text)?.[1],
          status: /^status:\s*(\S+)/m.exec(text)?.[1],
        };
      })
      .filter((t) => t.id && t.status === "open");
    if (!tasks.length) {
      new Notice("t9x: no open tasks");
      return;
    }
    new PickModal(this.app, tasks.map((t) => ({ key: t.id!, label: `${t.id}  ${t.name}` })), (id) => {
      new PickModal(this.app, Object.keys(this.settings.agents).map((a) => ({ key: a, label: a })), (agent) => {
        const prompt = render(this.settings.delegatePrompt, { ID: id });
        this.spawnAgent(agent, prompt, id);
      }).open();
    }).open();
  }

  async openBase() {
    const root = this.workspaceRoot();
    if (!root) return;
    this.bootstrap();
    const file = this.app.vault.getAbstractFileByPath(BASE_FILE);
    if (file instanceof TFile) await this.app.workspace.getLeaf().openFile(file);
    else new Notice(`t9x: ${BASE_FILE} not found`);
  }

  // --- delegation --------------------------------------------------------

  spawnAgent(agent: string, prompt: string, logBase: string) {
    const root = this.workspaceRoot();
    if (!root) return;
    const argvTemplate = this.settings.agents[agent];
    if (!argvTemplate) {
      new Notice(`t9x: unknown agent "${agent}"`);
      return;
    }
    const argv = argvTemplate.map((a) => a.replace("{{PROMPT}}", prompt));
    const logPath = path.join(root, ".agents", "runs", `${logBase}-${agent}.log`);
    try {
      const fd = fs.openSync(logPath, "a");
      const child = spawn(argv[0], argv.slice(1), {
        cwd: root,
        env: this.env(),
        detached: true,
        stdio: ["ignore", fd, fd],
      });
      child.on("error", (e) => new Notice(`t9x: ${agent} failed to start: ${e.message}`));
      child.on("exit", (code) => {
        fs.closeSync(fd);
        new Notice(`t9x: ${agent} finished (exit ${code}) — see ${path.basename(logPath)}`);
      });
      child.unref();
      new Notice(`t9x: delegated to ${agent} — log: ${path.basename(logPath)}`);
    } catch (e) {
      new Notice(`t9x: could not spawn ${agent}: ${e}`);
    }
  }

  // --- settings ----------------------------------------------------------

  async loadSettings() {
    this.settings = { ...DEFAULT_SETTINGS, ...(await this.loadData()) };
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }
}

class PromptModal extends Modal {
  constructor(
    app: App,
    private label: string,
    private initial: string,
    private onSubmit: (value: string) => void,
  ) {
    super(app);
  }

  onOpen() {
    this.contentEl.createEl("h3", { text: this.label });
    const input = this.contentEl.createEl("input", { type: "text", value: this.initial });
    input.style.width = "100%";
    input.focus();
    input.select();
    input.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        this.close();
        this.onSubmit(input.value);
      }
    });
  }

  onClose() {
    this.contentEl.empty();
  }
}

class PickModal extends SuggestModal<{ key: string; label: string }> {
  constructor(
    app: App,
    private items: { key: string; label: string }[],
    private onPick: (key: string) => void,
  ) {
    super(app);
  }

  getSuggestions(query: string) {
    const q = query.toLowerCase();
    return this.items.filter((i) => i.label.toLowerCase().includes(q));
  }

  renderSuggestion(item: { key: string; label: string }, el: HTMLElement) {
    el.setText(item.label);
  }

  onChooseSuggestion(item: { key: string; label: string }) {
    this.onPick(item.key);
  }
}

class T9xSettingTab extends PluginSettingTab {
  constructor(
    app: App,
    private plugin: T9xPlugin,
  ) {
    super(app, plugin);
  }

  display() {
    const { containerEl } = this;
    containerEl.empty();

    new Setting(containerEl).setName("t9x binary").addText((t) =>
      t.setValue(this.plugin.settings.t9xPath).onChange(async (v) => {
        this.plugin.settings.t9xPath = v;
        await this.plugin.saveSettings();
      }),
    );

    new Setting(containerEl)
      .setName("PATH prepend")
      .setDesc("Colon-separated dirs added to PATH for spawned processes (GUI apps do not inherit your shell PATH).")
      .addText((t) =>
        t.setValue(this.plugin.settings.pathPrepend).onChange(async (v) => {
          this.plugin.settings.pathPrepend = v;
          await this.plugin.saveSettings();
        }),
      );

    new Setting(containerEl).setName("Default agent").addDropdown((d) => {
      for (const a of Object.keys(this.plugin.settings.agents)) d.addOption(a, a);
      d.setValue(this.plugin.settings.defaultAgent).onChange(async (v) => {
        this.plugin.settings.defaultAgent = v;
        await this.plugin.saveSettings();
      });
    });

    new Setting(containerEl)
      .setName("Agents")
      .setDesc('JSON: {"name": ["cmd", "arg", "{{PROMPT}}"], ...}')
      .addTextArea((t) => {
        t.inputEl.rows = 8;
        t.inputEl.style.width = "100%";
        t.setValue(JSON.stringify(this.plugin.settings.agents, null, 2)).onChange(async (v) => {
          try {
            this.plugin.settings.agents = JSON.parse(v);
            await this.plugin.saveSettings();
          } catch {
            /* keep last valid value while the user is mid-edit */
          }
        });
      });

    new Setting(containerEl)
      .setName("Pickup prompt")
      .setDesc("Placeholders: {{FILE}}, {{LINE}}, {{MARKER}}")
      .addTextArea((t) => {
        t.inputEl.rows = 6;
        t.inputEl.style.width = "100%";
        t.setValue(this.plugin.settings.pickupPrompt).onChange(async (v) => {
          this.plugin.settings.pickupPrompt = v;
          await this.plugin.saveSettings();
        });
      });

    new Setting(containerEl)
      .setName("Delegate prompt")
      .setDesc("Placeholder: {{ID}}")
      .addTextArea((t) => {
        t.inputEl.rows = 6;
        t.inputEl.style.width = "100%";
        t.setValue(this.plugin.settings.delegatePrompt).onChange(async (v) => {
          this.plugin.settings.delegatePrompt = v;
          await this.plugin.saveSettings();
        });
      });
  }
}
