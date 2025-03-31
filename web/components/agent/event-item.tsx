'use client';

import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import type {
  Event,
  CheckPoint,
  BasicMetadata,
  Knowledge,
  LLMDecisionData,
  ToolStartData,
  RetrievalResultVerification,
  TaskInterruptedData,
  ErrorData,
  SearchAgentStartData,
  Status,
  SearchResult,
  Evidence,
  ToolEndData,
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
  ClipboardListIcon,
  BookOpenIcon,
  StopCircleIcon,
  SparkleIcon,
} from 'lucide-react';
import { toolDict } from '@/constants/tools';
import { cn } from '@/lib/utils';

export const EventItem = ({ event }: { event: Event }) => {
  const { event: eventType, data } = event;

  const EventIcon = () => {
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
      case 'tool_end':
        const ToolIcon = toolDict[data.tool_name].icon;
        return <ToolIcon />;
      case 'generate_answer_start':
      case 'generate_answer_end':
        return <GlobeIcon className="size-4" />;
      case 'evaluate_search_result_start':
        return <SparkleIcon className="size-4" />;
      case 'evaluate_search_result_end':
        return (data as RetrievalResultVerification).verified
          ? <ThumbsUpIcon className="size-4" />
          : <ThumbsDownIcon className="size-4" />;
      case 'write_fact_check_report_start':
      case 'write_fact_check_report_end':
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

  const EventTitle = () => {
    switch (eventType) {
      case 'agent_start':
        return '事实核查开始';
      case 'extract_check_point_start':
        return '正在提取核查点，这可能需要一些时间...';
      case 'extract_check_point_end':
        return '核查点提取完成';
      case 'extract_basic_metadata_start':
        return '正在提取新闻元数据';
      case 'extract_basic_metadata_end':
        return '新闻元数据提取完成';
      case 'extract_knowledge_start':
        return '正在提取知识元';
      case 'extract_knowledge_end':
        return '知识元提取完成';
      case 'retrieve_knowledge_start':
        return '正在检索知识定义';
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
        return toolDict[toolData.tool_name].alias;
      case 'tool_end':
        const toolEndData = data as ToolEndData;
        return `${toolDict[toolEndData.tool_name].alias}完成`;
      case 'generate_answer_start':
        return '正在分析检索结论...';
      case 'generate_answer_end':
        return '得出检索结论';
      case 'evaluate_search_result_start':
        return '正在评估检索结果...';
      case 'evaluate_search_result_end':
        return '检索结果评估完成';
      case 'write_fact_check_report_start':
        return '正在撰写核查报告，这可能需要一些时间...';
      case 'write_fact_check_report_end':
        return '核查报告撰写完成';
      case 'llm_decision':
        const decisionData = data as LLMDecisionData;
        return `LLM 决策: ${decisionData?.decision || ''}`;
      case 'task_complete':
        return '核查完成';
      case 'task_interrupted':
        const interruptData = data as TaskInterruptedData;
        return interruptData?.message || '任务已中断';
      case 'error':
        const errorData = data as ErrorData;
        return errorData?.message.length > 100
          ? errorData?.message.slice(0, 100) + '...'
          : errorData?.message
          || '服务器错误，请稍候再试';
      default:
        return eventType;
    }
  };

  const getEventClass = () => {
    switch (eventType) {
      case 'agent_start':
        return 'bg-blue-50 border-blue-100 text-blue-700 dark:bg-blue-900/40 dark:border-blue-800/50 dark:text-blue-200';
      case 'extract_check_point_start':
      case 'extract_check_point_end':
        return 'bg-indigo-50 border-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:border-indigo-800/50 dark:text-indigo-200';
      case 'extract_basic_metadata_start':
      case 'extract_basic_metadata_end':
      case 'extract_knowledge_start':
      case 'extract_knowledge_end':
      case 'retrieve_knowledge_start':
      case 'retrieve_knowledge_end':
        return 'bg-purple-50 border-purple-100 text-purple-700 dark:bg-purple-900/40 dark:border-purple-800/50 dark:text-purple-200';
      case 'search_agent_start':
      case 'evaluate_current_status_start':
      case 'evaluate_current_status_end':
      case 'generate_answer_start':
      case 'generate_answer_end':
        return 'bg-cyan-50 border-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:border-cyan-800/50 dark:text-cyan-200';
      case 'tool_start':
      case 'tool_end':
        return 'bg-blue-50 border-blue-100 text-blue-700 dark:bg-blue-900/40 dark:border-blue-800/50 dark:text-blue-200';
      case 'evaluate_search_result_start':
      case 'evaluate_search_result_end':
        return (data as RetrievalResultVerification)?.verified
          ? 'bg-green-50 border-green-100 text-green-700 dark:bg-green-900/50 dark:border-green-800/50 dark:text-green-200'
          : 'bg-amber-50 border-amber-100 text-amber-700 dark:bg-amber-900/50 dark:border-amber-800/50 dark:text-amber-200';
      case 'write_fact_check_report_start':
      case 'write_fact_check_report_end':
        return 'bg-emerald-50 border-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:border-emerald-800/50 dark:text-emerald-200';
      case 'llm_decision':
        return 'bg-violet-50 border-violet-100 text-violet-700 dark:bg-violet-900/40 dark:border-violet-800/50 dark:text-violet-200';
      case 'task_complete':
        return 'bg-green-50 border-green-100 text-green-700 dark:bg-green-900/40 dark:border-green-800/50 dark:text-green-200';
      case 'task_interrupted':
        return 'bg-orange-50 border-orange-100 text-orange-700 dark:bg-orange-900/40 dark:border-orange-800/50 dark:text-orange-200';
      case 'error':
        return 'bg-red-50 border-red-100 text-red-700 dark:bg-red-900/40 dark:border-red-800/50 dark:text-red-200';
      default:
        return 'bg-gray-50 border-gray-100 text-gray-700 dark:bg-gray-900/40 dark:border-gray-800/50 dark:text-gray-200';
    }
  };

  const EventDetail = () => {
    switch (eventType) {
      case 'extract_check_point_end':
        const checkPoints = data as CheckPoint[];
        if (checkPoints.length) {
          return (
            <div className="mt-2 space-y-2">
              <p className="text-sm font-medium">
                找到 {checkPoints.length} 个核查点:
              </p>
              {checkPoints
                .filter((cp: CheckPoint) => cp.is_verification_point)
                .map((cp: CheckPoint, idx: number) => (
                  <div key={idx} className="p-2 bg-white rounded-md border dark:bg-gray-800/50">
                    <p className="text-sm font-medium">
                      核查点 {idx + 1}: {cp.content}
                    </p>
                    {cp.importance &&
                      <p className="text-xs text-gray-600 dark:text-white">
                        {cp.importance}
                      </p>
                    }
                    {cp.retrieval_step && cp.retrieval_step.length > 0 && (
                      <div className="mt-1">
                        <p className="text-xs font-medium">检索计划:</p>
                        {cp.retrieval_step.map((step, stepIdx: number) => (
                          <p key={stepIdx} className="text-xs text-gray-600 dark:text-white">{idx + 1}. {step.purpose}</p>
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
        const formattedMetadata = Object.fromEntries(
          Object.entries(basicMetadata).map(([key, value]) => {
            if (Array.isArray(value)) {
              return [key, value.length > 0 ? value.join(', ') : '无'];
            }
            return [key, value];
          })
        );
        return (
          <div className="mt-2 space-y-1">
            <p className="text-xs">
              新闻类型:&nbsp;&nbsp;{formattedMetadata.news_type}
            </p>
            <p className="text-xs">
              人物 (Who) :&nbsp;&nbsp;{formattedMetadata.who}
            </p>
            <p className="text-xs">
              时间 (When) :&nbsp;&nbsp;{formattedMetadata.when}
            </p>
            <p className="text-xs">
              地点 (Where) :&nbsp;&nbsp;{formattedMetadata.where}
            </p>
            <p className="text-xs">
              事件 (What) :&nbsp;&nbsp;{formattedMetadata.what}
            </p>
            <p className="text-xs">
              原因 (Why) :&nbsp;&nbsp;{formattedMetadata.why}
            </p>
            <p className="text-xs">
              过程 (How) :&nbsp;&nbsp;{formattedMetadata.how}
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
                <div key={idx} className="p-2 bg-white dark:bg-black/20 rounded-md border space-y-1">
                  <p className="text-xs">
                    术语: {knowledge.term}
                  </p>
                  <p className="text-xs">
                    类别: {knowledge.category}
                  </p>
                  {knowledge.description && (
                    <p className="text-xs">
                      描述: {knowledge.description}
                    </p>
                  )}
                  {knowledge.source && (
                    <SourceBadge source={knowledge.source} />
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
            <p className="text-xs">
              术语: {retrievedKnowledge.term}
            </p>
            <p className="text-xs">
              类别: {retrievedKnowledge.category}
            </p>
            <p className="text-xs">
              定义: {retrievedKnowledge.description || '未检索到定义'}
            </p>
            {retrievedKnowledge.source && (
              <SourceBadge source={retrievedKnowledge.source} />
            )}
          </div>
        );

      case 'search_agent_start':
        const searchData = data as SearchAgentStartData;
        if (searchData) {
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs"><span className="font-medium">核查点:</span> {searchData.content}</p>
              <p className="text-xs"><span className="font-medium">核查目标:</span> {searchData.purpose}</p>
              {searchData.expected_sources && searchData.expected_sources.length > 0 && (
                <p className="text-xs">
                  <span className="font-medium">预期信源:</span> {searchData.expected_sources.join(', ')}
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
                    <div key={idx} className="p-2 bg-white rounded-md border dark:bg-gray-800">
                      <p className="text-xs"><span className="font-medium">内容:</span> {evidence.content}</p>
                      <p className="text-xs"><span className="font-medium">关系:</span> {evidence.relationship === 'support' ? '支持' : '反驳'}</p>
                      <p className="text-xs"><span className="font-medium">推理:</span> {evidence.reasoning}</p>
                      {evidence.source && Object.keys(evidence.source).length > 0 && (
                        <SourceBadge source={Object.values(evidence.source).join(', ')} className="mt-2" />
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
              <p className="text-xs break-all">
                {toolData.input_str}
              </p>
            </div>
          );
        }
        return null;

      case 'tool_end':
        const toolEndData = data as ToolEndData;
        if (toolEndData) {
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs break-all">
                {toolEndData.output_str}
              </p>
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
        <EventIcon />
        <div className="text-sm font-medium">
          <EventTitle />
        </div>
      </div>
      <EventDetail />
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

const SourceBadge = ({ source, className }: { source: string, className?: string }) => (
  <Link href={source} target="_blank">
    <Badge className={cn("rounded-full bg-gray-800/10 text-black", 
      "dark:bg-white/15 dark:text-white hover:bg-black/20 dark:hover:bg-white/30", 
      "transition-colors duration-150", 
      className
    )}>
      <GlobeIcon className="size-4" />
      {source.length > 30 ? source.slice(0, 30) + '...' : source}
    </Badge>
  </Link>
);

