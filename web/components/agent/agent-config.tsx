'use client';

import React, { useMemo } from 'react';
import { ModelSelector } from './model-selector';
import { NumberInput } from './number-input';
import type { ModelOption } from '@/constants/agent-default-config';
import type { 
  MainAgentConfig,
  MetadataExtractorConfig,
  SearchAgentConfig
} from '@/constants/agent-default-config';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { BotIcon, SearchIcon, InfoIcon } from 'lucide-react';

interface AgentConfigProps {
  agentType: 'main' | 'metadata' | 'searcher';
  config: MainAgentConfig | MetadataExtractorConfig | SearchAgentConfig;
  availableModels: ModelOption[];
  onChange: (updatedConfig: Partial<MainAgentConfig | MetadataExtractorConfig | SearchAgentConfig>) => void;
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

// 模型限制说明
const modelRestrictionTexts = {
  main: '主智能体不支持 GPT-4o Mini 和 Qwen Turbo 等轻量级模型',
  metadata: '元数据提取器不支持 DeepSeek R1 和 QWQ Plus Latest 等推理模型',
  searcher: '搜索智能体不支持 GPT-4o Mini 和 Qwen Turbo 等轻量级模型'
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
  const restrictionText = modelRestrictionTexts[agentType];

  // Filter available models based on agent type
  const filteredModels = useMemo(() => {
    if (agentType === 'metadata') {
      // Metadata extractor can't use deepseek-reasoner and qwq-plus-latest
      return availableModels.filter(model => 
        !(model.id === 'deepseek-reasoner' || model.id === 'qwq-plus-latest')
      );
    } else {
      // Main agent and searcher can't use gpt-4o-mini, qwen-turbo
      return availableModels.filter(model => 
        !(model.id === 'gpt-4o-mini' || model.id === 'qwen-turbo')
      );
    }
  }, [availableModels, agentType]);

  const handleModelChange = (modelId: string, provider: string) => {
    onChange({
      modelName: modelId,
      modelProvider: provider
    });
  };

  const handleMaxRetriesChange = (value: number) => {
    if (agentType === 'main') {
      onChange({ maxRetries: value } as Partial<MainAgentConfig>);
    }
  };

  const handleMaxSearchTokensChange = (value: number) => {
    if (agentType === 'searcher') {
      onChange({ maxSearchTokens: value } as Partial<SearchAgentConfig>);
    }
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
        <CardDescription className="text-xs text-muted-foreground mt-1">
          {restrictionText}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <ModelSelector
            models={filteredModels}
            selectedModelId={config.modelName}
            onModelChange={handleModelChange}
            disabled={disabled}
            label={`${label}模型选择`}
          />
          
          <div className="grid grid-cols-2 gap-2">
            {agentType === 'main' && (
              <NumberInput
                value={(config as MainAgentConfig).maxRetries ?? 3}
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
                  value={(config as SearchAgentConfig).maxSearchTokens ?? 10000}
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