import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { NewspaperIcon } from "lucide-react";

// Component to display example news cards
export const ExampleNewsCards = ({ onSelectExample }: { onSelectExample: (text: string) => void }) => {
    const examples = [
        {
            title: "国际政治",
            text: "最近有网络流传说法称，2025 年初，美国共和党议员Riley Moore通过了一项新法案，将禁止中国公民以学生身份来美国。这项法案会导致每年大约30万中国学生将无法获得F、J、M类签证，从而无法到美国学习或参与学术交流。",
        },
        {
            title: "科技新闻",
            text: "Open AI CEO 在 2025 年 3 月 25 日宣布，Open AI 将推出新的 AI 模型 GPT-5，称该模型将实现 AGI",
        },
        {
            title: "环境新闻",
            text: "2025 年 3 月 25 日，美国国家海洋和大气管理局（NOAA）发布报告称，由于全球变暖，北极冰川可能在2030年完全消失。",
        },
        {
            title: "亲友群经典健康养生传言",
            text: "有网络流传说法称，一份癌症调查报告宣称斐济从1971年至2010年这40年间，全国90万人，无人患癌",
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