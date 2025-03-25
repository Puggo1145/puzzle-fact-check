import { SparkleIcon } from "lucide-react"

export const Hero = () => {
    return (
        <div className="relative h-24 flex flex-col justify-center">
            <div className="flex flex-col gap-2">
                <h1 className="z-10 text-4xl font-bold font-playfair-display
            bg-linear-to-r from-primary/50 to-primary/80 bg-clip-text text-transparent">
                    Debunk Fake News with Confidence
                </h1>
                <p className="text-muted-foreground">
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
