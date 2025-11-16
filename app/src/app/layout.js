import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/Shared/Header";
import { AnimatedGraphBackground } from "@/components/Shared/AnimatedGraphBackground";
import { LayoutWrapper } from "@/components/Shared/LayoutWrapper";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "EpiHelix - Pandemic Insights Explorer",
  description: "Knowledge Graph for exploring pandemic data, cases, vaccinations, and insights from historical and real-time sources.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased flex flex-col min-h-screen`}
      >
        {/* Animated Graph Background */}
        <AnimatedGraphBackground />
        
        {/* Content Layer */}
        <div className="relative z-10 flex flex-col min-h-screen">
          <Header />
          <LayoutWrapper>{children}</LayoutWrapper>
        </div>
      </body>
    </html>
  );
}
