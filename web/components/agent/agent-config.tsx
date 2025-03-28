'use client';

import React from 'react';
import { ModelSelector } from './model-selector';
import { NumberInput } from './number-input';
import type { AgentConfig, ModelOption } from '@/lib/store';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { BotIcon, SearchIcon, InfoIcon } from 'lucide-react';

interface AgentConfigProps {
  agentType: 'main' | 'metadata' | 'searcher';
  config: AgentConfig;
  availableModels: ModelOption[];
  onChange: (updatedConfig: Partial<AgentConfig>) => void;
  disabled?: boolean;
}

const agentIcons = {
  main: BotIcon,
  metadata: InfoIcon,
  searcher: SearchIcon
};

const agentLabels = {
  main: '主智能体',
  metadata: '新闻元数据提取器',
  searcher: '检索智能体'
};

const agentDescriptions = {
  main: '负责协调整个事实核查的流程',
  metadata: '负责提取信息中的关键元数据',
  searcher: '负责搜索和验证信息'
};

export const AgentConfigPanel: React.FC<AgentConfigProps> = ({
  agentType,
  config,
  availableModels,
  onChange,
  disabled = false
}) => {
  const Icon = agentIcons[agentType];
  const label = agentLabels[agentType];
  const description = agentDescriptions[agentType];

  const handleModelChange = (modelId: string, provider: string) => {
    onChange({
      modelName: modelId,
      modelProvider: provider
    });
  };

  const handleMaxRetriesChange = (value: number) => {
    onChange({ maxRetries: value });
  };

  const handleMaxSearchTokensChange = (value: number) => {
    onChange({ maxSearchTokens: value });
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <Icon className="size-5" />
          {label}
          <span className="font-normal text-xs text-muted-foreground">
            {description}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <ModelSelector
            models={availableModels}
            selectedModelId={config.modelName}
            onModelChange={handleModelChange}
            disabled={disabled}
            label={`${label}模型选择`}
          />
          
          <div className="grid grid-cols-2 gap-2">
            {agentType === 'main' && (
              <NumberInput
                value={config.maxRetries}
                onChange={handleMaxRetriesChange}
                min={1}
                max={10}
                step={1}
                disabled={disabled}
                label="最大重试次数"
              />
            )}
            
            {agentType === 'searcher' && (
              <>
                <NumberInput
                  value={config.maxSearchTokens}
                  onChange={handleMaxSearchTokensChange}
                  min={1000}
                  max={100000}
                  step={1000}
                  disabled={disabled}
                  label="最大搜索 token 数"
                />
              </>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 