'use client';

import React from 'react';
// ui
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
// constants
import { ModelOption } from '@/constants/agent-default-config';
// icons
import { BrainIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ModelSelectorProps {
  models: ModelOption[];
  selectedModelId: string;
  onModelChange: (id: string, model: string, provider: string) => void;
  disabled?: boolean;
  label?: string;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  selectedModelId,
  onModelChange,
  disabled = false,
}) => {
  const handleValueChange = (value: string) => {
    const selectedModel = models.find(model => model.id === value);
    if (selectedModel) {
      onModelChange(selectedModel.id, selectedModel.model, selectedModel.provider);
    }
  };

  const selectedModel = models.find(model => model.id === selectedModelId);

  const providerBadgeClass: Record<string, string> = {
    openai: 'bg-green-100 text-green-800 border-green-200',
    qwen: 'bg-purple-100 text-purple-800 border-purple-200',
    deepseek: 'bg-blue-100 text-blue-800 border-blue-200',
    openai_third_party: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  };
  const providerLabel: Record<string, string> = {
    openai: 'OpenAI',
    qwen: 'Qwen',
    deepseek: 'DeepSeek',
    openai_third_party: 'Third Party',
  };

  const modelTypeLabel: Record<string, string> = {
    reasoning: 'Reasoning',
    non_reasoning: 'Non-Reasoning',
    light: 'Light',
  };

  return (
    <div className="space-y-1">
      <Select
        value={selectedModelId}
        onValueChange={handleValueChange}
        disabled={disabled}
      >
        <SelectTrigger className="w-full cursor-pointer hover:bg-muted-foreground/5">
          <div className="flex items-center gap-2">
            <BrainIcon className="size-4" />
            {selectedModel && (
              <div className="flex items-center gap-2">
                <span>{selectedModel.alias}</span>
                <Badge
                  variant="outline"
                  className={cn(
                    providerBadgeClass[selectedModel.provider],
                    "rounded-full"
                  )}
                >
                  {providerLabel[selectedModel.provider]}
                </Badge>
                <Badge
                  variant="outline"
                  className="rounded-full"
                >
                  {modelTypeLabel[selectedModel.modelType]}
                </Badge>
              </div>
            )}
            {!selectedModel && <SelectValue placeholder="Select model" />}
          </div>
        </SelectTrigger>
        <SelectContent>
          {models.map((model) => (
            <SelectItem
              key={model.id}
              value={model.id}
              className="cursor-pointer hover:bg-muted-foreground/5"
            >
              <div className="flex items-center justify-between w-full gap-2">
                <span>{model.alias}</span>
                <Badge
                  variant="outline"
                  className={cn(
                    providerBadgeClass[model.provider],
                    "rounded-full"
                  )}
                >
                  {providerLabel[model.provider]}
                </Badge>
                <Badge
                  variant="outline"
                  className="rounded-full"
                >
                  {modelTypeLabel[model.modelType]}
                </Badge>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}; 