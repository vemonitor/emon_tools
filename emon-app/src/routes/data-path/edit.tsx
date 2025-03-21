import { AddActionType, DataPathEdit, EditCrudComponentProps } from "@/lib/types";
import { DataPathForm, DataPathFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";
import { useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { Loader } from "@/components/layout/loader";
import { validateIds } from "@/lib/utils";

const EditDataPathAction = async (
  path_id: number,
  values: DataPathFormType,
  fetchWithAuth: (
    input: RequestInfo,
    init?: RequestInit
  ) => Promise<Response>
): AddActionType => {

  const data = {
    ...values,
    id: path_id
  }

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

  return { success: true, redirect: `/data-path` };
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