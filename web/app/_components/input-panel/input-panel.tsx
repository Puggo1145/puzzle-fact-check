"use client"

import type { ConfigPreset } from "@/constants/agent-default-config";
import { useState } from "react";
// icons
import {
    ArrowLeftIcon,
    ArrowUpIcon,
    CogIcon,
    StopCircleIcon,
} from "lucide-react";
// ui
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
// components
import { ToolSelector } from "./tool-selector";
import { ExampleNewsCards } from "./example-news-cards";
import { AgentConfigDialog } from "./agent-config-dialog";
import { QuickConfigSelector } from "@/components/agent/quick-config-selector";
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

    const hasNewsText = newsText.trim() !== "";
    const IDLE = status === 'idle';
    const RUNNING = status === 'running';
    const INTERRUPTING = status === 'interrupting';
    const INTERRUPTED = status === 'interrupted';
    const COMPLETED = status === 'completed';

    const [showConfirmDialog, setShowConfirmDialog] = useState(false);

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

    const handleApplyPreset = (preset: ConfigPreset) => {
        setMainAgentConfig(preset.mainConfig);
        setMetadataExtractorConfig(preset.metadataConfig);
        setSearcherConfig(preset.searchConfig);
    };
    
    const handleReset = () => {
        setShowConfirmDialog(false);
        resetState();
    };

    return (
        <div className={cn(
            "transition-all duration-300 ease-in-out", 
            "w-full border-2 border-primary/5 bg-background p-4 mx-auto",
            IDLE ? "max-w-2xl rounded-3xl" : "max-w-md rounded-4xl"
        )}>
            {IDLE &&
                <textarea
                    value={newsText}
                    onChange={onValueChange}
                    placeholder="Tell me the news you want to check. We care about what you believe"
                    className="w-full h-36 sm:h-20 px-1 outline-none resize-none"
                />}
            <div className="w-full flex items-center justify-between gap-2">
                {/* 左侧 configs */}
                <div className="flex items-center gap-2">
                    {IDLE && 
                        <QuickConfigSelector 
                            onApplyPreset={handleApplyPreset}
                            disabled={!IDLE}
                        />
                    }
                    {IDLE &&
                        <ToolSelector
                            selectedTools={selectedTools}
                            setSelectedTools={setSelectedTools}
                        />
                    }
                    <AgentConfigDialog
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
                            <span className="hidden lg:block text-xs">Settings</span>
                        </Button>
                    </AgentConfigDialog>
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
                            {INTERRUPTING ? 'Interrupting' : 'Interrupt'}
                        </span>
                    </Button>
                }
                {(INTERRUPTED || COMPLETED) &&
                    <Button
                        variant="outline"
                        onClick={() => setShowConfirmDialog(true)}
                        className="rounded-full flex items-center gap-1"
                        size="sm"
                    >
                        <ArrowLeftIcon className="size-4 rotate-180" />
                        <span className="text-xs">Back</span>
                    </Button>
                }
            </div>

            {IDLE && <ExampleNewsCards onSelectExample={setNewsText} />}

            <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Are you sure?</DialogTitle>
                        <DialogDescription>
                            Puzzle does not support saving your fact-checking results currently. You will lose all executed steps. Make sure you saved the results before going back.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter className="mt-4">
                        <Button variant="outline" onClick={() => setShowConfirmDialog(false)}>
                            Cancel
                        </Button>
                        <Button onClick={handleReset}>
                            Confirm
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
};
