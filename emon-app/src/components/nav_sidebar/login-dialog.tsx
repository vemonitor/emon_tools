import { Button } from "@/components/ui/button"
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";
import {
  Dialog,
  DialogContent,
  DialogTrigger,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { LoginForm } from "@/routes/user/login-form"

export function LoginDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Login</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px] border-none">
        <DialogHeader>
          <DialogTitle><VisuallyHidden>Login Form Dialog</VisuallyHidden></DialogTitle>
          <DialogDescription>
            <VisuallyHidden>Enter credentials to login.</VisuallyHidden>
          </DialogDescription>
        </DialogHeader>
        <div className="p-3">
          <LoginForm />
        </div>
      </DialogContent>
    </Dialog>
  )
}