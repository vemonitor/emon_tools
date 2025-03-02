import { LucideIcon } from "lucide-react"
import {
  SidebarMenuButton,
  SidebarMenuItem
} from "@/components/ui/sidebar"
import { NavLink } from "react-router";
import { createElement } from "react";

export type SimpleSideMenuProps = {
    title: string
    url: string
    icon?: LucideIcon
}

export function SimpleSideMenu({
    title,
    url,
    icon
  }: SimpleSideMenuProps) {
    return (
      <SidebarMenuItem>
        <SidebarMenuButton tooltip={title}>
          {icon && createElement(icon)}
          <NavLink to={url}>{title}</NavLink>
        </SidebarMenuButton>
      </SidebarMenuItem>
    )
  }