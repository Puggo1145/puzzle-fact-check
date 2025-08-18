import { 
    SearchIcon, 
    GlobeIcon, 
    EyeIcon,
    BookAIcon,
    PanelTopIcon,
    ClockIcon,
    FileTextIcon
} from "lucide-react";

interface Tool {
    id: string;
    name: string;
    description: string;
    icon: () => React.ReactNode;
    available: boolean;
}

export const tools: Tool[] = [
    {
        id: "tavily_search",
        name: "Tavily Search",
        icon: () => <SearchIcon className="size-4" />,
        description: "Provide faster and more efficient web search tools for Agent",
        available: false
    },
    {
        id: "browser_use",
        name: "Browser Use",
        icon: () => <GlobeIcon className="size-4" />,
        description: "Allow Agent to use browser to perform more complex tasks",
        available: true
    },
    {
        id: "vision",
        name: "Vision",
        icon: () => <EyeIcon className="size-4" />,
        description: "Allow Agent to use vision to understand more modal information",
        available: true
    },
]

interface ToolDict {
    [key: string]: {
        alias: string;
        icon: () => React.ReactNode;
    };
}

export const toolDict: ToolDict = {
    "search_google_official": {
        alias: "Google Search",
        icon: () => <SearchIcon className="size-4" />
    },
    "search_google_alternative": {
        alias: "Google Search (Alternative)",
        icon: () => <SearchIcon className="size-4" />
    },
    "search_bing": {
        alias: "Bing Search",
        icon: () => <SearchIcon className="size-4" />
    },
    "search_baidu": {
        alias: "Baidu Search",
        icon: () => <SearchIcon className="size-4" />
    },
    "search_wikipedia": {
        alias: "Wikipedia Search",
        icon: () => <BookAIcon className="size-4" />,
    },
    "tavily_search": {
        alias: "Tavily Search",
        icon: () => <SearchIcon className="size-4" />
    },
    "read_webpage": {
        alias: "Read Webpage",
        icon: () => <PanelTopIcon className="size-4" />
    },
    "read_pdf": {
        alias: "Read PDF",
        icon: () => <FileTextIcon className="size-4" />
    },
    "get_current_time": {
        alias: "Get Current Time",
        icon: () => <ClockIcon className="size-4" />
    },
    "browser_use": {
        alias: "Use Browser",
        icon: () => <GlobeIcon className="size-4" />
    },
    "vision": {
        alias: "Use Vision",
        icon: () => <EyeIcon className="size-4" />
    }
}
