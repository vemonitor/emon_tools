import {
  Boxes,
  ChartSpline,
  FileChartLine,
  Gauge,
  Globe,
  House,
  KeyRound,
  LogIn,
  User,
  UserRoundX,
} from "lucide-react"

import Dashboard from '@/routes/dashboard/dashboard';
import Login from '@/routes/user/login';
import Home from '@/routes/home/home';
import AddEmonHost from "./emon-host/add";
import ViewEmonHost from "./emon-host/view";
import EditEmonHost from "./emon-host/edit";
import ListEmonHost from "./emon-host/list";
import ListCategory from "./category/list";
import AddCategory from "./category/add";
import EditCategory from "./category/edit";
import ListArchiveFile from "./archive-file/list";
import AddArchiveFile from "./archive-file/add";
import EditArchiveFile from "./archive-file/edit";
import DeleteCategory from "./category/delete";
import DeleteEmonHost from "./emon-host/delete";
import DeleteArchiveFile from "./archive-file/delete";
import ListDataPath from "./data-path/list";
import AddDataPath from "./data-path/add";
import EditDataPath from "./data-path/edit";
import DeleteDataPath from "./data-path/delete";
import ViewDataPath from "./data-path/view";
import { ComponentType } from "react";
import Logout from "./user/logout";
import EditProfile from "./user/edit-profile";
import { Profile } from "./user/profile";
import { HostedViewer } from "./graph-feed/hostedViewer";
import { FinaViewer } from "./graph-fina/finaViewer";
import ViewArchiveFile from "./archive-file/view";

export const crudRoutes = [
  {
    title: "Add",
    path: "add",
  },
  {
    title: "View",
    path: "view/:item_id",
  },
  {
    title: "Edit",
    path: "edit/:item_id",
  },
  {
    title: "Delete",
    path: "delete/:item_id",
  }
]

export interface RouteListType {
  key_group?: string;
  title: string;
  path: string;
  icon?: ComponentType;
  element: ComponentType;
  routes?: RouteListType[];
}

export const publicRoutes: RouteListType[] = [
  {
    key_group: "home",
    title: "Home",
    path: "/",
    icon: House,
    element: Home,
  }
]


export const privateRoutes: RouteListType[] = [
  {
    key_group: "dashboard",
    title: "Dashboard",
    path: "/dashboard",
    icon: Gauge,
    element: Dashboard,
  },
  {
    key_group: "login",
    title: "Login",
    path: "/login",
    icon: KeyRound,
    element: Login,
  },
  {
    key_group: "logout",
    title: "Logout",
    path: "/logout",
    icon: UserRoundX,
    element: Logout,
  },
  {
    key_group: "signIn",
    title: "Sign In",
    path: "/sign-in",
    icon: LogIn,
    element: Login,
  },
  {
    key_group: "profile",
    title: "Profile",
    path: "/profile",
    icon: User,
    element: Profile,
    routes: [
      {
        title: "Edit Profile",
        path: "edit/",
        icon: LogIn,
        element: EditProfile,
      }
    ]
  },
  {
    key_group: "dataViewer",
    title: "PhpFina Viewer",
    icon: ChartSpline,
    path: "/dataViewer/",
    element: FinaViewer,
    routes: [
      {
        title: "Hosted",
        path: "hosted/:host_slug?",
        element: HostedViewer,
      },
      {
        title: "Fina",
        path: "fina/:host_slug?",
        element: FinaViewer,
      },
    ],
  },
  {
    key_group: "emonHosts",
    title: "Emoncms Hosts",
    icon: Globe,
    path: "/emon-host",
    element: ListEmonHost,
    routes: [
      {
        title: "Add",
        path: "add",
        element: AddEmonHost,
      },
      {
        title: "View",
        path: "view/:host_slug",
        element: ViewEmonHost,
      },
      {
        title: "Edit",
        path: "edit/:host_id",
        element: EditEmonHost,
      },
      {
        title: "Delete",
        path: "delete/:host_id",
        element: DeleteEmonHost,
      }
    ],
  },
  {
    key_group: "category",
    title: "Category",
    icon: Boxes,
    path: "/category",
    element: ListCategory,
    routes: [
      {
        title: "Add",
        path: "add",
        element: AddCategory,
      },
      {
        title: "View",
        path: "view/:category_id",
        element: ListCategory,
      },
      {
        title: "Edit",
        path: "edit/:category_id",
        element: EditCategory,
      },
      {
        title: "Delete",
        path: "delete/:category_id",
        element: DeleteCategory,
      }
    ],
  },
  {
    key_group: "dataPath",
    title: "Data Path",
    icon: Boxes,
    path: "/data-path",
    element: ListDataPath,
    routes: [
      {
        title: "Add",
        path: "add",
        element: AddDataPath,
      },
      {
        title: "View",
        path: "view/:path_slug",
        element: ViewDataPath,
      },
      {
        title: "Edit",
        path: "edit/:path_id",
        element: EditDataPath,
      },
      {
        title: "Delete",
        path: "delete/:path_id",
        element: DeleteDataPath,
      }
    ],
  },
  {
    key_group: "archiveFile",
    title: "Archive File",
    icon: FileChartLine,
    path: "/archive-file",
    element: ListArchiveFile,
    routes: [
      {
        title: "Add",
        path: "add",
        element: AddArchiveFile,
      },
      {
        title: "View",
        path: "view/:file_id",
        element: ViewArchiveFile,
      },
      {
        title: "Edit",
        path: "edit/:file_id",
        element: EditArchiveFile,
      },
      {
        title: "Delete",
        path: "delete/:file_id",
        element: DeleteArchiveFile,
      }
    ],
  }
];