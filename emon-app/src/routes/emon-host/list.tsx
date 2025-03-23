import { columns, EmonHost } from "./table-header-columns"
import { useAuth } from "@/hooks/use-auth";
import { useQuery } from "@tanstack/react-query";
import ListView from "@/components/layout/list-item-view";

function ListEmonHost() {
  const { fetchWithAuth } = useAuth();
  
  const items = useQuery(
    {
      queryKey: ['emon_hosts'],
      retry: false,
      queryFn: () =>
        fetchWithAuth(
          `/api/v1/emon_host/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );

  return (
    <div className="w-full mx-auto">
      <ListView<EmonHost, unknown>
        paneProps={{
          title: "Emoncms Hosts",
          classContainer: "",
          classHead: "w-full"
        }}
        columns={columns}
        queryResult={items}
      />
    </div>
  )
}

export default ListEmonHost