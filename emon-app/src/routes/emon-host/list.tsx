import { DataTable } from "@/components/data-table/data-table"
import { columns } from "./table-header-columns"
import { useAuth } from "@/hooks/use-auth";
import { useNavigate } from "react-router";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";

function ListEmonHost() {
  const { isAuthenticated, fetchWithAuth } = useAuth();
  const navigate = useNavigate();
  useEffect(() => {
      if (!isAuthenticated) {
        navigate("/login");
      }
    }, [isAuthenticated, navigate]);
  const { data, error, isError, isPending: loading } = useQuery(
    {
      queryKey: ['emon_hosts'],
      queryFn: () =>
        fetchWithAuth(
          `http://127.0.0.1:8000/api/v1/emon_host/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );

  return (
    <div className="container mx-auto py-10">
      {loading ? (
        <div>Loading...</div>
      ) : (
        <>
          {isError || !data || !data.data ? (
            <div>No data available: {error ? error.message : ''}</div>
          ) : (
          <DataTable columns={columns} data={data.data} />
          )}
        </>
      )}
    </div>
  )
}

export default ListEmonHost