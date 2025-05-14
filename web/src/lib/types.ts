import showdown from "showdown";
import sanitizeHtml from 'sanitize-html';

export type HumanChatEntry = {
    role: "human";
    content: string;
}
export type AIChatEntry = {
    role: "ai";
    content: string;
    reasoning: string | null;
}
export type ToolChatEntry = {
    role: "tool";
    sources: string[];
}

export type ChatEntry = HumanChatEntry | AIChatEntry;

const converter = new showdown.Converter({
    disableForced4SpacesIndentedSublists:
        true
});

function mdToHtml(md: string): string {
    return sanitizeHtml(converter.makeHtml(md));
}

export function makeHumanEntry(message: string): HumanChatEntry {
    return { role: "human", content: mdToHtml(message) };
}
export function makeToolEntry(sources: string[]): ToolChatEntry {
    return { role: "tool", sources };
}
function postProcessReasoning(reasoning: string): string {
    const r = reasoning.split(".").slice(0, -1).join(".") + ".";
    return r.replace(/<\|im_start\|>/g, "").trim();
}
export function postProcessAnswer(answer: string): string {
    return answer
        .trim()
        .replace(/-+$/, "")
        .replace(/<\|im_start\|>/g, "")
        .trim();
}
export function makeAIEntry(message: string): AIChatEntry {
    const components = message.split("<|im_start|>answer");
    if (components.length == 2) {
        const [reasoning2, answer2] = components;
        const [_, reasoning3] = reasoning2.split("<|im_start|>think");
        // cut at the last sentence
        const reasoning = postProcessReasoning(reasoning3);
        // remove stray im_starts
        const answer = postProcessAnswer(answer2);
        return {
            role: "ai",
            content: mdToHtml(answer),
            reasoning: mdToHtml(reasoning),
        };
    } else {
        // check if it is reasoning
        const maybeComponents = message.split("<|im_start|>think");
        if (maybeComponents.length == 2) {
            const reasoning = postProcessReasoning(maybeComponents[1]);
            return {
                role: "ai", content: "", reasoning: mdToHtml(reasoning),
            };
        } else {
            return {
                role: "ai", content: mdToHtml(message), reasoning: null,
            };
        }
    }
}
export function parseChatEntries(json: object): ChatEntry[] {
    let nextToolMessage: ToolChatEntry[] = [];

    if (json.messages === undefined) {
        return [];
    } else {
        return json.messages.flatMap((entry: any) => {
            if (entry.type === "human") {
                return [makeHumanEntry(entry.content)];
            }
            else if (entry.type === "ai") {
                if (entry.tool_calls.length > 0) {
                    return [];
                } else {
                    let e = [makeAIEntry(entry.content), ...nextToolMessage];
                    return e;
                }
            }
            else if (entry.type === "tool") {
                const sources = entry.artifact.context.map((ctx: any) => ctx.metadata.source);
                nextToolMessage = [makeToolEntry(sources)];
                return [];
            }
            else {
                console.warn("Unknown entry type ^^^ ", entry);
                return [];
            }
        });
    }
}

export type Demographics = {
    age: number;
    sex: "female" | "male" | "unspecified";
    occupation: string;
    supportSystem: string;
    medicalHistory: string;
}

export let emptyDemographics: Demographics = {
    age: 0,
    sex: "unspecified",
    occupation: "",
    supportSystem: "",
    medicalHistory: ""
}

export function demographicsToJson(demo: Demographics) {
    // could use JSON.stringify, but we want to avoid serialising
    // values that weren't provided
    let json = {};
    if (demo.age > 0) json = { ...json, age: demo.age };
    if (demo.sex !== "unspecified") json = { ...json, sex: demo.sex };
    if (demo.occupation !== "") json = { ...json, occupation: demo.occupation };
    if (demo.supportSystem !== "") json = { ...json, supportSystem: demo.supportSystem };
    if (demo.medicalHistory !== "") json = { ...json, medicalHistory: demo.medicalHistory };
    return JSON.stringify(json);
}
