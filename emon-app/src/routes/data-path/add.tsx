import {
  DataPathEdit,
  EditCrudComponentProps,
  PromiseFormActionType
} from "@/lib/types";
import { DataPathForm, DataPathFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";
import { requestCatchError, requestErrorResponse } from "@/helpers/formActions";

const AddDataPathAction = async(
  values: DataPathFormType,
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>,
): PromiseFormActionType => {
  
  const data = {
      ...values,
      id: undefined
  }
  const requestTitle = "Add Data Path";
  const redirect = `/data-path`;
  try {
    const response = await fetchWithAuth(
      `/api/v1/data_path/add/`,
      {
        method: 'POST',
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

function AddDataPath({
  is_dialog,
  successCallBack,
}: EditCrudComponentProps<DataPathEdit>) {
  const { fetchWithAuth } = useAuth();
  return (
    <div>
      <DataPathForm
        handleSubmit={
          (values: DataPathFormType) => AddDataPathAction(
            values,
            fetchWithAuth
          )
        }
        is_dialog={is_dialog}
        successCallBack={successCallBack}
      />
    </div>
  )
}

export default AddDataPath

