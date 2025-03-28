'use client';

import React from 'react';
import { Event } from '@/lib/store';
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
  LibraryIcon,
  SparklesIcon,
  StopCircleIcon,
  SparkleIcon
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface EventItemProps {
  event: Event;
}

export const EventItem: React.FC<EventItemProps> = ({ event }) => {
  const { event: eventType, data } = event;
  
  const getEventIcon = () => {
    switch (eventType) {
      case 'agent_created':
        return <SparklesIcon className="size-4" />;
      case 'run_started':
      case 'task_start':
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
      case 'evaluate_status_start':
      case 'status_evaluation_end':
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
        return data?.verification_result?.verified ? <ThumbsUpIcon className="size-4" /> : <ThumbsDownIcon className="size-4" />;
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
      case 'agent_created':
        return data.message;
      case 'run_started':
        return '开始核查流程';
      case 'task_start':
        return data.message || '任务开始执行';
      case 'extract_check_point_start':
        return '正在提取核查点（这可能需要一些时间）';
      case 'extract_check_point_end':
        return '核查点提取成功';
      case 'extract_basic_metadata_start':
        return '开始提取新闻元数据';
      case 'extract_basic_metadata_end':
        return '新闻元数据提取完成';
      case 'extract_knowledge_start':
        return '开始提取知识元';
      case 'extract_knowledge_end':
        return '知识元素提取完成';
      case 'retrieve_knowledge_start':
        return '开始检索知识定义';
      case 'retrieve_knowledge_end':
        return '知识定义检索完成';
      case 'search_agent_start':
        return '搜索代理已激活';
      case 'evaluate_status_start':
        return data.message || '评估搜索状态';
      case 'status_evaluation_end':
        return '搜索状态评估完成';
      case 'tool_start':
        return `使用工具: ${data.tool_name}`;
      case 'tool_result':
        return '工具执行完成';
      case 'generate_answer_start':
        return data.message || '开始生成回答';
      case 'generate_answer_end':
        return '回答生成完成';
      case 'evaluate_search_result_start':
        return '开始评估搜索结果';
      case 'evaluate_search_result_end':
        return '搜索结果评估完成';
      case 'write_fact_checking_report_start':
        return '开始撰写核查报告';
      case 'write_fact_checking_report_end':
        return '核查报告撰写完成';
      case 'llm_decision':
        return `LLM 决策: ${data.decision}`;
      case 'task_complete':
        return data.message || '任务完成';
      case 'task_interrupted':
        return data.message || '任务已中断';
      case 'error':
        return data.message || '发生错误';
      default:
        return eventType;
    }
  };
  
  const getEventClass = () => {
    switch (eventType) {
      case 'agent_created':
      case 'run_started':
      case 'task_start':
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
      case 'evaluate_status_start':
      case 'status_evaluation_end':
      case 'generate_answer_start':
        case 'generate_answer_end':
            return 'bg-cyan-50 border-cyan-100 text-cyan-700';
      case 'tool_start':
        return 'bg-blue-50 border-blue-100 text-blue-700';
      case 'tool_result':
        return 'bg-blue-50 border-blue-100 text-blue-700';
      case 'evaluate_search_result_start':
      case 'evaluate_search_result_end':
        return data?.verification_result?.verified 
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
        if (data.check_points?.items?.length) {
          return (
            <div className="mt-2 space-y-2">
              <p className="text-sm font-medium">
                Found {data.check_points.items.length} verification points:
              </p>
              {data.check_points.items
                .filter((cp: any) => cp.is_verification_point)
                .map((cp: any, idx: number) => (
                  <div key={idx} className="p-2 bg-white rounded-md border">
                    <p className="text-sm font-medium">Point {idx + 1}: {cp.content}</p>
                    {cp.importance && (
                      <p className="text-xs text-gray-600">Reason: {cp.importance}</p>
                    )}
                    {cp.retrieval_step?.length > 0 && (
                      <div className="mt-1">
                        <p className="text-xs font-medium">Retrieval plan:</p>
                        {cp.retrieval_step.map((step: any, stepIdx: number) => (
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
        if (data.basic_metadata) {
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs"><span className="font-medium">Type:</span> {data.basic_metadata.news_type || 'Unknown'}</p>
              <p className="text-xs"><span className="font-medium">Title:</span> {data.basic_metadata.title || 'Unknown'}</p>
              <p className="text-xs"><span className="font-medium">Time:</span> {data.basic_metadata.time || 'Unknown'}</p>
              {data.basic_metadata.who && data.basic_metadata.who.length > 0 && (
                <p className="text-xs"><span className="font-medium">Who:</span> {data.basic_metadata.who.join(', ')}</p>
              )}
              {data.basic_metadata.where && data.basic_metadata.where.length > 0 && (
                <p className="text-xs"><span className="font-medium">Where:</span> {data.basic_metadata.where.join(', ')}</p>
              )}
            </div>
          );
        }
        return null;
        
      case 'extract_knowledge_end':
        if (data.knowledges?.length) {
          return (
            <p className="mt-2 text-xs">
              Found {data.knowledges.length} knowledge elements
            </p>
          );
        }
        return null;
        
      case 'retrieve_knowledge_end':
        if (data.retrieved_knowledge) {
          const knowledge = data.retrieved_knowledge;
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs"><span className="font-medium">Term:</span> {knowledge.term || 'Unknown'}</p>
              <p className="text-xs"><span className="font-medium">Definition:</span> {
                // 首先尝试使用definition字段，如果没有则尝试description字段
                knowledge.definition || knowledge.description || 'Unknown'
              }</p>
              {knowledge.category && (
                <p className="text-xs"><span className="font-medium">Category:</span> {knowledge.category}</p>
              )}
              {knowledge.source && (
                <p className="text-xs"><span className="font-medium">Source:</span> {knowledge.source}</p>
              )}
            </div>
          );
        }
        return null;
        
      case 'search_agent_start':
        return (
          <div className="mt-2 space-y-1">
            <p className="text-xs"><span className="font-medium">Content:</span> {data.content}</p>
            <p className="text-xs"><span className="font-medium">Purpose:</span> {data.purpose}</p>
          </div>
        );
        
      case 'status_evaluation_end':
        if (data.status) {
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs"><span className="font-medium">Evaluation:</span> {data.status.evaluation || 'No evaluation available'}</p>
              <p className="text-xs"><span className="font-medium">Next step:</span> {data.status.next_step || 'No next step defined'}</p>
              {data.status.missing_information && (
                <p className="text-xs"><span className="font-medium">Missing info:</span> {data.status.missing_information}</p>
              )}
              {data.status.memory && (
                <p className="text-xs"><span className="font-medium">Memory:</span> {data.status.memory}</p>
              )}
              {data.status.action && data.status.action !== 'answer' && Array.isArray(data.status.action) && (
                <p className="text-xs"><span className="font-medium">Action:</span> Use tool{data.status.action.length > 1 ? 's' : ''}</p>
              )}
              {data.status.action === 'answer' && (
                <p className="text-xs"><span className="font-medium">Action:</span> Generate answer</p>
              )}
            </div>
          );
        }
        return null;
        
      case 'tool_start':
        return (
          <p className="mt-2 text-xs">
            <span className="font-medium">Input:</span> {data.input}
          </p>
        );
        
      case 'tool_result':
        return (
          <div className="mt-2">
            <p className="text-xs font-medium">Result:</p>
            <div className="mt-1 p-2 bg-white rounded-md border text-xs font-mono whitespace-pre-wrap overflow-x-auto max-h-32">
              {typeof data.output === 'string' ? data.output : JSON.stringify(data.output, null, 2)}
            </div>
          </div>
        );
        
      case 'generate_answer_end':
        if (data.result) {
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs"><span className="font-medium">Conclusion:</span> {data.result.conclusion}</p>
              <p className="text-xs"><span className="font-medium">Confidence:</span> {data.result.confidence}</p>
            </div>
          );
        }
        return null;
        
      case 'evaluate_search_result_end':
        if (data.verification_result) {
          const vr = data.verification_result;
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs">
                <span className="font-medium">Result:</span> {vr.verified ? 'Verified ✓' : 'Not Verified ×'}
              </p>
              <p className="text-xs"><span className="font-medium">Reasoning:</span> {vr.reasoning}</p>
            </div>
          );
        }
        return null;
        
      case 'llm_decision':
        if (data.reason) {
          return (
            <p className="mt-2 text-xs">
              <span className="font-medium">Reason:</span> {data.reason}
            </p>
          );
        }
        return null;
        
      default:
        return null;
    }
  };
  
  return (
    <div className={cn("p-3 rounded-lg border", getEventClass())}>
      <div className="flex gap-2 items-start">
        <div className="mt-0.5 flex-shrink-0">
          {getEventIcon()}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium">{getEventTitle()}</p>
          {renderEventDetail()}
        </div>
        <div className="flex-shrink-0 text-xs text-gray-500">
          {event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : ''}
        </div>
      </div>
    </div>
  );
};

// Custom Play icon since it's not in lucide-react by default
const PlayIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <polygon points="5 3 19 12 5 21 5 3"></polygon>
  </svg>
); 