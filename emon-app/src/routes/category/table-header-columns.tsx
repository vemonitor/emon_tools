import { DataTableColumnHeader } from "@/components/data-table/data-table-column-header"
import { ColumnDef } from "@tanstack/react-table"
import { CrudIconRowActions } from "@/components/data-table/crud-icons-row-actions"
import { CategoryList } from "@/lib/types"

export type Category = {
  id: number
  name: string
}

export const columns: ColumnDef<CategoryList>[] = [
  {
    accessorKey: "id",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Id" />
    ),
  },
 {
    id: "actions",
    cell: ({ row }) => <CrudIconRowActions row={row} base_path="/category/" />,
  },
  {
    accessorKey: "type",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Type" />
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
]