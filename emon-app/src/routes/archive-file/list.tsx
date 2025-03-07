import { columns } from "./table-header-columns"
import { useAuth } from "@/hooks/use-auth";
import { useNavigate } from "react-router";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArchiveFileList } from "@/lib/types";
import ListView from "@/components/layout/list-item-view";

function ListArchiveFile() {
  const { isAuthenticated, fetchWithAuth } = useAuth();
  const navigate = useNavigate();
  useEffect(() => {
      if (!isAuthenticated) {
        navigate("/login");
      }
    }, [isAuthenticated, navigate]);
  const items = useQuery(
    {
      queryKey: ['archive_file'],
      queryFn: () =>
        fetchWithAuth(
          `http://127.0.0.1:8000/api/v1/archive_file/`,
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