import showdown from "showdown";
import sanitizeHtml from 'sanitize-html';

type HumanChatEntry = {
    role: "human";
    content: string;
}
type AIChatEntry = {
    role: "ai";
    content: string;
    reasoning: string | null;
}
type ToolChatEntry = {
    role: "tool";
    sources: string[];
}

export type ChatEntry = HumanChatEntry | AIChatEntry | ToolChatEntry;

const converter = new showdown.Converter({
    disableForced4SpacesIndentedSublists:
        true
});

function mdToHtml(md: string): string {
    return sanitizeHtml(converter.makeHtml(md));
}

export function makeHumanEntry(message: string): ChatEntry {
    return { role: "human", content: mdToHtml(message) };
}
export function makeAIEntry(message: string): ChatEntry {
    // TODO: Some chat messages may require parsing to separate it into
    // reasoning + content.
    return { role: "ai", content: mdToHtml(message), reasoning: mdToHtml("Some kind of reasoning") };
}
export function makeToolEntry(sources: string[]): ChatEntry {
    return { role: "tool", sources: sources };
}

export function parseChatEntries(json: object): ChatEntry[] {
    if (json.messages === undefined) {
        return [];
    } else {
        return json.messages.flatMap((entry: any) => {
            console.log(entry);
            if (entry.type === "human") {
                return [makeHumanEntry(entry.content)];
            }
            else if (entry.type === "ai") {
                if (entry.tool_calls.length > 0) {
                    return [];
                } else {
                    return [makeAIEntry(entry.content)];
                }
            }
            else if (entry.type === "tool") {
                return [makeToolEntry(entry.artifact.context.map((ctx: any) =>
                    ctx.metadata.source))];
            }
            else {
                console.warn("Unknown entry type ^^^ ", entry);
                return [];
            }
        });
    }
}

export type Demographics = {
    name: string;
    age: number;
}

export let emptyDemographics = {
    name: "",
    age: 0
}
