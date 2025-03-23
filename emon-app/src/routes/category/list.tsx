import { columns } from "./table-header-columns"
import { useAuth } from "@/hooks/use-auth";
import { useQuery } from "@tanstack/react-query";
import ListView from "@/components/layout/list-item-view";
import { CategoryList } from "@/lib/types";

function ListCategory() {
  const { fetchWithAuth } = useAuth();
    const items = useQuery(
    {
      queryKey: ['category'],
      queryFn: () =>
        fetchWithAuth(
          `/api/v1/category/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );

  return (
    <div className="w-full mx-auto">
      <ListView<CategoryList, unknown>
        paneProps={{
          title: "Categories",
          classContainer: "",
          classHead: "w-full"
        }}
        columns={columns}
        queryResult={items}
      />
    </div>
  )
}

export default ListCategory