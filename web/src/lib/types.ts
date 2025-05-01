export type ChatEntry = {
    role: "human" | "ai";
    content: string;
};
export function makeHumanEntry(message: string): ChatEntry {
    return { role: "human", content: message };
}
export function makeAIEntry(message: string): ChatEntry {
    return { role: "ai", content: message };
}
