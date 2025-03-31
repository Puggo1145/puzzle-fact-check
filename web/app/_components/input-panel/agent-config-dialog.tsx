"use client"

import type { 
    MainAgentConfig,
    MetadataExtractorConfig, 
    SearchAgentConfig,
    ModelOption,
} from "@/constants/agent-default-config";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogTrigger,
} from "@/components/ui/dialog";
import { 
    MainAgentConfigPanel, 
    MetadataExtractorConfigPanel, 
    SearchAgentConfigPanel
} from "@/components/agent/agent-config";

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
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>高级配置</DialogTitle>
                    <DialogDescription>
                        Puzzle 是个人早期实验项目，所有成本均由个人承担，请大家在选择模型的时候手下留情，使用最适合自己新闻类型的模型组合就好了。无需一味追求推理模型，非推理模型在事实核查任务中的表现也还不错哦！😘
                    </DialogDescription>
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
