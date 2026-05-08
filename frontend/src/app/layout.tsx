import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PortfolioMatch — AI Job Matcher for Engineers",
  description:
    "Match your GitHub portfolio to engineering jobs. Code-level skill detection. Honest gap analysis. Built for SEA + remote markets.",
  metadataBase: new URL("https://github.com/Venta02/portfoliomatch"),
  openGraph: {
    title: "PortfolioMatch",
    description: "AI-powered job matching based on your actual GitHub code",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
