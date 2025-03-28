"use client"

import { SparkleIcon } from "lucide-react"
import { useAgentStore } from "@/lib/store"
import { cn } from "@/lib/utils"

export const Hero = () => {
    const { status, finalReport } = useAgentStore();
    
    // Check if we're in active mode (not idle)
    const isActive = status !== 'idle';
    
    return (
        <div 
            className={cn(
                "relative flex flex-col justify-center transition-all duration-500 ease-in-out mb-8",
                isActive ? "opacity-0 h-0 pointer-events-none" : "opacity-100"
            )}
        >
            <div className="flex flex-col gap-2">
                <h1 className="z-10 text-4xl font-bold font-playfair-display
            bg-linear-to-r from-primary/50 to-primary/80 bg-clip-text text-transparent">
                    Debunk Fake News with Confidence
                </h1>
                <p className="text-muted-foreground text-lg">
                    Let me figure it out for you
                </p>
            </div>
            <SparkleIcon
                fill="currentColor"
                strokeWidth={0}
                className="absolute z-0 size-28 text-muted-foreground/20 
                rotate-[24deg] right-0 bottom-1"
            />
        </div>
    )
}
