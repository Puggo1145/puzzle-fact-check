import Link from "next/link"
import { GithubIcon } from "lucide-react"

import { Logo } from "@/components/logo"
import { ModeToggle } from "@/components/theme-toggle"
import { Button } from "@/components/ui/button"

export function Header() {
  return (
    <header className="z-50 px-4 py-4 w-full flex items-center justify-between">
      <Logo />
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          asChild
          aria-label="GitHub Repository"
          className="hover:bg-muted-foreground/10"
        >
          <Link 
            href="https://github.com/Puggo1145/puzzle-fact-check" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            
            <GithubIcon className="size-4" />
          </Link>
        </Button>
        <ModeToggle />
      </div>
    </header>
  )
} 