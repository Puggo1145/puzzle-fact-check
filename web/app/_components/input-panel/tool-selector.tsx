import React, { useRef, useEffect } from "react";
import { PencilRulerIcon, SearchIcon, GlobeIcon, EyeIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

export const ToolSelector = ({ 
    selectedTools,
    setSelectedTools,
    showTools,
    setShowTools
}: { 
    selectedTools: string[];
    setSelectedTools: (tools: string[]) => void;
    showTools: boolean;
    setShowTools: (show: boolean) => void;
}) => {
    const panelRef = useRef<HTMLDivElement>(null);
    
    const tools = [
        {
            id: "tavily_search",
            name: "Tavily Search",
            icon: () => <SearchIcon className="size-4" />,
            description: "使用 Tavily 进行更快的网络搜索，需要 API Key",
            inDevelopment: false
        },
        {
            id: "browser_use",
            name: "Browser Use",
            icon: () => <GlobeIcon className="size-4" />,
            description: "允许 Agent 使用浏览器执行更复杂的任务",
            inDevelopment: true
        },
        {
            id: "vision",
            name: "Vision",
            icon: () => <EyeIcon className="size-4" />,
            description: "允许 Agent 查看更复杂的任务",
            inDevelopment: true
        },
    ];

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
                setShowTools(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [setShowTools]);

    const handleToolSelect = (toolId: string) => {
        // Don't allow selection of tools in development
        const tool = tools.find(t => t.id === toolId);
        if (!tool || tool.inDevelopment) return;
        
        // Create a new array based on the current selection
        const newSelectedTools = [...selectedTools];
        
        // If tool is already selected, remove it
        if (newSelectedTools.includes(toolId)) {
            setSelectedTools(newSelectedTools.filter(id => id !== toolId));
        } else {
            // Otherwise add it
            setSelectedTools([...newSelectedTools, toolId]);
        }
    };

    return (
        <div className="relative" ref={panelRef}>
            <Button
                variant="ghost"
                className="rounded-full hover:bg-accent flex items-center gap-2 h-9 p-0"
                onClick={() => setShowTools(!showTools)}
            >
                {selectedTools.length > 0 ? (
                    <div className="flex">
                        {selectedTools.map((toolId, i) => {
                            const tool = tools.find(t => t.id === toolId);
                            if (!tool) return null;
                            return (
                                <div 
                                    key={toolId}
                                    className="rounded-full bg-background flex items-center justify-center size-9"
                                    style={{
                                        marginLeft: i > 0 ? '-10px' : '0',
                                        zIndex: selectedTools.length - i,
                                        border: '1px solid var(--border)',
                                    }}
                                >
                                    <tool.icon />
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="px-3 pr-4 flex items-center gap-1">
                        <div className="rounded-full flex items-center justify-center size-7">
                            <PencilRulerIcon className="size-4" />
                        </div>
                        <span className="text-xs font-medium">使用更多工具</span>
                    </div>
                )}
            </Button>
            
            {showTools && (
                <div className="absolute left-0 top-full mt-2 w-64 bg-background border border-border rounded-xl shadow-md z-10">
                    <div className="p-2">
                        {tools.map((tool) => {
                            const isSelected = selectedTools.includes(tool.id);
                            return (
                                <div
                                    key={tool.id}
                                    className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                                        tool.inDevelopment 
                                            ? 'opacity-60 hover:bg-accent/20' 
                                            : `hover:bg-accent/50 ${isSelected ? 'bg-accent/30' : ''}`
                                    }`}
                                    onClick={() => handleToolSelect(tool.id)}
                                >
                                    <div className="mt-0.5 relative">
                                        {isSelected && !tool.inDevelopment && (
                                            <div className="absolute -right-1 -top-1 w-3 h-3 bg-primary rounded-full border-2 border-background" />
                                        )}
                                        <tool.icon />
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2">
                                            <h4 className="text-sm font-medium">{tool.name}</h4>
                                            {tool.inDevelopment && (
                                                <span className="text-[10px] bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 px-1.5 py-0.5 rounded-full">
                                                    开发中
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-xs text-muted-foreground">{tool.description}</p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}; 