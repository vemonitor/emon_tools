import { AlertCircle } from "lucide-react"
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "@/components/ui/alert"

export type AlertErrorProps = {
    title?: string;
    message: string;
}

export function AlertError({
    title,
    message
}: AlertErrorProps) {
    // Your session has expired. Please log in again.
  return (
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>{title ? title : "Error"}</AlertTitle>
      <AlertDescription>
        {message}
      </AlertDescription>
    </Alert>
  )
}
