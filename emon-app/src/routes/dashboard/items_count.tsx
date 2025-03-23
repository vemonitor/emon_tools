import { CardGroupBox, CardStatBox, CardStatListBox, ListBoxDataType } from "@/components/layout/card_stat";
import { Loader } from "@/components/layout/loader";
import Ut from "@/helpers/utils";
import { useAuth } from "@/hooks/use-auth";
import { useQuery } from "@tanstack/react-query";


const statsToView = [
    { label: "Emoncms Hosts", key: "nb_hosts" },
    { label: "Data Paths", key: "nb_paths" },
]

type DataInput = {
    [key: string]: {
        [source: string]: {
            [fileType: string]: number;
        };
    };
};


export function ItemsCountStat() {
    const { fetchWithAuth } = useAuth();
    const response = useQuery(
        {
            queryKey: ['dashboard'],
            retry: false,
            refetchOnMount: 'always',  // Always refetch when the component mounts
            queryFn: () =>
                fetchWithAuth(
                    `/api/v1/dashboard/view/`,
                    {
                        method: 'GET',
                    }
                ).then((response) => response.json()),
        }
    );
    const extract_by_file_type = (
        data: DataInput,
        file_type: string,
        file_source: string
    ): ListBoxDataType => {
        let result: ListBoxDataType = {
            count: 0,
            size: "0 Kb"
        };

        for (const source of Object.keys(data.nb_files)) {
            if (file_source === source) {
                const count = data.nb_files[source]?.[file_type] ?? 0;
                let size = data.file_sizes[source]?.[file_type] ?? 0;

                // Convert size to a number if it's a string
                if (typeof size === 'string' && !isNaN(Number(size))) {
                    size = Number(size)
                }

                result = {
                    count: count,
                    size: Ut.formatBytes(size)
                };
            }
        }

        return result;
    }
    return (
        <CardGroupBox
            title="Models Stats"
        >
            <div className="grid auto-rows-min gap-4 md:grid-cols-4">
                {response.isPending ? (
                    <Loader />
                ) : response.isError || response.data?.error ? (
                    <p>Error loading data: {response.error?.message}</p>
                ) : (
                    <>
                        {
                            statsToView.map((item: { label: string; key: string }, index: number) => (
                                <CardStatBox
                                    key={index}
                                    title={item.label}
                                    value={response.data[item.key]}
                                />
                            ))
                        }
                        <CardStatListBox
                            title="Archived Files"
                            data={extract_by_file_type(response.data, "fina", "archives")}
                        />
                        <CardStatListBox
                            title="Emoncms Files"
                            data={extract_by_file_type(response.data, "fina", "emoncms")}
                        />
                    </>
                )}
            </div>
        </CardGroupBox>

    )
}
