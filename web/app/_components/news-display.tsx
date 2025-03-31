"use client"

import { useAgentStore } from "@/stores/use-agent-store";
import { Loader2, CheckCircle2, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

export const NewsDisplay = () => {
    const { newsText, status, finalReport } = useAgentStore();

    // Only hide this component when we're in idle state with no report
    if (status === 'idle' && !finalReport) return null;

    // Choose the appropriate icon and status text based on the current status
    let StatusIcon;
    let statusText;
    let statusColor;

    switch (status) {
        case 'running':
            StatusIcon = Loader2;
            statusText = "正在核查中（核查期间请勿关闭页面）";
            statusColor = "text-primary animate-spin";
            break;
        case 'interrupting':
            StatusIcon = Loader2;
            statusText = "正在中断...";
            statusColor = "text-primary animate-spin";
            break;
        case 'interrupted':
            StatusIcon = AlertTriangle;
            statusText = "核查已中断";
            statusColor = "text-amber-500";
            break;
        case 'completed':
            StatusIcon = CheckCircle2;
            statusText = "核查结束";
            statusColor = "text-green-500";
            break;
        default:
            StatusIcon = CheckCircle2;
            statusText = "核查结束";
            statusColor = "text-green-500";
    }

    return (
        <div className="w-full bg-muted-foreground/5 rounded-xl p-6 animate-in fade-in slide-in-from-top-4 duration-500">
            <div className="flex items-center gap-2 mb-2">
                <StatusIcon className={cn("size-4", statusColor)} />
                <h2 className="font-medium">
                    {statusText}
                </h2>
            </div>
            <p className="text-sm text-muted-foreground whitespace-pre-line line-clamp-1">
                {newsText}
            </p>
        </div>
    );
}; 