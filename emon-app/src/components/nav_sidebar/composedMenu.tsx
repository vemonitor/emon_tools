import { ChevronRight, type LucideIcon } from "lucide-react"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar"
import { NavLink } from "react-router";

import { createElement } from "react";

export type ComposedSideMenuProps = {
    title: string
    isActive?: boolean
    icon?: LucideIcon
    items?: {
        title: string
        url: string
    }[]
}

export function ComposedSideMenu({
    title,
    isActive,
    icon,
    items
  }: ComposedSideMenuProps) {
    return (
      <Collapsible
        key={title}
        asChild
        defaultOpen={isActive}
        className="group/collapsible"
      >
        <SidebarMenuItem>
          <CollapsibleTrigger asChild>
            <SidebarMenuButton tooltip={title}>
              {icon && createElement(icon)}
              <span>{title}</span>
              <ChevronRight className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
            </SidebarMenuButton>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <SidebarMenuSub>
              {items?.map((subItem) => (
                <SidebarMenuSubItem key={subItem.title}>
                  <SidebarMenuSubButton asChild>
                    <NavLink to={subItem.url}>{subItem.title}</NavLink>
                  </SidebarMenuSubButton>
                </SidebarMenuSubItem>
              ))}
            </SidebarMenuSub>
          </CollapsibleContent>
        </SidebarMenuItem>
      </Collapsible>
    )
  }