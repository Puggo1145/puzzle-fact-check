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
        description: "为 Agent 提供更快和更高效的网络搜索工具",
        available: false
    },
    {
        id: "browser_use",
        name: "Browser Use",
        icon: () => <GlobeIcon className="size-4" />,
        description: "允许 Agent 使用浏览器执行更复杂的任务",
        available: true
    },
    {
        id: "vision",
        name: "Vision",
        icon: () => <EyeIcon className="size-4" />,
        description: "允许 Agent 使用视觉理解更多模态的信息",
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
        alias: "Google 搜索",
        icon: () => <SearchIcon className="size-4" />
    },
    "search_google_alternative": {
        alias: "Google 搜索(备用)",
        icon: () => <SearchIcon className="size-4" />
    },
    "search_bing": {
        alias: "Bing 搜索",
        icon: () => <SearchIcon className="size-4" />
    },
    "search_wikipedia": {
        alias: "维基百科搜索",
        icon: () => <BookAIcon className="size-4" />,
    },
    "tavily_search": {
        alias: "Tavily 搜索",
        icon: () => <SearchIcon className="size-4" />
    },
    "read_webpage": {
        alias: "阅读网页",
        icon: () => <PanelTopIcon className="size-4" />
    },
    "read_pdf": {
        alias: "阅读PDF",
        icon: () => <FileTextIcon className="size-4" />
    },
    "get_current_time": {
        alias: "获取当前时间",
        icon: () => <ClockIcon className="size-4" />
    },
    "browser_use": {
        alias: "使用浏览器",
        icon: () => <GlobeIcon className="size-4" />
    },
    "vision": {
        alias: "使用视觉理解",
        icon: () => <EyeIcon className="size-4" />
    }
}
