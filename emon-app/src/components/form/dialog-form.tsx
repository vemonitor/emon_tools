import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { ReactNode } from "react"
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";
type DialogFormProps = {
    title: string;
    description?: string;
    trigger: ReactNode;
    form: ReactNode;
    footer?: ReactNode;
    dialogOpen: boolean;
    dialogSetOpen: (value: boolean) => void
}

export default function DialogForm({
    title,
    description,
    trigger,
    form,
    footer,
    dialogOpen,
    dialogSetOpen
}: DialogFormProps) {
    return (
        <Dialog open={dialogOpen} onOpenChange={dialogSetOpen}>
            <DialogTrigger asChild>
                {trigger}
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>{title}</DialogTitle>
                    {description ? (
                        <DialogDescription>
                            {description}
                        </DialogDescription>
                    ) : (
                        <DialogDescription>
                            <VisuallyHidden>Dialog Form.</VisuallyHidden>
                        </DialogDescription>
                    )}
                </DialogHeader>
                {form}
                {footer && (
                    <DialogFooter>
                        {footer}
                    </DialogFooter>
                )}
                
            </DialogContent>
        </Dialog>
    )
}
