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
  IsNewsText,
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
  CircleXIcon,
  CircleEllipsisIcon,
  Loader2Icon,
} from 'lucide-react';
import { toolDict } from '@/constants/tools';
import { cn } from '@/lib/utils';

interface EventItemProps {
  event: Event;
  isLastEvent: boolean;
}

export const EventItem = ({ event, isLastEvent }: EventItemProps) => {
  const { event: eventType, data } = event;

  const EventIcon = () => {
    switch (eventType) {
      case 'agent_start':
        return <PlayIcon className="size-4" />;
      case 'check_if_news_text_start':
        return <CircleEllipsisIcon className="size-4" />;
      case 'check_if_news_text_end':
        const isNewsText = data as IsNewsText;
        return isNewsText.result ? <CheckCircleIcon className="size-4" /> : <CircleXIcon className="size-4" />;
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
        return 'Start Running';
      case 'check_if_news_text_start':
        return 'Preparing for Fact-Checking';
      case 'check_if_news_text_end':
        const isNewsText = data as IsNewsText;
        return isNewsText.result ? 'Ready to Start Fact-Checking' : 'We cannot check the text you provided';
      case 'extract_check_point_start':
        return 'Extracting Check Points, this may take some time...';
      case 'extract_check_point_end':
        return 'Check Points Extracted';
      case 'extract_basic_metadata_start':
        return 'Extracting Basic Metadata';
      case 'extract_basic_metadata_end':
        return 'Basic Metadata Extracted';
      case 'extract_knowledge_start':
        return 'Extracting Knowledge';
      case 'extract_knowledge_end':
        return 'Knowledge Extracted';
      case 'retrieve_knowledge_start':
        return 'Retrieving Knowledge Definition';
      case 'retrieve_knowledge_end':
        return 'Knowledge Definition Retrieved';
      case 'search_agent_start':
        return 'Processing Check Points';
      case 'evaluate_current_status_start':
        return 'Evaluating Current Retrieval Status...';
      case 'evaluate_current_status_end':
        return 'Current Retrieval Status Evaluated';
      case 'tool_start':
        const toolData = data as ToolStartData;
        return toolDict[toolData.tool_name].alias;
      case 'tool_end':
        const toolEndData = data as ToolEndData;
        return `${toolDict[toolEndData.tool_name].alias} Finished`;
      case 'generate_answer_start':
        return 'Analyzing Retrieval Conclusion...';
      case 'generate_answer_end':
        return 'Retrieval Conclusion Analyzed';
      case 'evaluate_search_result_start':
        return 'Evaluating Retrieval Result...';
      case 'evaluate_search_result_end':
        return 'Retrieval Result Evaluated';
      case 'write_fact_check_report_start':
        return 'Writing Fact-Checking Report, this may take some time...';
      case 'write_fact_check_report_end':
        return 'Fact-Checking Report Written';
      case 'llm_decision':
        const decisionData = data as LLMDecisionData;
        const decisionMap: Record<string, string> = {
          'continue': 'Continue to Next Retrieval',
          'force_continue': 'Exceeded Maximum Retrieval Retry Count, Force to Continue to Next Retrieval',
          'retry': 'Retry Current Retrieval',
          'finish': 'Finish All Retrieval Tasks',
        }
        return `LLM Decision: ${decisionMap[decisionData?.decision] || ''}`;
      case 'task_complete':
        return 'Fact-Checking Finished';
      case 'task_interrupted':
        const interruptData = data as TaskInterruptedData;
        return interruptData?.message || 'Task Interrupted';
      case 'error':
        const errorData = data as ErrorData;
        return errorData?.message.length > 100
          ? errorData?.message.slice(0, 100) + '...'
          : errorData?.message
          || 'Server Error, Please Try Again Later';
      default:
        return eventType;
    }
  };

  const getEventClass = () => {
    switch (eventType) {
      case 'agent_start':
        return 'bg-blue-50 border-blue-100 text-blue-700 dark:bg-blue-900/40 dark:border-blue-800/50 dark:text-blue-200';
      case 'check_if_news_text_start':
        return 'bg-sky-50 border-sky-100 text-sky-700 dark:bg-sky-900/40 dark:border-sky-800/50 dark:text-sky-200';
      case 'check_if_news_text_end':
        return (data as IsNewsText)?.result
          ? 'bg-green-50 border-green-100 text-green-700 dark:bg-green-900/40 dark:border-green-800/50 dark:text-green-200'
          : 'bg-red-50 border-red-100 text-red-700 dark:bg-red-900/40 dark:border-red-800/50 dark:text-red-200';
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
        return 'bg-gray-50 border-gray-200 text-gray-700 dark:bg-gray-900/40 dark:border-gray-800/50 dark:text-gray-200';
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
      case 'stream_closed':
        return 'bg-gray-50 border-gray-100 text-gray-700 dark:bg-gray-900/40 dark:border-gray-800/50 dark:text-gray-200';
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
                Found {checkPoints.length} Check Points:
              </p>
              {checkPoints
                .filter((cp: CheckPoint) => cp.is_verification_point)
                .map((cp: CheckPoint, idx: number) => (
                  <div key={idx} className="p-2 bg-white rounded-md border dark:bg-gray-800/50">
                    <p className="text-sm font-medium">
                      Check Point {idx + 1}: {cp.content}
                    </p>
                    {cp.importance &&
                      <p className="text-xs text-gray-600 dark:text-white">
                        {cp.importance}
                      </p>
                    }
                    {cp.retrieval_step && cp.retrieval_step.length > 0 && (
                      <div className="mt-1">
                        <p className="text-xs font-medium">Retrieval Plan:</p>
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
              return [key, value.length > 0 ? value.join(', ') : 'None'];
            }
            return [key, value];
          })
        );
        return (
          <div className="mt-2 space-y-1">
            <p className="text-xs">
              News Type:&nbsp;&nbsp;{formattedMetadata.news_type}
            </p>
            <p className="text-xs">
              Who:&nbsp;&nbsp;{formattedMetadata.who}
            </p>
            <p className="text-xs">
              When:&nbsp;&nbsp;{formattedMetadata.when}
            </p>
            <p className="text-xs">
              Where:&nbsp;&nbsp;{formattedMetadata.where}
            </p>
            <p className="text-xs">
              What:&nbsp;&nbsp;{formattedMetadata.what}
            </p>
            <p className="text-xs">
              Why:&nbsp;&nbsp;{formattedMetadata.why}
            </p>
            <p className="text-xs">
              How:&nbsp;&nbsp;{formattedMetadata.how}
            </p>
          </div>
        );

      case 'extract_knowledge_end':
        const knowledges = data as Knowledge[];
        if (knowledges.length) {
          return (
            <div className="mt-2 space-y-2">
              <p className="text-sm font-medium">
                Found {knowledges.length} Knowledge:
              </p>
              {knowledges.map((knowledge: Knowledge, idx: number) => (
                <div key={idx} className="p-2 bg-white dark:bg-black/20 rounded-md border space-y-1">
                  <p className="text-xs">
                    Term: {knowledge.term}
                  </p>
                  <p className="text-xs">
                    Category: {knowledge.category}
                  </p>
                  {knowledge.description && (
                    <p className="text-xs">
                      Description: {knowledge.description}
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
              Term: {retrievedKnowledge.term}
            </p>
            <p className="text-xs">
              Category: {retrievedKnowledge.category}
            </p>
            <p className="text-xs">
              Definition: {retrievedKnowledge.description || 'No Definition Retrieved'}
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
              <p className="text-xs"><span className="font-medium">Check Point:</span> {searchData.content}</p>
              <p className="text-xs"><span className="font-medium">Check Purpose:</span> {searchData.purpose}</p>
              {searchData.expected_source && (
                <p className="text-xs">
                  <span className="font-medium">Expected Source:</span> {searchData.expected_source}
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
              {/* <p className="text-xs"><span className="font-medium">评估:</span> {statusData.evaluation}</p> */}
              {/* <p className="text-xs"><span className="font-medium">缺失信息:</span> {statusData.missing_information}</p> */}
              <p className="text-xs">{statusData.next_step}</p>

              {statusData.new_evidence && statusData.new_evidence.length > 0 && (
                <div className="mt-1">
                  <p className="text-xs font-medium">New Evidence:</p>
                  {statusData.new_evidence.map((evidence: Evidence, idx: number) => (
                    <div key={idx} className="p-2 bg-white rounded-md border dark:bg-gray-800">
                      <p className="text-xs"><span className="font-medium">Content:</span> {evidence.content}</p>
                      <p className="text-xs"><span className="font-medium">Relationship:</span> {evidence.relationship === 'support' ? 'Support' : 'Refute'}</p>
                      <p className="text-xs"><span className="font-medium">Reasoning:</span> {evidence.reasoning}</p>
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
            <p className="text-xs"><span className="font-medium">Verification Conclusion:</span> {verificationResult.verified ? 'Accept' : 'Reject'}</p>
            <p className="text-xs"><span className="font-medium">Reasoning:</span> {verificationResult.reasoning}</p>
            {verificationResult.updated_purpose && (
              <p className="text-xs"><span className="font-medium">Updated Retrieval Purpose:</span> {verificationResult.updated_purpose}</p>
            )}
            {verificationResult.updated_expected_source && (
              <p className="text-xs"><span className="font-medium">Updated Expected Source:</span> {verificationResult.updated_expected_source}</p>
            )}
          </div>
        );

      case 'generate_answer_end':
        const resultData = data as SearchResult;
        if (resultData) {
          return (
            <div className="mt-2 space-y-1">
              <p className="text-xs"><span className="font-medium">Summary:</span> {resultData.summary}</p>
            </div>
          );
        }
        return null;

      case 'tool_start':
        const toolData = data as ToolStartData;

        if (!toolData) return null;

        switch (toolData.tool_name) {
          case "read_webpage":
            const url = JSON.parse(toolData.input_str).url;
            return (
              <div className="mt-2 space-y-1">
                <p className="text-xs break-all">
                  {url}
                </p>
              </div>
            );

          case "search_google_official":
            const query = JSON.parse(toolData.input_str).query;
            return (
              <div className="mt-2 space-y-1">
                <p className="text-xs break-all">
                  Keywords: {query}
                </p>
              </div>
            );

          default:
            return (
              <div className="mt-2 space-y-1">
                <p className="text-xs break-all">
                  {toolData.input_str.length > 200
                    ? toolData.input_str.slice(0, 200) + '...'
                    : toolData.input_str}
                </p>
              </div>
            );
        }

      case 'tool_end':
        const toolEndData = data as ToolEndData;
        switch (toolEndData.tool_name) {
          case "search_google_official":
            interface GoogleOfficialResult {
              title: string;
              link: string;
              snippet: string;
            }
            const result = JSON.parse(toolEndData.output_str) as GoogleOfficialResult[];
            return (
              <div className='mt-2'>
                <p className="text-xs">
                  {result.length > 0 ? `Viewed ${result.length} results` : 'No results found'}
                </p>
                {result.length > 0 && <div className="mt-2 flex flex-wrap gap-2">
                  {result.map((item) => (
                    <SourceBadge key={item.link} source={item.link} />
                  ))}
                </div>}
              </div>
            );
          case "search_baidu":
            interface BaiduResult {
              title: string;
              link: string;
              snippet: string;
            }
            const baiduResult = JSON.parse(toolEndData.output_str) as BaiduResult[];
            return (
              <div className='mt-2'>
                <p className="text-xs">Viewed {baiduResult.length} results</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {baiduResult.map((item) => (
                    <SourceBadge key={item.link} source={item.link} />
                  ))}
                </div>
              </div>
            );
          case "search_google_alternative":
            interface GoogleAlternativeResult {
              title: string;
              link: string;
              snippet: string;
            }
            const googleAlternativeResult = JSON.parse(toolEndData.output_str) as GoogleAlternativeResult[];
            return (
              <div className='mt-2'>
                <p className="text-xs">
                  {googleAlternativeResult.length > 0 ? `Viewed ${googleAlternativeResult.length} results` : 'No results found'}
                </p>
                {googleAlternativeResult.length > 0 && <div className="mt-2 flex flex-wrap gap-2">
                  {googleAlternativeResult.map((item, idx) => (
                    <SourceBadge key={idx} source={item.link} />
                  ))}
                </div>}
              </div>
            );
          case "read_webpage":
            return null;
          default:
            return (
              <div className="mt-2 space-y-1">
                <p className="text-xs break-all">
                  {toolEndData.output_str}
                </p>
              </div>
            );
        }

      case 'check_if_news_text_end':
        const isNewsText = data as IsNewsText;

        if (!isNewsText.result) {
          return (
            <div className="mt-2 text-sm">
              <p className="text-gray-700 dark:text-gray-300">
                {isNewsText.reason}
              </p>
            </div>
          );
        }

      default:
        return null;
    }
  };

  return (
    <div className={cn("p-3 rounded-md border transition-colors", getEventClass())}>
      <div className="flex items-center gap-2">
        {isLastEvent ? <Loader2Icon className="size-4 animate-spin" /> : <EventIcon />}
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

