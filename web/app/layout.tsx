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
        <div className="w-full flex flex-col items-center">
          <header className="fixed top-4 left-4 w-full flex items-center gap-2">
            <Logo />
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
