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
    const components = message.split("<|im_start|>answer");
    if (components.length == 2) {
        const [reasoning2, answer2] = components;
        const [_, reasoning3] = reasoning2.split("<|im_start|>think");
        // cut at the last sentence
        const reasoning4 = reasoning3.split(".").slice(0, -1).join(".") + ".";
        // remove stray im_starts
        const reasoning = reasoning4.replace(/<\|im_start\|>/g, "");
        const answer = answer2.replace(/<\|im_start\|>/g, "");
        return { role: "ai", content: mdToHtml(answer.trim()), reasoning: mdToHtml(reasoning.trim()) };
    } else {
        return { role: "ai", content: mdToHtml(message), reasoning: null };
    }
}
export function makeToolEntry(sources: string[]): ChatEntry {
    return { role: "tool", sources: sources };
}

export function parseChatEntries(json: object): ChatEntry[] {
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
    age: number;
    sex: "female" | "male" | "unspecified";
    occupation: string;
    supportSystem: string;
    medicalHistory: string;
}

export let emptyDemographics = {
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

export function generateCuteUUID() {
    const adjectives = [
        "adorable", "bubbly", "cheerful", "cuddly", "dizzy", "fluffy", "happy",
        "jolly", "kind", "lovely", "mellow", "nifty", "peppy", "plucky",
        "precious", "quiet", "rosy", "sleepy", "snuggly", "soft", "sparkly",
        "sunny", "sweet", "ticklish", "tiny", "warm", "wiggly", "zesty", "zany",
        "glowy", "gentle", "bright", "dreamy", "honeyed", "charming", "fuzzy",
        "smiley", "tender", "twinkly", "winsome", "chirpy"
    ];
    const animals = [
        "bunny", "kitten", "puppy", "duckling", "hedgehog", "penguin", "panda",
        "fawn", "lamb", "koala", "hamster", "otter", "sloth", "mouse", "calf",
        "seal", "whale", "swan", "cub", "foal", "quokka", "flamingo",
        "starling", "parakeet", "peep", "caterpillar", "guinea", "deerling",
        "shrew", "snail", "turtle", "lovebird", "wren", "goldfinch", "bluebird",
        "mole", "cygnet"
    ];
    const adjective = adjectives[Math.floor(Math.random() * adjectives.length)];
    const animal = animals[Math.floor(Math.random() * animals.length)];
    const number = Math.floor(Math.random() * 99);
    const numberString = number < 10 ? `0${number}` : `${number}`;
    return `${adjective}-${animal}-${numberString}`;
}
