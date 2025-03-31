'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ChevronDownIcon } from 'lucide-react';
import { CONFIG_PRESETS, type ConfigPreset } from '@/constants/agent-default-config';


interface QuickConfigSelectorProps {
    onApplyPreset: (preset: ConfigPreset) => void;
    disabled?: boolean;
    className?: string;
}

export const QuickConfigSelector: React.FC<QuickConfigSelectorProps> = ({
    onApplyPreset,
    disabled = false,
    className = '',
}) => {
    const [activePreset, setActivePreset] = useState<ConfigPreset>(CONFIG_PRESETS[1]); // 默认选择标准模式

    const handleSelectPreset = (preset: ConfigPreset) => {
        setActivePreset(preset);
        onApplyPreset(preset);
    };

    return (
        <div className={`flex items-center ${className}`}>
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <Button
                        variant="ghost"
                        size="sm"
                        className="flex items-center gap-1 rounded-full"
                        disabled={disabled}
                        onClick={() => handleSelectPreset(activePreset)}
                    >
                        <activePreset.icon className="size-4" />
                        <span className="text-xs">{activePreset.name}</span>
                        <ChevronDownIcon className="size-4" />
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                    {CONFIG_PRESETS.map((preset) => (
                        <DropdownMenuItem
                            key={preset.id}
                            onClick={() => handleSelectPreset(preset)}
                            className="flex items-center gap-2 cursor-pointer p-3"
                        >
                            <preset.icon className="size-4" />
                            <div className="flex flex-col">
                                <h4 className="text-sm font-medium">{preset.name}</h4>
                                <p className="text-xs text-muted-foreground">{preset.description}</p>
                            </div>
                        </DropdownMenuItem>
                    ))}
                </DropdownMenuContent>
            </DropdownMenu>
        </div>
    );
}; 