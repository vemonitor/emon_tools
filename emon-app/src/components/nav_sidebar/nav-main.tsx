import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu
} from "@/components/ui/sidebar"
import { SimpleSideMenu, SimpleSideMenuProps } from "@/components/nav_sidebar/simpleMenu";
import { ComposedSideMenu, ComposedSideMenuProps } from "@/components/nav_sidebar/composedMenu";

type NavMainProps = {
  items: ComposedSideMenuProps[] | SimpleSideMenuProps[]
}

export function NavMain({
  items
}: NavMainProps) {
  return (
    <SidebarGroup>
      <SidebarGroupLabel>Platform</SidebarGroupLabel>
      <SidebarMenu>
        {items.map((item, index) => (
          ('items' in item && item.items && item.items.length > 0) ? (
            <ComposedSideMenu key={index} {...item as ComposedSideMenuProps} />
          ) : (
            <SimpleSideMenu key={index} {...item as SimpleSideMenuProps} />
          )
        ))}
      </SidebarMenu>
    </SidebarGroup>
  )
}
