import { PromiseFormActionType, EditCrudComponentProps, EmonHostEdit } from "@/lib/types";
import { EmonHostForm, EmonHostFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";
import { useParams } from "react-router";
import { useQuery } from "@tanstack/react-query";
import { Loader } from "@/components/layout/loader";
import { validateIds } from "@/lib/utils";
import { requestCatchError, requestErrorResponse } from "@/helpers/formActions";

const EditEmonHostAction = async(
  host_id: number,
  values: EmonHostFormType,
  fetchWithAuth: (
    input: RequestInfo,
    init?: RequestInit
  ) => Promise<Response>
): PromiseFormActionType => {

  const data = {
      ...values,
      id: host_id
  }
  const requestTitle = "Edit Emoncms Host";
  const redirect = `/emon-host`;
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
    return requestErrorResponse(
      response,
      requestTitle,
      redirect
    )
  } catch (error: unknown) {
    return requestCatchError(error, requestTitle)
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