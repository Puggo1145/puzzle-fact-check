"use client"

import type { ChangeEvent } from "react";
import { useState, useMemo, useRef, useEffect } from "react";
import {
    ArrowUpIcon,
    ChevronsLeftRightEllipsisIcon,
    BinocularsIcon,
    PencilRulerIcon,
    SearchIcon,
    GlobeIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"

export const InputPanel = () => {
    const [input, setInput] = useState("")
    const hasInput = useMemo(() => input.trim() !== "", [input])

    const onValueChange = (value: ChangeEvent<HTMLTextAreaElement>) => setInput(value.target.value)

    return (
        <div className="max-w-2xl w-full p-4 border-2 border-primary/5 bg-background rounded-3xl">
            <textarea
                value={input}
                onChange={onValueChange}
                placeholder="Paste what you don't believe here"
                className="w-full min-h-20 px-1 outline-none resize-none"
            />
            <BottomFns hasInput={hasInput} />
        </div>
    )
}

export const BottomFns = ({ hasInput }: { hasInput: boolean }) => {
    return (
        <div className="w-full flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
                <ModelSelector />
                <ToolSelector />
            </div>
            <Button 
                className="rounded-full" 
                size="icon"
                disabled={!hasInput}
            >
                <ArrowUpIcon strokeWidth={4} className="size-4" />
            </Button>
        </div>
    )
}

export const ModelSelector = () => {
    const searchConfigs = [
        {
            name: "Balance",
            icon: () => <ChevronsLeftRightEllipsisIcon className="size-4" />,
            description: "Fact check with a balance between speed and accuracy.",
        },
        {
            name: "Deeper",
            icon: () => <BinocularsIcon className="size-4" />,
            description: "In-depth fact check by consuming more tokens for search. More accurate but slower and more expensive.",
        },
    ]

    return (
        <Select defaultValue={searchConfigs[0].name}>
            <SelectTrigger className="rounded-full cursor-pointer hover:bg-accent">
                <SelectValue />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
                {searchConfigs.map((searchConfig) => (
                    <SelectItem
                        className="p-3 rounded-lg cursor-pointer"
                        key={searchConfig.name}
                        value={searchConfig.name}
                    >
                        <div className="flex items-center gap-2 mr-2">
                            <searchConfig.icon />
                            <h4 className="text-sm font-medium">{searchConfig.name}</h4>
                        </div>
                    </SelectItem>
                ))}
            </SelectContent>
        </Select>
    )
}

export const ToolSelector = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [selectedTools, setSelectedTools] = useState<number[]>([]);
    const panelRef = useRef<HTMLDivElement>(null);
    
    const tools = [
        {
            name: "Tavily Search",
            icon: () => <SearchIcon className="size-4" />,
            description: "Search the web faster with Tavily. API Key is required for this tool.",
        },
        {
            name: "Browser Use",
            icon: () => <GlobeIcon className="size-4" />,
            description: "Enable Agent to use browser for more complex tasks.",
        },
    ];

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    const handleToolSelect = (index: number) => {
        setSelectedTools(prev => {
            // If tool is already selected, remove it
            if (prev.includes(index)) {
                return prev.filter(i => i !== index);
            }
            // Otherwise add it
            return [...prev, index];
        });
    };

    return (
        <div className="relative" ref={panelRef}>
            <Button
                variant="ghost"
                className="rounded-full hover:bg-accent flex items-center gap-2 h-9 p-0"
                onClick={() => setIsOpen(!isOpen)}
            >
                {selectedTools.length > 0 ? (
                    <div className="flex">
                        {selectedTools.map((toolIndex, i) => (
                            <div 
                                key={toolIndex}
                                className="rounded-full bg-background flex items-center justify-center size-9"
                                style={{
                                    marginLeft: i > 0 ? '-10px' : '0',
                                    zIndex: selectedTools.length - i,
                                    border: '1px solid var(--border)',
                                }}
                            >
                                {tools[toolIndex].icon()}
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="px-3 flex items-center gap-2">
                        <div className="rounded-full flex items-center justify-center size-7">
                            <PencilRulerIcon className="size-4" />
                        </div>
                        <span className="text-xs font-medium">Select tools</span>
                    </div>
                )}
            </Button>
            
            {isOpen && (
                <div className="absolute left-0 top-full mt-2 w-64 bg-background border border-border rounded-xl shadow-md z-10">
                    <div className="p-2">
                        {tools.map((tool, index) => {
                            const isSelected = selectedTools.includes(index);
                            return (
                                <div
                                    key={tool.name}
                                    className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer hover:bg-accent/50 transition-colors ${isSelected ? 'bg-accent/30' : ''}`}
                                    onClick={() => handleToolSelect(index)}
                                >
                                    <div className="mt-0.5 relative">
                                        {isSelected && (
                                            <div className="absolute -right-1 -top-1 w-3 h-3 bg-primary rounded-full border-2 border-background" />
                                        )}
                                        <tool.icon />
                                    </div>
                                    <div>
                                        <h4 className="text-sm font-medium">{tool.name}</h4>
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
