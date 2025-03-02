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
import { DataViewer } from "./data-viewer/dataViewer";
import AddEmonHost from "./emon-host/add";
import ViewEmonHost from "./emon-host/view";
import EditEmonHost from "./emon-host/edit";
import ListEmonHost from "./emon-host/list";
import ListArchiveGroup from "./archive-group/list";
import AddArchiveGroup from "./archive-group/add";
import EditArchiveGroup from "./archive-group/edit";
import ListArchiveFile from "./archive-file/list";
import AddArchiveFile from "./archive-file/add";
import EditArchiveFile from "./archive-file/edit";
import DeleteArchiveGroup from "./archive-group/delete";
import DeleteEmonHost from "./emon-host/delete";
import DeleteArchiveFile from "./archive-file/delete";

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

export const routes = [
    {
      key_group: "home",
      title: "Home",
      path: "/",
      icon: House,
      element: Home,
    },
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
      element: Login,
    },
    {
      key_group: "signIn",
      title: "Sign In",
      path: "/sign-in",
      icon: LogIn,
      element: Login,
    },
    {
      key_group: "account",
      title: "Account",
      path: "/account",
      icon: User,
      element: Login,
      routes: [
        {
          title: "Edit Profile",
          path: "edit",
          icon: LogIn,
          element: Login,
        }
      ]
    },
    {
      key_group: "dataViewer",
      title: "PhpFina Viewer",
      icon: ChartSpline,
      path: "/dataViewer/:source_ref",
      element: DataViewer,
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
          path: "view/:item_id",
          element: ViewEmonHost,
        },
        {
          title: "Edit",
          path: "edit/:item_id",
          element: EditEmonHost,
        },
        {
          title: "Delete",
          path: "delete/:item_id",
          element: DeleteEmonHost,
        }
      ],
    },
    {
      key_group: "archiveGroup",
      title: "Archive Group",
      icon: Boxes,
      path: "/archive-group",
      element: ListArchiveGroup,
      routes: [
        {
          title: "Add",
          path: "add",
          element: AddArchiveGroup,
        },
        {
          title: "View",
          path: "view/:item_id",
          element: ListArchiveGroup,
        },
        {
          title: "Edit",
          path: "edit/:item_id",
          element: EditArchiveGroup,
        },
        {
          title: "Delete",
          path: "delete/:item_id",
          element: DeleteArchiveGroup,
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
          path: "view/:item_id",
          element: DataViewer,
        },
        {
          title: "Edit",
          path: "edit/:item_id",
          element: EditArchiveFile,
        },
        {
          title: "Delete",
          path: "delete/:item_id",
          element: DeleteArchiveFile,
        }
      ],
    }
  ]