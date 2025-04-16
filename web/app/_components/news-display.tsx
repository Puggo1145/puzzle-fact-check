"use client"

import { useAgentStore } from "@/stores/use-agent-store";
import { Loader2, CheckCircle2, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";
import React from "react";

export const NewsDisplay = () => {
    const { newsText, status, result } = useAgentStore();

    if (status === 'idle' && !result.report) return null;

    // Calculate status display values based on current status
    let StatusIcon: LucideIcon;
    let statusText: string;
    let statusColor: string;

    // When completed and has a verdict, show the verdict badge
    // Otherwise show status as before
    switch (status) {
        case 'running':
            StatusIcon = Loader2;
            statusText = "正在核查中，请稍等片刻";
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
            statusText = "核查完成";
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