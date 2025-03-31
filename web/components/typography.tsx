import type { ComponentProps } from "react"

export function TypographyH1({ children, ...props }: ComponentProps<"h1">) {
    return (
        <h1 className="scroll-m-20 text-2xl font-extrabold tracking-tight lg:text-3xl" {...props}>
            {children}
        </h1>
    )
}

export function TypographyH2({ children, ...props }: ComponentProps<"h2">) {
    return (
        <h2 className="scroll-m-20 pb-2 text-xl font-semibold tracking-tight first:mt-0" {...props}>
            {children}
        </h2>
    )
}

export function TypographyH3({ children, ...props }: ComponentProps<"h3">) {
    return (
        <h3 className="scroll-m-20 text-lg font-semibold tracking-tight" {...props}>
            {children}
        </h3>
    )
}

export function TypographyH4({ children, ...props }: ComponentProps<"h4">) {
    return (
        <h4 className="scroll-m-20 text-base font-semibold tracking-tight" {...props}>
            {children}
        </h4>
    )
}

export function TypographyP({ children, ...props }: ComponentProps<"p">) {
    return (
        <p className="leading-7 [&:not(:first-child)]:mt-4" {...props}>
            {children}
        </p>
    )
}

export function TypographyBlockquote({ children, ...props }: ComponentProps<"blockquote">) {
    return (
        <blockquote className="mt-6 border-l-2 pl-6 italic" {...props}>
            {children}
        </blockquote>
    )
}

export function TypographyInlineCode({ children, ...props }: ComponentProps<"code">) {
    return (
        <code className="relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm font-semibold" {...props}>
            {children}
        </code>
    )
}

export function TypographyLead({ children, ...props }: ComponentProps<"p">) {
    return (
        <p className="text-xl text-muted-foreground" {...props}>
            {children}
        </p>
    )
}

export function TypographyLarge({ children, ...props }: ComponentProps<"div">) {
    return <div className="text-lg font-semibold" {...props}>
        {children}
    </div>
}

export function TypographySmall({ children, ...props }: ComponentProps<"small">) {
    return (
        <small className="text-sm font-medium leading-none" {...props}>
            {children}
        </small>
    )
}

export function TypographyMuted({ children, ...props }: ComponentProps<"p">) {
    return (
        <p className="text-sm text-muted-foreground" {...props}>
            {children}
        </p>
    )
}

export function TypographyList({ children, ...props }: ComponentProps<"ul">) {
    return (
      <ul className="my-2 ml-6 list-disc [&>li]:mt-2" {...props}>
        {children}
      </ul>
    )
  }
  