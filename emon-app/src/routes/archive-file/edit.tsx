import { PromiseFormActionType, ArchiveFileEdit, EditCrudComponentProps } from "@/lib/types";
import { ArchiveFileForm, ArchiveFileFormType } from "@/routes/archive-file/form";
import { useAuth } from "@/hooks/use-auth";
import { useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { Loader } from "@/components/layout/loader";
import { validateIds } from "@/lib/utils";
import { requestCatchError, requestErrorResponse } from "@/helpers/formActions";

const EditArchiveFileAction = async (
  file_id: number,
  values: ArchiveFileFormType,
  fetchWithAuth: (
    input: RequestInfo,
    init?: RequestInit
  ) => Promise<Response>
): PromiseFormActionType => {


  const data = {
    ...values,
    id: file_id
  }
  const requestTitle = "Edit File";
  const redirect = `/archive-file`;
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
    return requestErrorResponse(
      response,
      requestTitle,
      redirect
    )
  } catch (error: unknown) {
    return requestCatchError(error, requestTitle)
  }
};

function EditArchiveFile({
  row_id,
  is_dialog,
  successCallBack,
}: EditCrudComponentProps<ArchiveFileEdit>) {
  const { fetchWithAuth } = useAuth();
  const { file_id } = useParams();
  const out_id = validateIds(file_id, row_id);
  const currentItem = useQuery(
    {
      queryKey: ['archive_file_edit'],
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
      ) : currentItem.isError || !currentItem.data || !currentItem.data.data ? (
        <div>No data available: {currentItem.error ? currentItem.error.message : ''}</div>
      ) : (
        <ArchiveFileForm
          handleSubmit={(values: ArchiveFileFormType) => EditArchiveFileAction(
            out_id,
            values,
            fetchWithAuth
          )}
          is_dialog={is_dialog}
          successCallBack={successCallBack}
          data={{ ...currentItem.data.data }}
        />
      )}
    </div>
  )
}

export default EditArchiveFile