import { type FilePath } from "@vrtmrz/livesync-commonlib/compat/common/types";
import { setFetch } from "@vrtmrz/livesync-commonlib/compat/common/coreEnvFunctions";
import { Platform, requestUrl } from "obsidian";

// Android WebView can reject otherwise valid CouchDB requests with a generic
// `Failed to fetch`, while Obsidian's native requestUrl transport succeeds.
// The patched Fast Fetch uses finite feed=normal responses, so requestUrl can
// safely carry those responses without requiring a streaming ReadableStream.
if (Platform.isMobileApp) {
    setFetch(async (input, init) => {
        const url =
            typeof input === "string" ? input : input instanceof URL ? input.toString() : (input as Request).url;
        const headers = Object.fromEntries(new Headers(init?.headers).entries());
        const body = typeof init?.body === "string" ? init.body : undefined;
        const response = await requestUrl({
            url,
            method: init?.method ?? "GET",
            headers,
            body,
            throw: false,
        });
        return new Response(response.arrayBuffer, {
            status: response.status,
            headers: response.headers,
        });
    });
}

export {
    addIcon,
    App,
    debounce,
    Editor,
    FuzzySuggestModal,
    MarkdownRenderer,
    MarkdownView,
    Modal,
    Notice,
    Platform,
    Plugin,
    PluginSettingTab,
    requestUrl,
    sanitizeHTMLToDom,
    Setting,
    SettingPage,
    stringifyYaml,
    TAbstractFile,
    TextAreaComponent,
    TFile,
    TFolder,
    parseYaml,
    ItemView,
    WorkspaceLeaf,
    Menu,
    request,
    setIcon,
    getLanguage,
    requireApiVersion,
    ButtonComponent,
    TextComponent,
    ToggleComponent,
    DropdownComponent,
    Component,
} from "obsidian";
export type {
    DataWriteOptions,
    PluginManifest,
    RequestUrlParam,
    RequestUrlResponse,
    MarkdownFileInfo,
    ListedFiles,
    ValueComponent,
    Stat,
    Command,
    ViewCreator,
} from "obsidian";
import { normalizePath as normalizePath_ } from "obsidian";
const normalizePath = normalizePath_ as <T extends string | FilePath>(from: T) => T;
export { normalizePath };
export { type Diff, DIFF_DELETE, DIFF_EQUAL, DIFF_INSERT, diff_match_patch } from "diff-match-patch";
