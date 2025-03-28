import { Sparkle } from "lucide-react"

interface ILogoProps {
    showText?: boolean
}

export const Logo = ({ showText = true }: ILogoProps) => {
  return (
    <div className="flex items-center gap-2">
        <Sparkle 
            fill="currentColor" 
            strokeWidth={0} 
            className="size-8 text-primary/30 rotate-[24deg]" 
        />
        {showText && (
            <h1 className="text-2xl text-primary/30 font-bold">
                Puzzle Fact Check (Experimental)
            </h1>
        )}
    </div>
  )
}
