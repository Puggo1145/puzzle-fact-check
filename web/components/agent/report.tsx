'use client';

import React, { useEffect, useRef } from 'react';
import { useAgentStore } from '@/lib/store';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription
} from '../ui/card';
import { FileTextIcon, ClipboardCopyIcon, CheckCircleIcon } from 'lucide-react';
import { Button } from '../ui/button';
import ReactMarkdown from 'react-markdown';

export const Report: React.FC = () => {
  const finalReport = useAgentStore((state) => state.finalReport);
  const [copied, setCopied] = React.useState(false);
  const reportRef = useRef<HTMLDivElement>(null);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(finalReport);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  // Scroll report into view when it appears
  useEffect(() => {
    if (finalReport && reportRef.current) {
      reportRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, [finalReport]);

  // Don't render anything if no report is available
  if (!finalReport) {
    return null;
  }

  return (
    <Card ref={reportRef} className="w-full animate-in fade-in slide-in-from-bottom-4 duration-500 scroll-mt-4">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex flex-col gap-2">
            <CardTitle className="flex items-center gap-2">
              <FileTextIcon className="size-5" />
              事实核查报告
            </CardTitle>
            <CardDescription>
              Puzzle 目前不提供报告保存功能，请确保您已经保存了报告
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
            h1: ({node, ...props}) => <h1 className="text-2xl font-bold border-b pb-2 mb-6" {...props} />,
            h2: ({node, ...props}) => <h2 className="text-xl font-semibold mt-8 mb-4" {...props} />,
            h3: ({node, ...props}) => <h3 className="text-lg font-medium mt-6" {...props} />,
            ul: ({node, ...props}) => <ul className="my-4 ml-6 list-disc" {...props} />,
            ol: ({node, ...props}) => <ol className="my-4 ml-6 list-decimal" {...props} />,
            li: ({node, ...props}) => <li className="mb-2" {...props} />
          }}>
            {finalReport}
          </ReactMarkdown>
        </div>
      </CardContent>
    </Card>
  );
}; 