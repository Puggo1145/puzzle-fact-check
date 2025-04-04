import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/react";
import { Fira_Sans, Playfair_Display } from "next/font/google";
import "./globals.css";

// components
import { Header } from "@/components/header";
// providers
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/sonner";

const firaSans = Fira_Sans({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-fira-sans",
});

const playfairDisplay = Playfair_Display({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--font-playfair-display",
});

export const metadata: Metadata = {
  title: "Puzzle Fact Check",
  description: "Debunk fake news with confidence",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`bg-muted ${firaSans.variable} ${playfairDisplay.variable}`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="w-screen h-[100svh] flex flex-col">
            <Header />
            <div className="w-full flex-1">
              {children}
            </div>
          </div>
        </ThemeProvider>
        <Toaster />
        <Analytics />
      </body>
    </html>
  );
}
