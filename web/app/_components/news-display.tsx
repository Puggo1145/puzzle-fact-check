"use client"

import { useAgentStore } from "@/lib/store";
import { Loader2, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

export const NewsDisplay = () => {
    const { newsText, isRunning, finalReport, isInterrupting } = useAgentStore();

    if (!isRunning && !finalReport) return null;

    let StatusIcon = isRunning ? Loader2 : CheckCircle2;
    let statusText = isRunning 
        ? isInterrupting 
            ? "正在中断..." 
            : "正在核查中..." 
        : "核查完成";

    return (
        <div className="w-full bg-muted/30 rounded-xl p-6 mb-6 animate-in fade-in slide-in-from-top-4 duration-500">
            <div className="flex items-center gap-2 mb-2">
                <StatusIcon className={cn(
                    "size-4", 
                    isRunning ? "text-primary animate-spin" : "text-green-500"
                )} />
                <h2 className="font-medium">
                    {statusText}
                </h2>
            </div>
            <p className="text-sm text-muted-foreground whitespace-pre-line">
                {newsText}
            </p>
        </div>
    );
}; 