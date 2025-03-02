import * as React from "react"
import {
  Bot,
  Boxes,
  ChartSpline,
  FileArchive,
  FileChartLine,
  Gauge,
  Globe,
  House,
  Settings2,
} from "lucide-react"

import { NavMain } from "@/components/nav_sidebar/nav-main"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"
import { NavUser } from "@/components/nav_sidebar/nav-user"
import { LoginDialog } from "@/components/nav_sidebar/login-dialog"
import { useAuth } from "@/hooks/use-auth"

// This is sample data.
const navMain = [
  {
    key_group: "home",
    title: "Home",
    url: "/",
    icon: House,
    isActive: true
  },
  {
    key_group: "dashboard",
    title: "Dashboard",
    url: "/dashboard",
    icon: Gauge,
    isActive: true
  },
  {
    key_group: "dataViewer",
    title: "PhpFina Viewer",
    icon: ChartSpline,
    isActive: true,
    items: [
      {
        title: "Archived",
        url: "/dataViewer/archive",
        icon: FileArchive,
      },
      {
        title: "Emoncms",
        url: "/dataViewer/emoncms",
        icon: Globe,
      }
    ],
  },
  {
    key_group: "emonHosts",
    title: "Emoncms Hosts",
    icon: Globe,
    isActive: true,
    items: [
      {
        title: "View list",
        url: "/emon-host",
      },
      {
        title: "Add",
        url: "/emon-host/add",
      }
    ],
  },
  {
    key_group: "archiveGroup",
    title: "Archive Group",
    icon: Boxes,
    isActive: true,
    items: [
      {
        title: "View list",
        url: "/archive-group",
      },
      {
        title: "Add",
        url: "/archive-group/add",
      }
    ],
  },
  {
    key_group: "archiveFile",
    title: "Archive File",
    icon: FileChartLine,
    isActive: true,
    items: [
      {
        title: "View list",
        url: "/archive-file",
      },
      {
        title: "Add",
        url: "/archive-file/add",
      }
    ],
  },
  {
    key_group: "emonApi",
    title: "Emoncms Api",
    url: "#",
    icon: Bot,
    items: [
      {
        title: "Inputs",
        url: "#emonApi-Inputs",
      },
      {
        title: "Feeds",
        url: "#emonApi-Feeds",
      },
      {
        title: "Structure",
        url: "#emonApi-Structure",
      },
    ],
  },
  {
    title: "Settings",
    url: "#",
    icon: Settings2,
    items: [
      {
        title: "General",
        url: "#",
      },
      {
        title: "Team",
        url: "#",
      },
      {
        title: "Billing",
        url: "#",
      },
      {
        title: "Limits",
        url: "#",
      },
    ],
  },
]

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { isAuthenticated, user } = useAuth();
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        
      </SidebarHeader>
      <SidebarContent>
        <NavMain
          items={navMain}
        />
      </SidebarContent>
      <SidebarFooter>
        {isAuthenticated ? (
          <NavUser 
            user={user}
          />
        ) : (
          <LoginDialog />
        )}
        
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
