import {
    Avatar,
    AvatarFallback,
    AvatarImage,
} from "@/components/ui/avatar"
import { useAuth } from "@/hooks/use-auth";
import { getImagePath } from "@/lib/utils";

export function Profile() {
    const { user } = useAuth();
    const imagePath = getImagePath(user?.avatar)
    return (
        <div
            className="flex flex-col items-center justify-center"
        >
            <Avatar className="h-32 w-32 rounded-full">
                <AvatarImage src={imagePath} alt={user?.email} />
                <AvatarFallback className="rounded-full">CN</AvatarFallback>
            </Avatar>
            <div
                className="flex items-start justify-start py-4"
            >
                {user?.full_name}
            </div>
            <div
                className="flex items-start justify-start py-4"
            >
                {user?.email}
            </div>
        </div>
    )
}
