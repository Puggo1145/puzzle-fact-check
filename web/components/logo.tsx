import { Sparkle } from "lucide-react"
import { Badge } from "@/components/ui/badge"

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
                <div className="flex items-center gap-2">
                    <h1 className="text-xl text-primary/30 font-bold">
                        Puzzle Fact Check
                    </h1>
                    <Badge variant="outline">Early Preview</Badge>
                </div>
            )}
        </div>
    )
}
