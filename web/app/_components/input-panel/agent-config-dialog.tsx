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
import { ScrollArea } from "@/components/ui/scroll-area";

interface AgentConfigDialogProps {
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
    mainAgentConfig,
    metadataExtractorConfig,
    searcherConfig,
    setMainAgentConfig,
    setMetadataExtractorConfig,
    setSearcherConfig,
    disabled,
    children
}) => {
    return (
        <Dialog>
            <DialogTrigger asChild>
                {children}
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Settings</DialogTitle>
                    <DialogDescription>
                        Configure the model that is most suitable for your news type.
                    </DialogDescription>
                </DialogHeader>
                <ScrollArea className="h-80 sm:h-fit">
                    <div className="space-y-4 mt-4">
                        <MainAgentConfigPanel
                            config={mainAgentConfig}
                            onChange={setMainAgentConfig}
                            disabled={disabled}
                        />

                        <MetadataExtractorConfigPanel
                            config={metadataExtractorConfig}
                            onChange={setMetadataExtractorConfig}
                            disabled={disabled}
                        />

                        <SearchAgentConfigPanel
                            config={searcherConfig}
                            onChange={setSearcherConfig}
                            disabled={disabled}
                        />
                    </div>
                </ScrollArea>
            </DialogContent>
        </Dialog>
    );
};
