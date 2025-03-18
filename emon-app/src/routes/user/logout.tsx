import { Loader } from "@/components/layout/loader";
import { useAuth } from "@/hooks/use-auth";
import { useEffect } from "react";
import { useNavigate } from "react-router";

export default function Logout() {
    const navigate = useNavigate();
    const { logout } = useAuth();
    useEffect(() => {
        logout()
        navigate("/");
    }, [logout, navigate]);

    return (
        <Loader />
    )
}
