import type { Metadata } from "next";
import { Fira_Sans, Playfair_Display } from "next/font/google";
import "./globals.css";

import { Logo } from "@/components/logo";

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
    <html lang="en">
      <body className={`bg-muted ${firaSans.variable} ${playfairDisplay.variable}`}>
        <div className="w-full h-screen flex flex-col items-center">
          <header className="z-50 px-4 py-6 bg-muted w-full flex items-center gap-2">
            <Logo />
          </header>
          <div className="flex-1 w-full">
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}
