import { SparkleIcon } from "lucide-react"

export const Hero = () => {
    return (
        <div className="relative h-24 flex flex-col justify-center">
            <h1 className="z-10 text-3xl font-bold font-playfair-display text-primary">
                Debunk Fake News with Confidence
            </h1>
            <SparkleIcon 
                fill="currentColor" 
                strokeWidth={0}
                className="absolute z-0 size-28 text-muted-foreground/20 
                rotate-[24deg] right-0 bottom-1"
            />
        </div>
    )
}
