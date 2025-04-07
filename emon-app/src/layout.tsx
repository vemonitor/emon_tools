import { AppSidebar } from "@/routes/app-sidebar";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Toaster } from "@/components/ui/toaster";
import { Breadcrumbs } from "@/routes/breadcrumbs";
import { ReactNode } from "react";
import GitHubIcon from "./components/icons/GitHubIcon";

type LayoutProps = {
  children: ReactNode;
}

export default function Layout({
  children
}: LayoutProps) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex items-center justify-between h-20 px-6 bg-secondary shadow-md">
          {/* Left side: sidebar trigger, branding and breadcrumbs */}
          <div className="flex items-center gap-4">
            <SidebarTrigger className="text-primary" />
            <div className="hidden md:flex items-center gap-2">
              <img src="/public/emon_tools_logo.png" width={40} alt="Emon Tools Logo" className="h-8 w-auto" />
            </div>
            <Separator orientation="vertical" className="h-6" />
            <Breadcrumbs />
          </div>
          {/* Right side: optional header actions */}
          <div className="flex items-center gap-4">
            {/* Example action: notification or search button */}
            <a href="https://github.com/vemonitor/emon_tools" target="_blank" rel="noopener noreferrer">
              <button className="p-2 rounded-full hover:bg-muted transition-colors">
                {/* Example icon (replace with your icon) */}
                <GitHubIcon size={25} className="" />
              </button>
            </a>
            {/* Additional actions can be added here */}
          </div>
        </header>
        <div className="min-h-[100vh] md:min-h-min">
          {children}
        </div>
        <Toaster />
      </SidebarInset>
    </SidebarProvider>
  )
}