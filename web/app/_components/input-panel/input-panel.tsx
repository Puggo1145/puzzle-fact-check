"use client"

import {
    useState,
    useMemo,
} from "react";
// icons
import {
    ArrowLeftIcon,
    ArrowUpIcon,
    CogIcon,
    StopCircleIcon,
} from "lucide-react";
// ui
import { Button } from "@/components/ui/button";
// components
import { ToolSelector } from "./tool-selector";
import { ExampleNewsCards } from "./example-news-cards";
import { AgentConfigDialog } from "./agent-config-dialog";
// stores
import { useAgentStore } from "@/stores/use-agent-store";
// utils
import { cn } from "@/lib/utils";

export const InputPanel = () => {
    const {
        status,
        resetState,
        newsText,
        setNewsText,
        interruptAgent,
        createAndRunAgent,
        mainAgentConfig,
        metadataExtractorConfig,
        searcherConfig,
        availableModels,
        setMainAgentConfig,
        setMetadataExtractorConfig,
        setSearcherConfig,
        selectedTools,
        setSelectedTools
    } = useAgentStore();

    const hasNewsText = useMemo(() => newsText.trim() !== "", [newsText]);
    const [showTools, setShowTools] = useState(false);
    const [showAgentConfig, setShowAgentConfig] = useState(false);

    const IDLE = useMemo(() => status === 'idle', [status]);
    const RUNNING = useMemo(() => status === 'running', [status]);
    const INTERRUPTING = useMemo(() => status === 'interrupting', [status]);
    const INTERRUPTED = useMemo(() => status === 'interrupted', [status]);
    const COMPLETED = useMemo(() => status === 'completed', [status]);

    const handleRunAgent = async () => {
        if (!hasNewsText) return;
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

    const onValueChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => setNewsText(e.target.value);

    return (
        <div className={cn(
            "transition-all duration-500 ease-in-out", 
            "w-full border-2 border-primary/5 bg-background p-4 mx-auto",
            IDLE ? "max-w-2xl rounded-3xl" : "max-w-md rounded-4xl"
        )}>
            {IDLE &&
                <textarea
                    value={newsText}
                    onChange={onValueChange}
                    placeholder="告诉我你想核查的新闻..."
                    className="w-full min-h-20 px-1 outline-none resize-none"
                />}
            <div className="w-full flex items-center justify-between gap-2">
                {/* 左侧 configs */}
                <div className="flex items-center gap-2">
                    <AgentConfigDialog
                        open={showAgentConfig}
                        onOpenChange={setShowAgentConfig}
                        mainAgentConfig={mainAgentConfig}
                        metadataExtractorConfig={metadataExtractorConfig}
                        searcherConfig={searcherConfig}
                        availableModels={availableModels}
                        setMainAgentConfig={setMainAgentConfig}
                        setMetadataExtractorConfig={setMetadataExtractorConfig}
                        setSearcherConfig={setSearcherConfig}
                        disabled={!IDLE}
                    >
                        <Button
                            variant="outline"
                            size="sm"
                            className="rounded-full flex items-center gap-1"
                        >
                            <CogIcon className="size-4" />
                            <span className="text-xs">Agent 配置</span>
                        </Button>
                    </AgentConfigDialog>

                    {IDLE &&
                        <ToolSelector
                            selectedTools={selectedTools}
                            setSelectedTools={setSelectedTools}
                            showTools={showTools}
                            setShowTools={setShowTools}
                        />}
                </div>
                {/* 右侧 buttons */}
                {IDLE &&
                    <Button
                        className="rounded-full"
                        size="icon"
                        disabled={!hasNewsText}
                        onClick={handleRunAgent}
                    >
                        <ArrowUpIcon strokeWidth={2} className="size-4" />
                    </Button>
                }
                {RUNNING &&
                    <Button
                        variant="destructive"
                        onClick={handleInterrupt}
                        disabled={INTERRUPTING}
                        className="rounded-full flex items-center gap-1"
                        size="sm"
                    >
                        <StopCircleIcon className="size-4" />
                        <span className="text-xs">
                            {INTERRUPTING ? '正在中断' : '中断'}
                        </span>
                    </Button>
                }
                {(INTERRUPTED || COMPLETED) &&
                    <Button
                        variant="outline"
                        onClick={resetState}
                        className="rounded-full flex items-center gap-1"
                        size="sm"
                    >
                        <ArrowLeftIcon className="size-4 rotate-180" />
                        <span className="text-xs">返回</span>
                    </Button>
                }
            </div>

            {IDLE && <ExampleNewsCards onSelectExample={setNewsText} />}
        </div>
    );
};
