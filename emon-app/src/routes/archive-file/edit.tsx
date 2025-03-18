import { AddActionType, ArchiveFileEdit } from "@/lib/types";
import { ArchiveFileForm, ArchiveFileFormType } from "@/routes/archive-file/form";
import { useAuth } from "@/hooks/use-auth";
import { useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { Loader } from "@/components/layout/loader";
import { validateIds } from "@/lib/utils";

const AddArchiveFileAction = async(
  file_id: number,
  values: ArchiveFileFormType,
  fetchWithAuth: (
    input: RequestInfo,
    init?: RequestInit
  ) => Promise<Response>
): AddActionType => {
  

  const data = {
      ...values,
      id: file_id
  }

  try {
    const response = await fetchWithAuth(
      `/api/v1/archive_file/edit/${file_id}/`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    ).then((response) => response.json())
    if (!response.success) {
      return {
        success: false,
        msg: response.msg,
        errors: response.errors,
        from_error: response.from_error,
      }
    }
  } catch (error: unknown) {
    console.log('Error fetching data:', error);
    return {
      success: false,
      msg: 'Unable to save data, please control all fields',
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }

  return {success: true, redirect: `/archive-file`};
};

type EditCrudComponentProps = {
  row_id?: number
  is_dialog?: boolean,
  successCallBack?: () => void
  data?: ArchiveFileEdit
}

function EditArchiveFile({
  row_id,
  is_dialog,
  successCallBack,
}: EditCrudComponentProps) {
  const { fetchWithAuth } = useAuth();
  const { file_id } = useParams();
  const out_id = validateIds(file_id, row_id);
  const currentItem = useQuery(
    {
      queryKey: ['archive_file', file_id],
      retry: false,
      refetchOnMount: 'always',  // Always refetch when the component mounts
      queryFn: () =>
        fetchWithAuth(
          `/api/v1/archive_file/get/${out_id}/`,
          {
            method: 'GET',
          }
        ).then((response) => response.json()),
    }
  );

  return (
    <div>
      {currentItem.isPending ? (
        <Loader />
      ) : (
        <>
          {currentItem.isError || !currentItem.data ? (
            <div>No data available: {currentItem.error ? currentItem.error.message : ''}</div>
          ) : (
            <ArchiveFileForm
                handleSubmit={(values: ArchiveFileFormType) => AddArchiveFileAction(
                out_id,
                values,
                fetchWithAuth
              )}
              is_dialog={is_dialog}
              successCallBack={successCallBack}
              data={{...currentItem.data.data}}
            />
          )}
        </>
      )}
      
    </div>
  )
}

export default EditArchiveFile