import { columns } from "./table-header-columns"
import { useAuth } from "@/hooks/use-auth";
import { useQuery } from "@tanstack/react-query";
import ListView from "@/components/layout/list-item-view";
import { DataPathList } from "@/lib/types";

function ListDataPath() {
  const { fetchWithAuth } = useAuth();
    const items = useQuery(
    {
      queryKey: ['data_path'],
      queryFn: () =>
        fetchWithAuth(
          `/api/v1/data_path/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );

  return (
    <div className="w-full mx-auto">
      <ListView<DataPathList, unknown>
        paneProps={{
          title: "Data Paths",
          classContainer: "",
          classHead: "w-full"
        }}
        columns={columns}
        queryResult={items}
      />
    </div>
  )
}

export default ListDataPath