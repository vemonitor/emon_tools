import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu
} from "@/components/ui/sidebar"
import { SimpleSideMenu, SimpleSideMenuProps } from "@/components/nav_sidebar/simpleMenu";
import { ComposedSideMenu, ComposedSideMenuProps } from "@/components/nav_sidebar/composedMenu";
import { useAuth } from "@/hooks/use-auth";

type NavMainProps = {
  items: ComposedSideMenuProps[] | SimpleSideMenuProps[];
}

export function NavMain({
  items
}: NavMainProps) {
  const { isAuthenticated } = useAuth();
  const isItemMenu = (isPublic?: boolean): boolean => {
    return (
      !isPublic && isAuthenticated === true
    ) || isPublic === true
  }
  return (
    <SidebarGroup>
      <SidebarGroupLabel>Menu</SidebarGroupLabel>
      <SidebarMenu>
        {items.map((item: ComposedSideMenuProps | SimpleSideMenuProps, index) => (
          'items' in item && item.items && item.items.length > 0 ? (
            isItemMenu(item.isPublic) ? (
              <ComposedSideMenu key={index} {...item as ComposedSideMenuProps} />
            ) : null
          ) : (
            isItemMenu(item.isPublic) ? (
              <SimpleSideMenu key={index} {...item as SimpleSideMenuProps} />
            ) : null
          )
        ))}
      </SidebarMenu>
    </SidebarGroup>
  )
}
