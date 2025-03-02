import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Link, useLocation } from "react-router";
import { routes } from "./routes";

export function Breadcrumbs() {
  const location = useLocation();
  //const [crumbs, setCrumbs] = useState<User | null>(null);
  const crumbs = routes.reduce((res, route) => {
    const is_parent = location.pathname.includes(route.path);
    const has_child = route.routes
    if (is_parent && has_child) {
      const childs =  route.routes.filter((subroute) => {
        return location.pathname.includes(`${route.path}/${subroute.path}`);
      });
      res.push(route);
      if (childs.length > 0) {  
        res = res.concat(childs);
      }
    }
    else if (is_parent) {
      res.push(route);
    }
    return res;
  }, [])
  /*setCrumbs(routes.filter((route) => {
    return location.pathname.includes(route.path);
  }));*/

  const nb_crumbs = crumbs !== null ? crumbs.length : 0;
  if (nb_crumbs === 0) {
    return null;
  }
  return (
    <Breadcrumb>
      <BreadcrumbList>
        {crumbs && crumbs.map((crumb, i: number) => [
          (<BreadcrumbItem key={i}>
            {i<nb_crumbs-1 ? (
              <BreadcrumbLink asChild>
                <Link to={crumb.path}>{crumb.title}</Link>
              </BreadcrumbLink>
            ) : (
              crumb.title
            )}
            
          </BreadcrumbItem>),
          ((nb_crumbs > 1 && i >= 0) || i > 0) && i<nb_crumbs-1 ? (<BreadcrumbSeparator key={`sep_${i}`} />) : null,
        ]
        )}
      </BreadcrumbList>
    </Breadcrumb>
  )
}