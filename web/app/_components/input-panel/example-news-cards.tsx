import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { NewspaperIcon } from "lucide-react";

// Component to display example news cards
export const ExampleNewsCards = ({ onSelectExample }: { onSelectExample: (text: string) => void }) => {
    const examples = [
        {
            title: "International Politics",
            text: "On April 2, 2025, at 4:00 PM Eastern Time (GMT 20:00), Trump signed an executive order implementing a comprehensive new tariff policy, imposing a minimum 10% tariff on all imported goods from April 5, and higher tariffs on certain countries deemed to be trade \"violators\" starting April 9.",
        },
        {
            title: "Technology News",
            text: "On March 25, 2025, Open AI CEO Sam Altman announced that Open AI will launch a new AI model GPT-5, claiming that the model will achieve AGI.",
        },
        {
            title: "Health and Wellness Rumors",
            text: "There is a rumor circulating on the internet that a cancer survey report claims that Fiji has not had a single case of cancer in the past 40 years, with a population of 900,000.",
        },
        {
            title: "Environment News",
            text: "On March 25, 2025, the National Oceanic and Atmospheric Administration (NOAA) released a report stating that due to global warming, the Arctic ice cap may completely disappear by 2030.",
        },
    ];

    return (
        <div className="mt-6 space-y-3">
            <div className="flex items-center gap-2 text-muted-foreground">
                <NewspaperIcon className="size-4" />
                <h3 className="text-sm font-medium">Try these examples</h3>
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