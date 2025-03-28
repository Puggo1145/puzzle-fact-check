"use client"

import { useState, useMemo, useRef, useEffect } from "react";
import {
    ArrowUpIcon,
    PencilRulerIcon,
    SearchIcon,
    GlobeIcon,
    EyeIcon,
    StopCircleIcon,
    CogIcon,
    ChevronUpIcon,
    ChevronDownIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import { useAgentStore } from "@/lib/store";
import { AgentConfigPanel } from "@/components/agent/agent-config";

export const InputPanel = () => {
    const {
        newsText,
        setNewsText,
        status,
        interruptAgent,
        createAndRunAgent,
        mainAgentConfig,
        metadataExtractorConfig,
        searcherConfig,
        availableModels,
        setMainAgentConfig,
        setMetadataExtractorConfig,
        setSearcherConfig,
        finalReport,
        resetState,
        events
    } = useAgentStore();
    
    const [input, setInput] = useState(newsText);
    const [mode, setMode] = useState<"initial" | "running">("initial");
    const [showTools, setShowTools] = useState(false);
    const [showConfig, setShowConfig] = useState(false);
    const [showModelInfo, setShowModelInfo] = useState(false);
    const [selectedTools, setSelectedTools] = useState<number[]>([]);
    const hasInput = useMemo(() => input.trim() !== "", [input]);
    const panelRef = useRef<HTMLDivElement>(null);

    // Check if we're in active mode (running, completed, interrupted, or interrupting)
    const isActive = status !== 'idle';
    const isRunning = status === 'running';
    const isInterrupting = status === 'interrupting';

    useEffect(() => {
        if (isActive && mode === "initial") {
            setMode("running");
            setShowModelInfo(false);
        } else if (!isActive && mode === "running") {
            setMode("initial");
        }
    }, [isActive, mode]);

    useEffect(() => {
        setNewsText(input);
    }, [input, setNewsText]);

    const handleSendMessage = async () => {
        if (!hasInput) return;
        try {
            await createAndRunAgent();
        } catch (error) {
            console.error('Failed to run agent:', error);
        }
    };

    const handleInterrupt = async () => {
        try {
            await interruptAgent();
        } catch (error) {
            console.error('Failed to interrupt agent:', error);
        }
    };

    const handleReset = () => {
        resetState();
    };

    const toggleModelInfo = () => {
        setShowModelInfo(!showModelInfo);
    };

    const onValueChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value);

    return (
        <div 
            ref={panelRef}
            className={cn(
                "w-full transition-all duration-500 ease-in-out", 
                mode === "initial" 
                    ? "p-4 border-2 border-primary/5 bg-background rounded-3xl" 
                    : "fixed bottom-6 left-0 right-0 z-10"
            )}
        >
            {mode === "initial" ? (
                <>
                    <textarea
                        value={input}
                        onChange={onValueChange}
                        placeholder="告诉我你想核查的新闻..."
                        className="w-full min-h-20 px-1 outline-none resize-none"
                    />
                    <div className="w-full flex items-center justify-between gap-2 mt-2">
                        <div className="flex items-center gap-2">
                            <Dialog open={showConfig} onOpenChange={setShowConfig}>
                                <DialogTrigger asChild>
                                    <Button 
                                        variant="outline" 
                                        size="sm" 
                                        className="rounded-full flex items-center gap-1"
                                    >
                                        <CogIcon className="size-4" />
                                        <span className="text-xs">Agent 配置</span>
                                    </Button>
                                </DialogTrigger>
                                <DialogContent className="max-w-md">
                                    <DialogHeader>
                                        <DialogTitle>Agent 配置</DialogTitle>
                                    </DialogHeader>
                                    <div className="space-y-4 mt-4">
                                        <AgentConfigPanel
                                            agentType="main"
                                            config={mainAgentConfig}
                                            availableModels={availableModels}
                                            onChange={setMainAgentConfig}
                                            disabled={isRunning}
                                        />
                                        
                                        <AgentConfigPanel
                                            agentType="metadata"
                                            config={metadataExtractorConfig}
                                            availableModels={availableModels}
                                            onChange={setMetadataExtractorConfig}
                                            disabled={isRunning}
                                        />
                                        
                                        <AgentConfigPanel
                                            agentType="searcher"
                                            config={searcherConfig}
                                            availableModels={availableModels}
                                            onChange={setSearcherConfig}
                                            disabled={isRunning}
                                        />
                                    </div>
                                </DialogContent>
                            </Dialog>
                            <ToolSelector
                                selectedTools={selectedTools}
                                setSelectedTools={setSelectedTools}
                                showTools={showTools}
                                setShowTools={setShowTools}
                            />
                        </div>
                        <Button 
                            className="rounded-full" 
                            size="icon"
                            disabled={!hasInput}
                            onClick={handleSendMessage}
                        >
                            <ArrowUpIcon strokeWidth={2} className="size-4" />
                        </Button>
                    </div>
                </>
            ) : (
                <div className="container mx-auto max-w-2xl">
                    {showModelInfo && (
                        <div className="bg-background/95 backdrop-blur-sm border border-primary/5 rounded-xl p-4 mb-3 shadow-sm animate-in slide-in-from-bottom duration-300">
                            <div className="flex justify-between items-center mb-3">
                                <h3 className="text-sm font-medium">模型配置信息</h3>
                                <Button 
                                    variant="ghost" 
                                    size="sm" 
                                    className="size-6 p-0 rounded-full" 
                                    onClick={toggleModelInfo}
                                >
                                    <ChevronDownIcon className="size-4" />
                                </Button>
                            </div>
                            <div className="space-y-3">
                                <ModelInfoItem 
                                    title="主智能体" 
                                    model={mainAgentConfig.modelName}
                                    provider={mainAgentConfig.modelProvider}
                                />
                                <ModelInfoItem 
                                    title="元数据提取智能体" 
                                    model={metadataExtractorConfig.modelName}
                                    provider={metadataExtractorConfig.modelProvider}
                                />
                                <ModelInfoItem 
                                    title="检索智能体" 
                                    model={searcherConfig.modelName}
                                    provider={searcherConfig.modelProvider}
                                    tokens={`${searcherConfig.maxSearchTokens} tokens`}
                                />
                            </div>
                        </div>
                    )}
                    <div className="p-2 bg-background border border-primary/5 rounded-full shadow-sm flex justify-between items-center">
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={toggleModelInfo}
                            className="rounded-full flex items-center gap-1 p-2 pl-3"
                        >
                            {showModelInfo ? (
                                <ChevronDownIcon className="size-4" />
                            ) : (
                                <ChevronUpIcon className="size-4" />
                            )}
                            <span className="text-xs">Agent 配置</span>
                        </Button>
                        
                        {isRunning ? (
                            <Button
                                variant="destructive"
                                onClick={handleInterrupt}
                                disabled={isInterrupting}
                                className="rounded-full flex items-center gap-1"
                                size="sm"
                            >
                                <StopCircleIcon className="size-4" />
                                <span className="text-xs">{isInterrupting ? '正在中断...' : '中断'}</span>
                            </Button>
                        ) : (
                            <Button
                                variant="outline"
                                onClick={handleReset}
                                className="rounded-full flex items-center gap-1"
                                size="sm"
                            >
                                <ArrowUpIcon className="size-4 rotate-180" />
                                <span className="text-xs">返回</span>
                            </Button>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

// Component to display model information
const ModelInfoItem = ({ 
    title, 
    model, 
    provider, 
    tokens 
}: { 
    title: string; 
    model: string; 
    provider: string; 
    tokens?: string;
}) => {
    return (
        <div className="bg-muted/40 rounded-lg p-2 text-xs">
            <div className="font-medium mb-1">{title}</div>
            <div className="flex flex-wrap gap-2">
                <span className="bg-primary/10 rounded-full px-2 py-0.5">
                    {model}
                </span>
                <span className="bg-primary/10 rounded-full px-2 py-0.5">
                    {provider}
                </span>
                {tokens && (
                    <span className="bg-primary/10 rounded-full px-2 py-0.5">
                        {tokens}
                    </span>
                )}
            </div>
        </div>
    );
};

const ToolSelector = ({ 
    selectedTools,
    setSelectedTools,
    showTools,
    setShowTools
}: { 
    selectedTools: number[];
    setSelectedTools: React.Dispatch<React.SetStateAction<number[]>>;
    showTools: boolean;
    setShowTools: (show: boolean) => void;
}) => {
    const panelRef = useRef<HTMLDivElement>(null);
    
    const tools = [
        {
            name: "Tavily Search",
            icon: () => <SearchIcon className="size-4" />,
            description: "使用 Tavily 进行更快的网络搜索，需要 API Key",
        },
        {
            name: "Browser Use",
            icon: () => <GlobeIcon className="size-4" />,
            description: "允许 Agent 使用浏览器执行更复杂的任务",
        },
        {
            name: "Vision",
            icon: () => <EyeIcon className="size-4" />,
            description: "允许 Agent 查看更复杂的任务",
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

    const handleToolSelect = (index: number) => {
        setSelectedTools((prev: number[]) => {
            // If tool is already selected, remove it
            if (prev.includes(index)) {
                return prev.filter((i: number) => i !== index);
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
                onClick={() => setShowTools(!showTools)}
            >
                {selectedTools.length > 0 ? (
                    <div className="flex">
                        {selectedTools.map((toolIndex, i) => {
                            const ToolIcon = toolIndex === 0 
                                ? SearchIcon 
                                : toolIndex === 1 
                                    ? GlobeIcon 
                                    : EyeIcon;
                            return (
                                <div 
                                    key={toolIndex}
                                    className="rounded-full bg-background flex items-center justify-center size-9"
                                    style={{
                                        marginLeft: i > 0 ? '-10px' : '0',
                                        zIndex: selectedTools.length - i,
                                        border: '1px solid var(--border)',
                                    }}
                                >
                                    <ToolIcon className="size-4" />
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="px-3 pr-4 flex items-center gap-1">
                        <div className="rounded-full flex items-center justify-center size-7">
                            <PencilRulerIcon className="size-4" />
                        </div>
                        <span className="text-xs font-medium">更多工具</span>
                    </div>
                )}
            </Button>
            
            {showTools && (
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
