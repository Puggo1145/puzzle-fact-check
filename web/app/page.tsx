import { Hero } from "./_components/hero";
import { InputPanel } from "./_components/input-panel";

export default function Home() {
  return (
    <div className="w-[1440px] h-screen flex flex-col items-center justify-center gap-4">
      <Hero />
      <InputPanel />
      <p className="text-xs text-muted-foreground/50">AI can make mistakes, please verify the information.</p>
    </div>
  );
}
