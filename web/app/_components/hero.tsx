import type { ComponentProps } from "react"
import { SparkleIcon } from "lucide-react"
import { cn } from "@/lib/utils"

export const Hero = ({ className, ...props }: ComponentProps<"div">) => {
    return (
        <div 
            className={cn(
                "relative flex flex-col justify-center transition-all duration-300 ease-out",
                className
            )}
            {...props}
        >
            <div className="w-full flex justify-center mb-4">
            </div>
            <div className="ml-3 flex flex-col gap-2">
                <h1 className="z-10 text-3xl lg:text-4xl font-bold font-playfair-display
                bg-linear-to-r from-primary/50 to-primary/80 bg-clip-text text-transparent
                dark:from-primary/70 dark:to-primary">
                    Debunk Fake News with Confidence
                </h1>
                <p className="text-muted-foreground text-base md:text-lg">
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
