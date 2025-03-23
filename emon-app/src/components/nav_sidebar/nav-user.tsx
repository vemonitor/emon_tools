import {
    BadgeCheck,
    Bell,
    ChevronsUpDown,
    LogOut,
  } from "lucide-react"
  
  import {
    Avatar,
    AvatarFallback,
    AvatarImage,
  } from "@/components/ui/avatar"
  import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
  } from "@/components/ui/dropdown-menu"
  import {
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    useSidebar,
  } from "@/components/ui/sidebar"
import { useAuth } from "@/hooks/use-auth"
import { Link } from "react-router"
import { getImagePath } from "@/lib/utils"
  
  export function NavUser() {
    const { isMobile } = useSidebar()
    const { isAuthenticated, user } = useAuth();
    if (!isAuthenticated || !user) {
      return null
    }
    const imagePath = getImagePath(user?.avatar)
    return (
      <SidebarMenu>
        <SidebarMenuItem>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <SidebarMenuButton
                size="lg"
                className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
              >
                <Avatar className="h-8 w-8 rounded-3xl">
                  <AvatarImage src={imagePath} alt={user.full_name} />
                  <AvatarFallback className="rounded-lg">CN</AvatarFallback>
                </Avatar>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">{user.full_name}</span>
                  <span className="truncate text-xs">{user.email}</span>
                </div>
                <ChevronsUpDown className="ml-auto size-4" />
              </SidebarMenuButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-lg"
              side={isMobile ? "bottom" : "right"}
              align="end"
              sideOffset={4}
            >
              <DropdownMenuLabel className="p-0 font-normal">
                <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                  <Avatar className="h-8 w-8 rounded-3xl">
                    <AvatarImage src={imagePath} alt={user.full_name} />
                    <AvatarFallback className="rounded-lg">CN</AvatarFallback>
                  </Avatar>
                  <div className="grid flex-1 text-left text-sm leading-tight">
                    <span className="truncate font-semibold">{user.full_name}</span>
                    <span className="truncate text-xs">{user.email}</span>
                  </div>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              
              <DropdownMenuGroup>
                <DropdownMenuItem>
                  <BadgeCheck />
                  <Link to="/profile">Profile</Link>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <BadgeCheck />
                  <Link to={`/profile/edit/`}>Edit Profile</Link>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Bell />
                  Notifications
                </DropdownMenuItem>
              </DropdownMenuGroup>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <div className="w-full">
                  <LogOut />
                  <Link to="/logout" className="w-full">Log out</Link>
                </div>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarMenuItem>
      </SidebarMenu>
    )
  }