import { DataTableColumnHeader } from "@/components/data-table/data-table-column-header"
import { ColumnDef } from "@tanstack/react-table"
import { CrudIconRowActions } from "@/components/data-table/crud-icons-row-actions"
import { ArchiveGroupList } from "@/lib/types"


export const columns: ColumnDef<ArchiveGroupList>[] = [
  {
    accessorKey: "id",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Id" />
    ),
  },
  {
    id: "actions",
    cell: ({ row }) => <CrudIconRowActions row={row} base_path="/archive-group/" />,
  },
  {
    accessorKey: "name",
    header: ({ column }) => (
      <DataTableColumnHeader column={column} title="Name" />
    ),
  },
]