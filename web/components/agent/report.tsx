'use client';

import React from 'react';
import { useAgentStore } from '@/lib/store';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { FileTextIcon, ClipboardCopyIcon, CheckCircleIcon } from 'lucide-react';
import { Button } from '../ui/button';

export const Report: React.FC = () => {
  const finalReport = useAgentStore((state) => state.finalReport);
  const [copied, setCopied] = React.useState(false);
  
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(finalReport);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };
  
  // Don't render anything if no report is available
  if (!finalReport) {
    return null;
  }
  
  return (
    <Card className="w-full animate-in fade-in slide-in-from-bottom-4 duration-500">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <FileTextIcon className="size-5" />
            事实核查报告
          </CardTitle>
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
        <div className="prose prose-sm max-w-none">
          {finalReport.split('\n').map((line, index) => (
            <React.Fragment key={index}>
              {line}
              <br />
            </React.Fragment>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}; 