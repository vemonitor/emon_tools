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
import { ComponentProps, useEffect } from "react"


const navMain = [
  {
    key_group: "home",
    title: "Home",
    url: "/",
    icon: House,
    isActive: true,
    isPublic: true
  },
  {
    key_group: "dashboard",
    title: "Dashboard",
    url: "/dashboard",
    icon: Gauge,
    isActive: true,
    isPublic: false
  },
  {
    key_group: "dataViewer",
    title: "Data Viewer",
    icon: ChartSpline,
    isActive: false,
    isPublic: false,
    items: [
      {
        title: "Hosted",
        url: "/dataViewer/hosted",
        icon: FileArchive,
      },
      {
        title: "PhpFina",
        url: "/dataViewer/fina",
        icon: Globe,
      }
    ],
  },
  {
    key_group: "emonHosts",
    title: "Emoncms Hosts",
    icon: Globe,
    isActive: false,
    isPublic: false,
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
    key_group: "category",
    title: "Category",
    icon: Boxes,
    isActive: false,
    isPublic: false,
    items: [
      {
        title: "View list",
        url: "/category",
      },
      {
        title: "Add",
        url: "/category/add",
      }
    ],
  },
  {
    key_group: "dataPath",
    title: "DataPath",
    icon: Boxes,
    isActive: false,
    isPublic: false,
    items: [
      {
        title: "View list",
        url: "/data-path",
      },
      {
        title: "Add",
        url: "/data-path/add",
      }
    ],
  },
  {
    key_group: "archiveFile",
    title: "Archive File",
    icon: FileChartLine,
    isActive: true,
    isPublic: false,
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
    isPublic: false,
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
    isPublic: false,
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

type AppSidebarProps = ComponentProps<typeof Sidebar>

export function AppSidebar({
  ...props
}: AppSidebarProps) {
  const { isAuthenticated } = useAuth();
  useEffect(() => {
    return;
  }, [isAuthenticated]);
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
          <NavUser />
        ) : (
          <LoginDialog />
        )}

      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
