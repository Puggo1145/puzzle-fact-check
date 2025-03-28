import React from "react";

// Component to display model information
export const ModelInfoItem = ({ 
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