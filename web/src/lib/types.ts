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

export type ChatEntry = HumanChatEntry | AIChatEntry;

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
