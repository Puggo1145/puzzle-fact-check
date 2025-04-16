'use client';

import React, { useMemo } from 'react';
import { ModelSelector } from './model-selector';
import { NumberInput } from './number-input';
import type { ModelOption } from '@/constants/agent-default-config';
import type {
  MainAgentConfig,
  MetadataExtractorConfig,
  SearchAgentConfig,
} from '@/constants/agent-default-config';
import { MAIN_AGENT_MODELS, SEARCH_AGENT_MODELS, METADATA_EXTRACTOR_MODELS } from '@/constants/agent-default-config';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { BotIcon, SearchIcon, InfoIcon } from 'lucide-react';

// Base shared interface for agent config props
interface BaseAgentConfigProps {
  label: string;
  description: string;
  restrictionText: string;
  icon: React.FC<React.SVGProps<SVGSVGElement>>;
  disabled?: boolean;
  children: React.ReactNode;
}

// Base AgentConfigPanel component
export const AgentConfigPanel: React.FC<BaseAgentConfigProps> = ({
  label,
  description,
  restrictionText,
  icon: Icon,
  children
}) => {
  return (
    <Card className='gap-2'>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <Icon className="size-5" />
          {label}
        </CardTitle>
        <CardDescription className="text-xs text-muted-foreground mt-1">
          <p className="font-normal text-xs text-muted-foreground">
            {description}
          </p>
          <p className="font-normal text-xs text-muted-foreground">
            {restrictionText}
          </p>
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {children}
        </div>
      </CardContent>
    </Card>
  );
};

// Specialized MainAgentConfig component
interface MainAgentConfigProps {
  config: MainAgentConfig;
  onChange: (updatedConfig: Partial<MainAgentConfig>) => void;
  disabled?: boolean;
}

export const MainAgentConfigPanel: React.FC<MainAgentConfigProps> = ({
  config,
  onChange,
  disabled = false
}) => {
  const handleModelChange = (modelId: string, modelName: string, provider: string) => {
    onChange({
      modelId: modelId,
      modelName: modelName,
      modelProvider: provider
    });
  };

  const handleMaxRetriesChange = (value: number) => {
    onChange({ maxRetries: value });
  };

  return (
    <AgentConfigPanel
      label="主智能体"
      description="负责协调整个事实核查的流程"
      restrictionText="不支持轻量模型（Light）"
      icon={BotIcon}
      disabled={disabled}
    >
      <ModelSelector
        models={MAIN_AGENT_MODELS}
        selectedModelId={config.modelId}
        onModelChange={handleModelChange}
        disabled={disabled}
      />

      <NumberInput
        value={config.maxRetries ?? 3}
        onChange={handleMaxRetriesChange}
        min={1}
        max={3}
        step={1}
        disabled={disabled}
        label="每个检索 Agent 允许重试检索的最大次数"
      />
    </AgentConfigPanel>
  );
};

// Specialized MetadataExtractorConfig component
interface MetadataExtractorConfigProps {
  config: MetadataExtractorConfig;
  onChange: (updatedConfig: Partial<MetadataExtractorConfig>) => void;
  disabled?: boolean;
}

export const MetadataExtractorConfigPanel: React.FC<MetadataExtractorConfigProps> = ({
  config,
  onChange,
  disabled = false
}) => {
  const handleModelChange = (modelId: string, modelName: string, provider: string) => {
    onChange({
      modelId: modelId,
      modelName: modelName,
      modelProvider: provider
    });
  };

  return (
    <AgentConfigPanel
      label="元数据提取智能体"
      description="负责提取新闻中的关键元数据"
      restrictionText=""
      icon={InfoIcon}
      disabled={disabled}
    >
      <ModelSelector
        models={METADATA_EXTRACTOR_MODELS}
        selectedModelId={config.modelId}
        onModelChange={handleModelChange}
        disabled={disabled}
      />
    </AgentConfigPanel>
  );
};

// Specialized SearchAgentConfig component
interface SearchAgentConfigProps {
  config: SearchAgentConfig;
  onChange: (updatedConfig: Partial<SearchAgentConfig>) => void;
  disabled?: boolean;
}

export const SearchAgentConfigPanel: React.FC<SearchAgentConfigProps> = ({
  config,
  onChange,
  disabled = false
}) => {
  const handleModelChange = (modelId: string, modelName: string, provider: string) => {
    onChange({
      modelId: modelId,
      modelName: modelName,
      modelProvider: provider
    });
  };

  const handleMaxSearchTokensChange = (value: number) => {
    onChange({ maxSearchTokens: value });
  };

  return (
    <AgentConfigPanel
      label="检索智能体"
      description="负责进行深度搜索"
      restrictionText="不支持轻量模型（Light）"
      icon={SearchIcon}
      disabled={disabled}
    >
      <ModelSelector
        models={SEARCH_AGENT_MODELS}
        selectedModelId={config.modelId}
        onModelChange={handleModelChange}
        disabled={disabled}
      />

      <NumberInput
        value={config.maxSearchTokens ?? 10000}
        onChange={handleMaxSearchTokensChange}
        min={5000}
        max={30000}
        step={1000}
        disabled={disabled}
        label="每个检索 Agent 允许消耗的最大 token 数"
      />
    </AgentConfigPanel>
  );
}; 