import { PencilRulerIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { tools } from "@/constants/tools";

export const ToolSelector = ({
    selectedTools,
    setSelectedTools,
}: {
    selectedTools: string[];
    setSelectedTools: (tools: string[]) => void;
}) => {
    const handleToolSelect = (toolId: string) => {
        // Don't allow selection of tools in development
        const tool = tools.find(t => t.id === toolId);
        if (!tool || tool.available) return;

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
        <div className="relative">
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <Button
                        variant="outline"
                        size="sm"
                        className="rounded-full hover:bg-accent flex items-center gap-1"
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
                            <>
                                <PencilRulerIcon className="size-4" />
                                <span className="hidden lg:block text-xs font-medium">Advanced Tools</span>
                            </>
                        )}
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-52 md:w-60 lg:w-fit">
                    {tools.map((tool) => {
                        const isSelected = selectedTools.includes(tool.id);
                        return (
                            <DropdownMenuItem
                                key={tool.id}
                                onClick={() => handleToolSelect(tool.id)}
                                className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors ${tool.available
                                        ? 'opacity-60 hover:bg-accent/20'
                                        : `hover:bg-accent/50 ${isSelected ? 'bg-accent/30' : ''}`
                                    }`}
                                disabled={tool.available}
                            >
                                <div className="mt-0.5 relative">
                                    {isSelected && !tool.available && (
                                        <div className="absolute -right-1 -top-1 w-3 h-3 bg-primary rounded-full border-2 border-background" />
                                    )}
                                    <tool.icon />
                                </div>
                                <div>
                                    <div className="flex items-center gap-2">
                                        <h4 className="text-sm font-medium">{tool.name}</h4>
                                        {tool.available && (
                                            <span className="text-[10px] bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 px-1.5 py-0.5 rounded-full">
                                                Comming Soon
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-xs text-muted-foreground">{tool.description}</p>
                                </div>
                            </DropdownMenuItem>
                        );
                    })}
                </DropdownMenuContent>
            </DropdownMenu>
        </div>
    );
}; 