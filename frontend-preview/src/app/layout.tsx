import type { Metadata } from "next";
import { Hanken_Grotesk, IBM_Plex_Mono, IBM_Plex_Sans, Instrument_Serif, Newsreader, Schibsted_Grotesk } from "next/font/google";
import "./globals.css";

const newsreader = Newsreader({ variable: "--font-newsreader", subsets: ["latin"], style: ["normal", "italic"] });
const hanken = Hanken_Grotesk({ variable: "--font-hanken", subsets: ["latin"] });
const plexSans = IBM_Plex_Sans({ variable: "--font-plex-sans", subsets: ["latin"], weight: ["400", "500", "600"] });
const plexMono = IBM_Plex_Mono({ variable: "--font-plex-mono", subsets: ["latin"], weight: ["400", "500"] });
const instrument = Instrument_Serif({ variable: "--font-instrument", subsets: ["latin"], weight: "400", style: ["normal", "italic"] });
const schibsted = Schibsted_Grotesk({ variable: "--font-schibsted", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Strategic Intelligence Hub",
  description: "Design review: three directions for the AI Research Analyst redesign, with illustrative data.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  const fonts = [newsreader, hanken, plexSans, plexMono, instrument, schibsted].map((f) => f.variable).join(" ");
  return (
    <html lang="en" className={`${fonts} antialiased`}>
      <body>{children}</body>
    </html>
  );
}
