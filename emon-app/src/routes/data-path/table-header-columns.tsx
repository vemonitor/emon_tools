import { DataTableColumnHeader } from "@/components/data-table/data-table-column-header"
import { ColumnDef } from "@tanstack/react-table"
import { CrudIconRowActions } from "@/components/data-table/crud-icons-row-actions"
import { DataPathList } from "@/lib/types"

export type DataPath = {
  id: number
  name: string
  slug: string
  path_type: string
  file_type: string
  path: string
}

export const columns: ColumnDef<DataPathList>[] = [
  {
    accessorKey: "id",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Id" />
    ),
  },
 {
    id: "actions",
    cell: ({ row }) => <CrudIconRowActions row={row} base_path="/data-path/" by_slug={true} />,
  },
  {
    accessorKey: "path_type",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Type" />
    ),
  },
  {
    accessorKey: "file_type",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="File Type" />
    ),
  },
  {
    accessorKey: "name",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Name" />
    ),
  },
  {
    accessorKey: "slug",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Slug" />
    ),
  },
  {
    accessorKey: "path",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Path" />
    ),
  },
  
]