import { validateId } from "@/lib/utils";
import { useParams } from "react-router";
import { FinaViewer } from "../graph-fina/finaViewer";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/use-auth";
import { Loader } from "@/components/layout/loader";

function ViewArchiveFile() {
  const { fetchWithAuth } = useAuth();
  const { file_id } = useParams();
  const item_id = validateId(file_id);
  const currentItem = useQuery(
    {
      queryKey: ['archive_file_edit'],
      retry: false,
      refetchOnMount: 'always',  // Always refetch when the component mounts
      queryFn: () =>
        fetchWithAuth(
          `/api/v1/archive_file/get-path/${item_id}/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );
  return (
    <>
      {currentItem.isPending ? (
        <Loader />
      ) : currentItem.isError || !currentItem.data || !currentItem.data.data ? (
        <div>No data available: {currentItem.error ? currentItem.error.message : ''}</div>
      ) : (
        <FinaViewer
          slug={currentItem.data.data.slug}
        />
      )}
    </>


  )
}

export default ViewArchiveFile