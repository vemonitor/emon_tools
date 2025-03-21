import { AddActionType, EditCrudComponentProps, EmonHostEdit } from "@/lib/types";
import { EmonHostForm, EmonHostFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";
import { useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { Loader } from "@/components/layout/loader";
import { validateIds } from "@/lib/utils";

const EditEmonHostAction = async(
  host_id: number,
  values: EmonHostFormType,
  fetchWithAuth: (
    input: RequestInfo,
    init?: RequestInit
  ) => Promise<Response>
): AddActionType => {

  const data = {
      ...values,
      id: host_id
  }

  try {
    const response = await fetchWithAuth(
      `/api/v1/emon_host/edit/${host_id}/`,
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

  return {success: true, redirect: `/emon-host`};
};

function EditEmonHost({
  row_id,
  is_dialog,
  successCallBack,
}: EditCrudComponentProps<EmonHostEdit>) {
  const { fetchWithAuth } = useAuth();
  const { host_id } = useParams();
  const out_id = validateIds(host_id, row_id);
  const currentItem = useQuery(
    {
      queryKey: ['emon_host_edit'],
      retry: false,
      refetchOnMount: 'always',  // Always refetch when the component mounts
      queryFn: () =>
        fetchWithAuth(
          `/api/v1/emon_host/get/${out_id}/`,
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
        <EmonHostForm
          handleSubmit={(values: EmonHostFormType) => EditEmonHostAction(
            out_id,
            values,
            fetchWithAuth
          )}
          is_dialog={is_dialog}
          successCallBack={successCallBack}
          data={currentItem.data.data}
        />
      )}      
    </div>
  )
}

export default EditEmonHost