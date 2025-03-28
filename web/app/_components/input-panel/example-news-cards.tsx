import React from "react";
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
            title: "健康信息",
            text: "每天喝一杯咖啡可以降低40%的心脏病风险，新研究涉及超过 10 万参与者。",
        },
    ];

    return (
        <div className="mt-6 space-y-3">
            <div className="flex items-center gap-2 text-muted-foreground">
                <NewspaperIcon className="size-4" />
                <h3 className="text-sm font-medium">最近新闻</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
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
        </div>
    );
}; 