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
          {children}
        </div>
      </CardContent>
    </Card>
  );
};

// Specialized MainAgentConfig component
interface MainAgentConfigProps {
  config: MainAgentConfig;
  availableModels: ModelOption[];
  onChange: (updatedConfig: Partial<MainAgentConfig>) => void;
  disabled?: boolean;
}

export const MainAgentConfigPanel: React.FC<MainAgentConfigProps> = ({
  config,
  availableModels,
  onChange,
  disabled = false
}) => {
  const filteredModels = useMemo(() => {
    return availableModels.filter(model => 
      !(model.id === 'gpt-4o-mini' || model.id === 'qwen-turbo')
    );
  }, [availableModels]);

  const handleModelChange = (modelId: string, provider: string) => {
    onChange({
      modelName: modelId,
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
      restrictionText="主智能体不支持 GPT-4o Mini 和 Qwen Turbo 等轻量级模型"
      icon={BotIcon}
      disabled={disabled}
    >
      <ModelSelector
        models={filteredModels}
        selectedModelId={config.modelName}
        onModelChange={handleModelChange}
        disabled={disabled}
        label="主智能体模型选择"
      />
      
      <div className="grid grid-cols-2 gap-2">
        <NumberInput
          value={config.maxRetries ?? 3}
          onChange={handleMaxRetriesChange}
          min={1}
          max={10}
          step={1}
          disabled={disabled}
          label="最大重试次数"
        />
      </div>
    </AgentConfigPanel>
  );
};

// Specialized MetadataExtractorConfig component
interface MetadataExtractorConfigProps {
  config: MetadataExtractorConfig;
  availableModels: ModelOption[];
  onChange: (updatedConfig: Partial<MetadataExtractorConfig>) => void;
  disabled?: boolean;
}

export const MetadataExtractorConfigPanel: React.FC<MetadataExtractorConfigProps> = ({
  config,
  availableModels,
  onChange,
  disabled = false
}) => {
  const filteredModels = useMemo(() => {
    return availableModels.filter(model => 
      !(model.id === 'deepseek-reasoner' || model.id === 'qwq-plus-latest')
    );
  }, [availableModels]);

  const handleModelChange = (modelId: string, provider: string) => {
    onChange({
      modelName: modelId,
      modelProvider: provider
    });
  };

  return (
    <AgentConfigPanel
      label="新闻元数据提取器"
      description="负责提取信息中的关键元数据"
      restrictionText="元数据提取器不支持 DeepSeek R1 和 QWQ Plus Latest 等推理模型"
      icon={InfoIcon}
      disabled={disabled}
    >
      <ModelSelector
        models={filteredModels}
        selectedModelId={config.modelName}
        onModelChange={handleModelChange}
        disabled={disabled}
        label="新闻元数据提取器模型选择"
      />
    </AgentConfigPanel>
  );
};

// Specialized SearchAgentConfig component
interface SearchAgentConfigProps {
  config: SearchAgentConfig;
  availableModels: ModelOption[];
  onChange: (updatedConfig: Partial<SearchAgentConfig>) => void;
  disabled?: boolean;
}

export const SearchAgentConfigPanel: React.FC<SearchAgentConfigProps> = ({
  config,
  availableModels,
  onChange,
  disabled = false
}) => {
  const filteredModels = useMemo(() => {
    return availableModels.filter(model => 
      !(model.id === 'gpt-4o-mini' || model.id === 'qwen-turbo')
    );
  }, [availableModels]);

  const handleModelChange = (modelId: string, provider: string) => {
    onChange({
      modelName: modelId,
      modelProvider: provider
    });
  };

  const handleMaxSearchTokensChange = (value: number) => {
    onChange({ maxSearchTokens: value });
  };

  return (
    <AgentConfigPanel
      label="检索智能体"
      description="负责搜索和验证信息"
      restrictionText="搜索智能体不支持 GPT-4o Mini 和 Qwen Turbo 等轻量级模型"
      icon={SearchIcon}
      disabled={disabled}
    >
      <ModelSelector
        models={filteredModels}
        selectedModelId={config.modelName}
        onModelChange={handleModelChange}
        disabled={disabled}
        label="检索智能体模型选择"
      />
      
      <div className="grid grid-cols-2 gap-2">
        <NumberInput
          value={config.maxSearchTokens ?? 10000}
          onChange={handleMaxSearchTokensChange}
          min={1000}
          max={100000}
          step={1000}
          disabled={disabled}
          label="最大搜索 token 数"
        />
      </div>
    </AgentConfigPanel>
  );
}; 