import "./globals.css";
import { ReactNode } from "react";
import { Geist } from "next/font/google";
import { QueryProvider } from "../components/QueryProvider";

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className={geistSans.variable}>
        <QueryProvider>
          {children}
        </QueryProvider>
      </body>
    </html>
  );
}
