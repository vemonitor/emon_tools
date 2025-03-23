import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import {
    Avatar,
    AvatarFallback,
    AvatarImage,
} from "@/components/ui/avatar"
import { ChartConfig, ChartContainer, ChartLegend, ChartLegendContent, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { useAuth } from "@/hooks/use-auth";
import { useQuery } from "@tanstack/react-query";
import { Loader } from "@/components/layout/loader";
import { CardGroupBox, CardStatBox } from "@/components/layout/card_stat";
import { getImagePath } from "@/lib/utils";

const chartConfig = {
    added: {
        label: "added",
        color: "#2563eb",
    },
    updated: {
        label: "updated",
        color: "#60a5fa",
    },
} satisfies ChartConfig

type UserActivityChart = {
    data: {
        min: number,
        max: number,
        activity: unknown[]
    }
}

export function UserActivityChart({
    data
}: UserActivityChart) {

    return (
        <ChartContainer config={chartConfig} className="min-h-[300px] w-full">
            <BarChart
                accessibilityLayer
                data={data.activity}
                layout="horizontal"
                margin={{
                    left: 0,
                    top: 10,
                    bottom: 10
                }}
            >
                <CartesianGrid vertical={true} />
                <XAxis
                    type="category"
                    dataKey="model"
                    tickLine={false}
                    tickMargin={10}
                    axisLine={false}
                />
                <YAxis
                    type="number"
                    dataKey="updated"
                    tickLine={false}
                    tickMargin={10}
                    axisLine={false}
                    scale={'linear'}
                    domain={[0, Number(data.max)]}
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <ChartLegend content={<ChartLegendContent />} />
                <Bar dataKey="added" fill="var(--color-added)" radius={4} />
                <Bar dataKey="updated" fill="var(--color-updated)" radius={4} />
            </BarChart>
        </ChartContainer>
    )
}


export function UserStats() {
    const { fetchWithAuth } = useAuth();
    const query = useQuery(
        {
            queryKey: ['dashboard', 'users'],
            retry: false,
            refetchOnMount: 'always',  // Always refetch when the component mounts
            queryFn: () =>
                fetchWithAuth(
                    `/api/v1/dashboard/users/activity/`,
                    {
                        method: 'GET',
                    }
                ).then((response) => response.json()),
        }
    );

    return (
        <CardGroupBox
            title="Users Stats"
        >
            <div className="grid grid-cols-4">
                {query.isPending ? (
                    <Loader />
                ) : query.isError || query.data?.error ? (
                    <p>Error loading data: {query.error?.message}</p>
                ) : (
                    <>
                        <div
                            className="col-span-1"
                        >
                            <CardStatBox
                                title={"Users"}
                                value={query.data.nb_users}
                            />

                        </div>
                        <div
                            className="col-span-3"
                        >
                            <UserActivityChart
                                data={query.data.activity}
                            />
                            <div
                                className="flex justify-center items-center"
                            >Updated rows in last month</div>
                        </div>
                    </>

                )}
            </div>
        </CardGroupBox>

    )
}

export function CurrentUserStats() {
    const { fetchWithAuth, user } = useAuth();
    const query = useQuery(
        {
            queryKey: ['dashboard', 'users'],
            retry: false,
            refetchOnMount: 'always',  // Always refetch when the component mounts
            queryFn: () =>
                fetchWithAuth(
                    `/api/v1/dashboard/users/activity/current/`,
                    {
                        method: 'GET',
                    }
                ).then((response) => response.json()),
        }
    );
    const imagePath = getImagePath(user?.avatar)
    return (
        <CardGroupBox
            title="Current User Stats"
        >
            <div className="grid grid-cols-4">
                {query.isPending ? (
                    <Loader />
                ) : query.isError || query.data?.error ? (
                    <p>Error loading data: {query.error?.message}</p>
                ) : (
                    <>
                        <div
                            className="col-span-1"
                        >
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
                                    {user?.email}
                                </div>
                            </div>


                        </div>
                        <div
                            className="col-span-3"
                        >
                            <UserActivityChart
                                data={query.data.activity}
                            />
                            <div
                                className="flex justify-center items-center"
                            >Updated rows in last month</div>
                        </div>
                    </>

                )}
            </div>
        </CardGroupBox>

    )
}