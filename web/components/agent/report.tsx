'use client';

import React, { useEffect, useRef } from 'react';
import { useAgentStore } from '@/stores/use-agent-store';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription
} from '../ui/card';
import { ClipboardCopyIcon, CheckCircleIcon } from 'lucide-react';
import { Button } from '../ui/button';
import {
  TypographyH1,
  TypographyH2,
  TypographyH3,
  TypographyP,
  TypographyList,
  TypographyBlockquote,
  TypographyMuted
} from "@/components/typography"
import { SourceBadge } from "@/components/agent/source-badge";
import ReactMarkdown from 'react-markdown';

// Define verdict labels and colors
const verdictConfig = {
  'true': { label: '真实', color: 'bg-green-500 dark:bg-green-600 text-white' },
  'mostly-true': { label: '大部分真实', color: 'bg-emerald-400 dark:bg-emerald-600 text-white' },
  'mostly-false': { label: '大部分虚假', color: 'bg-orange-500 dark:bg-orange-600 text-white' },
  'false': { label: '虚假', color: 'bg-red-500 dark:bg-red-600 text-white' },
  'no-enough-evidence': { label: '无法证实', color: 'bg-gray-400 dark:bg-gray-600 text-white' },
};

export const Report: React.FC = () => {
  const result = useAgentStore((state) => state.result);
  const [copied, setCopied] = React.useState(false);
  const reportRef = useRef<HTMLDivElement>(null);

  const copyToClipboard = async () => {
    if (!result.report) return;

    try {
      await navigator.clipboard.writeText(result.report);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  useEffect(() => {
    if (result.report && reportRef.current) {
      reportRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [result.report]);

  if (!result.report) {
    return null;
  }

  const verdict = result.verdict || "no-enough-evidence";

  return (
    <Card ref={reportRef} className="mt-4 w-full animate-in fade-in slide-in-from-bottom-4 duration-500 scroll-mt-4">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex flex-col gap-2">
            <CardTitle className="flex items-center gap-2 text-2xl">
              核查报告
              <p className={`w-fit px-2 py-1 rounded text-xs font-medium 
                ${verdictConfig[verdict]?.color || verdictConfig['no-enough-evidence'].color}`
              }>
                {verdictConfig[verdict]?.label || verdictConfig['no-enough-evidence'].label}
              </p>
            </CardTitle>
            <CardDescription>
              <span className="text-sm text-muted-foreground">
                核查报告的撰写格式部分参考自：
              </span>
              <SourceBadge
                source="https://chinafactcheck.com/"
                label="有据国际新闻事实核查"
              />
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={copyToClipboard}
            className="flex items-center gap-1"
          >
            {copied ? (
              <>
                <CheckCircleIcon className="size-4" />
                已复制
              </>
            ) : (
              <>
                <ClipboardCopyIcon className="size-4" />
                复制
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="prose prose-sm dark:prose-invert max-w-none prose-headings:mb-4 prose-headings:mt-6 prose-p:my-4 prose-li:my-2">
          <ReactMarkdown components={{
            h1: ({ ...props }) => <TypographyH1 {...props} />,
            h2: ({ ...props }) => <TypographyH2 {...props} />,
            h3: ({ ...props }) => <TypographyH3 {...props} />,
            ul: ({ ...props }) => <TypographyList {...props} />,
            p: ({ ...props }) => <TypographyP {...props} />,
            ol: ({ ...props }) => <ol className="my-4 ml-6 list-decimal" {...props} />,
            li: ({ ...props }) => <li className="mb-2" {...props} />,
            hr: ({ ...props }) => <hr className="my-4" {...props} />,
            a: ({ ...props }) => <SourceBadge source={props.href || ''} {...props} />,
            code: ({ ...props }) => <SourceBadge source={props.children as string} {...props} />,
            blockquote: ({ ...props }) => <TypographyBlockquote {...props} />,
          }}>
            {result.report}
          </ReactMarkdown>
        </div>
        <TypographyMuted className="pt-6 pb-2 text-center">
          本事实核查报告由 Puzzle AI Agent 完成，AI 可能会出错，请核查重要信息
        </TypographyMuted>
      </CardContent>
    </Card>
  );
}; 