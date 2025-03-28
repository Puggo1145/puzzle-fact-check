'use client';

import React from 'react';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { ModelOption } from '@/lib/store';
import { BrainIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

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
  
  const getProviderBadgeClass = (provider: string) => {
    switch (provider) {
      case 'openai':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'qwen':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'deepseek':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="space-y-1">
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <Select
        value={selectedModelId}
        onValueChange={handleValueChange}
        disabled={disabled}
      >
        <SelectTrigger className="w-full">
          <div className="flex items-center gap-2">
            <BrainIcon className="size-4" />
            {selectedModel && (
              <div className="flex items-center gap-2">
                <span>{selectedModel.name}</span>
                <span className={cn(
                  "text-xs px-1.5 py-0.5 rounded-full border", 
                  getProviderBadgeClass(selectedModel.provider)
                )}>
                  {selectedModel.provider}
                </span>
              </div>
            )}
            {!selectedModel && <SelectValue placeholder="Select model" />}
          </div>
        </SelectTrigger>
        <SelectContent>
          {models.map((model) => (
            <SelectItem key={model.id} value={model.id}>
              <div className="flex items-center justify-between w-full">
                <span>{model.name}</span>
                <span className={cn(
                  "text-xs px-1.5 py-0.5 rounded-full border", 
                  getProviderBadgeClass(model.provider)
                )}>
                  {model.provider}
                </span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}; 