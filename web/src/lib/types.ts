export type ChatEntry = {
    role: "user" | "response";
    content: string;
};
export function makeUserEntry(message: string): ChatEntry {
    return { role: "user", content: message };
}
export function makeResponseEntry(message: string): ChatEntry {
    return { role: "response", content: message };
}
