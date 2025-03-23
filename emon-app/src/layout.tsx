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
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <Breadcrumbs />
          </div>
        </header>
        <div className="min-h-[100vh] md:min-h-min px-4">
          {children}
        </div>
        <Toaster />
      </SidebarInset>
    </SidebarProvider>
  )
}