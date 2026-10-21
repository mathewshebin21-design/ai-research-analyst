import { SessionProvider } from "@/components/app/session";
import { Shell } from "@/components/app/shell";

export default function AppLayout({ children }: LayoutProps<"/app">) {
  return (
    <SessionProvider>
      <Shell>{children}</Shell>
    </SessionProvider>
  );
}
