'use client';

import React, { useState, useEffect } from 'react';
import { useAgentStore } from '@/lib/store';
import { EventLog } from './event-log';
import { Report } from './report';
import { AgentConfigPanel } from './agent-config';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ArrowUpIcon, RefreshCw, CogIcon, XIcon, StopCircleIcon } from 'lucide-react';

export const FactChecker: React.FC = () => {
  const {
    sessionId,
    status,
    newsText,
    setNewsText,
    interruptAgent,
    resetState,
    events,
    closeEventSource,
    // Agent configurations
    mainAgentConfig,
    metadataExtractorConfig,
    searcherConfig,
    // Available models
    availableModels,
    // Action handlers
    setMainAgentConfig,
    setMetadataExtractorConfig,
    setSearcherConfig,
    createAndRunAgent // New combined method
  } = useAgentStore();
  
  // Derive isRunning and isInterrupting from status
  const isRunning = status === 'running';
  const isInterrupting = status === 'interrupting';
  
  const [loading, setLoading] = useState(false);
  const [showConfig, setShowConfig] = useState(false);
  
  // 确保在组件卸载时关闭EventSource连接
  useEffect(() => {
    return () => {
      closeEventSource();
    };
  }, [closeEventSource]);
  
  const handleFactCheck = async () => {
    setLoading(true);
    try {
      await createAndRunAgent();
    } finally {
      setLoading(false);
    }
  };
  
  const handleInterrupt = async () => {
    try {
      await interruptAgent();
    } catch (error) {
      console.error('Failed to interrupt agent:', error);
    }
  };
  
  const handleNewSession = () => {
    resetState();
  };
  
  const toggleConfig = () => {
    setShowConfig(!showConfig);
  };
  
  return (
    <div className="w-full h-full grid grid-cols-1 gap-6">
      {/* Input Section */}
      <div className="flex flex-col gap-4">
        <div className="rounded-lg border flex flex-col">
          <div className="p-3 border-b flex items-center justify-between">
            <h2 className="text-sm font-semibold">需要核查的新闻文本</h2>
            <div className="flex items-center gap-2">
              {sessionId && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">
                    Session: {sessionId.slice(0, 8)}...
                  </span>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="size-6"
                    onClick={handleNewSession}
                    disabled={isRunning || loading}
                  >
                    <RefreshCw className="size-4" />
                  </Button>
                </div>
              )}
              
              {/* Config Toggle Button */}
              <Button 
                variant="outline" 
                size="sm"
                className="flex items-center gap-1"
                onClick={toggleConfig}
                disabled={isRunning}
              >
                <CogIcon className="size-4" />
                <span className="hidden sm:inline">Agent 配置</span>
              </Button>
            </div>
          </div>
          
          {/* Configuration Panels */}
          {showConfig && (
            <div className="border-b p-4 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-sm font-medium">Agent 配置</h3>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="size-6"
                  onClick={toggleConfig}
                >
                  <XIcon className="size-4" />
                </Button>
              </div>
              
              <div className="space-y-4">
                <AgentConfigPanel
                  agentType="main"
                  config={mainAgentConfig}
                  availableModels={availableModels}
                  onChange={setMainAgentConfig}
                  disabled={isRunning}
                />
                
                <AgentConfigPanel
                  agentType="metadata"
                  config={metadataExtractorConfig}
                  availableModels={availableModels}
                  onChange={setMetadataExtractorConfig}
                  disabled={isRunning}
                />
                
                <AgentConfigPanel
                  agentType="searcher"
                  config={searcherConfig}
                  availableModels={availableModels}
                  onChange={setSearcherConfig}
                  disabled={isRunning}
                />
              </div>
            </div>
          )}
          
          <div className="p-3 flex-1">
            <textarea
              className="w-full h-64 p-3 text-sm resize-none border rounded-md focus:outline-none focus:ring-2 focus:ring-primary/20"
              placeholder="请输入需要核查的新闻文本..."
              value={newsText}
              onChange={(e) => setNewsText(e.target.value)}
              disabled={isRunning || loading}
            />
          </div>
          <div className="p-3 border-t flex items-center justify-between">
            {!isRunning ? (
              <Button
                variant="default"
                onClick={handleFactCheck}
                disabled={!newsText.trim() || loading}
                className="flex items-center gap-2"
              >
                {loading ? (
                  <RefreshCw className="size-4 animate-spin" />
                ) : (
                  <ArrowUpIcon className="size-4" />
                )}
                开始核查
              </Button>
            ) : (
              <Button
                variant="destructive"
                onClick={handleInterrupt}
                disabled={isInterrupting}
                className="flex items-center gap-2"
              >
                {isInterrupting ? (
                  <RefreshCw className="size-4 animate-spin" />
                ) : (
                  <StopCircleIcon className="size-4" />
                )}
                {isInterrupting ? '正在中断...' : '中断任务'}
              </Button>
            )}
            <span className="text-xs text-muted-foreground">
              {isRunning ? (isInterrupting ? '正在中断...' : '处理中...') : '就绪'}
            </span>
          </div>
        </div>
        
        {/* Report Section */}
        <Report />
      </div>
      
      {/* Event Log Section */}
      <div className="w-full">
        <EventLog />
      </div>
    </div>
  );
}; 