import { Row } from "@tanstack/react-table"
import { Link } from "react-router"
import { Button } from "@/components/ui/button"
import { Eye, Pencil, Trash2 } from "lucide-react"

interface CrudIconRowActionsProps<TData extends { id: string | number }> {
  row: Row<TData>,
  base_path: string,
  by_slug?: boolean
}

export function CrudIconRowActions<TData extends { id: string | number, slug?: string }>({
  row,
  base_path,
  by_slug = false
}: CrudIconRowActionsProps<TData>) {
  const row_id = row.original.id
  const row_slug = row.original.slug
  return (
    <div className="flex items-center space-x-2">
      <Button
        title="View"
        variant="ghost"
        asChild
      >
        <Link to={`${base_path}view/${by_slug ? row_slug : row_id}`}><Eye /></Link>
      </Button>
      <Button
        title="Edit"
        variant="ghost"
        asChild
      >
          <Link to={`${base_path}edit/${row_id}`}><Pencil /></Link>
      </Button>
      <Button
        title="Delete"
        variant="ghost"
        asChild
      >
        <Link to={`${base_path}delete/${row_id}`}><Trash2 /></Link>
      </Button>
    </div>
  )
}