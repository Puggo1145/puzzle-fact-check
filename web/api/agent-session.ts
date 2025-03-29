import {
  API_BASE_URL,
  MainAgentConfig,
  SearchAgentConfig,
  MetadataExtractorConfig
} from '../constants/agent-default-config';

/**
 * 创建并运行 Agent
 */
export async function createAndRunAgent(
  newsText: string,
  mainAgentConfig: MainAgentConfig,
  metadataExtractorConfig: MetadataExtractorConfig,
  searcherConfig: SearchAgentConfig,
) {
  const config = {
    main_agent: {
      model_name: mainAgentConfig.modelName,
      model_provider: mainAgentConfig.modelProvider,
      max_retries: mainAgentConfig.maxRetries
    },
    metadata_extractor: {
      model_name: metadataExtractorConfig.modelName,
      model_provider: metadataExtractorConfig.modelProvider
    },
    searcher: {
      model_name: searcherConfig.modelName,
      model_provider: searcherConfig.modelProvider,
      max_search_tokens: searcherConfig.maxSearchTokens,
      selected_tools: searcherConfig.selectedTools
    }
  };

  const response = await fetch(`${API_BASE_URL}/start-fact-check`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      news_text: newsText,
      config: config
    })
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));

    // For server errors (5xx), display a friendly error message
    if (response.status >= 500 && response.status < 600) {
      throw new Error('服务器出现问题，请稍后再试（Puzzle 是一个个人实验项目，计算资源较少，请谅解）');
    }

    throw new Error(errorData.error || 'Unknown error');
  }

  return await response.json();
}

/**
 * Interrupts a running agent task
 */
export async function interruptAgent(sessionId: string) {
  const response = await fetch(`${API_BASE_URL}/agents/${sessionId}/interrupt`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  });

  return await response.json();
}