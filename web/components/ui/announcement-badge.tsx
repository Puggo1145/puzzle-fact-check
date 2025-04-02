import type { ComponentProps } from "react"
import { BellIcon, ChevronRightIcon } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from "@/components/ui/dialog"
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import { TypographyP, TypographyList, TypographyMuted } from "../typography"
import { cn } from "@/lib/utils"

export function AnnouncementBadge({ className, ...props }: ComponentProps<"div">) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Badge
          variant="outline"
          className={cn(
            "cursor-pointer flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-full",
            "hover:animate-none hover:bg-blue-200/50",
            "bg-blue-200/30 text-blue-600 border-blue-200 dark:bg-blue-800/30 dark:text-blue-400 dark:border-blue-700",
            className
          )}
          {...props}
        >
          <BellIcon className="size-3.5" />
          关于 Puzzle 已知问题的说明和修复计划
          <ChevronRightIcon className="size-3.5" />
        </Badge>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-1.5">
            关于 Puzzle 已知问题的说明和修复计划
          </DialogTitle>
        </DialogHeader>
        <ScrollArea className="max-h-[55svh]">
          <TypographyP>
            感谢各位用户对 Puzzle 的支持与喜爱。Puzzle 在上线 1 天内收到了许多反馈，部分问题已经定位，并将在近期修复。<br />
            以下是已知问题的说明和修复计划：
          </TypographyP>
          <TypographyList>
            <li>
              1. Bing 搜索工具始终返回空结果，导致 Puzzle 在检索中只能参考有限的中文网络信息，对 Puzzle 在中文事实核查任务中的表现影响较大 <br />
              <TypographyMuted className="mt-1">
                此问题将于本周内修复
              </TypographyMuted>
            </li>
            <li>
              2. 由于参数配置错误，导致无法调用 ChatGPT 4o Latest 模型 <br />
              <TypographyMuted className="mt-1">
                此问题将于本周内修复
              </TypographyMuted>
            </li>
            <li>
              3. 元数据提取智能体有一定概率出错，导致核查中断 <br />
              <TypographyMuted className="mt-1">
                此问题将在本月内修复
              </TypographyMuted>
            </li>
            <li>
              4. 部分模型在输出核查报告时存在轻微的幻觉问题，例如缩小用户提供文本的核查范围。
              这通常是因为用户提供的文本过于模糊或简短，而 Puzzle 被设计为对具体新闻事件进行核查，因此 Puzzle 会尽可能地细化核查范围。
              但这不一定符合用户预期，且可能导致错误结论，我将在未来迭代中改进这一问题。<br />
              <TypographyMuted className="mt-1">
                此问题将在本月内修复
              </TypographyMuted>
            </li>
          </TypographyList>
          <ScrollBar />
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
} 