import {
    ArrowUpIcon,
    BotIcon,
    ChevronsLeftRightEllipsisIcon,
    BinocularsIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"

export const InputPanel = () => {
    return (
        <div className="max-w-3xl w-full p-4 border-2 border-primary/5 bg-background rounded-4xl">
            <textarea
                placeholder="Tell me what you want to check..."
                className="w-full min-h-20 outline-none resize-none"
            />
            <BottomButtons />
        </div>
    )
}

export const BottomButtons = () => {
    return (
        <div className="w-full flex items-center justify-between gap-2">
            <ModelSelector />
            <Button className="rounded-full" size="icon">
                <ArrowUpIcon strokeWidth={4} className="size-4" />
            </Button>
        </div>
    )
}

export const ModelSelector = () => {
    const searchConfigs = [
        {
            name: "Balance",
            icon: () => <ChevronsLeftRightEllipsisIcon className="size-4" />,
            description: "Fact check with a balance between speed and accuracy.",
        },
        {
            name: "Deeper",
            icon: () => <BinocularsIcon className="size-4" />,
            description: "In-depth fact check by consuming more tokens for search. More accurate but slower and more expensive.",
        },
    ]

    return (
        <Select defaultValue={searchConfigs[0].name}>
            <SelectTrigger className="rounded-full cursor-pointer hover:bg-accent">
                <SelectValue />
            </SelectTrigger>
            <SelectContent className="rounded-xl">
                {searchConfigs.map((searchConfig) => (
                    <SelectItem
                        className="p-3 rounded-lg cursor-pointer"
                        key={searchConfig.name}
                        value={searchConfig.name}
                    >
                        <div className="flex items-center gap-2 mr-2">
                            <searchConfig.icon />
                            <h4 className="text-sm font-medium">{searchConfig.name}</h4>
                        </div>
                    </SelectItem>
                ))}
            </SelectContent>
        </Select>
    )
}
