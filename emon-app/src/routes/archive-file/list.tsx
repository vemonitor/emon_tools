import { DataTable } from "@/components/data-table/data-table"
import { columns } from "./table-header-columns"
import { useAuth } from "@/hooks/use-auth";
import { useNavigate } from "react-router";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";

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
    <div className="container mx-auto py-10">
      {items.isPending ? (
        <div>Loading...</div>
      ) : (
        <>
          {items.isError || !items.data || !items.data.data ? (
            <div>No data available: {items.error ? items.error.message : ''}</div>
          ) : (
          <DataTable
            columns={columns}
            data={items.data.data}
          />
          )}
        </>
      )}
    </div>
  )
}

export default ListArchiveFile