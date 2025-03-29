'use client';

import type {
  Event,
  CheckPoints,
  CheckPoint,
  BasicMetadata,
  Knowledge,
  LLMDecisionData,
  ToolStartData,
  RetrievalResultVerification,
  TaskCompleteData,
  TaskInterruptedData,
  ErrorData,
  SearchAgentStartData,
  Status,
  SearchResult,
  Evidence,
  FactCheckReportData
} from '@/types/events';
import {
  BrainCircuitIcon,
  CheckCircleIcon,
  SearchIcon,
  ThumbsUpIcon,
  ThumbsDownIcon,
  AlertCircleIcon,
  TargetIcon,
  GlobeIcon,
  FileTextIcon,
  Layers3Icon,
  WrenchIcon,
  ClipboardListIcon,
  BookOpenIcon,
  StopCircleIcon,
  SparkleIcon
} from 'lucide-react';
import { cn } from '@/lib/utils';

export const EventItem = ({ event }: { event: Event<any> }) => {
  const { event: eventType, data } = event;

  const getEventIcon = () => {
    switch (eventType) {
      case 'agent_start':
        return <PlayIcon className="size-4" />;
      case 'extract_check_point_start':
      case 'extract_check_point_end':
        return <TargetIcon className="size-4" />;
      case 'extract_basic_metadata_start':
      case 'extract_basic_metadata_end':
        return <Layers3Icon className="size-4" />;
      case 'extract_knowledge_start':
      case 'extract_knowledge_end':
      case 'retrieve_knowledge_start':
      case 'retrieve_knowledge_end':
        return <BookOpenIcon className="size-4" />;
      case 'search_agent_start':
        return <SearchIcon className="size-4" />;
      case 'evaluate_current_status_start':
      case 'evaluate_current_status_end':
        return <BrainCircuitIcon className="size-4" />;
      case 'tool_start':
      case 'tool_result':
        return <WrenchIcon className="size-4" />;
      case 'generate_answer_start':
      case 'generate_answer_end':
        return <GlobeIcon className="size-4" />;
      case 'evaluate_search_result_start':
        return <SparkleIcon className="size-4" />;
      case 'evaluate_search_result_end':
        return (data as RetrievalResultVerification).verified ? <ThumbsUpIcon className="size-4" /> : <ThumbsDownIcon className="size-4" />;
      case 'write_fact_checking_report_start':
      case 'write_fact_checking_report_end':
        return <FileTextIcon className="size-4" />;
      case 'llm_decision':
        return <BrainCircuitIcon className="size-4" />;
      case 'task_complete':
        return <CheckCircleIcon className="size-4" />;
      case 'task_interrupted':
        return <StopCircleIcon className="size-4" />;
      case 'error':
        return <AlertCircleIcon className="size-4" />;
      default:
        return <ClipboardListIcon className="size-4" />;
    }
  };

  const getEventTitle = () => {
    switch (eventType) {
      case 'agent_start':
        return '事实核查开始';
      case 'extract_check_point_start':
        return '正在提取核查点，这可能需要一些时间...';
      case 'extract_check_point_end':
        return '核查点提取完成';
      case 'extract_basic_metadata_start':
        return '开始提取新闻元数据';
      case 'extract_basic_metadata_end':
        return '新闻元数据提取完成';
      case 'extract_knowledge_start':
        return '开始提取知识元';
      case 'extract_knowledge_end':
        return '知识元提取完成';
      case 'retrieve_knowledge_start':
        return '开始检索知识定义';
      case 'retrieve_knowledge_end':
        return '知识定义检索完成';
      case 'search_agent_start':
        return '检索智能体已激活';
      case 'evaluate_current_status_start':
        return '正在评估当前检索状态...';
      case 'evaluate_current_status_end':
        return '检索状态评估完成';
      case 'tool_start':
        const toolData = data as ToolStartData;
        return `使用工具: ${toolData?.tool_name || ''}`;
      case 'tool_result':
        return '工具执行完成';
      case 'generate_answer_start':
        return '正在生成检索结论...';
      case 'generate_answer_end':
        return '检索结论生成完成';
      case 'evaluate_search_result_start':
        return '正在评估检索结果...';
      case 'evaluate_search_result_end':
        return '检索结果评估完成';
      case 'write_fact_checking_report_start':
        return '开始撰写核查报告...';
      case 'write_fact_checking_report_end':
        return '核查报告撰写完成';
      case 'llm_decision':
        const decisionData = data as LLMDecisionData;
        return `LLM 决策: ${decisionData?.decision || ''}`;
      case 'task_complete':
        const completeData = data as TaskCompleteData;
        return completeData?.message || '任务完成';
      case 'task_interrupted':
        const interruptData = data as TaskInterruptedData;
        return interruptData?.message || '任务已中断';
      case 'error':
        const errorData = data as ErrorData;
        return errorData?.message || '发生错误';
      default:
        return eventType;
    }
  };

  const getEventClass = () => {
    switch (eventType) {
      case 'agent_start':
        return 'bg-blue-50 border-blue-100 text-blue-700';
      case 'extract_check_point_start':
      case 'extract_check_point_end':
        return 'bg-indigo-50 border-indigo-100 text-indigo-700';
      case 'extract_basic_metadata_start':
      case 'extract_basic_metadata_end':
      case 'extract_knowledge_start':
      case 'extract_knowledge_end':
      case 'retrieve_knowledge_start':
      case 'retrieve_knowledge_end':
        return 'bg-purple-50 border-purple-100 text-purple-700';
      case 'search_agent_start':
      case 'evaluate_current_status_start':
      case 'evaluate_current_status_end':
      case 'generate_answer_start':
      case 'generate_answer_end':
        return 'bg-cyan-50 border-cyan-100 text-cyan-700';
      case 'tool_start':
      case 'tool_result':
        return 'bg-blue-50 border-blue-100 text-blue-700';
      case 'evaluate_search_result_start':
      case 'evaluate_search_result_end':
        return (data as RetrievalResultVerification)?.verified
          ? 'bg-green-50 border-green-100 text-green-700'
          : 'bg-amber-50 border-amber-100 text-amber-700';
      case 'write_fact_checking_report_start':
      case 'write_fact_checking_report_end':
        return 'bg-emerald-50 border-emerald-100 text-emerald-700';
      case 'llm_decision':
        return 'bg-violet-50 border-violet-100 text-violet-700';
      case 'task_complete':
        return 'bg-green-50 border-green-100 text-green-700';
      case 'task_interrupted':
        return 'bg-orange-50 border-orange-100 text-orange-700';
      case 'error':
        return 'bg-red-50 border-red-100 text-red-700';
      default:
        return 'bg-gray-50 border-gray-100 text-gray-700';
    }
  };

  const renderEventDetail = () => {
    switch (eventType) {
      case 'extract_check_point_end':
        const checkPoints = data as CheckPoints;
        if (checkPoints.items?.length) {
          return (
            <div className="mt-2 space-y-2">
              <p className="text-sm font-medium">
                找到 {checkPoints.items.length} 个核查点:
              </p>
              {checkPoints.items
                .filter((cp: CheckPoint) => cp.is_verification_point)
                .map((cp: CheckPoint, idx: number) => (
                  <div key={idx} className="p-2 bg-white rounded-md border">
                    <p className="text-sm font-medium">核查点 {idx + 1}: {cp.content}</p>
                    {cp.importance && (
                      <p className="text-xs text-gray-600">重要性: {cp.importance}</p>
                    )}
                    {cp.retrieval_step && cp.retrieval_step.length > 0 && (
                      <div className="mt-1">
                        <p className="text-xs font-medium">检索步骤:</p>
                        {cp.retrieval_step.map((step, stepIdx: number) => (
                          <p key={stepIdx} className="text-xs text-gray-600">• {step.purpose}</p>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
            </div>
          );
        }
        return null;

      case 'extract_basic_metadata_end':
        const basicMetadata = data as BasicMetadata;
        return (
          <div className="mt-2 space-y-1">
            <p className="text-xs"><span className="font-medium">新闻类型: </span>
              {basicMetadata.news_type || '未知'}
            </p>
            <p className="text-xs"><span className="font-medium">人物: </span>
              {Array.isArray(basicMetadata.who) ? basicMetadata.who.join(', ') : '无'}
            </p>
            <p className="text-xs"><span className="font-medium">时间: </span>
              {Array.isArray(basicMetadata.when) ? basicMetadata.when.join(', ') : '无'}
            </p>
            <p className="text-xs"><span className="font-medium">地点: </span>
              {Array.isArray(basicMetadata.where) ? basicMetadata.where.join(', ') : '无'}
            </p>
            <p className="text-xs"><span className="font-medium">事件: </span>
              {Array.isArray(basicMetadata.what) ? basicMetadata.what.join(', ') : '无'}
            </p>
            <p className="text-xs"><span className="font-medium">原因: </span>
              {Array.isArray(basicMetadata.why) ? basicMetadata.why.join(', ') : '无'}
            </p>
            <p className="text-xs"><span className="font-medium">过程: </span>
              {Array.isArray(basicMetadata.how) ? basicMetadata.how.join(', ') : '无'}
            </p>
          </div>
        );

      case 'extract_knowledge_end':
        const knowledges = data as Knowledge[];
        if (knowledges.length) {
          return (
            <div className="mt-2 space-y-2">
              <p className="text-sm font-medium">
                提取到 {knowledges.length} 个知识元:
              </p>
              {knowledges.map((knowledge: Knowledge, idx: number) => (
                <div key={idx} className="p-2 bg-white rounded-md border">
                  <p className="text-xs"><span className="font-medium">术语:</span> {knowledge.term}</p>
                  <p className="text-xs"><span className="font-medium">类别:</span> {knowledge.category}</p>
                  {knowledge.description && (
                    <p className="text-xs"><span className="font-medium">描述:</span> {knowledge.description}</p>
                  )}
                  {knowledge.source && (
                    <p className="text-xs"><span className="font-medium">来源:</span> {knowledge.source}</p>
                  )}
                </div>
              ))}
            </div>
          );
        }
        return null;

      case 'retrieve_knowledge_end':
        const retrievedKnowledge = data as Knowledge;
        return (
          <div className="mt-2 space-y-1">
            <p className="text-xs"><span className="font-medium">术语:</span> {retrievedKnowledge.term}</p>
            <p className="text-xs"><span className="font-medium">类别:</span> {retrievedKnowledge.category}</p>
            <p className="text-xs"><span className="font-medium">定义:</span> {retrievedKnowledge.description || '未检索到定义'}</p>
            {retrievedKnowledge.source && (
              <p className="text-xs"><span className="font-medium">来源:</span> {retrievedKnowledge.source}</p>
            )}
          </div>
        );

      case 'search_agent_start':
        const searchData = data as SearchAgentStartData;
        if (searchData) {
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs"><span className="font-medium">内容:</span> {searchData.content}</p>
              <p className="text-xs"><span className="font-medium">目的:</span> {searchData.purpose}</p>
              {searchData.expected_sources && searchData.expected_sources.length > 0 && (
                <p className="text-xs">
                  <span className="font-medium">预期来源:</span> {searchData.expected_sources.join(', ')}
                </p>
              )}
            </div>
          );
        }
        return null;

      case 'evaluate_current_status_end':
        const statusData = data as Status;
        if (statusData) {
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs"><span className="font-medium">评估:</span> {statusData.evaluation}</p>
              <p className="text-xs"><span className="font-medium">缺失信息:</span> {statusData.missing_information}</p>
              {statusData.memory && (
                <p className="text-xs"><span className="font-medium">记忆:</span> {statusData.memory}</p>
              )}
              <p className="text-xs"><span className="font-medium">下一步:</span> {statusData.next_step}</p>
              
              {statusData.new_evidence && statusData.new_evidence.length > 0 && (
                <div className="mt-1">
                  <p className="text-xs font-medium">新证据:</p>
                  {statusData.new_evidence.map((evidence: Evidence, idx: number) => (
                    <div key={idx} className="p-2 bg-white rounded-md border mt-1">
                      <p className="text-xs"><span className="font-medium">内容:</span> {evidence.content}</p>
                      <p className="text-xs"><span className="font-medium">关系:</span> {evidence.relationship === 'support' ? '支持' : '反驳'}</p>
                      <p className="text-xs"><span className="font-medium">推理:</span> {evidence.reasoning}</p>
                      {evidence.source && Object.keys(evidence.source).length > 0 && (
                        <p className="text-xs"><span className="font-medium">来源:</span> {Object.entries(evidence.source).map(([k, v]) => `${k}: ${v}`).join(', ')}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        }
        return null;

      case 'evaluate_search_result_end':
        const verificationResult = data as RetrievalResultVerification;
        return (
          <div className="mt-2 space-y-1">
            <p className="text-xs"><span className="font-medium">核验结论:</span> {verificationResult.verified ? '认可' : '不认可'}</p>
            <p className="text-xs"><span className="font-medium">推理:</span> {verificationResult.reasoning}</p>
            {verificationResult.updated_purpose && (
              <p className="text-xs"><span className="font-medium">更新后的检索目的:</span> {verificationResult.updated_purpose}</p>
            )}
            {verificationResult.updated_expected_sources && (
              <p className="text-xs"><span className="font-medium">更新后的检索预期来源:</span> {verificationResult.updated_expected_sources.join(', ')}</p>
            )}
          </div>
        );

      case 'generate_answer_end':
        const resultData = data as SearchResult;
        if (resultData) {
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs"><span className="font-medium">概要:</span> {resultData.summary}</p>
              <p className="text-xs"><span className="font-medium">结论:</span> {resultData.conclusion}</p>
              <p className="text-xs"><span className="font-medium">置信度:</span> {resultData.confidence}</p>
            </div>
          );
        }
        return null;

      case 'tool_start':
        const toolData = data as ToolStartData;
        if (toolData) {
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs break-all"><span className="font-medium">输入:</span> {toolData.input}</p>
            </div>
          );
        }
        return null;

      case 'tool_result':
        if (data) {
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs break-all">
                <span className="font-medium">输出:</span>
                {data}
              </p>
            </div>
          );
        }
        return null;

      case 'llm_decision':
        const decisionData = data as LLMDecisionData;
        if (decisionData) {
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs"><span className="font-medium">决策:</span> {decisionData.decision}</p>
              {decisionData.reason && (
                <p className="text-xs"><span className="font-medium">原因:</span> {decisionData.reason}</p>
              )}
            </div>
          );
        }
        return null;

      default:
        return null;
    }
  };

  return (
    <div className={cn("p-3 rounded-md border transition-colors", getEventClass())}>
      <div className="flex items-center gap-2">
        {getEventIcon()}
        <div className="text-sm font-medium">{getEventTitle()}</div>
      </div>
      {renderEventDetail()}
    </div>
  );
};

const PlayIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className={className}
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polygon points="5 3 19 12 5 21 5 3" />
  </svg>
); 