import { Button } from "@/components/ui/button";
import { Link } from "react-router";
import { AlertTriangle } from "lucide-react";

export default function Error404() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground px-4">
      <AlertTriangle className="w-20 h-20 text-destructive mb-4" strokeWidth={1.5} />

      <h1 className="text-6xl font-bold mb-2">404</h1>
      <p className="text-xl mb-4 text-muted-foreground">Oops! Page not found.</p>

      <p className="text-center max-w-md text-base mb-6">
        The page you're looking for doesn't exist or may have been moved. You can always head back to the homepage.
      </p>

      <Button asChild>
        <Link to="/">Go to Homepage</Link>
      </Button>
    </div>
  )
}
