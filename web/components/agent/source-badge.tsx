import Link from "next/link";
import { Badge } from "../ui/badge";
import { GlobeIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface SourceBadgeProps {
    source: string;
    label?: string;
    className?: string;
}

export const SourceBadge = ({ 
    source, 
    label,
    className 
}: SourceBadgeProps) => (
    <Link href={source} target="_blank">
        <Badge className={cn("rounded-full bg-gray-800/10 text-black",
            "dark:bg-white/15 dark:text-white hover:bg-black/20 dark:hover:bg-white/30",
            "transition-colors duration-150",
            className
        )}>
            <GlobeIcon className="size-4" />
            {label 
                ? label
                : source.length > 30 
                    ? source.slice(0, 30) + '...' 
                    : source
            }
        </Badge>
    </Link>
);
