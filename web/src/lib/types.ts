import showdown from "showdown";
import sanitizeHtml from 'sanitize-html';

export type ChatEntry = {
    role: "human" | "ai";
    content: string;
};

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
    return { role: "ai", content: mdToHtml(message) };
}
