"use client"

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { 
    MainAgentConfigPanel, 
    MetadataExtractorConfigPanel, 
    SearchAgentConfigPanel 
} from "@/components/agent/agent-config";
import type { 
    MainAgentConfig,
    MetadataExtractorConfig, 
    SearchAgentConfig,
    ModelOption 
} from "@/constants/agent-default-config";

interface AgentConfigDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    mainAgentConfig: MainAgentConfig;
    metadataExtractorConfig: MetadataExtractorConfig;
    searcherConfig: SearchAgentConfig;
    availableModels: ModelOption[];
    setMainAgentConfig: (config: Partial<MainAgentConfig>) => void;
    setMetadataExtractorConfig: (config: Partial<MetadataExtractorConfig>) => void;
    setSearcherConfig: (config: Partial<SearchAgentConfig>) => void;
    disabled: boolean;
    children: React.ReactNode;
}

export const AgentConfigDialog: React.FC<AgentConfigDialogProps> = ({
    open,
    onOpenChange,
    mainAgentConfig,
    metadataExtractorConfig,
    searcherConfig,
    availableModels,
    setMainAgentConfig,
    setMetadataExtractorConfig,
    setSearcherConfig,
    disabled,
    children
}) => {
    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogTrigger asChild>
                {children}
            </DialogTrigger>
            <DialogContent className="max-w-md">
                <DialogHeader>
                    <DialogTitle>Agent 配置</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                    <MainAgentConfigPanel
                        config={mainAgentConfig}
                        availableModels={availableModels}
                        onChange={setMainAgentConfig}
                        disabled={disabled}
                    />
                    
                    <MetadataExtractorConfigPanel
                        config={metadataExtractorConfig}
                        availableModels={availableModels}
                        onChange={setMetadataExtractorConfig}
                        disabled={disabled}
                    />
                    
                    <SearchAgentConfigPanel
                        config={searcherConfig}
                        availableModels={availableModels}
                        onChange={setSearcherConfig}
                        disabled={disabled}
                    />
                </div>
            </DialogContent>
        </Dialog>
    );
};
