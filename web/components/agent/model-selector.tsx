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

interface ModelSelectorProps {
  models: ModelOption[];
  selectedModelId: string;
  onModelChange: (modelId: string, provider: string) => void;
  disabled?: boolean;
  label?: string;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  selectedModelId,
  onModelChange,
  disabled = false,
  label = 'Model'
}) => {
  const handleValueChange = (value: string) => {
    const selectedModel = models.find(model => model.id === value);
    if (selectedModel) {
      onModelChange(selectedModel.id, selectedModel.provider);
    }
  };

  const selectedModel = models.find(model => model.id === selectedModelId);
  
  const getProviderBadgeClass: Record<string, string> = {
    openai: 'bg-green-100 text-green-800 border-green-200',
    qwen: 'bg-purple-100 text-purple-800 border-purple-200',
    deepseek: 'bg-blue-100 text-blue-800 border-blue-200',
  };
  const getProviderLabel: Record<string, string> = {
    openai: 'OpenAI',
    qwen: 'Qwen',
    deepseek: 'DeepSeek',
  };

  const getModelTypeLabel: Record<string, string> = {
    reasoning: 'Reasoning',
    non_reasoning: 'Non-Reasoning',
    light: 'Light',
  };

  return (
    <div className="space-y-1">
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
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
                <span>{selectedModel.name}</span>
                <Badge variant="outline" className={getProviderBadgeClass[selectedModel.provider]}>
                  {getProviderLabel[selectedModel.provider]}
                </Badge>
                <Badge variant="outline">
                  {getModelTypeLabel[selectedModel.modelType]}
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
                <span>{model.name}</span>
                <Badge 
                  variant="outline" 
                  className={getProviderBadgeClass[model.provider]}
                >
                  {getProviderLabel[model.provider]}
                </Badge>
                <Badge variant="outline">
                  {getModelTypeLabel[model.modelType]}
                </Badge>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}; 