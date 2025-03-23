import { columns } from "@/routes/archive-file/table-header-columns"
import { useAuth } from "@/hooks/use-auth";
import { useQuery } from "@tanstack/react-query";
import { ArchiveFileList } from "@/lib/types";
import ListView from "@/components/layout/list-item-view";

function ListArchiveFile() {
  const { fetchWithAuth } = useAuth();

  const items = useQuery(
    {
      queryKey: ['archive_file'],
      queryFn: () =>
        fetchWithAuth(
          `/api/v1/archive_file/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );

  return (
    <div className="w-full mx-auto">
      <ListView<ArchiveFileList, unknown>
        paneProps={{
          title: "Archive Files",
          classContainer: "",
          classHead: "w-full"
        }}
        columns={columns}
        queryResult={items}
      />
    </div>
  )
}

export default ListArchiveFile