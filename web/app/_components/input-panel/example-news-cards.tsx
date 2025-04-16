import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { NewspaperIcon } from "lucide-react";

// Component to display example news cards
export const ExampleNewsCards = ({ onSelectExample }: { onSelectExample: (text: string) => void }) => {
    const examples = [
        {
            title: "国际政治",
            text: "美国东部时间4月2日下午4时（格林尼治标准时间20：00），特朗普签署行政令执行全面新对等关税政策，从4月5日起对所有进口美国商品征收至少10%的关税，并从4月9日起对一些被视为贸易“违规严重国”征收更高关税。",
        },
        {
            title: "科技新闻",
            text: "Open AI CEO 在 2025年3月25日宣布，Open AI 将推出新的 AI 模型 GPT-5，称该模型将实现 AGI",
        },
        {
            title: "健康养生传言",
            text: "有网络流传说法称，一份癌症调查报告宣称斐济从1971年至2010年这40年间，全国90万人，无人患癌",
        },
        {
            title: "环境新闻",
            text: "2025年3月25日，美国国家海洋和大气管理局（NOAA）发布报告称，由于全球变暖，北极冰川可能在2030年完全消失。",
        },
    ];

    return (
        <div className="mt-6 space-y-3">
            <div className="flex items-center gap-2 text-muted-foreground">
                <NewspaperIcon className="size-4" />
                <h3 className="text-sm font-medium">尝试这些案例</h3>
            </div>
            <ScrollArea className="h-36 md:h-fit">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {examples.map((example, index) => (
                        <div
                            key={index}
                            className="p-3 border border-primary/10 rounded-lg cursor-pointer hover:bg-accent/50 transition-colors"
                            onClick={() => onSelectExample(example.text)}
                        >
                            <h4 className="text-sm font-medium mb-1">{example.title}</h4>
                            <p className="text-xs text-muted-foreground line-clamp-2">{example.text}</p>
                        </div>
                    ))}
                </div>
                <ScrollBar orientation="horizontal" />
            </ScrollArea>
        </div>
    );
}; 