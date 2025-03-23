import { PromiseFormActionType, DataPathEdit, EditCrudComponentProps } from "@/lib/types";
import { DataPathForm, DataPathFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";
import { useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { Loader } from "@/components/layout/loader";
import { validateIds } from "@/lib/utils";
import { requestCatchError, requestErrorResponse } from "@/helpers/formActions";

const EditDataPathAction = async (
  path_id: number,
  values: DataPathFormType,
  fetchWithAuth: (
    input: RequestInfo,
    init?: RequestInit
  ) => Promise<Response>
): PromiseFormActionType => {

  const data = {
    ...values,
    id: path_id
  }
  const requestTitle = "Edit Data Path";
  const redirect = `/data-path`;
  try {
    const response = await fetchWithAuth(
      `/api/v1/data_path/edit/${path_id}/`,
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

function EditDataPath({
  row_id,
  is_dialog,
  successCallBack,
}: EditCrudComponentProps<DataPathEdit>) {
  const { fetchWithAuth } = useAuth();
  const { path_id } = useParams();
  const out_id = validateIds(path_id, row_id);
  const currentItem = useQuery(
    {
      queryKey: ['data_path_edit'],
      retry: false,
      refetchOnMount: 'always',  // Always refetch when the component mounts
      queryFn: () =>
        fetchWithAuth(
          `/api/v1/data_path/get/${out_id}/`,
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
        <DataPathForm
          handleSubmit={(values: DataPathFormType) => EditDataPathAction(
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

export default EditDataPath