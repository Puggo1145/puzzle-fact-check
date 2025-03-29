"use client"

import { useState, useMemo, useRef, useEffect } from "react";
import {
    ArrowLeftIcon,
    ArrowUpIcon,
    ChevronUpIcon,
    ChevronDownIcon,
    CogIcon,
    StopCircleIcon,
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
import { useAgentStore } from "@/stores/use-agent-store";
import { AgentConfigPanel } from "@/components/agent/agent-config";

// Import extracted components
import { ToolSelector } from "./tool-selector";
import { ExampleNewsCards } from "./example-news-cards";
import { ModelInfoItem } from "./model-info-item";

export const InputPanel = () => {
    const {
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
        resetState,
        events,
        selectedTools,
        setSelectedTools
    } = useAgentStore();
    
    const [input, setInput] = useState("");
    const [mode, setMode] = useState<"initial" | "running">("initial");
    const [showTools, setShowTools] = useState(false);
    const [showConfig, setShowConfig] = useState(false);
    const [showModelInfo, setShowModelInfo] = useState(false);
    const hasInput = useMemo(() => input.trim() !== "", [input]);
    const panelRef = useRef<HTMLDivElement>(null);
    const modelInfoRef = useRef<HTMLDivElement>(null);

    // Check if we're in active mode (running, completed, interrupted, or interrupting)
    const isActive = status !== 'idle';
    const isRunning = status === 'running';
    const isInterrupting = status === 'interrupting';
    const hasEvents = events.length > 0;

    // 检查是否存在超时错误事件
    const timeoutEvent = useMemo(() => {
        return events.find(event => 
            event.event === 'error' && 
            event.data && 
            typeof event.data.message === 'string' &&
            event.data.message.includes('请求超时')
        );
    }, [events]);

    useEffect(() => {
        if (isActive && mode === "initial") {
            setMode("running");
            setShowModelInfo(false);
        } else if (!isActive && mode === "running" && !hasEvents) {
            // Only switch back to initial if there are no events to display
            setMode("initial");
        }
    }, [isActive, mode, hasEvents]);

    useEffect(() => {
        setNewsText(input);
    }, [input, setNewsText]);

    // Add click outside handler for the model info panel
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (modelInfoRef.current && 
                !modelInfoRef.current.contains(event.target as Node) && 
                showModelInfo) {
                setShowModelInfo(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [showModelInfo]);

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
        // Only reset state if not currently interrupting
        if (status === 'interrupting') {
            // Just update local UI state without resetting the agent state
            // This prevents race conditions with the interruptAgent completion
            setMode("initial");
        } else {
            // Normal case - fully reset the state
            resetState();
        }
    };

    const toggleModelInfo = () => {
        setShowModelInfo(!showModelInfo);
    };

    const onValueChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value);

    // Common container class that maintains consistent width
    const containerClass = mode === "initial" 
        ? "max-w-2xl w-full mx-auto p-4 border-2 border-primary/5 bg-background rounded-3xl"
        : "max-w-2xl w-full mx-auto";

    return (
        <div 
            ref={panelRef}
            className={cn(
                "transition-all duration-500 ease-in-out",
                containerClass,
                // mode === "running" && "fixed bottom-6 left-0 right-0 z-10"
            )}
        >
            {/* Content switcher based on mode */}
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
                    
                    {/* Example News Cards */}
                    <ExampleNewsCards onSelectExample={setInput} />
                </>
            ) : (
                <div className="p-2 bg-background border border-primary/5 rounded-full shadow-sm">
                    {/* 显示超时通知 - 使用绝对定位避免撑开父容器 */}
                    {timeoutEvent && (
                        <div className="absolute left-0 right-0 bottom-full mb-3 max-w-2xl mx-auto p-3 bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-200 rounded-lg border border-amber-300 dark:border-amber-800">
                            <p className="text-sm font-medium">{timeoutEvent.data.message}</p>
                            <p className="text-xs mt-1">请考虑切换至其他模型或重试操作</p>
                        </div>
                    )}
                
                    {showModelInfo && (
                        <div ref={modelInfoRef} className="absolute bottom-full left-0 right-0 mb-3 bg-background/95 backdrop-blur-sm border border-primary/5 rounded-xl p-4 shadow-sm animate-in slide-in-from-bottom duration-300 z-10 max-w-2xl mx-auto">
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
                    <div className="flex justify-between items-center">
                        <Dialog open={showConfig} onOpenChange={setShowConfig}>
                            <DialogTrigger asChild>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="rounded-full flex items-center gap-1 p-2 pl-3"
                                >
                                    {showModelInfo ? (
                                        <ChevronDownIcon className="size-4" />
                                    ) : (
                                        <ChevronUpIcon className="size-4" />
                                    )}
                                    <span className="text-xs">Agent 配置</span>
                                </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-md fixed">
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
                                <ArrowLeftIcon className="size-4 rotate-180" />
                                <span className="text-xs">返回</span>
                            </Button>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}; 